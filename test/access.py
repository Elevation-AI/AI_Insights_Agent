from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.products import Products
import os

# Load environment variables
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "68fa3c7a9c89800021008220")
PLAID_SECRET = os.getenv("PLAID_SECRET", "7223d0e600bd24822d76e92a1734eb")

# Configure the Plaid client
configuration = Configuration(
    host="https://sandbox.plaid.com",
    api_key={
        "clientId": PLAID_CLIENT_ID,
        "secret": PLAID_SECRET
    }
)
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

print("SUCCESS: Plaid Sandbox client initialized successfully!")

# Create a sandbox public token
sandbox_request = SandboxPublicTokenCreateRequest(
    institution_id="ins_109508",  # Plaid test bank
    initial_products=[Products("transactions"), Products("investments")],  # products to test
    options={"webhook": "https://yourwebhook.com"}  # optional, can be None
)
sandbox_response = client.sandbox_public_token_create(sandbox_request)
public_token = sandbox_response.public_token
print(f"SUCCESS: Sandbox public_token created: {public_token}")
