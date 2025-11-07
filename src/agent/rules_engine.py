"""
Rules Engine (The Quant)
This module performs 100% accurate mathematical calculations and rule-based checks
on financial data to identify specific findings.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

# Global constant for today's date
TODAY = datetime(2025, 11, 3)


def check_stale_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Check for stale private equity valuations.
    
    Loops through data['assets'] of type 'private_equity' and checks if
    the last_valuation_date is more than 365 days before TODAY.
    
    Args:
        data: Dictionary containing 'assets' key with list of asset dictionaries
        
    Returns:
        List of findings dictionaries with 'finding_type', 'asset_name', and 'days_stale'
    """
    findings = []
    
    # Handle case where data might be nested under family office key
    if 'assets' not in data:
        # Try to get first family office's data
        if data and isinstance(data, dict):
            first_fo_key = next(iter(data.keys()))
            data = data[first_fo_key]
    
    assets = data.get('assets', [])
    
    for asset in assets:
        if asset.get('type') == 'private_equity':
            last_valuation_date_str = asset.get('last_valuation_date')
            if last_valuation_date_str:
                # Parse the date string
                try:
                    last_valuation_date = datetime.strptime(last_valuation_date_str, '%Y-%m-%d')
                    days_stale = (TODAY - last_valuation_date).days
                    
                    if days_stale > 365:
                        findings.append({
                            'finding_type': 'stale_valuation',
                            'asset_name': asset.get('name', 'Unknown'),
                            'days_stale': days_stale
                        })
                except (ValueError, TypeError) as e:
                    # Skip assets with invalid date formats
                    continue
    
    return findings


def check_liquidity(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Check for liquidity shortfalls from upcoming capital calls.
    
    Sums all cash_accounts balances, then loops through data['liabilities']
    of type 'capital_call'. If a call is due within 90 days of TODAY and
    its value is greater than total_cash, it's flagged as a shortfall.
    
    Args:
        data: Dictionary containing 'cash_accounts' and 'liabilities' keys
        
    Returns:
        List of findings dictionaries with 'finding_type', 'shortfall_usd', and 'due_date'
    """
    findings = []
    
    # Handle case where data might be nested under family office key
    if 'cash_accounts' not in data:
        # Try to get first family office's data
        if data and isinstance(data, dict):
            first_fo_key = next(iter(data.keys()))
            data = data[first_fo_key]
    
    # Sum all cash account balances
    cash_accounts = data.get('cash_accounts', [])
    total_cash = 0.0
    
    for account in cash_accounts:
        # Handle both 'balance' and 'value' fields
        balance = account.get('balance') or account.get('value', 0)
        if isinstance(balance, (int, float)):
            total_cash += float(balance)
    
    # Check capital calls
    liabilities = data.get('liabilities', [])
    
    for liability in liabilities:
        if liability.get('type') == 'capital_call':
            due_date_str = liability.get('due_date')
            call_value = liability.get('value', 0)
            
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                    days_until_due = (due_date - TODAY).days
                    
                    # Check if due within 90 days and value exceeds total cash
                    if 0 <= days_until_due <= 90 and call_value > total_cash:
                        shortfall_usd = call_value - total_cash
                        findings.append({
                            'finding_type': 'liquidity_shortfall',
                            'shortfall_usd': shortfall_usd,
                            'due_date': due_date_str
                        })
                except (ValueError, TypeError) as e:
                    # Skip liabilities with invalid date formats
                    continue
    
    return findings


def check_asset_protection(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Check for real estate assets with inactive insurance.
    
    Loops through data['assets'] of type 'real_estate' and checks if
    insurance_status is 'inactive'.
    
    Args:
        data: Dictionary containing 'assets' key with list of asset dictionaries
        
    Returns:
        List of findings dictionaries with 'finding_type' and 'asset_name'
    """
    findings = []
    
    # Handle case where data might be nested under family office key
    if 'assets' not in data:
        # Try to get first family office's data
        if data and isinstance(data, dict):
            first_fo_key = next(iter(data.keys()))
            data = data[first_fo_key]
    
    assets = data.get('assets', [])
    
    for asset in assets:
        if asset.get('type') == 'real_estate':
            insurance_status = asset.get('insurance_status')
            if insurance_status == 'inactive':
                findings.append({
                    'finding_type': 'asset_protection_risk',
                    'asset_name': asset.get('name', 'Unknown')
                })
    
    return findings


def run_all_rules(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Run all rule checks and combine results.
    
    Calls check_stale_data, check_liquidity, and check_asset_protection,
    then combines their results into one list.
    
    Args:
        data: Dictionary containing financial data with 'assets', 'liabilities', and 'cash_accounts'
        
    Returns:
        Combined list of all findings from all rule checks
    """
    all_findings = []
    
    # Run all rule checks
    stale_data_findings = check_stale_data(data)
    liquidity_findings = check_liquidity(data)
    asset_protection_findings = check_asset_protection(data)
    
    # Combine all findings
    all_findings.extend(stale_data_findings)
    all_findings.extend(liquidity_findings)
    all_findings.extend(asset_protection_findings)
    
    return all_findings

