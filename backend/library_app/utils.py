import secrets
import os
import redis
from functools import wraps
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from flask import Blueprint, current_app, jsonify, request
from library_app import db, ist
from flask_mail import Message
from library_app import mail
from datetime import datetime, timedelta
import jwt
from weasyprint import HTML
import inspect
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


class DecoratedBlueprint(Blueprint):
    def __init__(self, name, import_name, decorators=None, **kwargs):
        super().__init__(name, import_name, **kwargs)
        self.decorators = decorators

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        if view_func and self.decorators:
            for decorator in reversed(self.decorators):
                view_func = decorator(view_func)
        super().add_url_rule(rule, endpoint, view_func, **options)


def login_required(role="user or librarian"):
    def wrapper(fn):
        @wraps(fn)
        def func(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return "Token is missing", 403
            from library_app.models import User, BlacklistedToken

            try:
                if token.startswith("Bearer "):
                    token = token[len("Bearer ") :]
                blacklisted_token = BlacklistedToken.query.filter_by(
                    token=token
                ).first()
                if blacklisted_token:
                    if blacklisted_token.is_expired():
                        db.session.delete(blacklisted_token)
                        db.session.commit()
                        return (
                            jsonify(
                                {"error": "Token has expired. Please login again."}
                            ),
                            403,
                        )
                    else:
                        return jsonify({"message": "Token is blacklisted"}), 401
                decoded_token = jwt.decode(
                    token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
                )
                userid = decoded_token.get("userid")
                user = User.query.get(userid)
                if not user:
                    return jsonify({"error": "Please login again."}), 404
                if user.urole != role and role != "user or librarian":
                    return jsonify({"error": "Not authorized."}), 403
                sig = inspect.signature(fn)
                if "userid" in sig.parameters:
                    return fn(userid=userid, *args, **kwargs)
                else:
                    return fn(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return (
                    jsonify({"error": "Token has expired. Please login again."}),
                    403,
                )
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid token. Please login"}), 403
            except Exception:
                db.session.rollback()
                return jsonify({"error": "An unexpected error occurred."}), 500

        return func

    return wrapper


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"error": "A database error occurred."}), 500
        except Exception:
            db.session.rollback()
            return jsonify({"error": "An unexpected error occurred."}), 500

    return wrapper


def make_cache_key(userid=None, *args, **kwargs):
    return f"{request.endpoint}:{'userid:'+userid+':' if userid else ''}{':'.join(map(str, args))}:{':'.join(f'{k}={v}' for k, v in kwargs.items())}"


def clear_user_cache(user_id):
    redis_client = redis.Redis(
        host=current_app.config["CACHE_REDIS_HOST"],
        port=current_app.config["CACHE_REDIS_PORT"],
        db=0,
    )
    cache_key_pattern = f"user_id:{user_id}:*"
    for key in redis_client.scan_iter(pattern=cache_key_pattern):
        redis_client.delete(key)


def form_errors(errors):
    return next(iter(errors)) + " : " + errors[next(iter(errors))][0]


def validate_file(file, type="image"):
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    if type == "image":
        if file.mimetype not in ["image/jpeg", "image/png", "image/jpg"]:
            return {"error": "Image type must be jpg or jpeg or png."}
        if file_ext not in [".jpeg", ".jpg", ".png"]:
            return {"error": "Image extension must be .jpg or .jpeg or .png."}
        return ""
    elif type == "pdf":
        if file.mimetype != "application/pdf":
            return {"error": "PDF type must be pdf."}
        if file_ext != ".pdf":
            return {"error": "PDF extension must be .pdf."}
        return ""
    else:
        return {"error": "Unsupported file type."}


def export_empty(file_name, column_names):
    file_path = os.path.join(
        current_app.root_path, "static", "user", "stats", file_name
    )
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        file.write(",".join(column_names) + "\n")
    return file_name


def save_file(file, path):
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    file_name = secrets.token_hex(16) + file_ext
    file_path = os.path.join(current_app.root_path, "static", path, file_name)
    with open(file_path, "wb") as f:
        f.write(file.read())
    return file_name


def delete_file(path, file):
    file_path = os.path.join(current_app.root_path, "static", path, file)
    if os.path.exists(file_path):
        os.remove(file_path)


