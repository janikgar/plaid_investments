import json
from datetime import datetime

import pytest
import pook
import uuid
from flask.testing import FlaskClient
from plaid.model.link_token_create_response import LinkTokenCreateResponse
from plaid.model.item_public_token_exchange_response import (
    ItemPublicTokenExchangeResponse,
)

from .conftest import AuthActions


@pytest.fixture(autouse=True)
def use_pook():
    pook.on()


def test_create_link_token(flask_client: FlaskClient, auth: AuthActions):
    response_dict = {
        "link_token": "0123456",
        "expiration": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "request_id": "abcdefg",
    }
    pook.post(
        "https://sandbox.plaid.com:443/link/token/create",
        response=LinkTokenCreateResponse(
            response_dict["link_token"],
            datetime.strptime(response_dict["expiration"], "%Y-%m-%d %H:%M:%S"),
            response_dict["request_id"],
            _body=json.dumps(response_dict),
            _headers="",
            _status=200,
        ),
    )
    auth.login()
    with flask_client:
        response = flask_client.get("/api/create_link_token")
        assert response.status_code == 200


def test_exchange_public_token(flask_client: FlaskClient):
    response_dict = {
        "access_token": str(uuid.uuid4()),
        "item_id": "foo",
        "request_id": "bar",
    }
    pook.post(
        "https://sandbox.plaid.com:443/item/public_token/exchange",
        response=ItemPublicTokenExchangeResponse(
            str(uuid.uuid4()),
            "foo",
            "bar",
            _body=json.dumps(response_dict),
            _headers="",
            _status=200,
        ),
    )
    response = flask_client.post(
        "/api/exchange_public_token",
        json={"public_token": f"access-test-{str(uuid.uuid4())}"},
    )
    assert response.status_code == 200
