import pook
from plaid_investments.client import Client
from plaid.model.auth_get_request import AuthGetRequest
from plaid.api import plaid_api


def test_client_type(plaid_client: Client):
    assert type(plaid_client) == Client
    assert pook.unmatched() == 0


def test_client_plaid_client_type(plaid_client: Client):
    plaid_client.init_plaid_client()
    assert type(plaid_client.plaid_client) == plaid_api.PlaidApi
    assert pook.unmatched() == 0
