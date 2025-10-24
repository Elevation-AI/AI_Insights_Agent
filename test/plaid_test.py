from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model import *

# --- Step 1: Configure your environment ---
configuration = Configuration(
    host="https://sandbox.plaid.com",
    api_key={
        "clientId": "68fa3c7a9c89800021008220",
        "secret": "7223d0e600bd24822d76e92a1734eb"
    }
)

# --- Step 2: Create API client instance ---
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

print("✅ Plaid Sandbox client initialized successfully!")


