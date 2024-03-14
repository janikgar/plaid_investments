from flask import (
    jsonify,
    url_for,
    render_template,
    request,
    send_from_directory,
    redirect,
    flash,
    session,
    Blueprint,
)
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import os
import requests

static_page = Blueprint('static_page',__name__)

@static_page.route("/")
def hello_world():
    return jsonify(
        {
            "name": "Plaid Investments",
            "version": "0.1.0",
        }
    )

@static_page.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(static_page.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

@static_page.route("/auth/register", methods=("GET", "POST"))
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
            return redirect(url_for("static_page.login"))

    return render_template("register.html")

@static_page.route("/auth/login", methods=("GET", "POST"))
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
            return redirect(url_for("static_page.index"))
        else:
            flash(error)

    return render_template("login.html")

@static_page.route("/auth/logout")
def logout():
    session.clear()
    return redirect(url_for("static_page.index"))

@static_page.route("/link")
def link():
    return render_template("link.html")

@static_page.route("/accounts")
def accounts():
    return render_template("accounts.html")

@static_page.route("/index")
def index():
    return render_template("index.html")
