from datetime import datetime, timedelta
import os
from flask import request, jsonify, current_app
from library_app import db, ist, cache
from library_app.models import Section, Book, Request, IssuedBook
from library_app.utils import (
    custom_sort,
    save_file,
    delete_file,
    form_errors,
    auto_reject_and_revoke,
    validate_file,
)
from library_app.librarian.forms import (
    CreateSectionForm,
    UpdateSectionForm,
    CreateBookForm,
    UpdateBookForm,
)
from library_app.tasks import export_csv
from celery.result import AsyncResult
import os
from . import librarian


@librarian.route("/export/<name>", methods=["GET"])
def start_export(name):
    task = None
    if name in ["sections", "books", "requests", "issuedbooks"]:
        task = export_csv.delay(name)
    else:
        return jsonify({"error": "Invalid export name."}), 400
    return jsonify({"taskid": task.id}), 200


@librarian.route("/export-result/<taskid>", methods=["GET"])
def export_result(taskid):
    result = AsyncResult(taskid)
    if not result:
        return jsonify({"error": "Task not found."}), 404
    if result.ready():
        file_name = result.get()
        return jsonify({"status": "Task is ready.", "file": file_name}), 200
    else:
        return jsonify({"status": "Task is not ready."}), 400


@librarian.route("/section", methods=["POST"])
def create_section():
    data = request.form.to_dict()
    print(data)
    form = CreateSectionForm(data=data)
    if form.validate():
        picture_data = request.files.get("picture")
        if picture_data:
            return_val = validate_file(picture_data, "image")
            if return_val:
                return jsonify(return_val), 400
            picture = save_file(picture_data, "section")
        else:
            picture = "default_section_picture.jpeg"
        section = Section(
            title=form.title.data,
            description=form.description.data,
            picture=picture,
        )
        db.session.add(section)
        db.session.commit()
        cache.clear()
        return jsonify({"message": f"New Section {form.title.data} created!"}), 201
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@librarian.route("/section/<int:sectionid>", methods=["PUT"])
def update_section(sectionid):
    if sectionid == 1:
        return jsonify({"error": "You cannot modify Miscellaneous Section."}), 403
    data = request.form.to_dict()
    section = Section.query.get(sectionid)
    if not section:
        return jsonify({"error": f"Section {sectionid} not found."}), 404
    form = UpdateSectionForm(data=data, current_section=section)
    print(form.data)
    if form.validate():
        print("hello")
        picture_data = request.files.get("picture")
        if picture_data:
            return_val = validate_file(picture_data, "image")
            if return_val:
                return jsonify(return_val), 400
            if section.picture != "default_section_picture.jpeg":
                delete_file("section", section.picture)
            section.picture = save_file(picture_data, "section")
        elif form.delete_picture.data == "yes":
            if section.picture != "default_section_picture.jpeg":
                delete_file("section", section.picture)
            section.picture = "default_section_picture.jpeg"
        section.date_modified = datetime.now(ist).replace(tzinfo=None)
        section.title = form.title.data
        section.description = form.description.data
        db.session.commit()
        cache.clear()
        return jsonify({"message": f"Section {form.title.data} updated!"}), 200
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@librarian.route("/section/<int:sectionid>", methods=["DELETE"])
def delete_section(sectionid):
    if sectionid == 1:
        return jsonify({"error": "You cannot Miscellaneous Section"}), 403
    section = Section.query.get(sectionid)
    if not section:
        return jsonify({"error": f"Section {sectionid} not found."}), 404
    if section.picture != "default_section_picture.jpeg":
        delete_file("section", section.picture)
    for book in section.books:
        book.sectionid = 1
    db.session.delete(section)
    db.session.commit()
    cache.clear()
    return "", 204


