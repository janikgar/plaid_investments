import pytest
import re
from flask.testing import FlaskClient


def test_link(flask_client: FlaskClient):
    response = flask_client.get("/link")
    assert response.status_code == 200
    assert re.search("Link account", response.get_data(as_text=True))

def test_index(flask_client: FlaskClient):
    response = flask_client.get("/index")
    assert response.status_code == 200
    assert re.search("Home", response.get_data(as_text=True))
