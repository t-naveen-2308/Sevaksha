from flask import jsonify, request, current_app
from sevaksha_app import db, bcrypt
from sevaksha_app.models import User, WelfareScheme
from sevaksha_app.utils import (
    save_file,
    send_reset_email,
    form_errors,
    validate_file,
)
from sevaksha_app.main.forms import (
    ResetRequestForm,
    ResetPasswordForm,
    LoginForm,
    RegistrationForm,
    SearchForm,
)
from . import main
from datetime import datetime, timezone, timedelta
import jwt
import os
from sevaksha_app.rag.qa_chain import create_qa_chain
import jwt


qa_chain = create_qa_chain()


@main.route("/search", methods=["POST"])
def search():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    form = SearchForm(data=request.get_json())
    if not form.validate():
        return jsonify({"error": form_errors(form.errors)}), 400

    response_text = qa_chain.run(form.search_term.data).strip()

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


@main.route("/register", methods=["POST"])
def register():
    data = request.form.to_dict()
    form = RegistrationForm(data=data)
    if form.validate():
        profile_picture_data = request.files.get("profile_picture")
        if profile_picture_data:
            return_val = validate_file(profile_picture_data, "image")
            if return_val:
                return jsonify(return_val), 400
            profile_picture = save_file(
                profile_picture_data, os.path.join("user", "profile_pictures")
            )
        else:
            profile_picture = "default_profile_picture.png"
        user = User(
            name=form.name.data,
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
            profile_picture=profile_picture,
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": f"Account created for {form.username.data}!"}), 201
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@main.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    if "role" not in data:
        return jsonify({"error": "Role is required"}), 400
    form = LoginForm(data=data)
    if form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.urole == "user" or user.urole == "librarian":
                if user.urole != data["role"]:
                    return (
                        jsonify({"roleError": "Role is not same."}),
                        400,
                    )
                try:
                    token = jwt.encode(
                        {
                            "userid": user.userid,
                            "exp": datetime.now(timezone.utc) + timedelta(days=1),
                        },
                        current_app.config["SECRET_KEY"],
                        algorithm="HS256",
                    )
                except Exception as e:
                    return (
                        jsonify(
                            {
                                "error": "An unexpected error has occurred. Please try again. Couldn't generate the token."
                            }
                        ),
                        400,
                    )
                user.authenticated = True
                db.session.commit()
                return (
                    jsonify({"message": "Logged in successfully.", "token": token}),
                    200,
                )
            else:
                return (
                    jsonify(
                        {
                            "error": "An unexpected error has occurred. Please try again. Role wrong."
                        }
                    ),
                    400,
                )
        else:
            return jsonify({"error": "Invalid Username or Password"}), 404
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@main.route("/reset", methods=["POST"])
def reset_request():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    form = ResetRequestForm(data=data)
    if form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        token = jwt.encode(
            {
                "userid": user.userid,
                "exp": datetime.now(timezone.utc) + timedelta(seconds=1800),
            },
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )
        send_reset_email(user, "main")
        return (
            jsonify(
                {
                    "message": "An email has been sent with instructions to reset your password.",
                    "token": token,
                }
            ),
            200,
        )
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@main.route("/password-reset/<token>", methods=["POST"])
def reset_password(token):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    user = User.verify_reset_token(token)
    if user is None:
        return jsonify({"error": "That is an invalid or expired token."}), 400
    try:
        token2 = request.headers.get("Authorization")
        if not token2:
            return jsonify({"error": "Authorization header required."}), 401
        if token2.startswith("Bearer "):
            token2 = token2[len("Bearer ") :]
        print(token2)
        decoded_token = jwt.decode(
            token2, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        userid = decoded_token.get("userid")
        if user.userid != userid:
            return jsonify({"error": "Token does not match user."}), 400
    except:
        return (
            jsonify({"error": "An unexpected error has occurred. Please try again."}),
            400,
        )
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


@main.route("/schemes", methods=["GET"])
def get_schemes():
    schemes = WelfareScheme.query.all()
    schemes_data = [
        {
            "scheme_id": scheme.scheme_id,
            "scheme_name": scheme.scheme_name,
            "min_age": scheme.min_age,
            "max_age": scheme.max_age,
            "income_limit": float(scheme.income_limit) if scheme.income_limit else None,
            "target_occupation": scheme.target_occupation,
            "eligibility_criteria": scheme.eligibility_criteria,
            "required_documents": scheme.required_documents,
            "scheme_description": scheme.scheme_description,
            "application_process": scheme.application_process,
            "benefits": scheme.benefits,
            "application_link": scheme.application_link,
            "language_support": scheme.language_support,
            "is_active": scheme.is_active,
            "created_at": scheme.created_at.isoformat(),
            "updated_at": scheme.updated_at.isoformat() if scheme.updated_at else None,
        }
        for scheme in schemes
    ]
    return jsonify(schemes_data), 200
