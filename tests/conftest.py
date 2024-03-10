import os
import tempfile

import pytest
from plaid_investments import create_app
from plaid_investments.client import Client
from plaid_investments.db import get_db, init_db
from flask import Flask
from flask.testing import FlaskClient, FlaskCliRunner

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as _f:
    _data_sql = _f.read().decode("utf8")


@pytest.fixture
def app() -> Flask:
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "SECRET_KEY": "test",
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def flask_client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app) -> FlaskCliRunner:
    return app.test_cli_runner()

@pytest.fixture
def plaid_client():
    return Client("", "", "sandbox")


class AuthActions(object):
    def __init__(self, flask_client: FlaskClient):
        self._client: FlaskClient = flask_client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password},
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(flask_client):
    return AuthActions(flask_client)
