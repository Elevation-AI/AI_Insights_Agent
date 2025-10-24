#!/usr/bin/env python3
"""
AI Insights Agent - Main Entry Point
This script runs the complete pipeline with real Plaid sandbox data.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Main entry point - runs complete Plaid analysis pipeline"""
    print("AI Insights Agent - Real Data Analysis Pipeline")
    print("=" * 60)
    
    try:
        # Step 1: Fetch Plaid data
        print("\nStep 1: Fetching real Plaid sandbox data...")
        from src.agent.plaid_data_fetcher_simple import main as fetch_data
        fetch_result = fetch_data()
        if fetch_result != 0:
            print("ERROR: Failed to fetch Plaid data")
            return 1
        
        # Step 2: Transform data
        print("\nStep 2: Transforming Plaid data to family office format...")
        from src.agent.plaid_data_transformer import main as transform_data
        transform_result = transform_data()
        if transform_result != 0:
            print("ERROR: Failed to transform data")
            return 1
        
        # Step 3: Run AI analysis
        print("\nStep 3: Running AI analysis on real financial data...")
        from src.agent.run_analysis_with_plaid import main as run_analysis
        analysis_result = run_analysis()
        if analysis_result != 0:
            print("ERROR: Failed to run analysis")
            return 1
        
        print("\n" + "=" * 60)
        print("COMPLETE PIPELINE SUCCESSFUL!")
        print("=" * 60)
        print("SUCCESS: Fetched real Plaid sandbox data")
        print("SUCCESS: Transformed data to family office format")
        print("SUCCESS: Generated AI-powered insights")
        print("\nCheck the 'output/' directory for results:")
        print("  - plaid_data.json (raw Plaid data)")
        print("  - transformed_plaid_data.json (converted format)")
        print("  - analysis_results_plaid.json (AI insights)")
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Pipeline failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure GOOGLE_API_KEY is set in .env file")
        print("2. Check that Plaid credentials are correct")
        print("3. Verify all dependencies are installed")
        return 1

if __name__ == "__main__":
    exit(main())
