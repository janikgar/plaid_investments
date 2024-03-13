from flask import (
    Flask,
    jsonify,
    url_for,
    render_template,
    request,
    send_from_directory,
    redirect,
    flash,
    session,
    g,
    make_response,
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from .client import Client
from . import db
import os


def create_app(test_config: dict = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY="dev",
            DATABASE=os.path.join(app.instance_path, "plaid-investments.sqlite"),
        )
    else:
        app.config.from_mapping(test_config)

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    load_dotenv()

    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET_KEY = os.getenv("PLAID_SECRET_KEY")
    PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

    plaid_client = Client(PLAID_CLIENT_ID, PLAID_SECRET_KEY, PLAID_ENV)
    plaid_client.init_plaid_client()

    @app.before_request
    def load_logged_in_user():
        user_id = session.get("user_id")

        if user_id is None:
            g.user = None
        else:
            g.user = (
                db.get_db()
                .execute(
                    "SELECT * FROM user WHERE id = ?",
                    (user_id,),
                )
                .fetchone()
            )

    @app.route("/")
    def hello_world():
        return jsonify(
            {
                "name": "Plaid Investments",
                "version": "0.1.0",
            }
        )

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    @app.route("/auth/register", methods=("GET", "POST"))
    def register():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            password2 = request.form["password2"]

            if (not username) or (not password) or (not password2):
                flash("all fields must be entered")

            this_db = db.get_db()
            try:
                this_db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                this_db.commit()
            except Exception as e:
                flash(f"Username {username} already registered: {e}")
            else:
                return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/auth/login", methods=("GET", "POST"))
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]

            this_db = db.get_db()
            error = None
            user = this_db.execute(
                "SELECT * FROM user WHERE username = ?", (username,)
            ).fetchone()

            if user is None:
                error = "no such user"
            elif not check_password_hash(user["password"], password):
                error = "user and password not correct"

            if error is None:
                session.clear()
                session["user_id"] = user["id"]
                return redirect(url_for("index"))
            else:
                flash(error)

        return render_template("login.html")

    @app.route("/auth/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/link")
    def link():
        return render_template("link.html")

    @app.route("/accounts")
    def accounts():
        account_list = []
        accounts = get_accounts()
        if accounts.status_code == 200:
            account_list = accounts.json["accounts"]
        return render_template("accounts.html", accounts=account_list)

    @app.route("/index")
    def index():
        return render_template("index.html")

    @app.route("/api/create_link_token")
    def create_link_token():
        if g.user:
            user_id = session.get("user_id")
            print(type(user_id))
            return jsonify(plaid_client.create_link_token(str(user_id)))

    @app.route("/api/exchange_public_token", methods=["POST"])
    def exchange_public_token():
        public_token = request.json["public_token"]
        return jsonify(plaid_client.exchange_public_token(public_token))

    @app.route("/api/create_item", methods=["POST"])
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

    @app.route("/api/create_accounts_from_item", methods=["POST"])
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

    @app.route("/api/get_accounts", methods=["GET"])
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

    db.init_app(app)

    return app
