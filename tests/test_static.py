import pytest
import re
from flask.testing import FlaskClient


def test_favicon(flask_client: FlaskClient):
    response = flask_client.get("/favicon.ico")
    assert response.status_code == 200


def test_health_check(flask_client: FlaskClient):
    response = flask_client.get("/")
    assert response.status_code == 200
    assert response.json["name"] == "Plaid Investments"


def test_index(flask_client: FlaskClient):
    response = flask_client.get("/index")
    assert response.status_code == 200
    assert re.search("Home", response.get_data(as_text=True))


def test_link(flask_client: FlaskClient):
    response = flask_client.get("/link")
    assert response.status_code == 200
    assert re.search("Link account", response.get_data(as_text=True))

def test_accounts(flask_client: FlaskClient):
    response = flask_client.get("/accounts")
    assert response.status_code == 200
    assert re.search("Accounts", response.get_data(as_text=True))
