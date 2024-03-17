import plaid
from plaid.api import plaid_api
from plaid.model.sandbox_public_token_create_request import (
    SandboxPublicTokenCreateRequest,
)
from plaid.model.institutions_get_request import InstitutionsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.item_public_token_exchange_request import (
    ItemPublicTokenExchangeRequest,
)


class Client:
    def __init__(self, client_id: str, secret_key: str, env: str):
        self.api_key: dict = {
            "clientId": client_id,
            "secret": secret_key,
            "plaid_version": "2020-09-14",
        }
        self.env: str = env
        self.plaid_client: plaid_api.PlaidApi = plaid_api.PlaidApi

    def init_plaid_client(self):
        host = self.env

        config = plaid.Configuration(host=host, api_key=self.api_key)

        api_client = plaid.ApiClient(config)
        client = plaid_api.PlaidApi(api_client)

        self.plaid_client = client

    def create_link_token(self, client_user_id: str) -> dict:
        req = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name=__name__,
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id,
            ),
        )
        res = self.plaid_client.link_token_create(req)

        return res.to_dict()

    def exchange_public_token(self, public_token: str) -> dict:
        req = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        res = self.plaid_client.item_public_token_exchange(req)

        return res.to_dict()

    def get_account_info(self, access_token: str) -> dict:
        req = AccountsGetRequest(access_token=access_token)
        res = self.plaid_client.accounts_get(req)

        return res.to_dict()

    def get_account_balance(self, access_token: str, item: str, account_ids: list[str] = []):
        req = AccountsBalanceGetRequest(access_token=access_token, options={"account_ids": account_ids})
        res = self.plaid_client.accounts_balance_get(req)

        return res.to_dict()