def get_month_range(date):
    first_day = date  # .replace(day=1)
    last_day_previous = first_day  # - timedelta(days=1)
    first_day_previous = last_day_previous.replace(day=1)
    return first_day_previous, last_day_previous


def generate_plots(dicti, name, username, flag=False, threshold=5):
    lis = [(key, dicti[key]) for key in dicti]
    lis.sort(key=lambda x: (-x[1], x[0]))
    if len(lis) > threshold:
        key, value = lis[threshold - 1]
        for i in range(threshold, len(lis)):
            value += lis[i][1]
        lis = lis[: threshold - 1] + [("Others", value)]
    data = {
        name.title(): [lis[i][0] for i in range(len(lis))],
        "Frequency": [lis[i][1] for i in range(len(lis))],
    }
    df = pd.DataFrame(data).sort_values(by="Frequency", ascending=False)
    background_color = "#dcdada"
    plt.figure(figsize=(10, 6), facecolor=background_color)
    sns.set_style("whitegrid")
    ax = sns.barplot(
        x=name.title(),
        y="Frequency",
        data=df,
        hue=name.title(),
        palette="husl",
        legend=False,
    )
    desired_width = 0.5
    for patch in ax.patches:
        patch.set_width(desired_width)
        patch.set_x(patch.get_x() + (patch.get_width() - desired_width) / 2)
    ax.set_facecolor(background_color)
    plt.xlabel(name.title())
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    bar_chart_path = os.path.join(
        current_app.root_path,
        "static",
        "user",
        "stats",
        f"{username}_{name}_bar_chart{'1' if flag else ''}.png",
    )
    if os.path.exists(bar_chart_path):
        os.remove(bar_chart_path)
    plt.savefig(bar_chart_path)
    plt.close()
    plt.figure(figsize=(7, 7), facecolor=background_color)
    non_zero_sections = df[df["Frequency"] > 0]
    colors = sns.color_palette("husl", len(non_zero_sections))
    explode = [0.02] * len(non_zero_sections)
    plt.pie(
        non_zero_sections["Frequency"],
        labels=non_zero_sections[name.title()],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.85,
        explode=explode,
        colors=colors,
        wedgeprops=dict(width=0.3),
    )
    plt.gca().set_facecolor(background_color)
    plt.axis("equal")
    plt.tight_layout()
    plt.legend(title=name.title(), loc="upper right")
    pie_chart_path = os.path.join(
        current_app.root_path,
        "static",
        "user",
        "stats",
        f"{username}_{name}_pie_chart{'1' if flag else ''}.png",
    )
    if os.path.exists(pie_chart_path):
        os.remove(pie_chart_path)
    plt.savefig(pie_chart_path)
    plt.close()
    return {
        f"{name}_bar_path": f"{username}_{name}_bar_chart{'1' if flag else ''}.png",
        f"{name}_pie_path": f"{username}_{name}_pie_chart{'1' if flag else ''}.png",
    }


def send_reset_email(user, role):
    token = user.get_reset_token()
    reset_link = f"http://localhost:5000/{'' if role == 'main' else 'user/account/' if user.urole == 'user' else 'librarian/account/'}password-reset/{token}"

    message = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )

    message.body = f"""Dear {user.name},

We have received a request to reset your password. If you initiated this request, please use the following link to reset your password:

{reset_link}

This link will expire in 30 minutes. If you did not request a password reset, please ignore this email. No changes will be made to your account.

If you encounter any issues or need further assistance, please contact our support team at support@demo.com.

Best regards,
The Support Team
"""

    mail.send(message)


def format_date(date):
    if not isinstance(date, datetime):
        date = datetime.fromisoformat(date)
    return date.strftime("%B %d, %Y at %I:%M %p")


def send_remainder_email(user, books_with_return_dates):
    books_info = "\n".join(
        [
            f"**Book Name:** {book_name} | **Return Date:** {format_date(return_date)}"
            for book_name, return_date in books_with_return_dates
        ]
    )

    message = Message(
        "Book Return Reminder", sender="noreply@demo.com", recipients=[user.email]
    )

    message.body = f"""Dear {user.name},

This is a friendly reminder that the return dates for the following books are approaching. Please ensure that the books are returned by their respective due dates.

{books_info}

If you have already returned any of these books or need to extend the return dates, please contact us at support@demo.com.

Thank you for your attention to this matter.

Best regards,
The Library Team
"""

    mail.send(message)


