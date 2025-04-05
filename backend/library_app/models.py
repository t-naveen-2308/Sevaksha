import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app
from library_app import db, bcrypt, ist
from sqlalchemy import CheckConstraint
from library_app.utils import custom_sort


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
    urole = db.Column(db.String(20), default="user")
    issuedbooks = db.relationship(
        "IssuedBook", back_populates="user", lazy=True, cascade="all, delete-orphan"
    )
    requests = db.relationship(
        "Request", back_populates="user", lazy=True, cascade="all, delete-orphan"
    )
    feedbacks = db.relationship(
        "Feedback", back_populates="user", lazy=True, cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(urole.in_(["user", "librarian"]), name="check_urole"),
    )

    def __repr__(self):
        return f"User('{self.userid}', '{self.name}', '{self.username}', '{self.email}', '{self.password}', '{self.profile_picture}', '{self.authenticated}', '{self.urole}')"

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
                "exp": datetime.now(timezone.utc)
                + timedelta(seconds=expires_sec),
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
        if "requests" in include_relationships:
            dt["requests"] = custom_sort(self.requests)
        if "feedbacks" in include_relationships:
            dt["feedbacks"] = custom_sort(self.feedbacks)
        if "issuedbooks" in include_relationships:
            dt["issuedbooks"] = custom_sort(self.issuedbooks, ["book"])
        return dt


class Section(db.Model):
    __tablename__ = "section"
    sectionid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(60), unique=True, nullable=False)
    date_modified = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(ist).replace(tzinfo=None),
        onupdate=datetime.now(ist).replace(tzinfo=None),
    )
    picture = db.Column(
        db.String(20), nullable=False, default="default_section_picture.jpeg"
    )
    description = db.Column(db.String(120), nullable=False)
    books = db.relationship("Book", back_populates="section", lazy=True)

    def __init__(
        self,
        title,
        description,
        picture,
        date_modified=datetime.now(ist).replace(tzinfo=None),
    ):
        self.title = title
        self.description = description
        self.picture = picture
        self.date_modified = date_modified

    def __repr__(self):
        return f"Section('{self.sectionid}', '{self.title}', '{self.date_modified}', '{self.description}', '{self.picture}')"

    def to_dict(self, include_relationships=[]):
        dt = {
            "sectionid": self.sectionid,
            "title": self.title,
            "date_modified": self.date_modified.isoformat(),
            "picture": self.picture,
            "description": self.description,
        }
        if "books" in include_relationships:
            dt["books"] = custom_sort(self.books)
        return dt


class Book(db.Model):
    __tablename__ = "book"
    bookid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(60), unique=True, nullable=False)
    author = db.Column(db.String(60), nullable=False)
    date_modified = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(ist).replace(tzinfo=None),
        onupdate=datetime.now(ist).replace(tzinfo=None),
    )
    picture = db.Column(
        db.String(20), nullable=False, default="default_book_picture.png"
    )
    description = db.Column(db.String(120), nullable=False)
    pdf_file = db.Column(db.String(20), nullable=False)
    sectionid = db.Column(
        db.Integer, db.ForeignKey("section.sectionid"), nullable=False, default=1
    )
    section = db.relationship("Section", back_populates="books")
    issuedbooks = db.relationship(
        "IssuedBook", back_populates="book", lazy=True, cascade="all, delete-orphan"
    )
    feedbacks = db.relationship(
        "Feedback", back_populates="book", lazy=True, cascade="all, delete-orphan"
    )
    requests = db.relationship(
        "Request", back_populates="book", lazy=True, cascade="all, delete-orphan"
    )

    def __init__(
        self,
        title,
        author,
        picture,
        description,
        pdf_file="sample_pdf.pdf",
        sectionid=1,
        date_modified=datetime.now(ist).replace(tzinfo=None),
    ):
        self.title = title
        self.author = author
        self.date_modified = date_modified
        self.picture = picture
        self.description = description
        self.pdf_file = pdf_file
        self.sectionid = sectionid

    def __repr__(self):
        return f"Book('{self.bookid}', '{self.title}', '{self.author}', '{self.date_modified}', '{self.picture}', '{self.description}', '{self.pdf_file}', '{self.sectionid}')"

    def to_dict(self, include_relationships=[]):
        dt = {
            "bookid": self.bookid,
            "title": self.title,
            "author": self.author,
            "date_modified": self.date_modified.isoformat(),
            "picture": self.picture,
            "description": self.description,
            "sectionid": self.sectionid,
        }
        if "pdf_file" in include_relationships:
            dt["pdf_file"] = self.pdf_file
        if "section" in include_relationships:
            dt["section"] = self.section.to_dict()
        if "issuedbooks" in include_relationships:
            dt["issuedbooks"] = custom_sort(self.issuedbooks)
        if "feedbacks" in include_relationships:
            dt["feedbacks"] = custom_sort(self.feedbacks, ["user"])
        if "requests" in include_relationships:
            dt["requests"] = custom_sort(self.requests)
        return dt


