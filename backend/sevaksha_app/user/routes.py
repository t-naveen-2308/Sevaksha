import os
import jwt
from flask import jsonify, request
from sevaksha_app.models import User, BlacklistedToken, WelfareScheme
from sevaksha_app import db, ist
from sevaksha_app.user.forms import (
    UpdateProfileForm,
    ChangePasswordForm,
    DeleteAccountForm,
    ResetPasswordForm,
    ChatForm,
)

from flask import current_app
from datetime import datetime
from sevaksha_app import bcrypt
from sevaksha_app.utils import (
    delete_file,
    save_file,
    form_errors,
    send_reset_email,
    validate_file,
)
from . import user
from sevaksha_app.rag.qa_chain import create_qa_chain
from .user_rag.user_qa_chain import create_user_qa_chain
import jwt
import threading


qa_chain = create_qa_chain()

user_qa_chain = create_user_qa_chain()


@user.route("/recommendation", methods=["POST"])
def recommendation(userid):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    current_user = User.query.get(userid)

    response_text = qa_chain.run(
        " ".join(
            [
                str(current_user.age),
                str(current_user.income),
                current_user.occupation,
                current_user.gender,
                current_user.martial_status,
            ]
        )
    )

    if "couldn't find any scheme" in response_text.lower():
        return jsonify({"results": None}), 200

    scheme_names = [
        line.lstrip("- ").strip()
        for line in response_text.splitlines()
        if line.startswith("- ")
    ]

    schemes = WelfareScheme.query.filter(
        WelfareScheme.scheme_name.in_(scheme_names)
    ).all()

    result = []
    for scheme in schemes:
        result.append(
            {
                "scheme_name": scheme.scheme_name,
                "min_age": scheme.min_age,
                "max_age": scheme.max_age,
                "income_limit": scheme.income_limit,
                "target_occupation": scheme.target_occupation,
                "eligibility_criteria": scheme.eligibility_criteria,
                "required_documents": scheme.required_documents,
                "scheme_description": scheme.scheme_description,
                "application_process": scheme.application_process,
                "benefits": scheme.benefits,
                "application_link": scheme.application_link,
                "language_support": scheme.language_support,
                "is_active": scheme.is_active,
            }
        )

    return jsonify({"results": result}), 200


@user.route("/chat", methods=["POST"])
def chat(userid):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    current_user = User.query.get(userid)

    form = ChatForm(data=request.get_json())
    if not form.validate():
        return jsonify({"error": form_errors(form.errors)}), 400

    try:
        response = qa_chain.run(
            " ".join(
                [
                    str(current_user.age),
                    str(current_user.income),
                    current_user.occupation,
                    current_user.gender,
                    current_user.martial_status,
                ]
            )
        )
        return jsonify({"response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user.route("/account", methods=["POST"])
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


@user.route("/account", methods=["PUT"])
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


@user.route("/reset", methods=["GET"])
def reset_request(userid):
    user = User.query.get(userid)
    send_reset_email(user, "user")
    return (
        jsonify(
            {
                "message": "An email has been sent with instructions to reset your password.",
            }
        ),
        200,
    )


@user.route("/password-reset/<token>", methods=["POST"])
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


@user.route("/logout", methods=["GET"])
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


@user.route("/account", methods=["POST"])
def delete_account(userid):
    current_user = User.query.get(userid)
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    form = DeleteAccountForm(data=data)
    if form.validate():
        if bcrypt.check_password_hash(current_user.password, form.password.data):
            if current_user.profile_picture != "default_profile_picture.png":
                delete_file(
                    os.path.join("user", "profile_pictures"),
                    current_user.profile_picture,
                )
            db.session.delete(current_user)
            db.session.commit()

            return jsonify({"message": "Account deleted successfully."}), 200
        else:
            return jsonify({"error": "The password is incorrect."}), 400
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )
