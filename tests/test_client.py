import pook
from plaid_investments.client import Client
from plaid.model.auth_get_request import AuthGetRequest
from plaid.api import plaid_api

pook.on()

# pook.get(pook.regex(".*"))

class TestClient:
    def test_client_type(self):
        client = Client("", "", "sandbox")
        assert type(client) == Client
        assert pook.unmatched() == 0

    def test_client_plaid_client_type(self):
        assert pook.isactive() == True
        client = Client("", "", "sandbox")
        client.init_plaid_client()
        assert type(client.plaid_client) == plaid_api.PlaidApi
        assert pook.unmatched() == 0
