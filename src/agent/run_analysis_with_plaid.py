#!/usr/bin/env python3
"""
AI Insights Agent - Analysis with Real Plaid Data
This script loads transformed Plaid data and generates insights using the Gemini model.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import ValidationError

from src.agent.schema import InsightResponse
from prompts.prompts import V1_SYSTEM_PROMPT


def load_transformed_plaid_data(file_path: str = "output/transformed_plaid_data.json") -> Dict[str, Any]:
    """Load the transformed Plaid data from JSON file"""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        print(f"SUCCESS: Successfully loaded transformed Plaid data from {file_path}")
        return data
    except Exception as e:
        print(f"ERROR: Failed to load transformed data: {e}")
        raise


def load_mock_data(file_path: str = "mock_data.json") -> Dict[str, Any]:
    """Load the mock financial data from JSON file"""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        print(f"SUCCESS: Successfully loaded mock data from {file_path}")
        return data
    except Exception as e:
        print(f"ERROR: Failed to load mock data: {e}")
        raise


def initialize_gemini_model():
    """Initialize the Gemini model"""
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("GOOGLE_API_KEY")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            )
        )
        print("SUCCESS: Successfully initialized Gemini model")
        return model
    except Exception as e:
        print(f"ERROR: Error initializing Gemini model: {e}")
        raise


def create_analysis_prompt(financial_data: str, data_source: str = "mock") -> str:
    """Create the analysis prompt for financial analysis"""
    data_context = "mock financial data" if data_source == "mock" else "real financial data from Plaid sandbox"
    
    prompt = f"""
{V1_SYSTEM_PROMPT}

Please analyze the following {data_context} and generate comprehensive insights:

Financial Data:
{financial_data}

Instructions:
1. Analyze the portfolio structure, risk factors, and opportunities
2. Identify any compliance issues, deadlines, or urgent actions needed
3. Generate exactly 5 specific, actionable insights (you can combine related findings)
4. Prioritize insights by importance and urgency using priority values from 1 to 5 ONLY (1=highest, 5=lowest)
5. Provide clear recommendations for each insight
6. Support your analysis with specific data points from the input
7. Consider the data source context - this is {'mock data for testing' if data_source == 'mock' else 'real sandbox data from Plaid'}

