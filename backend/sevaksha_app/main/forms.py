from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    StringField,
    ValidationError,
    IntegerField,
    FloatField,
)
from wtforms.validators import DataRequired, Length
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
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=60)]
    )
    mobile = StringField("Mobile", validators=[DataRequired(), Length(min=10, max=10)])
    age = IntegerField("Age")
    income = FloatField("Income")
    occupation = StringField("Occupation", validators=[Length(max=100)])
    gender = StringField("Gender")
    marital_status = StringField("Marital Status")

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

    def validate_password(self, password):
        pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{};:,<.>]).{8,60}$"
        )
        if not re.match(pattern, password.data):
            raise ValidationError(
                "Password must contain at least eight characters, one uppercase letter, one lowercase letter, one number and one special character."
            )

    def validate_mobile(self, mobile):
        pattern = r"^[0-9]{10}$"
        if not re.match(pattern, mobile.data):
            raise ValidationError("Mobile number must be 10 digits.")
        user = User.query.filter_by(mobile=mobile.data).first()
        if user:
            raise ValidationError("That mobile number is already registered.")

    def validate_gender(self, gender):
        if gender.data and gender.data not in ["Male", "Female"]:
            raise ValidationError("Gender must be either Male or Female.")

    def validate_marital_status(self, marital_status):
        valid_statuses = [
            "Never Married",
            "Currently Married",
            "Widowed",
            "Divorced",
            "Separated",
        ]
        if marital_status.data and marital_status.data not in valid_statuses:
            raise ValidationError(
                f"Marital status must be one of: {', '.join(valid_statuses)}"
            )


class LoginForm(FlaskForm):
    class Meta:
        csrf = False

    identifier = StringField(
        "Email or Phone", validators=[DataRequired(), Length(min=3, max=60)]
    )
    password = PasswordField("Password", validators=[DataRequired()])


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
