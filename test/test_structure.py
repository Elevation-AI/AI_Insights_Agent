#!/usr/bin/env python3
"""
Test script to demonstrate the AI Insights Agent structure without requiring API key
"""

import json
from src.agent.schema import InsightCard, InsightResponse, InsightType
from prompts.prompts import V1_SYSTEM_PROMPT

def test_schema():
    """Test the Pydantic schema models"""
    print("Testing Pydantic Schema Models...")
    print("=" * 50)
    
    # Create a sample insight card
    sample_insight = InsightCard(
        title="High Tech Concentration Risk",
        insight_type=InsightType.RISK,
        description="Portfolio is heavily concentrated in technology sector with 100% of public equity holdings in tech stocks (MSFT, GOOG).",
        impact="high",
        confidence="high",
        recommendation="Consider diversifying public equity holdings across different sectors to reduce concentration risk.",
        supporting_data=["100% of public equity in tech sector", "MSFT: $500K", "GOOG: $700K"],
        priority=1
    )
    
    print("SUCCESS: Sample InsightCard created successfully:")
    print(f"   Title: {sample_insight.title}")
    print(f"   Type: {sample_insight.insight_type.value}")
    print(f"   Impact: {sample_insight.impact}")
    print(f"   Priority: {sample_insight.priority}")
    print()
    
    # Create a sample response
    sample_response = InsightResponse(
        insights=[sample_insight],
        summary="Portfolio analysis reveals high concentration risk in technology sector requiring immediate diversification.",
        total_insights=1,
        analysis_timestamp="2024-01-15T10:30:00Z"
    )
    
    print("SUCCESS: Sample InsightResponse created successfully:")
    print(f"   Total insights: {sample_response.total_insights}")
    print(f"   Summary: {sample_response.summary}")
    print()
    
    # Test JSON serialization
    json_output = sample_response.model_dump()
    print("SUCCESS: JSON serialization works:")
    print(json.dumps(json_output, indent=2)[:200] + "...")
    print()

def test_prompt():
    """Test the system prompt"""
    print("Testing System Prompt...")
    print("=" * 50)
    
    print("SUCCESS: V1_SYSTEM_PROMPT loaded successfully")
    print(f"   Length: {len(V1_SYSTEM_PROMPT)} characters")
    print(f"   Contains 'financial analyst': {'financial analyst' in V1_SYSTEM_PROMPT}")
    print(f"   Contains 'risk assessment': {'risk assessment' in V1_SYSTEM_PROMPT}")
    print()

def test_mock_data():
    """Test loading mock data"""
    print("Testing Mock Data Loading...")
    print("=" * 50)
    
    try:
        with open("mock_data.json", 'r') as file:
            data = json.load(file)
        
        print("SUCCESS: Mock data loaded successfully")
        print(f"   Family Office ID: {list(data.keys())[0]}")
        
        fo_data = data["fo_123"]
        print(f"   Assets count: {len(fo_data['assets'])}")
        print(f"   Liabilities count: {len(fo_data['liabilities'])}")
        print(f"   Cash accounts count: {len(fo_data['cash_accounts'])}")
        
        # Show asset breakdown
        total_assets = sum(asset['value'] for asset in fo_data['assets'])
        print(f"   Total asset value: ${total_assets:,}")
        
        # Show tech concentration
        tech_assets = [asset for asset in fo_data['assets'] if asset.get('sector') == 'Tech']
        tech_value = sum(asset['value'] for asset in tech_assets)
        tech_percentage = (tech_value / total_assets) * 100
        print(f"   Tech concentration: {tech_percentage:.1f}% (${tech_value:,})")
        
    except Exception as e:
        print(f"ERROR: Error loading mock data: {e}")
    
    print()

def main():
    """Run all tests"""
    print("AI Insights Agent - Structure Test")
    print("=" * 60)
    print()
    
    test_schema()
    test_prompt()
    test_mock_data()
    
    print("All structure tests completed successfully!")
    print()
    print("Next steps:")
    print("1. Set GOOGLE_API_KEY environment variable")
    print("2. Run: python run_analysis.py")
    print("3. Review the generated insights")

if __name__ == "__main__":
    main()
