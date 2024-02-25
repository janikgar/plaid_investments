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
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

class Client:
    def __init__(self, client_id: str, secret_key: str, env: str):
        self.api_key = {
                "clientId": client_id,
                "secret": secret_key,
                "plaid_version": "2020-09-14",
        }
        self.env = env
        self.plaid_client = plaid_api.PlaidApi

    def init_plaid_client(self):
        host = plaid.Environment.Sandbox
        if self.env == "development":
            host = plaid.Environment.Development
        elif self.env == "production":
            host = plaid.Environment.Production

        config = plaid.Configuration(
            host=host,
            api_key=self.api_key
        )

        api_client = plaid.ApiClient(config)
        client = plaid_api.PlaidApi(api_client)

        self.plaid_client = client

    def list_institutions(self):
        institution_get = InstitutionsGetRequest(count=(1), offset=(0), country_codes=([CountryCode("US")]))
        print(self.plaid_client.institutions_get(institution_get))

    def get_temp_token(self):
        if self.env == 'sandbox':
            request = SandboxPublicTokenCreateRequest(
                institution_id=("ins_130958"), initial_products=[Products("assets"), Products("transactions")]
            )
            response = self.plaid_client.sandbox_public_token_create(request)
            print(response)

    def create_link_token(self, client_user_id: str) -> dict:
        req = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name=__name__,
            country_codes=[CountryCode("US")],
            language='en',
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id,
            )
            # redirect_uri='/api/redirect',
        )
        res = self.plaid_client.link_token_create(req)

        return res.to_dict()

    def exchange_public_token(self, public_token: str) -> dict:
        req = ItemPublicTokenExchangeRequest(
            public_token=public_token,
        )
        res = self.plaid_client.item_public_token_exchange(req)

        return res.to_dict()