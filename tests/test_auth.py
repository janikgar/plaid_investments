import pytest
import re
from flask import g, session, Flask
from flask.testing import FlaskClient
from plaid_investments.db import get_db


def test_register(client: FlaskClient, app: Flask):
    assert client.get("/auth/register").status_code == 200
    response = client.post(
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

    response = client.post(
        "/auth/register",
        data={"username": "b", "password": "b", "password2": ""},
        follow_redirects=True,
    )
    assert re.search("all fields must be entered", response.get_data(as_text=True))

    response = client.post(
        "/auth/register",
        data={"username": "test", "password": "test", "password2": "test"},
        follow_redirects=True,
    )
    assert re.search(
        "Username test already registered", response.get_data(as_text=True)
    )