@librarian.route("/book/<int:sectionid>", methods=["POST"])
def create_book(sectionid):
    section = Section.query.get(sectionid)
    if not section:
        return jsonify({"error": f"Section {sectionid} not found."}), 404
    data = request.form.to_dict()
    print(data)
    form = CreateBookForm(data=data)
    print(form.data)
    if form.validate():
        picture_data = request.files.get("picture")
        if picture_data:
            return_val = validate_file(picture_data, "image")
            if return_val:
                return jsonify(return_val), 400
            picture = save_file(picture_data, os.path.join("book", "pictures"))
        else:
            picture = "default_book_picture.png"
        pdf_file_data = request.files.get("pdf_file")
        if pdf_file_data:
            return_val = validate_file(pdf_file_data, "pdf")
            if return_val:
                return jsonify(return_val), 400
            pdf_file = save_file(pdf_file_data, os.path.join("book", "pdfs"))
        else:
            pdf_file = "sample_pdf.pdf"
        book = Book(
            title=form.title.data,
            author=form.author.data,
            picture=picture,
            description=form.description.data,
            sectionid=sectionid,
            pdf_file=pdf_file,
        )
        db.session.add(book)
        db.session.commit()
        cache.clear()
        return jsonify({"message": f"New Book {form.title.data} created!"}), 201
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@librarian.route("/book/<int:bookid>", methods=["GET"])
def book(bookid):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": f"Book {bookid} not found"}), 404
    auto_reject_and_revoke(bookid=bookid)
    issuedbooks = IssuedBook.query.filter_by(bookid=bookid, status="current").all()
    requests = Request.query.filter_by(bookid=bookid, status="pending").all()
    return (
        jsonify(
            {
                "issuedbooks": custom_sort(issuedbooks, ["user", "book"]),
                "requests": custom_sort(requests, ["user", "book"]),
            }
        ),
        200,
    )


@librarian.route("/book/<int:bookid>", methods=["PUT"])
def update_book(bookid):
    data = request.form.to_dict()
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": f"Book {bookid} not found."}), 404
    form = UpdateBookForm(data=data, current_book=book)
    if form.validate():
        picture_data = request.files.get("picture")
        if picture_data:
            return_val = validate_file(picture_data, "image")
            if return_val:
                return jsonify(return_val), 400
            if book.picture != "default_book_picture.png":
                delete_file(
                    os.path.join("book", "pictures"),
                    book.picture,
                )
            book.picture = save_file(picture_data, os.path.join("book", "pictures"))
        elif form.delete_picture.data == "yes":
            if book.picture != "default_book_picture.png":
                delete_file(os.path.join("book", "pictures"), book.picture)
            book.picture = "default_book_picture.png"
        pdf_file_data = request.files.get("pdf_file")
        if pdf_file_data:
            return_val = validate_file(pdf_file_data, "pdf")
            if return_val:
                return jsonify(return_val), 400
            if book.pdf_file != "sample_pdf.pdf":
                delete_file(os.path.join("book", "pdfs"), book.pdf_file)
            book.pdf_file = save_file(pdf_file_data, os.path.join("book", "pdfs"))
        elif form.delete_pdf_file.data == "yes":
            if book.pdf_file != "sample_pdf.pdf":
                delete_file(os.path.join("book", "pdfs"), book.pdf_file)
            book.pdf_file = "sample_pdf.pdf"
        book.title = form.title.data
        book.author = form.author.data
        book.description = form.description.data
        book.sectionid = form.sectionid.data
        db.session.commit()
        cache.clear()
        return jsonify({"message": f"Book {book.title} updated!"}), 200
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@librarian.route("/view-book/<int:bookid>", methods=["GET"])
@cache.cached()
def view_book(bookid):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    return (
        jsonify(
            {
                "bookid": book.bookid,
                "title": book.title,
                "pdf_file": book.pdf_file,
                "datetime": datetime.now(ist),
            }
        ),
        200,
    )


@librarian.route("/book/<int:bookid>", methods=["DELETE"])
def delete_book(bookid):
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    if book.picture != "default_book_picture.png":
        delete_file(os.path.join("book", "pictures"), book.picture)
    if book.pdf_file != "sample_pdf.pdf":
        delete_file(os.path.join("book", "pdfs"), book.pdf_file)
    db.session.delete(book)
    db.session.commit()
    cache.clear()
    return "", 204


@librarian.route("/requests", methods=["GET"])
def requests():
    auto_reject_and_revoke()
    return (
        jsonify(
            {
                "requests": custom_sort(
                    Request.query.filter_by(status="pending").all(), ["book", "user"]
                ),
                "issuedbooks": custom_sort(
                    IssuedBook.query.filter_by(status="current").all(), ["book", "user"]
                ),
            }
        ),
        200,
    )
