# backend/app/utils/mongo_user.py

from flask_login import UserMixin


class MongoUser(UserMixin):
    """
    Wraps a MongoDB user document (e.g. { "_id": "some_username", "email": "...", ... })
    so that Flask-Login can handle it.
    """

    def __init__(self, user_doc: dict):
        self.user_doc = user_doc
        # Typically user_doc["_id"] is the unique user identifier
        self.id = str(user_doc["_id"])

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
