from datetime import datetime
import os
from flask import jsonify, request
from library_app.models import User, Book, Feedback, IssuedBook, Request
from library_app import db, ist
from library_app.user.forms import (
    BookRequestForm,
    CreateFeedbackForm,
    UpdateFeedbackForm,
    DeleteAccountForm,
)
from library_app import bcrypt
from library_app.utils import (
    auto_reject_and_revoke,
    delete_file,
    form_errors,
    custom_sort,
)
from . import user


@user.route("/books-list", methods=["GET"])
def bookslist(userid):
    auto_reject_and_revoke(userid=userid)
    current_user = User.query.get(userid)
    seti1 = set(
        issuedbook.bookid
        for issuedbook in current_user.issuedbooks
        if issuedbook.status == "current"
    )
    seti2 = set(
        request.bookid
        for request in current_user.requests
        if request.status == "pending"
    )
    books = Book.query.all()
    newbooks = [
        book for book in books if book.bookid not in seti1 and book.bookid not in seti2
    ]
    return jsonify(custom_sort(newbooks)), 200


@user.route("/request/<int:bookid>", methods=["POST"])
def create_request(userid, bookid):
    current_user = User.query.get(userid)
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    cou1 = 0
    for issuedbook in current_user.issuedbooks:
        if issuedbook.bookid == bookid and issuedbook.status == "current":
            return jsonify({"error": "The book has already been issued."}), 400
        if issuedbook.status == "current":
            cou1 += 1
    cou2 = 0
    for user_request in current_user.requests:
        if user_request.bookid == bookid and user_request.status == "pending":
            return jsonify({"error": "The request has already been placed."}), 400
        if user_request.status == "pending":
            cou2 += 1
    if cou1 + cou2 >= 5:
        return jsonify({"error": "You can only borrow 5 books at maximum."}), 400
    if not Book.query.get(bookid):
        return jsonify({"error": "Book not found."}), 404
    form = BookRequestForm(data=data)
    if form.validate():
        book_request = Request(
            userid=current_user.userid,
            days=form.days.data,
            bookid=bookid,
        )
        db.session.add(book_request)
        db.session.commit()
        return jsonify({"message": "The book has been requested!"}), 200
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )

@user.route("/request/<int:requestid>", methods=["DELETE"])
def delete_request(userid, requestid):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    req = Request.query.get(requestid)
    if not req:
        return jsonify({"error": "Request not found."}), 404
    if req.status!='pending':
        return jsonify({"error": "You can only delete your pending requests."}), 400
    current_user = User.query.get(userid)
    for ureq in current_user.requests:
        if ureq.requestid==requestid:
            db.session.delete(req)
            db.session.commit()
            return jsonify({"message": "The request has been deleted!"}), 200
    return jsonify({"error": "You can only delete your requests."}), 403

@user.route("/mybooks", methods=["GET"])
def mybooks(userid):
    auto_reject_and_revoke(userid=userid)
    current_user = User.query.get(userid)
    dicti = {}
    for issuedbook in current_user.issuedbooks:
        if issuedbook.status == "current":
            dicti[issuedbook.bookid] = {"issueid": issuedbook.issueid}
    for feedback in current_user.feedbacks:
        if feedback.bookid in dicti:
            dicti[feedback.bookid]["feedbackid"] = feedback.feedbackid
    return (
        jsonify(
            {
                "current": custom_sort(
                    [
                        issuedbook
                        for issuedbook in current_user.issuedbooks
                        if issuedbook.status == "current"
                    ],
                    ["book"],
                ),
                "requests": custom_sort(current_user.requests, ["book"]),
                "completed": custom_sort(
                    [
                        issuedbook
                        for issuedbook in current_user.issuedbooks
                        if issuedbook.status == "returned"
                    ],
                    ["book"],
                ),
                "feedbackids": {
                    dicti[bookid]["issueid"]: dicti[bookid]["feedbackid"]
                    for bookid in dicti
                    if len(dicti[bookid]) == 2
                },
            }
        ),
        200,
    )


