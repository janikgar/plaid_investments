import os
from dotenv import load_dotenv
from plaid_investments.client import Client

load_dotenv()

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET_KEY = os.getenv("PLAID_SECRET_KEY")
PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")


def main():
    client = Client(PLAID_CLIENT_ID, PLAID_SECRET_KEY, PLAID_ENV)
    client.init_plaid_client()
    client.get_temp_token()


if __name__ == "__main__":
    main()
