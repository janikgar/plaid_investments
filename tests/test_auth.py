import pytest
import re
from flask import g, session, Flask
from flask.testing import FlaskClient
from plaid_investments.db import get_db
from .conftest import AuthActions


def test_register(flask_client: FlaskClient, app: Flask):
    assert flask_client.get("/auth/register").status_code == 200
    response = flask_client.post(
        "/auth/register", data={"username": "a", "password": "a", "password2": "a"}
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert (
            get_db()
            .execute(
                "SELECT * FROM user WHERE username = 'a'",
            )
            .fetchone()
            is not None
        )

    response = flask_client.post(
        "/auth/register",
        data={"username": "b", "password": "b", "password2": ""},
        follow_redirects=True,
    )
    assert re.search("all fields must be entered", response.get_data(as_text=True))

    response = flask_client.post(
        "/auth/register",
        data={"username": "test", "password": "test", "password2": "test"},
        follow_redirects=True,
    )
    assert re.search(
        "Username test already registered", response.get_data(as_text=True)
    )


def test_login(flask_client: FlaskClient, app: Flask):
    assert flask_client.get("/auth/login").status_code == 200

    response = flask_client.post("/auth/login", data={"username": "test", "password": "test"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/index"

    response = flask_client.post(
        "/auth/login",
        data={"username": "test", "password": "test2"},
        follow_redirects=True,
    )
    assert re.search("user and password not correct", response.get_data(as_text=True))

    response = flask_client.post(
        "/auth/login",
        data={"username": "no such user", "password": "test2"},
        follow_redirects=True,
    )
    assert re.search("no such user", response.get_data(as_text=True))

def test_logout(flask_client: FlaskClient, auth: AuthActions):
    assert flask_client.get("/auth/logout").status_code == 302
    
    auth.login()
    with flask_client:
        auth.logout()
        assert 'user_id' not in session
