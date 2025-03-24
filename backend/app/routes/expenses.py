# backend/app/routes/expenses.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from urllib.parse import unquote
from datetime import datetime
from app import create_app
import json

expenses = Blueprint("expenses", __name__)


@expenses.route("/add_expense", methods=["POST"])
@login_required
def add_expense():
    """
    Creates a new transaction document in MongoDB following the GoCardlessTransaction model structure.
    """
    data = request.get_json() or request.form

    # Extract fields from the request, mapping them to GoCardlessTransaction
    transaction_id = data.get("transactionId")
    end_to_end_id = data.get("endToEndId")
    booking_date = data.get("bookingDate")  # e.g. "YYYY-MM-DD" or None
    amount_str = data.get("amount")  # part of transactionAmount
    currency = data.get("currency", "EUR")
    debtor_name = data.get("debtorName")
    debtor_iban = data.get("debtorIban")
    creditor_name = data.get("creditorName")
    creditor_iban = data.get("creditorIban")
    remittance_info = data.get("remittanceInformationUnstructured")
    bank_tx_code = data.get("proprietaryBankTransactionCode")
    internal_tx_id = data.get("internalTransactionId")
    transaction_type = data.get("transactionType")  # "expense" or "income"
    category = data.get("category")
    sub_category = data.get("sub_category")
    username = data.get("username")

    # Basic validation: some fields might be required
    if not username or not transaction_type or not amount_str:
        return jsonify(
            {"error": "Missing required fields (username, transactionType, amount)"}
        ), 400

    # Convert amount to float
    try:
        amount_val = float(amount_str)
    except ValueError:
        return jsonify({"error": "Invalid amount value"}), 400

    # Convert bookingDate to a valid date if provided
    parsed_date_str = None
    if booking_date:
        try:
            # Validate date format "YYYY-MM-DD"
            dt_obj = datetime.strptime(booking_date, "%Y-%m-%d")
            parsed_date_str = booking_date  # store as string if you like, or dt_obj if you want a real date
        except ValueError:
            return jsonify(
                {"error": "Invalid bookingDate format (expected YYYY-MM-DD)"}
            ), 400

    # Build the Mongo doc
    new_transaction_doc = {
        "transactionId": transaction_id,
        "endToEndId": end_to_end_id,
        "bookingDate": parsed_date_str,
        "transactionAmount": {"amount": amount_val, "currency": currency},
        "debtorName": debtor_name,
        "debtorAccount": {"iban": debtor_iban} if debtor_iban else None,
        "creditorName": creditor_name,
        "creditorAccount": {"iban": creditor_iban} if creditor_iban else None,
        "remittanceInformationUnstructured": remittance_info,
        "proprietaryBankTransactionCode": bank_tx_code,
        "internalTransactionId": internal_tx_id,
        "transactionType": transaction_type,  # "expense" or "income"
        "category": category,
        "sub_category": sub_category,
        "username": current_user.id,
        "createdAt": datetime.now(),
    }

    app = create_app()
    # Insert into the 'Transactions' collection
    inserted = app.mongo.transactions.insert_one(new_transaction_doc)
    print("New Transaction Inserted:")
    print(json.dumps(new_transaction_doc, indent=2, default=str))

    return jsonify({"success": True, "inserted_id": str(inserted.inserted_id)}), 200


@expenses.route("/edit_expense/<expense_id>", methods=["POST"])
@login_required
def edit_expense(expense_id):
    """
    Updates an existing transaction in MongoDB. We find by _id = expense_id,
    then set fields from the GoCardlessTransaction structure.
    """
    app = create_app()
    existing_doc = app.mongo.transactions.find_one({"_id": expense_id})
    if not existing_doc:
        return jsonify({"error": "Transaction not found"}), 404
    # Check ownership
    if existing_doc.get("user_id") != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json() or request.form

    # Extract the same fields as in add_expense
    transaction_id = data.get("transactionId")
    end_to_end_id = data.get("endToEndId")
    booking_date = data.get("bookingDate")
    amount_str = data.get("amount")
    currency = data.get("currency", "EUR")
    debtor_name = data.get("debtorName")
    debtor_iban = data.get("debtorIban")
    creditor_name = data.get("creditorName")
    creditor_iban = data.get("creditorIban")
    remittance_info = data.get("remittanceInformationUnstructured")
    bank_tx_code = data.get("proprietaryBankTransactionCode")
    internal_tx_id = data.get("internalTransactionId")
    transaction_type = data.get("transactionType")
    category = data.get("category")
    sub_category = data.get("sub_category")
    username = current_user.id

    update_fields = {}
    # Convert if present
    if transaction_id is not None:
        update_fields["transactionId"] = transaction_id
    if end_to_end_id is not None:
        update_fields["endToEndId"] = end_to_end_id
    if booking_date:
        try:
            datetime.strptime(booking_date, "%Y-%m-%d")  # Validate format
            update_fields["bookingDate"] = booking_date
        except ValueError:
            return jsonify({"error": "Invalid bookingDate format"}), 400
    if amount_str:
        try:
            amt_val = float(amount_str)
            update_fields["transactionAmount"] = {
                "amount": amt_val,
                "currency": currency,
            }
        except ValueError:
            return jsonify({"error": "Invalid amount value"}), 400
    if debtor_name is not None:
        update_fields["debtorName"] = debtor_name
    if debtor_iban is not None:
        update_fields["debtorAccount"] = {"iban": debtor_iban}
    if creditor_name is not None:
        update_fields["creditorName"] = creditor_name
    if creditor_iban is not None:
        update_fields["creditorAccount"] = {"iban": creditor_iban}
    if remittance_info is not None:
        update_fields["remittanceInformationUnstructured"] = remittance_info
    if bank_tx_code is not None:
        update_fields["proprietaryBankTransactionCode"] = bank_tx_code
    if internal_tx_id is not None:
        update_fields["internalTransactionId"] = internal_tx_id
    if transaction_type is not None:
        update_fields["transactionType"] = transaction_type
    if category is not None:
        update_fields["category"] = category
    if sub_category is not None:
        update_fields["sub_category"] = sub_category
    if username is not None:
        update_fields["username"] = username

    # Last modified
    update_fields["updatedAt"] = datetime.utcnow()

    app.mongo.transactions.update_one({"_id": expense_id}, {"$set": update_fields})

    print(f"Transaction {expense_id} updated with:")
    print(json.dumps(update_fields, indent=2, default=str))

    return jsonify({"success": True}), 200


@expenses.route("/delete_expense/<expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    """
    Deletes a transaction doc from Mongo by _id, checking ownership.
    """
    app = create_app()
    expense_doc = app.mongo.transactions.find_one({"_id": expense_id})
    if not expense_doc:
        return jsonify({"error": "Transaction not found"}), 404
    if expense_doc.get("username") != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    app.mongo.transactions.delete_one({"_id": expense_id})
    return jsonify({"success": True}), 200


@expenses.route("/all_categories", methods=["GET"])
def get_categories():
    app = create_app()
    categories = list(app.mongo.categories.find())

    if not categories:
        return jsonify({"error": "No categories found"}), 404

    return jsonify(categories), 200


@expenses.route("/get_subcategories/<category>", methods=["GET"])
def get_subcategories(category):
    """
    Returns sub-categories for a given category from the 'Categories' collection,
    where doc._id = category, doc.subCategories = [...]
    """
    cat = unquote(category)
    app = create_app()
    cat_doc = app.mongo.categories.find_one({"_id": cat})
    if not cat_doc:
        return jsonify([])
    return jsonify(cat_doc.get("subCategories", []))
