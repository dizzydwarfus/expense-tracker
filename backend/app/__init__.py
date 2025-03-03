# backend/app/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv
from app.utils._constants import categories_dict

from app.utils.mongodb_connector import ExpenseTrackerWebAppDB
from app.utils.mongo_user import MongoUser  # We'll create this file

load_dotenv()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env("FLASK")

    # Initialize CORS with default settings
    CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True,
    )

    # Initialize the MongoDB connection
    app.mongo = ExpenseTrackerWebAppDB(app.config["MONGODB_URI"])

    # Attempt to seed categories if needed:
    # You might want to check if categories are empty first, then seed:
    if app.mongo.categories.count_documents({}) == 0:
        for cat_name, sub_cats in categories_dict.items():
            app.mongo.categories.insert_one(
                {"_id": cat_name, "subCategories": sub_cats}
            )

    # Initialize Flask-Login
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """
        For MongoDB: fetch user from "Users" collection by _id
        Then return a user object that implements Flask-Login’s requirements (MongoUser).
        """
        user_doc = app.mongo.users.find_one({"_id": user_id})
        if user_doc:
            return MongoUser(user_doc)
        return None

    # Register blueprints
    from app.routes.auth import auth as auth_blueprint
    from app.routes.main import main as main_blueprint
    from app.routes.expenses import expenses as expenses_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(expenses_blueprint)

    return app
