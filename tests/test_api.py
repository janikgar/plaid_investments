import json
from datetime import datetime

import pytest
import pook
from flask.testing import FlaskClient
from plaid.model.link_token_create_response import LinkTokenCreateResponse


@pytest.fixture(autouse=True)
def use_pook():
    pook.on()


def test_create_link_token(flask_client: FlaskClient):
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
    response = flask_client.get("/api/create_link_token")
    assert response.status_code == 200


# def test_exchange_public_token(flask_client: FlaskClient):
#     response = flask_client.post(
#         "/api/exchange_public_token",
#         data={"public_token": "0123456"},
#         headers={
#             "Content-Type": "application/json",
#         },
#     )
#     assert response.data == None
