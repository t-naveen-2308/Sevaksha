import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from sevaksha_app import db, bcrypt, ist


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
    ):
        self.name = name
        self.email = email
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")
        self.profile_picture = profile_picture
        self.authenticated = authenticated
        self.urole = urole

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
        }
        return dt


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
