#!/usr/bin/env python3
"""
Data Transformer - Converts Plaid data to our AI Insights Agent schema
This module transforms real Plaid data into the format expected by our analysis pipeline.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from src.agent.schema import InsightResponse


class PlaidDataTransformer:
    """Transforms Plaid API data to match our family office schema"""
    
    def __init__(self):
        self.transformed_data = {}
    
    def load_plaid_data(self, filename: str = "output/plaid_data.json") -> Dict[str, Any]:
        """Load Plaid data from JSON file"""
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
            print(f"SUCCESS: Loaded Plaid data from {filename}")
            return data
        except Exception as e:
            print(f"ERROR: Failed to load Plaid data: {e}")
            raise
    
    def transform_accounts_to_assets(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform Plaid accounts to our asset format"""
        assets = []
        
        for account in accounts:
            # Skip accounts with zero balance
            if not account['balances']['current'] or account['balances']['current'] <= 0:
                continue
            
            account_type = account['type']
            subtype = account['subtype']
            balance = account['balances']['current']
            
            # Map Plaid account types to our asset types
            if account_type == 'depository':
                if subtype == 'checking':
                    asset_type = 'cash_account'
                    asset_name = f"{account['name']} (Checking)"
                elif subtype == 'savings':
                    asset_type = 'cash_account'
                    asset_name = f"{account['name']} (Savings)"
                elif subtype == 'cd':
                    asset_type = 'cash_account'
                    asset_name = f"{account['name']} (CD)"
                else:
                    asset_type = 'cash_account'
                    asset_name = account['name']
            elif account_type == 'investment':
                asset_type = 'investment_account'
                asset_name = account['name']
            elif account_type == 'credit':
                # Skip credit accounts for now (they're liabilities)
                continue
            else:
                asset_type = 'other'
                asset_name = account['name']
            
            asset_data = {
                "type": asset_type,
                "value": balance,
                "name": asset_name,
                "account_id": account['account_id'],
                "mask": account['mask'],
                "connection_status": "active"  # Plaid data is always active
            }
            
            assets.append(asset_data)
        
        return assets
    
    def transform_investment_holdings_to_assets(self, holdings: List[Dict[str, Any]], accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform investment holdings to our asset format"""
        assets = []
        
        # Create account lookup
        account_lookup = {acc['account_id']: acc for acc in accounts}
        
        for holding in holdings:
            if not holding.get('institution_value') or holding['institution_value'] <= 0:
                continue
            
            account = account_lookup.get(holding['account_id'], {})
            
            asset_data = {
                "type": "investment_holding",
                "value": holding['institution_value'],
                "name": f"Security {holding['security_id']}",
                "account_id": holding['account_id'],
                "security_id": holding['security_id'],
                "quantity": holding.get('quantity', 0),
                "institution_price": holding.get('institution_price', 0),
                "connection_status": "active"
            }
            
            assets.append(asset_data)
        
        return assets
    
    def transform_accounts_to_liabilities(self, accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform credit accounts to liabilities"""
        liabilities = []
        
        for account in accounts:
            if account['type'] == 'credit':
                balance = account['balances']['current']
                limit = account['balances']['limit']
                
                liability_data = {
                    "type": "credit_card",
                    "value": abs(balance) if balance else 0,  # Credit balances are negative
                    "name": account['name'],
                    "account_id": account['account_id'],
                    "credit_limit": limit,
                    "mask": account['mask']
                }
                
                liabilities.append(liability_data)
        
        return liabilities
    
    def transform_to_family_office_format(self, plaid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform complete Plaid dataset to our family office format"""
        accounts = plaid_data['accounts']
        holdings = plaid_data.get('investment_holdings', [])
        
        # Transform data
        cash_assets = self.transform_accounts_to_assets(accounts)
        investment_assets = self.transform_investment_holdings_to_assets(holdings, accounts)
        liabilities = self.transform_accounts_to_liabilities(accounts)
        
        # Combine all assets
        all_assets = cash_assets + investment_assets
        
        # Create family office structure
        family_office_data = {
            "fo_plaid_sandbox": {
                "assets": all_assets,
                "liabilities": liabilities,
                "cash_accounts": cash_assets,  # Duplicate for compatibility
                "metadata": {
                    "source": "plaid_sandbox",
                    "transformed_at": datetime.now().isoformat(),
                    "original_item_id": plaid_data['metadata']['item_id'],
                    "total_accounts": len(accounts),
                    "total_assets": len(all_assets),
                    "total_liabilities": len(liabilities)
                }
            }
        }
        
        return family_office_data
    
    def save_transformed_data(self, data: Dict[str, Any], filename: str = "output/transformed_plaid_data.json") -> None:
        """Save transformed data to JSON file"""
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=2, default=str)
            print(f"SUCCESS: Transformed data saved to {filename}")
        except Exception as e:
            print(f"ERROR: Failed to save transformed data: {e}")
            raise
    
    def print_summary(self, original_data: Dict[str, Any], transformed_data: Dict[str, Any]) -> None:
        """Print summary of transformation"""
        print("\n" + "=" * 60)
        print("DATA TRANSFORMATION SUMMARY")
        print("=" * 60)
        
        # Original data summary
        print(f"\nORIGINAL PLAID DATA:")
        print(f"   Accounts: {len(original_data['accounts'])}")
        print(f"   Transactions: {len(original_data.get('transactions', []))}")
        print(f"   Investment Holdings: {len(original_data.get('investment_holdings', []))}")
        
        # Transformed data summary
        fo_data = transformed_data['fo_plaid_sandbox']
        print(f"\nTRANSFORMED FAMILY OFFICE DATA:")
        print(f"   Total Assets: {len(fo_data['assets'])}")
        print(f"   Cash Accounts: {len(fo_data['cash_accounts'])}")
        print(f"   Liabilities: {len(fo_data['liabilities'])}")
        
        # Asset breakdown
        asset_types = {}
        total_value = 0
        for asset in fo_data['assets']:
            asset_type = asset['type']
            asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
            total_value += asset['value']
        
        print(f"\nASSET BREAKDOWN:")
        for asset_type, count in asset_types.items():
            print(f"   {asset_type}: {count} items")
        print(f"   Total Portfolio Value: ${total_value:,.2f}")
        
        # Top assets by value
        sorted_assets = sorted(fo_data['assets'], key=lambda x: x['value'], reverse=True)
        print(f"\nTOP 5 ASSETS BY VALUE:")
        for i, asset in enumerate(sorted_assets[:5], 1):
            print(f"   {i}. {asset['name']}: ${asset['value']:,.2f}")


def main():
    """Test the data transformer"""
    try:
        # Initialize transformer
        transformer = PlaidDataTransformer()
        
        # Load Plaid data
        plaid_data = transformer.load_plaid_data()
        
        # Transform data
        transformed_data = transformer.transform_to_family_office_format(plaid_data)
        
        # Save transformed data
        transformer.save_transformed_data(transformed_data)
        
        # Print summary
        transformer.print_summary(plaid_data, transformed_data)
        
        print("\n" + "=" * 60)
        print("DATA TRANSFORMATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("Next steps:")
        print("1. Review transformed_plaid_data.json")
        print("2. Use this data with run_analysis.py")
        print("3. Compare insights from real vs mock data")
        
    except Exception as e:
        print(f"\nERROR: Data transformation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
