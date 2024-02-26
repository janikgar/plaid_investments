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
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = db.get_db().execute(
                'SELECT * FROM user WHERE id = ?',
                (user_id,),
            ).fetchone()

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

        return render_template("login.html")

    @app.route("/auth/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.route("/link")
    def link():
        return render_template("link.html")

    @app.route("/index")
    def index():
        return render_template("index.html")

    @app.route("/api/create_link_token")
    def create_link_token():
        return jsonify(plaid_client.create_link_token("1"))

    @app.route("/api/exchange_public_token", methods=["POST"])
    def exchange_public_token():
        public_token = request.json["public_token"]
        return jsonify(plaid_client.exchange_public_token(public_token))

    db.init_app(app)

    return app
