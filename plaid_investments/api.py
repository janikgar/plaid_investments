from flask import (
    jsonify,
    request,
    flash,
    session,
    Blueprint,
    g,
)
from . import db
from .client import Client
import os
from dotenv import load_dotenv

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET_KEY = os.getenv("PLAID_SECRET_KEY")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

plaid_client = Client(PLAID_CLIENT_ID, PLAID_SECRET_KEY, PLAID_ENV)
plaid_client.init_plaid_client()

api = Blueprint('api',__name__)

@api.route("/api/create_link_token")
def create_link_token():
    if g.user:
        user_id = session.get("user_id")
        print(type(user_id))
        return jsonify(plaid_client.create_link_token(str(user_id)))

@api.route("/api/exchange_public_token", methods=["POST"])
def exchange_public_token():
    public_token = request.json["public_token"]
    return jsonify(plaid_client.exchange_public_token(public_token))

@api.route("/api/create_item", methods=["POST"])
def create_item():
    item_id = request.json["item_id"]
    access_token = request.json["access_token"]

    if g.user:
        this_db = db.get_db()
        try:
            this_db.execute(
                """
                INSERT INTO item (
                    id,
                    user_id,
                    access_token
                ) VALUES (?, ?, ?)
                """,
                (item_id, session["user_id"], access_token),
            )
            this_db.commit()
            return jsonify(
                {
                    "status": "added",
                    "user": session["user_id"],
                    "item_id": item_id,
                    "access_token": access_token,
                }
            )
        except Exception as e:
            flash(f"Could not add account: {e}")
            response = make_response(
                jsonify({"error": f"could not add account: {e}"}), 500, []
            )
            return response

@api.route("/api/create_accounts_from_item", methods=["POST"])
def create_accounts_from_item():
    access_token = request.json["access_token"]
    item_id = request.json["item_id"]

    account_info = plaid_client.get_account_info(access_token=access_token)

    if g.user:
        this_db = db.get_db()
        try:
            for account in account_info["accounts"]:
                this_db.execute(
                    """
                    INSERT INTO account (
                        id,
                        user_id,
                        item_id,
                        friendly_name,
                        official_name,
                        mask,
                        account_type,
                        account_subtype,
                        persistent_account_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?),
                    """,
                    (
                        account["account_id"],
                        session["user_id"],
                        item_id,
                        account["name"],
                        account["official_name"],
                        account["mask"],
                        account["type"],
                        account["subtype"],
                        account["persistent_account_id"],
                    ),
                )
                this_db.commit()
            return jsonify(
                {
                    "status": f"added {len(account_info["accounts"])} accounts",
                    "user": session["user_id"],
                }
            )
        except Exception as e:
            flash(f"could not add accounts: {e}")
            response = make_response(
                jsonify({"error": f"could not add accounts: {e}"}), 500, []
            )
            return response

@api.route("/api/get_accounts", methods=["GET"])
def get_accounts():
    if g.user:
        this_db = db.get_db()
        try:
            raw_accounts = this_db.execute(
                """
                SELECT item_id,
                    friendly_name,
                    mask,
                    account_subtype,
                    official_name
                    FROM account WHERE user_id = (?)
                """,
                (session["user_id"],),
            ).fetchall()

            accounts = [
                {
                    "item_id": item["item_id"],
                    "friendly_name": item["friendly_name"],
                    "mask": item["mask"],
                    "subtype": item["account_subtype"],
                    "official_name": item["official_name"],
                    }
                for item in raw_accounts
            ]
            return jsonify({
                "user_id": session["user_id"],
                "accounts": accounts,
                })
        except Exception as e:
            response = make_response(
                jsonify({"error": f"could not get accounts: {e}"}), 500, []
            )
            return response
