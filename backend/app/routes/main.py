# backend/app/routes/main.py

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import create_app
from collections import defaultdict
from app.models.transactions import GoCardlessTransaction
from pydantic import ValidationError

main = Blueprint("main", __name__)


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Returns JSON data for the authenticated user's transactions (GoCardlessTransaction),
    plus chart usage.
    """
    app = create_app()
    user_id = current_user.id
    print(user_id)
    # Query all transactions for this user.
    # If your doc references user by e.g. "debtorName == user_id", adapt as needed:
    docs = list(app.mongo.transactions.find({"username": user_id}))

    if not docs:
        return jsonify(
            {
                "user": {"id": user_id},
                "transactions": [],
                "chart_data": {
                    "categories": [],
                    "amounts": [],
                    "dates": [],
                    "categoryData": [],
                },
            }
        ), 200

    # Convert each doc to a Python dict that includes the fields from GoCardlessTransaction
    transactions_for_frontend = []
    for doc in docs:
        try:
            # Validate doc with GoCardlessTransaction
            gtxn = GoCardlessTransaction(**doc)
        except ValidationError:
            # skip or handle
            continue

        # Format bookingDate if it's a datetime
        booked_str = ""
        if gtxn.bookingDate:
            booked_str = gtxn.bookingDate.strftime("%Y-%m-%d")

        # Build a dictionary for front end usage
        # e.g. "amount" is from gtxn.transactionAmount.amount
        txn_dict = {
            "id": str(gtxn.id) if gtxn.id else "",
            "transactionId": gtxn.transactionId,
            "endToEndId": gtxn.endToEndId,
            "bookingDate": booked_str,  # or None if pending
            "amount": gtxn.transactionAmount.amount,
            "currency": gtxn.transactionAmount.currency,
            "debtorName": gtxn.debtorName,
            "debtorAccount": gtxn.debtorAccount.model_dump()
            if gtxn.debtorAccount
            else None,
            "creditorName": gtxn.creditorName,
            "creditorAccount": gtxn.creditorAccount.model_dump()
            if gtxn.creditorAccount
            else None,
            "remittanceInformationUnstructured": gtxn.remittanceInformationUnstructured,
            "proprietaryBankTransactionCode": gtxn.proprietaryBankTransactionCode,
            "internalTransactionId": gtxn.internalTransactionId,
            "transactionType": gtxn.transactionType,
            "category": gtxn.category or "Uncategorized",
            "sub_category": gtxn.sub_category or "",
        }
        transactions_for_frontend.append(txn_dict)

    # Group for charting by month-year + category, using transactionType=expense as example
    expenses_by_month_category = defaultdict(lambda: defaultdict(list))

    for txn in transactions_for_frontend:
        # parse bookingDate
        date_str = txn["bookingDate"]
        if not date_str:
            # If no bookingDate => consider pending or ignore
            date_str = "Pending"

        try:
            dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_year = dt_obj.strftime("%B %Y")
        except ValueError:
            month_year = date_str  # "Pending" or "Unknown"

        cat = txn["category"]
        expenses_by_month_category[month_year][cat].append(txn)

    # Unique categories
    all_categories = set(txn["category"] for txn in transactions_for_frontend)
    unique_categories = sorted(all_categories)

    # For a simple "pie chart" style: sum amounts for transactionType=expense by category
    categories_list = list(unique_categories)
    amounts_list = []
    for cat in categories_list:
        total_for_cat = 0.0
        for txn in transactions_for_frontend:
            if txn["category"] == cat and txn["transactionType"] == "expense":
                total_for_cat += float(txn["amount"])
        amounts_list.append(total_for_cat)

    # Build stacked bar style data
    dates_list = sorted(expenses_by_month_category.keys())
    categoryData = []
    for cat in categories_list:
        dataset_values = []
        for d in dates_list:
            cat_sum = 0.0
            if cat in expenses_by_month_category[d]:
                for txn in expenses_by_month_category[d][cat]:
                    if txn["transactionType"] == "expense":
                        cat_sum += float(txn["amount"])
            dataset_values.append(cat_sum)
        dataset = {
            "label": cat,
            "data": dataset_values,
            "backgroundColor": "rgba(255, 99, 132, 0.2)",
        }
        categoryData.append(dataset)

    return jsonify(
        {
            "user": {"id": user_id},
            "transactions": transactions_for_frontend,
            "chart_data": {
                "categories": categories_list,
                "amounts": amounts_list,
                "dates": dates_list,
                "categoryData": categoryData,
            },
        }
    ), 200
