#!/usr/bin/env python3
"""
Plaid Data Fetcher - Complete integration with Plaid API
This module handles token exchange and fetches real financial data from Plaid sandbox.
"""

import os
import json
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional

from plaid.api import plaid_api
from plaid import Configuration, ApiClient
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
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
    
    def get_transactions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch transactions for all accounts"""
        if not self.access_token:
            raise ValueError("Access token not available. Call exchange_public_token first.")
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()
        
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
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
                    "merchant_name": transaction.merchant_name,
                    "category": transaction.category,
                    "subcategory": transaction.subcategory,
                    "account_owner": transaction.account_owner,
                    "iso_currency_code": transaction.iso_currency_code,
                    "unofficial_currency_code": transaction.unofficial_currency_code
                }
                transactions.append(transaction_data)
            
            print(f"SUCCESS: Fetched {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            print(f"ERROR: Failed to fetch transactions: {e}")
            raise
    
    def get_investment_holdings(self) -> List[Dict[str, Any]]:
        """Fetch investment holdings"""
        if not self.access_token:
            raise ValueError("Access token not available. Call exchange_public_token first.")
        
        try:
            holdings_request = InvestmentsHoldingsGetRequest(access_token=self.access_token)
            holdings_response = self.client.investments_holdings_get(holdings_request)
            
            holdings = []
            for holding in holdings_response.holdings:
                holding_data = {
                    "account_id": holding.account_id,
                    "security_id": holding.security_id,
                    "institution_price": holding.institution_price,
                    "institution_price_as_of": holding.institution_price_as_of,
                    "institution_value": holding.institution_value,
                    "cost_basis": holding.cost_basis,
                    "quantity": holding.quantity,
                    "iso_currency_code": holding.iso_currency_code,
                    "unofficial_currency_code": holding.unofficial_currency_code
                }
                holdings.append(holding_data)
            
            print(f"SUCCESS: Fetched {len(holdings)} investment holdings")
            return holdings
            
        except Exception as e:
            print(f"ERROR: Failed to fetch investment holdings: {e}")
            raise
    
    def get_investment_transactions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch investment transactions"""
        if not self.access_token:
            raise ValueError("Access token not available. Call exchange_public_token first.")
        
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        if not end_date:
            end_date = datetime.now().date()
        
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        try:
            transactions_request = InvestmentsTransactionsGetRequest(
                access_token=self.access_token,
                start_date=start_date,
                end_date=end_date
            )
            transactions_response = self.client.investments_transactions_get(transactions_request)
            
            transactions = []
            for transaction in transactions_response.investment_transactions:
                transaction_data = {
                    "investment_transaction_id": transaction.investment_transaction_id,
                    "account_id": transaction.account_id,
                    "security_id": transaction.security_id,
                    "date": transaction.date,
                    "name": transaction.name,
                    "amount": transaction.amount,
                    "quantity": transaction.quantity,
                    "price": transaction.price,
                    "fees": transaction.fees,
                    "type": transaction.type.value if transaction.type else None,
                    "subtype": transaction.subtype.value if transaction.subtype else None,
                    "iso_currency_code": transaction.iso_currency_code,
                    "unofficial_currency_code": transaction.unofficial_currency_code
                }
                transactions.append(transaction_data)
            
            print(f"SUCCESS: Fetched {len(transactions)} investment transactions")
            return transactions
            
        except Exception as e:
            print(f"ERROR: Failed to fetch investment transactions: {e}")
            raise
    
    def fetch_all_data(self, public_token: str) -> Dict[str, Any]:
        """Fetch all available financial data"""
        print("Starting comprehensive data fetch from Plaid...")
        print("=" * 50)
        
        # Exchange token
        token_data = self.exchange_public_token(public_token)
        
        # Fetch all data
        accounts = self.get_accounts()
        transactions = self.get_transactions()
        holdings = self.get_investment_holdings()
        investment_transactions = self.get_investment_transactions()
        
        # Compile comprehensive data
        financial_data = {
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "item_id": self.item_id,
                "access_token": self.access_token[:20] + "...",  # Truncated for security
                "data_source": "plaid_sandbox"
            },
            "accounts": accounts,
            "transactions": transactions,
            "investment_holdings": holdings,
            "investment_transactions": investment_transactions,
            "summary": {
                "total_accounts": len(accounts),
                "total_transactions": len(transactions),
                "total_holdings": len(holdings),
                "total_investment_transactions": len(investment_transactions)
            }
        }
        
        print("\nData fetch completed successfully!")
        print(f"   Accounts: {len(accounts)}")
        print(f"   Transactions: {len(transactions)}")
        print(f"   Investment Holdings: {len(holdings)}")
        print(f"   Investment Transactions: {len(investment_transactions)}")
        
        return financial_data
    
    def save_data(self, data: Dict[str, Any], filename: str = "plaid_data.json") -> None:
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
        
        # Fetch all data
        financial_data = fetcher.fetch_all_data(public_token)
        
        # Save data
        fetcher.save_data(financial_data)
        
        print("\n" + "=" * 50)
        print("PLAID DATA FETCH COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print("Next steps:")
        print("1. Review the plaid_data.json file")
        print("2. Integrate with AI analysis pipeline")
        print("3. Transform data to match your schema")
        
    except Exception as e:
        print(f"\nERROR: Data fetch failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
