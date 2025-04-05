import os
from datetime import datetime, timedelta
from celery import shared_task
from flask import current_app, render_template
import flask_excel as excel
from sevaksha_app.utils import send_report_email, send_remainder_email


@shared_task(ignore_result=True)
def daily_remainder():
    return "OK"


@shared_task(ignore_result=True)
def monthly_report():
    return "OK"


@shared_task(ignore_result=True)
def delete_blacklisted_tokens():
    from sevaksha_app import db, ist
    from sevaksha_app.models import BlacklistedToken

    try:
        expired_tokens = BlacklistedToken.query.filter(
            BlacklistedToken.expiry <= datetime.now(ist)
        ).all()
        for blacklisted_token in expired_tokens:
            db.session.delete(blacklisted_token)
        db.session.commit()
        print(f"Deleted {len(expired_tokens)} blacklisted tokens.")
    except Exception as e:
        print(f"Error occurred while deleting blacklisted tokens: {e}")
        db.session.rollback()
        raise
