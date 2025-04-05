import os
from datetime import datetime, timedelta
from celery import shared_task
from flask import current_app, render_template
import flask_excel as excel
from library_app.utils import send_report_email, send_remainder_email


@shared_task(ignore_result=False)
def export_csv(name):
    from library_app.models import User, Book, Section, Request, IssuedBook
    from library_app.utils import export_empty
    from library_app import db

    csv_out = None
    file_name = None
    if name == "sections":
        file_name = "sections.csv"
        column_names = ["Section Title", "Description", "Date Modified"]
        sections = Section.query.with_entities(
            Section.title.label("Section Title"),
            Section.description.label("Description"),
            Section.date_modified.label("Date Modified"),
        ).all()
        if len(sections) == 0:
            return export_empty(file_name, column_names)
        csv_out = excel.make_response_from_query_sets(
            sections,
            column_names,
            "csv",
            file_name,
        )
    elif name == "books":
        file_name = "books.csv"
        column_names = [
            "Book Title",
            "Author",
            "Description",
            "Date Modified",
            "Section Title",
        ]
        books = (
            db.session.query(
                Book.title.label("Book Title"),
                Book.author.label("Author"),
                Book.description.label("Description"),
                Book.date_modified.label("Date Modified"),
                Section.title.label("Section Title"),
            )
            .select_from(Book)
            .join(Section, Book.sectionid == Section.sectionid)
            .all()
        )
        if len(books) == 0:
            return export_empty(file_name, column_names)
        csv_out = excel.make_response_from_query_sets(
            books,
            column_names,
            "csv",
            file_name,
        )
    elif name == "requests":
        file_name = "requests.csv"
        column_names = ["Username", "Book Title", "Days", "Date Created"]
        requests = (
            db.session.query(
                User.username.label("Username"),
                Book.title.label("Book Title"),
                Request.days.label("Days"),
                Request.date_modified.label("Date Created"),
            )
            .select_from(Request)
            .join(User, User.userid == Request.userid)
            .join(Book, Book.bookid == Request.bookid)
            .filter(Request.status == "pending")
            .all()
        )
        if len(requests) == 0:
            return export_empty(file_name, column_names)
        csv_out = excel.make_response_from_query_sets(
            requests,
            column_names,
            "csv",
            file_name,
        )
    else:
        file_name = "issuedbooks.csv"
        column_names = ["Username", "Book Title", "From Date", "To Date"]
        issuedbooks = (
            db.session.query(
                User.username.label("Username"),
                Book.title.label("Book Title"),
                IssuedBook.from_date.label("From Date"),
                IssuedBook.to_date.label("To Date"),
            )
            .select_from(IssuedBook)
            .join(User, User.userid == IssuedBook.userid)
            .join(Book, Book.bookid == IssuedBook.bookid)
            .filter(IssuedBook.status == "current")
            .all()
        )
        if len(issuedbooks) == 0:
            return export_empty(file_name, column_names)
        csv_out = excel.make_response_from_query_sets(
            issuedbooks,
            column_names,
            "csv",
            file_name,
        )
    with open(
        os.path.join(current_app.root_path, "static", "user", "stats", file_name), "wb"
    ) as file:
        file.write(csv_out.data)
    return file_name


@shared_task(ignore_result=False)
def generate_data(userid):
    from library_app import cache

    cache_key = f"generate_data_{userid}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    from library_app.models import User, IssuedBook, Section, Book, Request
    from library_app.utils import generate_plots

    current_user = User.query.get(userid)
    dicti1 = {"Miscellaneous": 0}
    issuedbooks = (
        IssuedBook.query.all()
        if current_user.urole == "librarian"
        else current_user.issuedbooks
    )
    issuedbook_count = {"current": 0, "returned": 0}
    for issuedbook in issuedbooks:
        issuedbook_count[issuedbook.status] += 1
        title = issuedbook.book.section.title
        if title not in dicti1:
            dicti1[title] = 1
        else:
            dicti1[title] += 1

    d = generate_plots(dicti1, "section", current_user.username)

    requests = (
        Request.query.all()
        if current_user.urole == "librarian"
        else current_user.requests
    )
    dicti2 = {"Accepted": 0, "Pending": 0, "Rejected": 0}
    for request in requests:
        dicti2[request.status.title()] += 1
    d.update(generate_plots(dicti2, "status", current_user.username))

    if current_user.urole == "user":
        cache.set(cache_key, d, timeout=300)
        return d

    else:
        d.update(
            {
                "cards": [
                    ("Active Users", User.query.filter_by(authenticated=True).count()),
                    ("Total Sections", Section.query.count()),
                    ("Total Books", Book.query.count()),
                    ("Total Requests", len(requests)),
                    ("Pending Requests", dicti2["Pending"]),
                    ("Accepted Requests", dicti2["Accepted"]),
                    ("Rejected Requests", dicti2["Rejected"]),
                    ("Total IssuedBooks", len(issuedbooks)),
                    ("Current IssuedBooks", issuedbook_count["current"]),
                    ("Completed IssuedBooks", issuedbook_count["returned"]),
                ]
            }
        )
        cache.set(cache_key, d, timeout=300)
        return d


