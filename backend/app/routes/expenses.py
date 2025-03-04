# backend/app/routes/expenses.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.utils.mongo_user import MongoUser
from urllib.parse import unquote
from app import create_app
import json

expenses = Blueprint("expenses", __name__)


@expenses.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    data = request.get_json() or request.form
    description = data.get("expenseDescription")
    category = data.get("expenseCategory")
    sub_category = data.get("expenseSubCategory")
    date = data.get("expenseDate")
    cost = data.get("expenseCost")

    if not all([description, category, cost]):
        return {"error": "Missing fields"}, 400

    app = create_app()
    user_id = current_user.id  # from MongoUser
    new_expense_doc = {
        "description": description,
        "category": category,
        "sub_category": sub_category,
        "date_of_expense": date,
        "cost": float(cost),
        "user_id": user_id,
        # maybe store a createdAt, updatedAt, etc.
    }
    print(json.dumps(new_expense_doc, indent=2))
    # app.mongo.transactions.insert_one(new_expense_doc)
    return {"success": True}


@expenses.route("/delete_expense/<expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    app = create_app()
    # find expense
    expense_doc = app.mongo.transactions.find_one({"_id": expense_id})
    if not expense_doc:
        return {"error": "Expense not found"}, 404
    # Check ownership
    if expense_doc["user_id"] != current_user.id:
        return {"error": "Unauthorized"}, 403

    app.mongo.transactions.delete_one({"_id": expense_id})
    return {"success": True}


@expenses.route("/edit_expense/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    app = create_app()
    expense_doc = app.mongo.transactions.find_one({"_id": expense_id})
    if not expense_doc:
        return {"error": "Expense not found"}, 404
    if expense_doc["user_id"] != current_user.id:
        return {"error": "Unauthorized"}, 403

    data = request.get_json() or request.form
    description = data.get("expenseDescription")
    category = data.get("expenseCategory")
    sub_category = data.get("expenseSubCategory")
    date = data.get("expenseDate")
    cost = data.get("expenseCost")

    update_fields = {}
    if description:
        update_fields["description"] = description
    if category:
        update_fields["category"] = category
    if sub_category:
        update_fields["sub_category"] = sub_category
    if date:
        update_fields["date_of_expense"] = date
    if cost:
        update_fields["cost"] = float(cost)

    app.mongo.transactions.update_one({"_id": expense_id}, {"$set": update_fields})
    return {"success": True}


@expenses.route("/get_subcategories/<category>", methods=["GET"])
def get_subcategories(category):
    category = unquote(category)
    app = create_app()
    # We store categories in app.mongo.categories with _id=categoryName, subCategories=[...]
    cat_doc = app.mongo.categories.find_one({"_id": category})
    if not cat_doc:
        return jsonify([])
    return jsonify(cat_doc.get("subCategories", []))
