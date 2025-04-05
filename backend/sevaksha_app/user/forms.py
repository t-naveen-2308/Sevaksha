from flask_wtf import FlaskForm
from wtforms import (
    PasswordField,
    RadioField,
    StringField,
    ValidationError,
)
import re
from sevaksha_app.models import User
from wtforms.validators import DataRequired, Length, EqualTo

class ChatForm(FlaskForm):
    class Meta:
        csrf = False

    query = StringField("Query", validators=[DataRequired()])


class UpdateProfileForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=60)])
    email = StringField("Email", validators=[DataRequired()])
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=5, max=32)]
    )
    delete_profile_picture = RadioField(
        "Delete Existing Profile Picture",
        choices=[("yes", "yes"), ("no", "yes")],
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Enter Your Password To Update",
        validators=[DataRequired(), Length(min=8, max=60)],
    )

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop("current_user", None)
        super().__init__(*args, **kwargs)

    def validate_name(self, name):
        pattern = r"^[A-Za-z\s,'.]{3,60}$"
        if not re.match(pattern, name.data):
            raise ValidationError(
                "Name can only have only have letters, spaces, apostrophes, commas and period."
            )

    def validate_username(self, username):
        pattern = r"^[a-z][a-z0-9_]{4,31}$"
        if not re.match(pattern, username.data):
            raise ValidationError(
                "Username can only contain lowercase letters, digits and underscore."
            )
        if username.data != self.current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is already taken. Please choose different username."
                )

    def validate_email(self, email):
        pattern = r"^([a-z\d\.-]+)@([a-z\d-]+)\.([a-z]{2,8})(\.[a-z]{2,8})?$"
        if not re.match(pattern, email.data):
            raise ValidationError("Invalid email address.")
        if email.data != self.current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError(
                    "That email already exists. Please choose a different email."
                )


class ChangePasswordForm(FlaskForm):
    class Meta:
        csrf = False

    current_password = PasswordField(
        "Current Password", validators=[DataRequired(), Length(min=8, max=60)]
    )
    new_password = PasswordField(
        "New Password", validators=[DataRequired(), Length(min=8, max=60)]
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("new_password")]
    )

    def validate_new_password(self, new_password):
        pattern = (
            r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+{};:,<.>]).{8,60}$"
        )
        if not re.match(pattern, new_password.data):
            raise ValidationError(
                "Password must contain at least eight characters, one uppercase letter, one lowercase letter, one number and one special character."
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


class DeleteAccountForm(FlaskForm):
    class Meta:
        csrf = False

    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=60)]
    )
