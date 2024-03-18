from flask import (
    jsonify,
    request,
    flash,
    session,
    Blueprint,
    make_response,
    g,
    Response,
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
def create_link_token() -> Response:
    if g.user:
        user_id = session.get("user_id")
        print(type(user_id))
        return jsonify(plaid_client.create_link_token(str(user_id)))
            
    return make_response(jsonify({"error": "not authorized"}), 401, [])

@api.route("/api/exchange_public_token", methods=["POST"])
def exchange_public_token() -> Response:
    public_token = request.json["public_token"]
    return jsonify(plaid_client.exchange_public_token(public_token))

@api.route("/api/create_item", methods=["POST"])
def create_item() -> Response:
    item_id = request.json["item_id"]
    access_token = request.json["access_token"]

    if g.user:
        this_db = db.get_db()
        try:
            print(item_id, session["user_id"], access_token)
            this_db.execute("""
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
            flash(f"could not add item: {e}")
            response = make_response(
                jsonify({"error": f"could not add item: {e}"}), 500, []
            )
            return response

    return make_response(jsonify({"error": "not authorized"}), 401, [])

@api.route("/api/create_accounts_from_item", methods=["POST"])
def create_accounts_from_item() -> Response:
    access_token = request.json["access_token"]
    item_id = request.json["item_id"]

    if g.user:
        account_info = plaid_client.get_account_info(access_token=access_token)
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
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    return make_response(jsonify({"error": "not authorized"}), 401, [])

@api.route("/api/get_accounts", methods=["GET"])
def get_accounts() -> Response:
    if g.user:
        this_db = db.get_db()
        try:
            raw_accounts = this_db.execute(
                """
                SELECT item_id,
                    friendly_name,
                    mask,
                    account_subtype,
                    official_name,
                    id
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
                    "account_id": item["id"],
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
    else:
        return make_response(jsonify({"error": "not authorized"}), 401, [])

@api.route("/api/get_account_balance")
def get_account_balance():
    if g.user:
        item = request.args['item']
        account_ids = request.args['account_ids']
        if type(account_ids) == str:
            account_ids = [account_ids]

        access_token = access_token_for_item(item)

        account_balance_info = plaid_client.get_account_balance(access_token,item, account_ids)
        accounts_with_balance = [
            {
                "account_id": account["account_id"],
                "balance_available": account["balances"]["available"],
                "balance_current": account["balances"]["current"],
                "balance_limit": account["balances"]["limit"],
                "currency": account["balances"]["iso_currency_code"]
            } for account in account_balance_info['accounts']
        ]
        return jsonify({
            "user_id": session["user_id"],
            "item": item,
            "accounts_balances": accounts_with_balance,
        })
    else:
        return make_response(jsonify({"error": "not authorized"}), 401, [])

def access_token_for_item(item_id: str) -> str:
    if g.user:
        this_db = db.get_db()
        try:
            row = this_db.execute("SELECT access_token FROM item WHERE id = (?)", (item_id,)).fetchone()
            if row is None:
                return ""
            return row['access_token']
        except Exception as e:
            raise Exception(f"could not get access_token for item {item_id}: {e}")
    pass
