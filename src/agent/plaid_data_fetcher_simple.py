#!/usr/bin/env python3
"""
Plaid Data Fetcher - Simplified version for testing
This version focuses on getting accounts data first, then handles product readiness issues.
"""

import os
import json
import time
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional

from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.products import Products


class PlaidDataFetcher:
    """Handles all Plaid API interactions for fetching financial data"""
    
    def __init__(self):
        """Initialize Plaid client with sandbox credentials"""
        self.client_id = os.getenv("PLAID_CLIENT_ID", "68fa3c7a9c89800021008220")
        self.secret = os.getenv("PLAID_SECRET", "7223d0e600bd24822d76e92a1734eb")
        
        # Configure Plaid client
        configuration = Configuration(
            host="https://sandbox.plaid.com",
            api_key={
                "clientId": self.client_id,
                "secret": self.secret
            }
        )
        self.api_client = ApiClient(configuration)
        self.client = plaid_api.PlaidApi(self.api_client)
        
        self.access_token = None
        self.item_id = None
        
        print("SUCCESS: Plaid Data Fetcher initialized")
    
    def create_public_token(self) -> str:
        """Create a sandbox public token for testing"""
        try:
            sandbox_request = SandboxPublicTokenCreateRequest(
                institution_id="ins_109508",  # Plaid test bank
                initial_products=[Products("transactions"), Products("investments")],
                options={"webhook": "https://yourwebhook.com"}
            )
            sandbox_response = self.client.sandbox_public_token_create(sandbox_request)
            public_token = sandbox_response.public_token
            print(f"SUCCESS: Public token created: {public_token}")
            return public_token
        except Exception as e:
            print(f"ERROR: Failed to create public token: {e}")
            raise
    
    def exchange_public_token(self, public_token: str) -> Dict[str, str]:
        """Exchange public token for access token"""
        try:
            exchange_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            exchange_response = self.client.item_public_token_exchange(exchange_request)
            
            self.access_token = exchange_response.access_token
            self.item_id = exchange_response.item_id
            
            print(f"SUCCESS: Token exchanged successfully")
            print(f"   Access Token: {self.access_token[:20]}...")
            print(f"   Item ID: {self.item_id}")
            
            return {
                "access_token": self.access_token,
                "item_id": self.item_id
            }
        except Exception as e:
            print(f"ERROR: Failed to exchange token: {e}")
            raise
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """Fetch all accounts for the item"""
        if not self.access_token:
            raise ValueError("Access token not available. Call exchange_public_token first.")
        
        try:
            accounts_request = AccountsGetRequest(access_token=self.access_token)
            accounts_response = self.client.accounts_get(accounts_request)
            
            accounts = []
            for account in accounts_response.accounts:
                account_data = {
                    "account_id": account.account_id,
                    "name": account.name,
                    "official_name": account.official_name,
                    "type": account.type.value if account.type else None,
                    "subtype": account.subtype.value if account.subtype else None,
                    "mask": account.mask,
                    "balances": {
                        "available": account.balances.available,
                        "current": account.balances.current,
                        "limit": account.balances.limit,
                        "iso_currency_code": account.balances.iso_currency_code,
                        "unofficial_currency_code": account.balances.unofficial_currency_code
                    }
                }
                accounts.append(account_data)
            
            print(f"SUCCESS: Fetched {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            print(f"ERROR: Failed to fetch accounts: {e}")
            raise
    
    def get_transactions_with_retry(self, max_retries: int = 3, delay: int = 5) -> List[Dict[str, Any]]:
        """Fetch transactions with retry logic for product readiness"""
        if not self.access_token:
            raise ValueError("Access token not available. Call exchange_public_token first.")
        
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
        
        for attempt in range(max_retries):
            try:
                transactions_request = TransactionsGetRequest(
                    access_token=self.access_token,
                    start_date=start_date,
                    end_date=end_date
                )
                transactions_response = self.client.transactions_get(transactions_request)
                
                transactions = []
                for transaction in transactions_response.transactions:
                    transaction_data = {
                        "transaction_id": transaction.transaction_id,
                        "account_id": transaction.account_id,
                        "amount": transaction.amount,
                        "date": transaction.date,
                        "name": transaction.name,
                        "merchant_name": getattr(transaction, 'merchant_name', None),
                        "category": getattr(transaction, 'category', None),
                        "subcategory": getattr(transaction, 'subcategory', None),
                        "account_owner": getattr(transaction, 'account_owner', None),
                        "iso_currency_code": getattr(transaction, 'iso_currency_code', None),
                        "unofficial_currency_code": getattr(transaction, 'unofficial_currency_code', None)
                    }
                    transactions.append(transaction_data)
                
                print(f"SUCCESS: Fetched {len(transactions)} transactions")
                return transactions
                
            except Exception as e:
                if "PRODUCT_NOT_READY" in str(e) and attempt < max_retries - 1:
                    print(f"Product not ready, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"ERROR: Failed to fetch transactions: {e}")
                    if attempt == max_retries - 1:
                        print("Max retries reached. Returning empty list.")
                        return []
                    raise
    
    def get_investment_holdings_with_retry(self, max_retries: int = 3, delay: int = 5) -> List[Dict[str, Any]]:
        """Fetch investment holdings with retry logic"""
        if not self.access_token:
            raise ValueError("Access token not available. Call exchange_public_token first.")
        
        for attempt in range(max_retries):
            try:
                holdings_request = InvestmentsHoldingsGetRequest(access_token=self.access_token)
                holdings_response = self.client.investments_holdings_get(holdings_request)
                
                holdings = []
                for holding in holdings_response.holdings:
                    holding_data = {
                        "account_id": holding.account_id,
                        "security_id": holding.security_id,
                        "institution_price": getattr(holding, 'institution_price', None),
                        "institution_price_as_of": getattr(holding, 'institution_price_as_of', None),
                        "institution_value": getattr(holding, 'institution_value', None),
                        "cost_basis": getattr(holding, 'cost_basis', None),
                        "quantity": getattr(holding, 'quantity', None),
                        "iso_currency_code": getattr(holding, 'iso_currency_code', None),
                        "unofficial_currency_code": getattr(holding, 'unofficial_currency_code', None)
                    }
                    holdings.append(holding_data)
                
                print(f"SUCCESS: Fetched {len(holdings)} investment holdings")
                return holdings
                
            except Exception as e:
                if "PRODUCT_NOT_READY" in str(e) and attempt < max_retries - 1:
                    print(f"Investment product not ready, retrying in {delay} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"ERROR: Failed to fetch investment holdings: {e}")
                    if attempt == max_retries - 1:
                        print("Max retries reached. Returning empty list.")
                        return []
                    raise
    
    def fetch_basic_data(self, public_token: str) -> Dict[str, Any]:
        """Fetch basic financial data (accounts + transactions with retry)"""
        print("Starting basic data fetch from Plaid...")
        print("=" * 50)
        
        # Exchange token
        token_data = self.exchange_public_token(public_token)
        
        # Fetch accounts (always works)
        accounts = self.get_accounts()
        
        # Fetch transactions with retry
        transactions = self.get_transactions_with_retry()
        
        # Try to fetch investment holdings
        holdings = self.get_investment_holdings_with_retry()
        
        # Compile data
        financial_data = {
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "item_id": self.item_id,
                "access_token": self.access_token[:20] + "...",
                "data_source": "plaid_sandbox"
            },
            "accounts": accounts,
            "transactions": transactions,
            "investment_holdings": holdings,
            "summary": {
                "total_accounts": len(accounts),
                "total_transactions": len(transactions),
                "total_holdings": len(holdings)
            }
        }
        
        print("\nBasic data fetch completed!")
        print(f"   Accounts: {len(accounts)}")
        print(f"   Transactions: {len(transactions)}")
        print(f"   Investment Holdings: {len(holdings)}")
        
        return financial_data
    
    def save_data(self, data: Dict[str, Any], filename: str = "output/plaid_data.json") -> None:
        """Save fetched data to JSON file"""
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=2, default=str)
            print(f"SUCCESS: Data saved to {filename}")
        except Exception as e:
            print(f"ERROR: Failed to save data: {e}")
            raise


def main():
    """Test the Plaid Data Fetcher"""
    try:
        # Initialize fetcher
        fetcher = PlaidDataFetcher()
        
        # Create public token
        public_token = fetcher.create_public_token()
        
        # Fetch basic data
        financial_data = fetcher.fetch_basic_data(public_token)
        
        # Save data
        fetcher.save_data(financial_data)
        
        print("\n" + "=" * 50)
        print("PLAID DATA FETCH COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("Next steps:")
        print("1. Review the plaid_data.json file")
        print("2. Transform data to match your schema")
        print("3. Integrate with AI analysis pipeline")
        
    except Exception as e:
        print(f"\nERROR: Data fetch failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
