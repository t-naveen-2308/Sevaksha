from datetime import datetime, timezone, timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_caching import Cache
from library_app.config import Config
from library_app.worker import celery_init_app
from celery.schedules import crontab
import flask_excel as excel

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
cache = Cache()
celery_app = None
ist = timezone(timedelta(hours=5, minutes=30))


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    excel.init_excel(app)
    celery_app = celery_init_app(app)

    from library_app.models import User, Section

    with app.app_context():
        db.create_all()

        section = Section.query.get(1)

        if not section:
            section = Section(
                title="Miscellaneous",
                description="This section consists of books which do not belong to any other section.",
                picture="default_section_picture.jpeg",
                date_modified=datetime.now(ist).replace(tzinfo=None),
            )
            db.session.add(section)
            db.session.commit()

        librarian = User.query.get(1)

        if not librarian:
            librarian = User(
                name="Library Admin",
                username="library_admin",
                email="naveentummala033@gmail.com",
                password="LibraryAdmin@2024",
                urole="librarian",
            )
            db.session.add(librarian)
            db.session.commit()

    from library_app.tasks import daily_remainder, monthly_report, delete_blacklisted_tokens

    celery_app.conf.beat_schedule = {
        "monthly-report": {
            "task": "library_app.tasks.monthly_report",
            "schedule": crontab(minute="*/10"),
        },
        "delete-blacklisted-tokens": {
            "task": "library_app.tasks.delete_blacklisted_tokens",
            "schedule": crontab(minute="*/10"),
        },
        "daily-remainder": {
            "task": "library_app.tasks.daily_remainder",
            "schedule": crontab(minute="*/10"),
        },
    }

    from library_app.main import main
    from library_app.common import common
    from library_app.user import user
    from library_app.librarian import librarian

    app.register_blueprint(main, url_prefix="/api/main")
    app.register_blueprint(common, url_prefix="/api/common")
    app.register_blueprint(user, url_prefix="/api/user")
    app.register_blueprint(librarian, url_prefix="/api/librarian")

    return app, celery_app
