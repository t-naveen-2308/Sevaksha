from datetime import timezone, timedelta
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from flask_mail import Mail
from flask_caching import Cache
from sevaksha_app.config import Config
from sevaksha_app.worker import celery_init_app
from celery.schedules import crontab
import flask_excel as excel
import json

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

    from sevaksha_app.models import User, WelfareScheme
    with app.app_context():
        db.create_all()

        json_path = os.path.join(app.root_path, "static", "data", "schemes.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                schemes = json.load(f)
            print(json_path)
            for scheme_data in schemes:
                # print(scheme_data) 
                existing = WelfareScheme.query.filter_by(
                    scheme_name=scheme_data["scheme_name"]
                ).first()
                print(existing)
                if not existing:
                    print("Hi")
                    scheme = WelfareScheme(
                        scheme_name=scheme_data.get("scheme_name"),
                        min_age=scheme_data.get("min_age"),
                        max_age=scheme_data.get("max_age"),
                        income_limit=scheme_data.get("income_limit"),
                        target_occupation=scheme_data.get("target_occupation"),
                        eligibility_criteria=scheme_data.get("eligibility_criteria"),
                        required_documents=scheme_data.get("required_documents"),
                        scheme_description=scheme_data.get("scheme_description"),
                        application_process=scheme_data.get("application_process"),
                        benefits=scheme_data.get("benefits"),
                        application_link=scheme_data.get("application_link"),
                        language_support=scheme_data.get("language_support"),
                        is_active=scheme_data.get("is_active", True),
                    )
                    db.session.add(scheme)
            db.session.commit()

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
