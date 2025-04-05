from flask_wtf import FlaskForm
from wtforms import (
    ValidationError,
    IntegerField,
    TextAreaField,
    RadioField,
    PasswordField,
)
import re
from library_app.models import Book
from wtforms.validators import DataRequired, Length, NumberRange


class BookRequestForm(FlaskForm):
    class Meta:
        csrf = False

    days = IntegerField("Days", validators=[DataRequired(), NumberRange(min=1, max=7)])


class CreateFeedbackForm(FlaskForm):
    class Meta:
        csrf = False

    bookid = IntegerField(
        "Book ID", validators=[DataRequired(), NumberRange(min=1)]
    )
    rating = RadioField(
        "Rating",
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
        validators=[DataRequired()],
    )
    content = TextAreaField(
        "Content", validators=[DataRequired(), Length(min=10, max=120)]
    )

    def validate_bookid(self, bookid):
        book = Book.query.get(bookid.data)
        if not book:
            raise ValidationError("That book doesn't exist.")

    def validate_content(self, content):
        pattern = r"^[\w\s.,!?'\-:;\"()]{10,120}$"
        if not re.match(pattern, content.data):
            raise ValidationError(
                "Content can only contain letters, digits, spaces and punctuation marks."
            )


class UpdateFeedbackForm(FlaskForm):
    class Meta:
        csrf = False

    rating = RadioField(
        "Rating",
        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
        validators=[DataRequired()],
    )
    content = TextAreaField(
        "Content", validators=[DataRequired(), Length(min=10, max=120)]
    )

    def validate_content(self, content):
        pattern = r"^[\w\s.,!?'\-:;\"()]{10,120}$"
        if not re.match(pattern, content.data):
            raise ValidationError(
                "Content can only contain letters, digits, spaces and punctuation marks."
            )


class DeleteAccountForm(FlaskForm):
    class Meta:
        csrf = False

    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=60)]
    )
