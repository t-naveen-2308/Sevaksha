import secrets
import os
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
from flask import Blueprint, current_app, jsonify, request
from sevaksha_app import db
from flask_mail import Message
from sevaksha_app import mail
from datetime import datetime
import jwt
from weasyprint import HTML
import inspect


class DecoratedBlueprint(Blueprint):
    def __init__(self, name, import_name, decorators=None, **kwargs):
        super().__init__(name, import_name, **kwargs)
        self.decorators = decorators

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        if view_func and self.decorators:
            for decorator in reversed(self.decorators):
                view_func = decorator(view_func)
        super().add_url_rule(rule, endpoint, view_func, **options)


def login_required():
    def wrapper(fn):
        @wraps(fn)
        def func(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return "Token is missing", 403
            from sevaksha_app.models import User, BlacklistedToken

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
                print(user)
                if not user:
                    return jsonify({"error": "Please login again."}), 404
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
