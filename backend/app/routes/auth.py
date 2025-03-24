# backend/app/routes/auth.py

from flask import Blueprint, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.utils._password_utils import check_password
from app.utils.mongo_user import MongoUser

from app import create_app

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["POST"])
def login():
    # JSON-based login or form-based login - adjust as needed
    data = request.get_json() or request.form
    username_email = data.get("username_email")
    password = data.get("password")

    if not username_email or not password:
        return {"error": "Missing username/email or password"}, 400

    # Access the mongo instance
    app = create_app()
    user_doc = app.mongo.users.find_one(
        {
            "$or": [
                {"_id": username_email},  # if you store username in _id
                {"email": username_email},
            ]
        }
    )

    if not user_doc:
        flash("Please check your login details and try again.")
        return {"error": "Invalid credentials"}, 401

    stored_password = user_doc["password"]
    if not check_password(stored_password, password):
        flash("Invalid password.")
        return {"error": "Invalid credentials"}, 401

    # If okay, create a MongoUser object
    user_obj = MongoUser(user_doc)
    login_user(user_obj, remember=True)

    return {"success": True, "message": "Logged in"}


@auth.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or request.form
    username = data.get("username")
    nickname = data.get("nickname")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return {"error": "Missing username, email, or password"}, 400

    # Access the mongo instance
    app = create_app()

    # Check if user or email exist
    # We assume _id is the username
    existing_user = app.mongo.users.find_one({"_id": username})
    existing_email = app.mongo.users.find_one({"email": email})

    if existing_user:
        return {"error": "Username already exists"}, 400
    if existing_email:
        return {"error": "Email already exists"}, 400

    app.mongo.upsert_user(
        username=username, name=nickname, email=email, password=password
    )
    return {"success": True, "message": "User registered successfully"}


@auth.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"success": True, "message": "Logged out"}


@auth.route("/delete_user/<username>", methods=["DELETE"])
@login_required
def delete_user(username):
    app = create_app()

    # If the current user is the one being deleted
    if current_user.id == username:
        app.mongo.users.delete_one({"_id": username})
        logout_user()
        return {"success": True, "message": "User deleted and logged out"}
    else:
        return {"error": "Unauthorized"}, 403
