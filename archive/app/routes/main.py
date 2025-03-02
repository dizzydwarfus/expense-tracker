# backend/app/routes/main.py

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app import create_app
from datetime import datetime

main = Blueprint("main", __name__)


@main.route("/")
def index():
    # Could serve index.html or just respond with JSON
    return {"message": "Welcome to the Expense Tracker Backend"}


@main.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Return JSON data for the user's expenses, categories, etc.
    to be consumed by the Next.js frontend.
    """
    app = create_app()

    # fetch user’s expenses
    user_id = current_user.id
    expense_docs = list(app.mongo.transactions.find({"user_id": user_id}))

    # Group them by month & category
    expenses_by_month_category = {}
    for exp in expense_docs:
        # exp["date_of_expense"] might be a string
        date_str = exp.get("date_of_expense", "")
        if date_str:
            dt_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_year = dt_obj.strftime("%B %Y")
        else:
            month_year = "No Date"

        cat = exp.get("category", "Uncategorized")
        if month_year not in expenses_by_month_category:
            expenses_by_month_category[month_year] = {}
        if cat not in expenses_by_month_category[month_year]:
            expenses_by_month_category[month_year][cat] = []
        expenses_by_month_category[month_year][cat].append(exp)

    # fetch categories
    cat_docs = list(app.mongo.categories.find({}))
    unique_categories = [c["_id"] for c in cat_docs]
    # if subCategories embedded, you can aggregate them
    unique_sub_categories = []
    for c in cat_docs:
        scs = c.get("subCategories", [])
        for sc in scs:
            if sc not in unique_sub_categories:
                unique_sub_categories.append(sc)

    # For chart data
    # 1) categories: array of category names
    # 2) amounts: sum of cost for each category
    # 3) dates: list of month-year keys
    # 4) categoryData: array of datasets
    amounts = []
    for catName in unique_categories:
        sum_for_cat = 0.0
        for exp in expense_docs:
            if exp.get("category") == catName:
                sum_for_cat += float(exp.get("cost", 0))
        amounts.append(sum_for_cat)

    dates = list(expenses_by_month_category.keys())

    categoryData = []
    for catName in unique_categories:
        cat_data_points = []
        for d in dates:
            cat_sum = 0.0
            if catName in expenses_by_month_category[d]:
                for e in expenses_by_month_category[d][catName]:
                    cat_sum += float(e.get("cost", 0))
            cat_data_points.append(cat_sum)
        dataset = {
            "label": catName,
            "data": cat_data_points,
            "backgroundColor": "random color",
        }
        categoryData.append(dataset)

    response = {
        "user": {
            "id": user_id,
            # If you stored more data in user doc, e.g. userDoc["email"]
            "username": user_id,
        },
        "expenses_by_month_category": expenses_by_month_category,
        "categories": unique_categories,
        "sub_categories": unique_sub_categories,
        "chart_data": {
            "categories": unique_categories,
            "amounts": amounts,
            "dates": dates,
            "categoryData": categoryData,
        },
    }

    return jsonify(response)