class Request(db.Model):
    __tablename__ = "request"
    requestid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    date_modified = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(ist).replace(tzinfo=None),
        onupdate=datetime.now(ist).replace(tzinfo=None),
    )
    days = db.Column(db.Integer, nullable=False)
    bookid = db.Column(db.Integer, db.ForeignKey("book.bookid"), nullable=False)
    status = db.Column(db.String(20), default="pending")
    user = db.relationship("User", back_populates="requests")
    book = db.relationship("Book", back_populates="requests")

    __table_args__ = (
        CheckConstraint("days >= 1 AND days <= 7", name="check_days"),
        CheckConstraint(
            status.in_(["pending", "accepted", "rejected"]), name="check_status"
        ),
    )

    def __init__(
        self,
        userid,
        days,
        bookid,
        status="pending",
        date_modified=datetime.now(ist).replace(tzinfo=None),
    ):
        self.userid = userid
        self.date_modified = date_modified
        self.days = days
        self.bookid = bookid
        self.status = status

    def __repr__(self):
        return f"Request('{self.requestid}','{self.userid}', '{self.date_modified}','{self.days}', '{self.bookid}', '{self.status}')"

    def to_dict(self, include_relationships=[]):
        dt = {
            "requestid": self.requestid,
            "userid": self.userid,
            "date_modified": self.date_modified.isoformat(),
            "days": self.days,
            "bookid": self.bookid,
            "status": self.status,
        }
        if "user" in include_relationships:
            dt["user"] = self.user.to_dict()
        if "book" in include_relationships:
            dt["book"] = self.book.to_dict()
        return dt


class IssuedBook(db.Model):
    __tablename__ = "issuedbook"
    issueid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    bookid = db.Column(db.Integer, db.ForeignKey("book.bookid"), nullable=False)
    from_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now(ist).replace(tzinfo=None)
    )
    to_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="current")
    user = db.relationship("User", back_populates="issuedbooks")
    book = db.relationship("Book", back_populates="issuedbooks")

    __table_args__ = (
        CheckConstraint(status.in_(["current", "returned"]), name="check_status"),
    )

    def __init__(self, userid, bookid, from_date, to_date, status="current"):
        self.userid = userid
        self.bookid = bookid
        self.from_date = from_date
        self.to_date = to_date
        self.status = status

    def __repr__(self):
        return f"IssuedBook({self.issueid}', '{self.userid}', '{self.bookid}', '{self.from_date}', '{self.to_date}', '{self.status}')"

    def to_dict(self, include_relationships=[]):
        dt = {
            "issueid": self.issueid,
            "userid": self.userid,
            "bookid": self.bookid,
            "from_date": self.from_date.isoformat(),
            "to_date": self.to_date.isoformat(),
            "status": self.status,
        }
        if "user" in include_relationships:
            dt["user"] = self.user.to_dict()
        if "book" in include_relationships:
            dt["book"] = self.book.to_dict()
        return dt


class Feedback(db.Model):
    __tablename__ = "feedback"
    feedbackid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)
    bookid = db.Column(db.Integer, db.ForeignKey("book.bookid"), nullable=False)
    date_modified = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(ist).replace(tzinfo=None),
        onupdate=datetime.now(ist).replace(tzinfo=None),
    )
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    user = db.relationship("User", back_populates="feedbacks")
    book = db.relationship("Book", back_populates="feedbacks")

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating"),
    )

    def __init__(
        self,
        userid,
        bookid,
        rating,
        content,
        date_modified=datetime.now(ist).replace(tzinfo=None),
    ):
        self.userid = userid
        self.bookid = bookid
        self.date_modified = date_modified
        self.rating = rating
        self.content = content

    def __repr__(self):
        return f"Feedback('{self.feedbackid}', '{self.userid}', '{self.bookid}', '{self.date_modified}', '{self.rating}', '{self.content}')"

    def to_dict(self, include_relationships=[]):
        dt = {
            "feedbackid": self.feedbackid,
            "userid": self.userid,
            "bookid": self.bookid,
            "date_modified": self.date_modified.isoformat(),
            "rating": self.rating,
            "content": self.content,
        }
        if "user" in include_relationships:
            dt["user"] = self.user.to_dict()
        if "book" in include_relationships:
            dt["book"] = self.book.to_dict()
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