@user.route("/books", methods=["GET"])
def books(userid):
    auto_reject_and_revoke(userid=userid)
    current_user = User.query.get(userid)
    dicti = {}
    for issuedbook in current_user.issuedbooks:
        if issuedbook.status == "current":
            dicti[issuedbook.bookid] = {
                "book": issuedbook.book.to_dict(),
                "issuedbook": issuedbook.to_dict(),
            }
    for feedback in current_user.feedbacks:
        if feedback.bookid in dicti:
            dicti[feedback.bookid]["feedback"] = feedback.to_dict()
    for request in current_user.requests:
        if request.status == "pending":
            if request.bookid in dicti:
                dicti[request.bookid]["request"] = request.to_dict()
            else:
                dicti[request.bookid] = {
                    "book": request.book.to_dict(),
                    "request": request.to_dict(),
                }
    return (
        jsonify(dicti),
        200,
    )


@user.route("/view-book/<int:bookid>", methods=["GET"])
def view_book(userid, bookid):
    auto_reject_and_revoke(userid=userid)
    current_user = User.query.get(userid)
    flag = True
    for issuedbook in current_user.issuedbooks:
        if issuedbook.status == "current" and issuedbook.bookid == bookid:
            flag = False
            break
    if flag:
        return jsonify({"error": "Unauthorized Access."}), 403
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found."}), 404
    return (
        jsonify(
            {"bookid": book.bookid, "title": book.title, "pdf_file": book.pdf_file}
        ),
        200,
    )


@user.route("/return/<int:issueid>", methods=["GET"])
def return_book(userid, issueid):
    current_user = User.query.get(userid)
    issuedbook = IssuedBook.query.get(issueid)
    if not issuedbook:
        return jsonify({"error": "Issued Book not found."}), 404
    if issuedbook.userid != current_user.userid:
        return jsonify({"error": "Unauthorized Access."}), 403
    if issuedbook.status == "returned":
        return jsonify({"error": "The book has already been returned."}), 400
    issuedbook.status = "returned"
    issuedbook.to_date = datetime.now(ist).replace(tzinfo=None)
    db.session.commit()
    return jsonify({"message": "The Book has been returned successfully."}), 200


@user.route("/feedback/<int:bookid>", methods=["POST"])
def create_feedback(userid, bookid):
    current_user = User.query.get(userid)
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    book = Book.query.get(bookid)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not (
        any(issuedbook.bookid == bookid for issuedbook in current_user.issuedbooks)
    ):
        return (
            jsonify(
                {"error": f"You can only give feedback of the books you borrowed."}
            ),
            400,
        )
    if any(feedback.userid == current_user.userid for feedback in book.feedbacks):
        return (
            jsonify(
                {
                    "error": "You can only give one feedback. Please edit your existing feedback.",
                }
            ),
            400,
        )
    form = CreateFeedbackForm(data=data)
    if form.validate():
        if not (
            any(
                issuedbook.bookid == form.bookid.data
                for issuedbook in current_user.issuedbooks
            )
        ):
            return (
                jsonify(
                    {"error": f"You can only give feedback of the books you borrowed."}
                ),
                400,
            )
        if any(
            feedback.userid == current_user.userid
            and feedback.bookid == form.bookid.data
            for feedback in Feedback.query.all()
        ):
            return (
                jsonify(
                    {
                        "error": "You can only give one feedback. Please edit your existing feedback.",
                    }
                ),
                400,
            )
        feedback = Feedback(
            userid=current_user.userid,
            bookid=form.bookid.data,
            rating=form.rating.data,
            content=form.content.data,
        )
        db.session.add(feedback)
        db.session.commit()
        return jsonify({"message": "Thanks for giving your feedback!"}), 200
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


@user.route("/feedback/<int:feedbackid>", methods=["PUT"])
def update_feedback(userid, feedbackid):
    current_user = User.query.get(userid)
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    feedback = Feedback.query.get(feedbackid)
    if not feedback:
        return jsonify({"error": "Feedback not found"}), 404
    if current_user.userid != feedback.userid:
        return jsonify({"error": "Unauthorized Access"}), 403
    if not (
        any(
            issuedbook.bookid == feedback.bookid
            for issuedbook in current_user.issuedbooks
        )
    ):
        return (
            jsonify({"error": "You can only give feedback of the books you borrowed."}),
            400,
        )
    form = UpdateFeedbackForm(data=data)
    if form.validate():
        feedback.rating = form.rating.data
        feedback.content = form.content.data
        db.session.commit()
        return jsonify({"message": "Your feedback has been edited!"}), 200
    else:
        return (
            jsonify({"error": form_errors(form.errors)}),
            400,
        )


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
                delete_file(os.path.join("user", "profile_pictures"), current_user.profile_picture)
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
