# backend/app/routes/banks.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import create_app
from app.utils.bank_auth.gocardless_api import ApiClient
import os
from dotenv import load_dotenv

load_dotenv()

bank_bp = Blueprint("bank", __name__)


@bank_bp.route("/banks/link_bank", methods=["POST"])
@login_required
def link_bank():
    """
    1. Creates an end user agreement
    2. Creates a link to bank account
    3. Returns the link for the user to open
    """
    # We'll store the user-specific tokens, etc. in your Mongo "Users" or a dedicated collection
    # For demonstration, let's assume user doc has fields for 'gocardless_agreement', 'gocardless_requisition', etc.
    data = request.get_json() or {}
    institution_id = data.get("institution_id", "ING_INGBNL2A")
    max_historical_days = data.get("max_historical_days", "90")
    access_valid_for_days = data.get("access_valid_for_days", "180")
    access_scope = data.get("access_scope", ["balances", "transactions", "details"])

    app = create_app()
    user_doc = app.mongo.users.find_one({"_id": current_user.id})
    if not user_doc:
        return jsonify({"error": "User not found"}), 404

    # We'll create a new ApiClient instance with user's access token (or global if none yet)
    access_token = os.environ.get("GOCARDLESS_ACCESS_TOKEN", "")
    base_url = os.environ.get("GOCARDLESS_BANK_ACCOUNT_INFO_BASE_URL", "")
    if not access_token or not base_url:
        return jsonify({"error": "Missing GoCardless tokens or base URL in env"}), 400

    client = ApiClient(base_url=base_url, access_token=access_token)

    # 1) Create end user agreement
    agreement_resp = client.create_end_user_agreement(
        path="agreements/enduser/",
        institution_id=institution_id,  # or pass from front end
        max_historical_days=max_historical_days,
        access_valid_for_days=access_valid_for_days,
        access_scope=access_scope,
    )
    # store it in user doc
    app.mongo.users.update_one(
        {"_id": current_user.id}, {"$set": {"gocardless_agreement": agreement_resp}}
    )

    # 2) Link bank account (create requisition), get the link
    link_resp = client.link_bank_account(
        path="requisitions/",
        redirect_url="http://localhost:8000/callback",  # or your real callback
        open_browser=True,  # We'll just return the link instead
        user_language="EN",
    )
    # store it
    app.mongo.users.update_one(
        {"_id": current_user.id}, {"$set": {"gocardless_requisition": link_resp}}
    )

    return jsonify({"success": True}), 200


@bank_bp.route("/banks/import", methods=["POST"])
@login_required
def import_transactions():
    """
    Called from the ImportTransactionsModal. We read date_from, date_to,
    then call get_transactions on the user's linked account, storing them in DB.
    """
    data = request.get_json() or {}
    date_from = data.get("date_from")
    date_to = data.get("date_to")
    if not date_from or not date_to:
        return jsonify({"error": "Missing date_from or date_to"}), 400

    app = create_app()

    # get user doc
    user_doc = app.mongo.users.find_one({"_id": current_user.id})
    if not user_doc:
        return jsonify({"error": "User not found"}), 404

    # check if user has a linked account
    gocardless_req = user_doc.get("gocardless_requisition", {})
    accounts = gocardless_req.get("accounts", [])
    if not accounts:
        return jsonify({"error": "No linked bank accounts"}), 400

    account_id = accounts[0]  # or let user pick which account from your front end

    # create client
    access_token = os.environ.get("GOCARDLESS_ACCESS_TOKEN", "")
    base_url = os.environ.get("GOCARDLESS_BANK_ACCOUNT_INFO_BASE_URL", "")

    client = ApiClient(base_url=base_url, access_token=access_token)

    trans_resp = client.get_transactions(account_id, date_from, date_to)
    print("Account ID: ", account_id)
    print("Date From: ", date_from)
    print("Date To: ", date_to)
    # print("Transactions ", trans_resp)

    # store each transaction doc in your "transactions" collection, or do further processing
    # e.g. trans_resp["transactions"]["booked"]
    booked = trans_resp["transactions"].get("booked", [])
    pending = trans_resp["transactions"].get("pending", [])

    # we'll add user_id = current_user.id so we can filter them later
    for t in booked:
        t["username"] = current_user.id
    for t in pending:
        t["username"] = current_user.id

    # insert in your DB
    if booked:
        app.mongo.upsert_transaction(booked)
    if pending:
        app.mongo.upsert_transaction(pending)

    return jsonify({"success": True, "imported": len(booked) + len(pending)}), 200


