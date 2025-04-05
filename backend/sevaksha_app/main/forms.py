from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    ValidationError,
)
from wtforms.validators import DataRequired, Length, EqualTo
import re
from sevaksha_app.models import User
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    class Meta:
        csrf = False

    search_term = StringField(
        "Search Term", validators=[DataRequired(), Length(min=1, max=60)]
    )

    def validate_search_term(self, search_term):
        pattern = r"^[A-Za-z0-9\s\-',.!?]{1,60}$"
        if not re.match(pattern, search_term.data):
            raise ValidationError(
                "Search Term can only contain letters, digits, spaces, spaces, hyphens, commas, periods, exclamation and question marks."
            )


class RegistrationForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=60)])
    email = StringField("Email", validators=[DataRequired()])
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=5, max=32)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=60)]
    )

    def validate_name(self, name):
        pattern = r"^[A-Za-z\s,'.]{3,60}$"
        if not re.match(pattern, name.data):
            raise ValidationError(
                "Name can only have only have letters, spaces, apostrophes, commas and period."
            )

    def validate_email(self, email):
        pattern = r"^([a-z\d\.-]+)@([a-z\d-]+)\.([a-z]{2,8})(\.[a-z]{2,8})?$"
        if not re.match(pattern, email.data):
            raise ValidationError("Invalid email address.")
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError(
                "That email already exists. Please choose a different email."
            )

    def validate_username(self, username):
        pattern = r"^[a-z][a-z0-9_]{4,31}$"
        if not re.match(pattern, username.data):
            raise ValidationError(
                "Username can only contain lowercase letters, digits and underscore."
            )
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is already taken. Please choose different username."
            )

    def validate_password(self, password):
        pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{};:,<.>]).{8,60}$"
        )
        if not re.match(pattern, password.data):
            raise ValidationError(
                "Password must contain at least eight characters, one uppercase letter, one lowercase letter, one number and one special character."
            )


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=5, max=32)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=60)]
    )


class ResetRequestForm(FlaskForm):
    class Meta:
        csrf = False

    email = StringField("Email", validators=[DataRequired()])

    def validate_email(self, email):
        pattern = r"^([a-z\d\.-]+)@([a-z\d-]+)\.([a-z]{2,8})(\.[a-z]{2,8})?$"
        if not re.match(pattern, email.data):
            raise ValidationError("Invalid email address.")
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                "There is no account with that email. You must register first."
            )


class ResetPasswordForm(FlaskForm):
    class Meta:
        csrf = False

    password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8, max=60)]
    )

    def validate_password(self, password):
        pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{};:,<.>]).{8,60}$"
        )
        if not re.match(pattern, password.data):
            raise ValidationError(
                "Password must contain at least eight characters, one uppercase letter, one lowercase letter, one number and one special character."
            )
