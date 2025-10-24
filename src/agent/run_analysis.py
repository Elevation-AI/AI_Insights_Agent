#!/usr/bin/env python3
"""
AI Insights Agent - Main Analysis Script
This script loads mock data, initializes the Gemini model via LangChain,
and generates structured insights using Pydantic schemas.
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


def load_mock_data(file_path: str = "mock_data.json") -> Dict[str, Any]:
    """Load the mock financial data from JSON file"""
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(f"SUCCESS: Successfully loaded mock data from {file_path}")
    return data
    


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


def create_analysis_prompt(financial_data: str) -> str:
    """Create the analysis prompt for financial analysis"""
    prompt = f"""
{V1_SYSTEM_PROMPT}

Please analyze the following financial data and generate comprehensive insights:

Financial Data:
{financial_data}

Instructions:
1. Analyze the portfolio structure, risk factors, and opportunities
2. Identify any compliance issues, deadlines, or urgent actions needed
3. Generate exactly 5 specific, actionable insights (you can combine related findings)
4. Prioritize insights by importance and urgency using priority values from 1 to 5 ONLY (1=highest, 5=lowest)
5. Provide clear recommendations for each insight
6. Support your analysis with specific data points from the input

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


def run_analysis() -> InsightResponse:
    """Main analysis function that orchestrates the entire process"""
    print("Starting AI Insights Agent Analysis...")
    print("=" * 50)
    
    # Step 1: Load mock data
    print("\nLoading financial data...")
    financial_data = load_mock_data()
    
    # Step 2: Initialize Gemini model
    print("\nInitializing AI model...")
    model = initialize_gemini_model()
    
    # Step 3: Create analysis prompt
    print("\nPreparing analysis prompt...")
    formatted_data = json.dumps(financial_data, indent=2)
    prompt = create_analysis_prompt(formatted_data)
    
    # Step 4: Run the analysis
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


def print_insights(insights: InsightResponse) -> None:
    """Print the insights in a formatted way"""
    print("\n" + "=" * 60)
    print("AI INSIGHTS AGENT - ANALYSIS RESULTS")
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


def save_results(insights: InsightResponse, filename: str = "analysis_results.json") -> None:
    """Save the analysis results to a JSON file"""
    try:
        with open(filename, 'w') as file:
            json.dump(insights.model_dump(), file, indent=2)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"ERROR: Error saving results: {e}")


def main():
    """Main entry point"""
    try:
        # Run the analysis
        insights = run_analysis()
        
        # Print results
        print_insights(insights)
        
        # Save results
        save_results(insights)
        
        print("\nAnalysis complete! Check the results above and the saved JSON file.")
        
    except Exception as e:
        print(f"\nAnalysis failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure you have set GOOGLE_API_KEY in your environment")
        print("2. Check that all required packages are installed: pip install -r requirements.txt")
        print("3. Verify your Google Cloud credentials and permissions")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
