from datetime import timezone, timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_caching import Cache
from sevaksha_app.config import Config
from sevaksha_app.worker import celery_init_app
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

    from sevaksha_app.models import User

    from sevaksha_app.tasks import (
        daily_remainder,
        monthly_report,
        delete_blacklisted_tokens,
    )

    celery_app.conf.beat_schedule = {
        "monthly-report": {
            "task": "sevaksha_app.tasks.monthly_report",
            "schedule": crontab(minute="*/10"),
        },
        "delete-blacklisted-tokens": {
            "task": "sevaksha_app.tasks.delete_blacklisted_tokens",
            "schedule": crontab(minute="*/10"),
        },
        "daily-remainder": {
            "task": "sevaksha_app.tasks.daily_remainder",
            "schedule": crontab(minute="*/10"),
        },
    }

    from sevaksha_app.main import main
    from sevaksha_app.user import user

    app.register_blueprint(main, url_prefix="/api/main")
    app.register_blueprint(user, url_prefix="/api/user")

    return app, celery_app