@shared_task(ignore_result=True)
def daily_remainder():
    from library_app import ist
    from library_app.models import User, Book

    users = User.query.all()
    for user in users:
        if user.urole != "librarian":
            issuedbooks = []
            date = datetime.now(ist) + timedelta(days=1)
            for issuedbook in user.issuedbooks:
                if issuedbook.status == "current" and date > issuedbook.to_date:
                    issuedbooks.append(issuedbook)
            if len(issuedbooks):
                send_remainder_email(
                    user,
                    [
                        (issuedbook.book.title, issuedbook.to_date)
                        for issuedbook in issuedbooks
                    ],
                )
    return "OK"


@shared_task(ignore_result=True)
def monthly_report():
    from library_app import ist
    from library_app.models import User, IssuedBook, Section, Book, Request
    from library_app.utils import generate_plots, get_month_range
    from sqlalchemy import and_

    start_date, end_date = get_month_range(datetime.now(ist))

    current_user = User.query.get(1)
    dicti1 = {"Miscellaneous": 0}
    issuedbooks = IssuedBook.query.filter(
        and_(IssuedBook.from_date >= start_date, IssuedBook.from_date <= end_date)
    ).all()
    print(issuedbooks)
    issuedbook_count = {"current": 0, "returned": 0}
    for issuedbook in issuedbooks:
        issuedbook_count[issuedbook.status] += 1
        title = issuedbook.book.section.title
        if title not in dicti1:
            dicti1[title] = 1
        else:
            dicti1[title] += 1

    d = generate_plots(dicti1, "section", current_user.username, True)

    requests = Request.query.filter(
        and_(Request.date_modified >= start_date, Request.date_modified <= end_date)
    ).all()
    print(requests)
    dicti2 = {"Accepted": 0, "Pending": 0, "Rejected": 0}
    for request in requests:
        dicti2[request.status.title()] += 1
    d.update(generate_plots(dicti2, "status", current_user.username, True))
    d.update(
        {
            "cards": [
                (
                    "Total Sections",
                    Section.query.filter(
                        and_(
                            Section.date_modified >= start_date,
                            Section.date_modified <= end_date,
                        )
                    ).count(),
                ),
                (
                    "Total Books",
                    Book.query.filter(
                        and_(
                            Book.date_modified >= start_date,
                            Book.date_modified <= end_date,
                        )
                    ).count(),
                ),
                ("Total Requests", len(requests)),
                ("Pending Requests", dicti2["Pending"]),
                ("Accepted Requests", dicti2["Accepted"]),
                ("Rejected Requests", dicti2["Rejected"]),
                ("Total IssuedBooks", len(issuedbooks)),
                ("Current IssuedBooks", issuedbook_count["current"]),
                ("Completed IssuedBooks", issuedbook_count["returned"]),
            ]
        }
    )
    report_date = datetime.now(ist).strftime("%B %Y")
    html_report = render_template(
        "report.html",
        paths=d,
        report_date=report_date,
    )
    librarian = User.query.get(1)
    send_report_email(librarian.email, html_report)
    return "OK"


@shared_task(ignore_result=True)
def delete_blacklisted_tokens():
    from library_app import db, ist
    from library_app.models import BlacklistedToken

    try:
        expired_tokens = BlacklistedToken.query.filter(
            BlacklistedToken.expiry <= datetime.now(ist)
        ).all()
        for blacklisted_token in expired_tokens:
            db.session.delete(blacklisted_token)
        db.session.commit()
        print(f"Deleted {len(expired_tokens)} blacklisted tokens.")
    except Exception as e:
        print(f"Error occurred while deleting blacklisted tokens: {e}")
        db.session.rollback()
        raise
