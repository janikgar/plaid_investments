import json
from datetime import datetime
import re

import pytest
import pook
import uuid
from flask.testing import FlaskClient
from plaid.model.accounts_get_response import AccountsGetResponse
from plaid.model.account_base import AccountBase
from plaid.model.account_balance import AccountBalance
from plaid.model.account_type import AccountType
from plaid.model.account_subtype import AccountSubtype
from plaid.model.item import Item
from plaid.model.plaid_error import PlaidError
from plaid.model.plaid_error_type import PlaidErrorType
from plaid.model.item_public_token_exchange_response import (
    ItemPublicTokenExchangeResponse,
)
from plaid.model.link_token_create_response import LinkTokenCreateResponse

from unittest.mock import MagicMock

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

    auth.logout()
    with flask_client:
        response = flask_client.get("api/create_link_token")
        assert response


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


@pytest.mark.parametrize(
    "logged_in,response_code,response_text,access_token",
    [
        (True, 200, "added", "0123456"),
        (False, 401, "not authorized", ""),
        (True, 500, "could not add item", None),
    ],
)
def test_create_item(
    flask_client: FlaskClient,
    auth: AuthActions,
    logged_in: bool,
    response_code: int,
    response_text: str,
    access_token: any,
):
    if logged_in:
        auth.login()
    with flask_client:
        response = flask_client.post(
            "/api/create_item",
            json={"item_id": "0123456", "access_token": access_token},
        )
        assert response.status_code == response_code
        assert re.search(response_text, response.get_data(as_text=True))


@pytest.mark.parametrize(
    "logged_in,response_code,response_text,access_token",
    [
        (True, 200, "added 1 accounts", "0123456"),
        (False, 401, "not authorized", ""),
        (True, 500, "could not add accounts", "0123456"),
    ],
)
def test_create_accounts_from_item(
    flask_client: FlaskClient,
    auth: AuthActions,
    logged_in: bool,
    response_code: int,
    response_text: str,
    access_token: any,
):
    if logged_in:
        mock_json = {
            "accounts": [
                {
                    "account_id": "0",
                    "balances": {
                        "available": 0.0,
                        "current": 1.1,
                        "limit": 2.2,
                        "iso_currency_code": "3",
                        "unofficial_currency_code": "4",
                    },
                    "mask": "2",
                    "name": "3",
                    "official_name": "4",
                    "type": "foo",
                    "subtype": "bar",
                    "persistent_account_id": "5",
                },
            ],
            "request_id": "",
            "item": {
                "item_id": "",
                "webhook": "",
                "error": {
                    "error_type": "",
                    "error_code": "",
                    "error_message": "",
                    "display_message": "",
                },
                "available_products": [],
                "billed_products": [],
                "consent_expiration_time": None,
                "update_type": "",
            },
        }
        mock_response = AccountsGetResponse(
            accounts=[
                AccountBase(
                    "0",
                    AccountBalance(0.0, 1.1, 2.2, "3", "4"),
                    "2",
                    "3",
                    "4",
                    AccountType("foo"),
                    AccountSubtype("bar"),
                    persistent_account_id="5",
                ),
            ],
            request_id="",
            item=Item(
                item_id="",
                webhook="",
                error=PlaidError(
                    error_type=PlaidErrorType(""),
                    error_code="",
                    error_message="",
                    display_message="",
                ),
                available_products=[],
                billed_products=[],
                consent_expiration_time=None,
                update_type="",
            ),
            _body=json.dumps(mock_json),
            _headers="",
            _status=200,
        )

        pook.post(
            "https://sandbox.plaid.com:443/accounts/get",
            response=mock_response,
        ).times(2)
        auth.login()
    with flask_client:
        if response_code == 500:
            flask_client.post(
                "/api/create_accounts_from_item",
                json={"item_id": "78910", "access_token": access_token},
            )
        response = flask_client.post(
            "/api/create_accounts_from_item",
            json={"item_id": "78910", "access_token": access_token},
        )
        assert response.status_code == response_code
        assert re.search(response_text, response.get_data(as_text=True))


@pytest.mark.parametrize(
    "logged_in,response_code,response_text",
    [
        (True, 200, "accounts"),
        (False, 401, "not authorized"),
    ],
)
def test_get_accounts(
    flask_client: FlaskClient,
    auth: AuthActions,
    logged_in: bool,
    response_code: int,
    response_text: str,
):
    if logged_in:
        if response_code == 500:
            auth.alt_login()
        else:
            auth.login()

    with flask_client:
        response = flask_client.get("/api/get_accounts")
        assert response.status_code == response_code
        assert re.search(response_text, response.get_data(as_text=True))
