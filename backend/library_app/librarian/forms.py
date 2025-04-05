from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    TextAreaField,
    ValidationError,
    RadioField,
)
import re
from library_app.models import Section, Book
from wtforms.validators import DataRequired, Length, NumberRange


class CreateSectionForm(FlaskForm):
    class Meta:
        csrf = False

    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=60)])
    description = TextAreaField(
        "Description", validators=[DataRequired(), Length(min=10, max=120)]
    )

    def validate_title(self, title):
        pattern = r"^[A-Za-z0-9\s\-',.!?]{3,60}$"
        if not re.match(pattern, title.data):
            raise ValidationError(
                "Title can only contain letters, digits, spaces, spaces, hyphens, commas, periods, exclamation and question marks."
            )
        section = Section.query.filter_by(title=title.data).first()
        if section:
            raise ValidationError(
                "That title already exists. Please choose a different title."
            )

    def validate_description(self, description):
        pattern = r"^[\w\s.,!?'\-:;\"()]{10,120}$"
        if not re.match(pattern, description.data):
            raise ValidationError(
                "Description can only contain letters, digits, spaces and punctuation marks."
            )


class UpdateSectionForm(FlaskForm):
    class Meta:
        csrf = False

    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=60)])
    delete_picture = RadioField(
        "Delete Picture",
        choices=[("yes", "yes"), ("no", "no")],
        validators=[DataRequired()],
    )
    description = TextAreaField(
        "Description", validators=[DataRequired(), Length(min=10, max=120)]
    )

    def __init__(self, *args, **kwargs):
        self.current_section = kwargs.pop("current_section", None)
        super().__init__(*args, **kwargs)

    def validate_title(self, title):
        pattern = r"^[A-Za-z0-9\s\-',.!?]{3,60}$"
        if not re.match(pattern, title.data):
            raise ValidationError(
                "Title can only contain letters, digits, spaces, spaces, hyphens, commas, periods, exclamation and question marks."
            )
        if title.data != self.current_section.title:
            section = Section.query.filter_by(title=title.data).first()
            if section:
                raise ValidationError(
                    "That Section Title already exists. Please choose a different title."
                )

    def validate_description(self, description):
        pattern = r"^[\w\s.,!?'\-:;\"()]{10,120}$"
        if not re.match(pattern, description.data):
            raise ValidationError(
                "Description can only contain letters, digits, spaces and punctuation marks."
            )


class CreateBookForm(FlaskForm):
    class Meta:
        csrf = False

    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=60)])
    author = StringField("Author", validators=[DataRequired(), Length(min=3, max=60)])
    description = TextAreaField(
        "Description", validators=[DataRequired(), Length(min=10, max=120)]
    )

    def validate_title(self, title):
        pattern = r"^[A-Za-z0-9\s\-',.!?]{3,60}$"
        if not re.match(pattern, title.data):
            raise ValidationError(
                "Title can only contain letters, digits, spaces, spaces, hyphens, commas, periods, exclamation and question marks."
            )
        book = Book.query.filter_by(title=title.data).first()
        if book:
            raise ValidationError(
                "That book title already exists. Please choose a different title."
            )

    def validate_author(self, author):
        pattern = r"^[A-Za-z\s,'.]{3,60}$"
        if not re.match(pattern, author.data):
            raise ValidationError(
                "Author Name can only have only have letters, spaces, apostrophes, commas and period."
            )

    def validate_description(self, description):
        pattern = r"^[\w\s.,!?'\-:;\"()]{10,120}$"
        if not re.match(pattern, description.data):
            raise ValidationError(
                "Description can only contain letters, digits, spaces and punctuation marks."
            )

    def validate_sectionid(self, sectionid):
        section = Section.query.get(sectionid.data)
        if not section:
            raise ValidationError("Invalid section selected.")


class UpdateBookForm(FlaskForm):
    class Meta:
        csrf = False

    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=60)])
    author = StringField("Author", validators=[DataRequired(), Length(min=3, max=60)])
    delete_picture = RadioField(
        "Delete Existing Picture",
        choices=[("yes", "yes"), ("no", "no")],
        validators=[DataRequired()],
    )
    delete_pdf_file = RadioField(
        "Delete Existing PDF",
        choices=[("yes", "yes"), ("no", "no")],
        validators=[DataRequired()],
    )
    sectionid = IntegerField(
        "Section ID", validators=[DataRequired(), NumberRange(min=1)]
    )
    description = TextAreaField(
        "Description", validators=[DataRequired(), Length(min=10, max=120)]
    )

    def __init__(self, *args, **kwargs):
        self.current_book = kwargs.pop("current_book", None)
        super().__init__(*args, **kwargs)

    def validate_title(self, title):
        pattern = r"^[A-Za-z0-9\s\-',.!?]{3,60}$"
        if not re.match(pattern, title.data):
            raise ValidationError(
                "Title can only contain letters, digits, spaces, spaces, hyphens, commas, periods, exclamation and question marks."
            )
        if title.data != self.current_book.title:
            book = Book.query.filter_by(title=title.data).first()
            if book:
                raise ValidationError(
                    "That Book Title already exists. Please choose a different title."
                )

    def validate_author(self, author):
        pattern = r"^[A-Za-z\s,'.]{3,60}$"
        if not re.match(pattern, author.data):
            raise ValidationError(
                "Author Name can only have only have letters, spaces, apostrophes, commas and period."
            )

    def validate_description(self, description):
        pattern = r"^[\w\s.,!?'\-:;\"()]{10,120}$"
        if not re.match(pattern, description.data):
            raise ValidationError(
                "Description can only contain letters, digits, spaces and punctuation marks."
            )

    def validate_sectionid(self, sectionid):
        section = Section.query.get(sectionid.data)
        if not section:
            raise ValidationError("Invalid section selected.")