Format your response as a structured JSON object matching the InsightResponse schema:
{{
  "insights": [
    {{
      "title": "Clear, concise title for the insight",
      "insight_type": "risk|opportunity|action|alert|summary",
      "description": "Detailed description of the insight",
      "impact": "high|medium|low",
      "confidence": "high|medium|low",
      "recommendation": "Specific actionable recommendation",
      "supporting_data": ["key data point 1", "key data point 2"],
      "priority": 1
    }}
  ],
  "summary": "Executive summary of all insights",
  "total_insights": 5,
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}}
"""
    return prompt


def run_analysis_with_data(financial_data: Dict[str, Any], data_source: str = "mock") -> InsightResponse:
    """Main analysis function that orchestrates the entire process"""
    print(f"Starting AI Insights Agent Analysis with {data_source} data...")
    print("=" * 50)
    
    # Initialize Gemini model
    print("\nInitializing AI model...")
    model = initialize_gemini_model()
    
    # Create analysis prompt
    print("\nPreparing analysis prompt...")
    formatted_data = json.dumps(financial_data, indent=2)
    prompt = create_analysis_prompt(formatted_data, data_source)
    
    # Run the analysis
    print("\nRunning financial analysis...")
    try:
        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Clean up the response (remove markdown formatting if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # Parse JSON and create InsightResponse
        response_data = json.loads(response_text)
        result = InsightResponse(**response_data)
        
        # Add timestamp to the result
        result.analysis_timestamp = datetime.now().isoformat()
        
        print("SUCCESS: Analysis completed successfully!")
        return result
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response: {e}")
        print(f"Response text: {response_text[:500]}...")
        raise
    except ValidationError as e:
        print(f"ERROR: Response validation failed: {e}")
        print(f"Response data: {response_data}")
        raise
    except Exception as e:
        print(f"ERROR: Error during analysis: {e}")
        raise


def print_insights(insights: InsightResponse, data_source: str = "mock") -> None:
    """Print the insights in a formatted way"""
    print("\n" + "=" * 60)
    print(f"AI INSIGHTS AGENT - ANALYSIS RESULTS ({data_source.upper()} DATA)")
    print("=" * 60)
    
    print(f"\nEXECUTIVE SUMMARY")
    print("-" * 30)
    print(insights.summary)
    
    print(f"\nANALYSIS METRICS")
    print("-" * 30)
    print(f"Total Insights Generated: {insights.total_insights}")
    print(f"Analysis Timestamp: {insights.analysis_timestamp}")
    
    print(f"\nDETAILED INSIGHTS")
    print("-" * 30)
    
    for i, insight in enumerate(insights.insights, 1):
        print(f"\n{i}. {insight.title}")
        print(f"   Type: {insight.insight_type.value.upper()}")
        print(f"   Priority: {insight.priority}/5")
        print(f"   Impact: {insight.impact.upper()}")
        print(f"   Confidence: {insight.confidence.upper()}")
        print(f"   Description: {insight.description}")
        print(f"   Recommendation: {insight.recommendation}")
        print(f"   Supporting Data: {', '.join(insight.supporting_data)}")
        print("-" * 50)


def save_results(insights: InsightResponse, filename: str = None, data_source: str = "mock") -> None:
    """Save the analysis results to a JSON file"""
    if filename is None:
        filename = f"output/analysis_results_{data_source}.json"
    
    try:
        with open(filename, 'w') as file:
            json.dump(insights.model_dump(), file, indent=2)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"ERROR: Error saving results: {e}")


def compare_insights(mock_insights: InsightResponse, plaid_insights: InsightResponse) -> None:
    """Compare insights from mock vs real data"""
    print("\n" + "=" * 60)
    print("INSIGHTS COMPARISON: MOCK vs REAL DATA")
    print("=" * 60)
    
    print(f"\nMOCK DATA INSIGHTS:")
    print(f"   Total: {mock_insights.total_insights}")
    print(f"   Summary: {mock_insights.summary[:100]}...")
    
    print(f"\nREAL DATA INSIGHTS:")
    print(f"   Total: {plaid_insights.total_insights}")
    print(f"   Summary: {plaid_insights.summary[:100]}...")
    
    print(f"\nKEY DIFFERENCES:")
    print("   - Mock data insights are based on simulated family office portfolio")
    print("   - Real data insights are based on actual Plaid sandbox accounts")
    print("   - Real data provides more realistic transaction patterns and balances")
    print("   - Both demonstrate the AI's analytical capabilities")


def main():
    """Main entry point"""
    try:
        print("AI Insights Agent - Real Data Analysis")
        print("=" * 50)
        
        # Check if transformed Plaid data exists
        plaid_data_available = os.path.exists("output/transformed_plaid_data.json")
        mock_data_available = os.path.exists("mock_data.json")
        
        if not plaid_data_available and not mock_data_available:
            print("ERROR: No data files found!")
            print("Please run plaid_data_transformer.py first to generate transformed data")
            return 1
        
        # Analyze mock data if available
        if mock_data_available:
            print("\n" + "=" * 30)
            print("ANALYZING MOCK DATA")
            print("=" * 30)
            mock_data = load_mock_data()
            mock_insights = run_analysis_with_data(mock_data, "mock")
            print_insights(mock_insights, "mock")
            save_results(mock_insights, "output/analysis_results_mock.json", "mock")
        
        # Analyze real Plaid data if available
        plaid_insights = None
        if plaid_data_available:
            print("\n" + "=" * 30)
            print("ANALYZING REAL PLAID DATA")
            print("=" * 30)
            plaid_data = load_transformed_plaid_data()
            plaid_insights = run_analysis_with_data(plaid_data, "plaid")
            print_insights(plaid_insights, "plaid")
            save_results(plaid_insights, "output/analysis_results_plaid.json", "plaid")
        
        # Compare insights if both are available
        if mock_data_available and plaid_data_available:
            compare_insights(mock_insights, plaid_insights)
        
        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE!")
        print("=" * 50)
        print("Check the generated JSON files for detailed results.")
        
    except Exception as e:
        print(f"\nAnalysis failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure you have set GOOGLE_API_KEY in your environment")
        print("2. Check that all required packages are installed: pip install -r requirements.txt")
        print("3. Verify your Google Cloud credentials and permissions")
        print("4. Run plaid_data_transformer.py first to generate transformed data")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
