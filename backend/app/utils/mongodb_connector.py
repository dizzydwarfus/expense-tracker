# backend/app/utils/mongodb_connector.py

# Built-in libraries
import datetime as dt
from typing import Union

# Third party libraries
from pymongo import MongoClient

# Internal imports
from app.utils._logger import MyLogger
from app.utils._password_utils import hash_password
from app.models.users import User
from app.models.transactions import GoCardlessTransaction


class MongoConnector(MyLogger):
    def __init__(self, connection_string):
        super().__init__(
            name="ExpenseTrackerWebApp", level="DEBUG", log_file="././logs.log"
        )
        self.client = MongoClient(connection_string)
        self.db = self.client.ExpenseTrackerWebApp

    @property
    def server_info(self):
        return self.client.server_info()

    @property
    def get_collection_names(self):
        return self.db.list_collection_names()

    def test_connection(self):
        try:
            self.client.server_info()  # Will raise an exception if cannot connect to MongoDB.
            self.logger.info("Connected to MongoDB!")
            print("Connected to MongoDB!")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            return False


class ExpenseTrackerWebAppDB(MongoConnector):
    @classmethod
    def parse_date(cls, date: Union[str, dt.datetime]):
        if isinstance(date, str):
            try:
                date = dt.datetime.strptime(date, "%Y-%m-%d")
            except Exception as e:  # defaults to today
                print(e)
                date = dt.datetime.now()
        return date

    def __init__(self, connection_string):
        super().__init__(connection_string)
        self.users = self.db.Users
        self.categories = self.db.Categories
        self.transactions = self.db.Transactions

    def upsert_user(self, username, name, email, password):
        now = dt.datetime.now()
        user = User(
            name=name, email=email, password=hash_password(password), groups=[]
        ).model_dump()

        self.users.update_one(
            {"_id": username},
            {
                # '$currentDate': {
                #     'updated_at': True,
                #     # 'deleted_at': True
                # },
                "$set": {**user, "updatedDate": now},
                "$setOnInsert": {"createdDate": now},
            },
            upsert=True,
        )
        return True

    def upsert_transaction(self, transaction_doc: dict) -> bool:
        """
        Insert or update a transaction in the database based on new GoCardlessTransaction fields.
        'transaction_doc' should have the keys that match GoCardlessTransaction.
        """
        now = dt.datetime.now()

        txn_model = GoCardlessTransaction(**transaction_doc)

        unique_id = None
        if txn_model.transactionId:
            unique_id = txn_model.transactionId
        elif txn_model.internalTransactionId:
            unique_id = txn_model.internalTransactionId
        else:
            # fallback? possibly user + bookingDate + something
            unique_id = str(now.timestamp())

        txn_dict = txn_model.model_dump(by_alias=True, exclude_none=True)

        self.transactions.update_one(
            {"_id": unique_id},
            {
                "$set": {**txn_dict, "updatedDate": now},
                "$setOnInsert": {"createdDate": now},
            },
            upsert=True,
        )
        return True

    def delete_user(self, username):
        return self.users.delete_one({"_id": username})

    def delete_all_users(self):
        return self.users.delete_many({})

    def delete_all_categories(self):
        return self.categories.delete_many({})

    def delete_all_transactions(self):
        return self.transactions.delete_many({})

    def delete_all(self):
        self.delete_all_users()
        self.delete_all_categories()
        self.delete_all_transactions()

    def close(self):
        self.client.close()

    def __del__(self):
        self.close()
