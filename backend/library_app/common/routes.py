from datetime import datetime
import os
from flask import jsonify, request, current_app
from library_app import db, bcrypt, ist
from library_app.models import User, BlacklistedToken
from library_app.utils import (
    delete_file,
    save_file,
    form_errors,
    send_reset_email,
    validate_file,
)
from library_app.common.forms import (
    ResetPasswordForm,
    UpdateProfileForm,
    ChangePasswordForm,
)
from library_app.tasks import generate_data
from celery.result import AsyncResult
from . import common
import jwt


@common.route("/is-valid", methods=["GET"])
def is_valid(userid):
    if userid:
        return jsonify({"message": "The token is still valid."}), 200
    else:
        return jsonify({"error": "The token is expired or invalid."}), 400


@common.route("/account", methods=["GET"])
def account(userid):
    current_user = User.query.get(userid)
    user = User.query.get(current_user.userid)
    return jsonify(user.to_dict()), 200


@common.route("/stats", methods=["GET"])
def stats(userid):
    task = generate_data.delay(userid)
    return jsonify({"taskid": task.id}), 200


@common.route("/stats/<taskid>", methods=["GET"])
def stats_result(taskid):
    result = AsyncResult(taskid)
    if not result:
        return jsonify({"error": "Task not found."}), 404
    if result.ready():
        d = result.get()
        d["status"] = "Task is ready."
        return jsonify(d), 404
    else:
        return jsonify({"status": "Task is not ready."}), 400


@common.route("/account", methods=["POST"])
def update_profile(userid):
    current_user = User.query.get(userid)
    data = request.form.to_dict()
    form = UpdateProfileForm(data=data, current_user=current_user)
    if current_user.urole == "librarian" and (
        form.name.data != current_user.name
        or form.username.data != current_user.username
    ):
        return (
            jsonify(
                {"error": "Unauthorized. Cannot change name or username of librarian."}
            ),
            403,
        )
    if form.validate():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            profile_picture_data = request.files.get("profile_picture")
            if profile_picture_data:
                return_val = validate_file(profile_picture_data, "image")
                if return_val:
                    return jsonify(return_val), 400
                if current_user.profile_picture != "default_profile_picture.png":
                    delete_file(
                        os.path.join("user", "profile_pictures"),
                        current_user.profile_picture,
                    )
                current_user.profile_picture = save_file(
                    profile_picture_data, "user/profile_pictures"
                )
            elif form.delete_profile_picture.data == "yes":
                if current_user.profile_picture != "default_profile_picture.png":
                    delete_file(
                        os.path.join("user", "profile_pictures"),
                        current_user.profile_picture,
                    )
                current_user.profile_picture = "default_profile_picture.png"
            if current_user.urole != "librarian":
                current_user.name = form.name.data
                current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            return jsonify({"message": "Account has been updated successfully."}), 200
        else:
            return jsonify({"error": "The password is incorrect."}), 400
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@common.route("/account", methods=["PUT"])
def change_password(userid):
    current_user = User.query.get(userid)
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    form = ChangePasswordForm(data=data)
    if form.validate():
        if bcrypt.check_password_hash(
            current_user.password, form.current_password.data
        ):
            current_user.password = bcrypt.generate_password_hash(
                form.new_password.data
            ).decode("utf-8")
            db.session.commit()
            return jsonify({"message": "Your password has been updated!"}), 200
        else:
            return jsonify({"error": "The password is incorrect."}), 400
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@common.route("/reset", methods=["GET"])
def reset_request(userid):
    user = User.query.get(userid)
    send_reset_email(user, "common")
    return (
        jsonify(
            {
                "message": "An email has been sent with instructions to reset your password.",
            }
        ),
        200,
    )


@common.route("/password-reset/<token>", methods=["POST"])
def reset_password(userid, token):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    user = User.verify_reset_token(token)
    if user is None:
        return jsonify({"error": "That is an invalid or expired token."}), 400
    if userid != user.userid:
        return jsonify({"error": "Token does not match the user."}), 400
    form = ResetPasswordForm(data=data)
    if form.validate():
        user.password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        db.session.commit()

        return jsonify({"message": "Your password has been updated!"}), 201
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@common.route("/logout", methods=["GET"])
def logout(userid):
    token = request.headers.get("Authorization")
    try:
        if token.startswith("Bearer "):
            token = token[len("Bearer ") :]
        decoded = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        expiry = datetime.fromtimestamp(decoded["exp"], ist)
        blacklisted_token = BlacklistedToken(token=token, expiry=expiry)
        user = User.query.get(userid)
        user.authenticated = False
        db.session.add(blacklisted_token)
        db.session.commit()
        return jsonify({"message": "Logged out successfully."}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token already expired."}), 400
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token."}), 400
    except Exception:
        return jsonify({"error": "An error occurred."}), 500