def send_report_email(email, html_report):
    current_month_year = datetime.now().strftime("%B %Y")

    pdf_path = os.path.join(
        current_app.root_path,
        "static",
        "user",
        "stats",
        f"Monthly Report {current_month_year}.pdf",
    )
    HTML(string=html_report).write_pdf(pdf_path)

    message = Message(
        f"Monthly Report for {current_month_year}",
        sender="noreply@demo.com",
        recipients=[email],
    )

    message.body = """Dear Librarian,

Please find attached the monthly report for the library. The report includes details of all active users and other relevant data.

If you have any questions or need further assistance, feel free to contact us.

Best regards,
The Library Team
"""

    with open(pdf_path, "rb") as pdf_file:
        message.attach(
            filename=os.path.basename(pdf_path),
            content_type="application/pdf",
            data=pdf_file.read(),
        )

    mail.send(message)
    os.remove(pdf_path)


def auto_reject_and_revoke(bookid=None, userid=None):
    from library_app.models import Request, IssuedBook

    query = Request.query.filter_by(status="pending")
    if bookid:
        query = query.filter_by(bookid=bookid)
    if userid:
        query = query.filter_by(userid=userid)
    outdated_requests = query.all()
    for outdated_request in outdated_requests:
        if datetime.now(ist).replace(
            tzinfo=None
        ) > outdated_request.date_modified + timedelta(days=7):
            outdated_request.status = "rejected"
    db.session.commit()
    query = IssuedBook.query.filter_by(status="current")
    if bookid:
        query = query.filter_by(bookid=bookid)
    if userid:
        query = query.filter_by(userid=userid)
    issuedbooks = query.all()
    for issuedbook in issuedbooks:
        if datetime.now(ist).replace(tzinfo=None) > issuedbook.to_date:
            issuedbook.status = "returned"
    db.session.commit()


def custom_sort(lis, include_relationships=[], flag=True):
    if len(lis) == 0:
        return []
    cs = lis[0].__class__.__name__
    if cs == "Section":
        sections = lis
        sections = sorted(
            sections,
            key=lambda x: (x.date_modified, len(x.books)) if flag else len(x.books),
            reverse=True,
        )
        lis = sections
    elif cs == "Book":
        books = lis
        books = sorted(
            books,
            key=lambda x: (
                sum(feedback.rating for feedback in x.feedbacks),
                x.date_modified,
            ),
            reverse=True,
        )
        lis = books
    elif cs == "Request":
        requests = lis
        requests1 = sorted(
            [request for request in requests if request.status == "pending"],
            key=lambda x: (x.date_modified, x.days),
            reverse=True,
        )
        requests2 = sorted(
            [request for request in requests if request.status == "accepted"],
            key=lambda x: (x.date_modified, x.days),
            reverse=True,
        )
        requests3 = sorted(
            [request for request in requests if request.status == "rejected"],
            key=lambda x: (x.date_modified, x.days),
            reverse=True,
        )
        requests = requests1 + requests2 + requests3
        lis = requests
    elif cs == "IssuedBook":
        issuedbooks = lis
        issuedbooks1 = sorted(
            [
                issuedbook
                for issuedbook in issuedbooks
                if issuedbook.status == "current"
            ],
            key=lambda x: (x.to_date, x.from_date),
        )
        issuedbooks2 = sorted(
            [
                issuedbook
                for issuedbook in issuedbooks
                if issuedbook.status == "returned"
            ],
            key=lambda x: (x.to_date, x.from_date),
            reverse=True,
        )
        issuedbooks = issuedbooks1 + issuedbooks2
        lis = issuedbooks
    elif cs == "Feedback":
        feedbacks = lis
        feedbacks = sorted(
            feedbacks,
            key=lambda x: (x.date_modified, x.rating),
            reverse=True,
        )
        lis = feedbacks
    lis = [item.to_dict(include_relationships) for item in lis]
    return lis
