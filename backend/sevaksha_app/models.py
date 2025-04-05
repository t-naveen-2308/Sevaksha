import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from sevaksha_app import db, bcrypt, ist
from sqlalchemy import CheckConstraint


class User(db.Model):
    __tablename__ = "user"
    userid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    username = db.Column(db.String(32), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_picture = db.Column(
        db.String(20), nullable=False, default="default_profile_picture.png"
    )
    authenticated = db.Column(db.Boolean, default=False)
    age = db.Column(db.Integer, nullable=True)
    income = db.Column(db.Numeric(10, 2), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    __table_args__ = (
        CheckConstraint(
            "gender IN ('Male', 'Female')", name="check_gender_valid_values"
        ),
        CheckConstraint(
            "marital_status IN ('Never Married', 'Currently Married', 'Widowed', 'Divorced', 'Separated')",
            name="check_marital_status_valid_values",
        ),
    )

    def __repr__(self):
        return f"User('{self.userid}', '{self.name}', '{self.username}', '{self.email}', '{self.password}', '{self.profile_picture}', '{self.authenticated}')"

    def __init__(
        self,
        name,
        username,
        email,
        password,
        profile_picture="default_profile_picture.png",
        authenticated=False,
        urole="user",
        age=None,
        income=None,
        occupation=None,
        gender=None,
        marital_status=None,
    ):
        self.name = name
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")
        self.profile_picture = profile_picture
        self.authenticated = authenticated
        self.urole = urole
        self.age = age
        self.income = income
        self.occupation = occupation
        self.gender = gender
        self.marital_status = marital_status

    def get_reset_token(self, expires_sec=1800):
        secret_key = jwt.encode(
            {
                "userid": self.userid,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_sec),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        return secret_key

    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                leeway=timedelta(seconds=10),
                algorithms=["HS256"],
                options={"verify_exp": True},
            )
        except:
            return None
        return User.query.filter(User.userid == int(data["userid"])).first()

    def to_dict(self, include_relationships=[]):
        dt = {
            "userid": self.userid,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "profile_picture": self.profile_picture,
            "age": self.age,
            "income": float(self.income) if self.income else None,
            "occupation": self.occupation,
            "gender": self.gender,
            "marital_status": self.marital_status,
        }
        return dt


class WelfareScheme(db.Model):
    __tablename__ = "welfare_schemes"

    scheme_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scheme_name = db.Column(db.String(255), nullable=False)
    min_age = db.Column(db.Integer, nullable=True)
    max_age = db.Column(db.Integer, nullable=True)
    income_limit = db.Column(db.Numeric(10, 2), nullable=True)
    target_occupation = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    required_documents = db.Column(db.Text, nullable=True)
    scheme_description = db.Column(db.Text, nullable=True)
    application_process = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    application_link = db.Column(db.String(500), nullable=True)
    language_support = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    __table_args__ = (
        CheckConstraint(
            "gender IN ('Male', 'Female', 'Neutral')",
            name="check_gender_valid_values",
        ),
        CheckConstraint(
            "marital_status IN ('Never Married', 'Currently Married', 'Widowed', 'Divorced', 'Separated')",
            name="check_marital_status_valid_values",
        ),
    )

    def __init__(
        self,
        scheme_name,
        min_age=None,
        max_age=None,
        income_limit=None,
        target_occupation=None,
        eligibility_criteria=None,
        required_documents=None,
        scheme_description=None,
        application_process=None,
        benefits=None,
        application_link=None,
        language_support=None,
        is_active=True,
        gender=None,
        marital_status=None,
    ):
        self.scheme_name = scheme_name
        self.min_age = min_age
        self.max_age = max_age
        self.income_limit = income_limit
        self.target_occupation = target_occupation
        self.eligibility_criteria = eligibility_criteria
        self.required_documents = required_documents
        self.scheme_description = scheme_description
        self.application_process = application_process
        self.benefits = benefits
        self.application_link = application_link
        self.language_support = language_support
        self.is_active = is_active
        self.gender = gender
        self.marital_status = marital_status

    def __repr__(self):
        return (
            f"WelfareScheme('{self.scheme_id}', '{self.scheme_name}', "
            f"min_age={self.min_age}, max_age={self.max_age}, income_limit={self.income_limit}, "
            f"target_occupation='{self.target_occupation}', gender='{self.gender}', "
            f"marital_status='{self.marital_status}', is_active={self.is_active})"
        )


class BlacklistedToken(db.Model):
    __tablename__ = "blacklistedtoken"
    blacklistedid = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(512), unique=True, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, expiry):
        self.token = token
        self.expiry = expiry

    def __repr__(self):
        return (
            f"BlacklistedToken('{self.blacklistedid}', '{self.token}', '{self.expiry}')"
        )

    def is_expired(self):
        return datetime.now(ist).replace(tzinfo=None) > self.expiry

    def to_dict(self):
        return {
            "blacklistedid": self.blacklistedid,
            "token": self.token,
            "expiry": self.expiry.isoformat(),
        }