@bank_bp.route("/callback", methods=["GET"])
def callback():
    """
    Called by GoCardless after user finishes linking the bank account.
    Example URL: http://localhost:8000/callback?ref={requisition_id}
    We can use 'ref' to list user accounts, and also fetch the end-user agreement to update our DB.
    """

    # 1. Parse the requisition_id from query param 'ref'
    requisition_id = request.args.get("ref")
    if not requisition_id:
        return (
            """
        <html>
          <body>
            <h2>Callback Error</h2>
            <p>Missing ?ref={requisition_id}</p>
          </body>
        </html>
        """,
            400,
        )

    app = create_app()

    # 2. Check if user is logged in or how you track user.
    #    Sometimes the callback might not have a session, so you might store the requisition_id in the user's doc earlier.
    #    For demonstration, let's assume you can find the user doc by searching for gocardless_requisition.id == requisition_id
    #    or you do an open callback without login_required.
    user_doc = app.mongo.users.find_one({"gocardless_requisition.id": requisition_id})
    if not user_doc:
        # no user doc found with that requisition
        return (
            """
        <html>
          <body>
            <h2>Callback Error</h2>
            <p>No user found with requisition_id = {0}</p>
          </body>
        </html>
        """.format(requisition_id),
            404,
        )

    # 3. Build the client with your stored or global access token
    access_token = os.environ.get("GOCARDLESS_ACCESS_TOKEN", "")
    base_url = os.environ.get("GOCARDLESS_BANK_ACCOUNT_INFO_BASE_URL", "")
    if not access_token or not base_url:
        return (
            """
        <html>
          <body>
            <h2>Callback Error</h2>
            <p>Missing GOCARDLESS_ACCESS_TOKEN or base_url</p>
          </body>
        </html>
        """,
            500,
        )

    client = ApiClient(base_url=base_url, access_token=access_token)

    # 4. List accounts for that requisition
    #    e.g. client.list_accounts(path="requisitions/", requisition_id=requisition_id)
    accounts_resp = client.list_accounts(
        path="requisitions/", requisition_id=requisition_id
    )
    # Typically returns a structure like { "id": "xxxx", "accounts": [...] } or so
    # or maybe { "results": [...] }. Adjust as needed
    print(f"Accounts for requisition {requisition_id}:", accounts_resp)

    # 6. If you need the agreement_id from either your user doc or from accounts_resp
    #    Let's say your user doc has the 'gocardless_requisition.agreement'
    #    or we do a quick get: agreement_id = user_doc["gocardless_requisition"]["agreement"]
    agreement_id = user_doc.get("gocardless_requisition", {}).get("agreement")
    if not agreement_id:
        return (
            """
        <html>
          <body>
            <h2>Callback Error</h2>
            <p>No agreement_id found in user doc. Possibly not stored earlier?</p>
          </body>
        </html>
        """,
            400,
        )

    agreement_resp = client.get_agreement(
        path="agreements/enduser", agreement_id=agreement_id
    )
    print("Updated End User Agreement:", agreement_resp)

    update_data = {
        "gocardless_requisition": accounts_resp,
        "gocardless_agreement": agreement_resp,
    }
    app.mongo.users.update_one({"_id": user_doc["_id"]}, {"$set": update_data})

    # 9. Show a success message or redirect to your front end
    return jsonify(
        {
            "success": True,
        }
    ), 200


@bank_bp.route("/banks/refresh_link", methods=["POST"])
@login_required
def refresh_link_account():
    """
    Refreshes the user's bank link status by re-calling:
      1) list_accounts with the stored requisition_id
      2) get_agreement with the stored agreement_id
    Then updates user doc with new data.
    For example, a "Refresh Link Status" button can call this route.
    """
    app = create_app()
    user_doc = app.mongo.users.find_one({"_id": current_user.id})
    if not user_doc:
        return jsonify({"error": "User not found"}), 404

    # Retrieve previously stored data
    gocardless_req = user_doc.get("gocardless_requisition", {})
    requisition_id = gocardless_req.get("id")
    if not requisition_id:
        return jsonify({"error": "No requisition_id found in user doc"}), 400

    agreement_id = gocardless_req.get("agreement") or user_doc.get(
        "gocardless_agreement", {}
    ).get("id")
    if not agreement_id:
        return jsonify({"error": "No agreement_id found in user doc"}), 400

    # Build the ApiClient
    access_token = os.environ.get("GOCARDLESS_ACCESS_TOKEN", "")
    base_url = os.environ.get("GOCARDLESS_BANK_ACCOUNT_INFO_BASE_URL", "")
    if not access_token or not base_url:
        return jsonify(
            {"error": "Missing GOCARDLESS_ACCESS_TOKEN or base_url in env"}
        ), 500

    client = ApiClient(base_url=base_url, access_token=access_token)

    # 1) List accounts with requisition_id
    accounts_resp = client.list_accounts(
        path="requisitions/", requisition_id=requisition_id
    )
    # 2) Get updated agreement data
    agreement_resp = client.get_agreement(
        path="agreements/enduser", agreement_id=agreement_id
    )

    # 3) Update the user doc
    update_data = {
        "gocardless_requisition": accounts_resp,  # or merge with existing if you prefer
        "gocardless_agreement": agreement_resp,
    }
    app.mongo.users.update_one({"_id": current_user.id}, {"$set": update_data})

    return jsonify(
        {"success": True, "accounts": accounts_resp, "agreement": agreement_resp}
    ), 200
