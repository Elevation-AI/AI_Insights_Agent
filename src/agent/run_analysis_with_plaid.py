#!/usr/bin/env python3
"""
AI Insights Agent - Analysis with Real Plaid Data
This script loads transformed Plaid data and generates insights using the Gemini model.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

from colorama import Fore, Style, init
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import ValidationError

from src.agent.schema import InsightResponse
from prompts.prompts import V1_SYSTEM_PROMPT

# Initialize colorama for Windows support
init(autoreset=True)

# Load environment variables from .env file at module level
load_dotenv()

# Verify that GOOGLE_API_KEY is set
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY not found in environment variables. "
        "Please set it in your .env file or environment variables."
    )


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
    """Initialize the Gemini model using LangChain"""
    # Environment variables are already loaded at module level
    # Verify API key is available
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Please ensure your .env file contains GOOGLE_API_KEY=your_key_here"
        )
    
    try:
        # Initialize LangChain ChatGoogleGenerativeAI model
        model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            max_output_tokens=4096,
        )
        print("SUCCESS: Successfully initialized Gemini model via LangChain")
        return model
    except Exception as e:
        print(f"ERROR: Error initializing Gemini model: {e}")
        raise


def create_analysis_prompt(financial_data: str, data_source: str = "mock"):
    """Create the analysis prompt using LangChain ChatPromptTemplate"""
    data_context = "mock financial data" if data_source == "mock" else "real financial data from Plaid sandbox"
    data_note = "mock data for testing" if data_source == "mock" else "real sandbox data from Plaid"
    
    # Create system message
    system_template = V1_SYSTEM_PROMPT + f"""

Please analyze {data_context} and generate comprehensive insights following these instructions:
1. Analyze the portfolio structure, risk factors, and opportunities
2. Identify any compliance issues, deadlines, or urgent actions needed
3. Generate exactly 5 specific, actionable insights (you can combine related findings)
4. Prioritize insights by importance and urgency using priority values from 1 to 5 ONLY (1=highest, 5=lowest)
5. Provide clear recommendations for each insight
6. Support your analysis with specific data points from the input
7. Consider the data source context - this is {data_note}

CRITICAL FORMATTING REQUIREMENT:
- Each insight's "description" field MUST be exactly 2 lines
- Line 1: State WHAT the finding is, WHERE it occurs, and include KEY NUMBERS (amounts, percentages, dates, counts)
- Line 2: Explain WHY it matters, what the IMPACT is, and the URGENCY level
- Be concise but comprehensive - include all essential information in these 2 lines

You MUST return a JSON object with this EXACT structure:
- Root object with: insights (array), summary (string), total_insights (number), analysis_timestamp (ISO string)
- Each insight in the insights array must have:
  * title (string)
  * insight_type (one of: "risk", "opportunity", "action", "alert", "summary")
  * description (string with EXACTLY 2 lines separated by \\n)
  * impact (one of: "high", "medium", "low")
  * confidence (one of: "high", "medium", "low")
  * recommendation (string)
  * supporting_data (array of strings)
  * priority (number 1-5)

CRITICAL: Use "insight_type" NOT "category". Include ALL required fields: insight_type, impact, confidence, supporting_data, summary, total_insights.
"""
    
    # Create human message template
    # Use double braces for financial_data to escape it when formatting data_context
    human_template = """Analyze the following {data_context} and generate comprehensive insights:

Financial Data:
{{financial_data}}

Provide your analysis as a JSON object matching the InsightResponse schema."""
    
    # Format data_context into the template first (double braces become single braces)
    human_template = human_template.format(data_context=data_context)
    
    # Create prompt template (now financial_data is in single braces for LangChain)
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_template),
        HumanMessagePromptTemplate.from_template(human_template)
    ])
    
    return prompt


def run_analysis_with_data(financial_data: Dict[str, Any], data_source: str = "mock") -> InsightResponse:
    """Main analysis function that orchestrates the entire process"""
    print(f"Starting AI Insights Agent Analysis with {data_source} data...")
    print("=" * 50)
    
    # Initialize Gemini model
    print("\nInitializing AI model...")
    model = initialize_gemini_model()
    
    # Create analysis prompt using LangChain
    print("\nPreparing analysis prompt...")
    formatted_data = json.dumps(financial_data, indent=2)
    prompt_template = create_analysis_prompt(formatted_data, data_source)
    
    # Create output parser for structured output
    output_parser = PydanticOutputParser(pydantic_object=InsightResponse)
    
    # Run the analysis
    print("\nRunning financial analysis...")
    print(Fore.GREEN + "=" * 60)
    print(Fore.GREEN + ">>> LangChain: Invoking model with formatted prompt...")
    try:
        # Format the prompt with data
        formatted_prompt = prompt_template.format_messages(financial_data=formatted_data)
        
        # Generate response using LangChain
        print(Fore.GREEN + ">>> LangChain: Sending request to Gemini model...")
        print(Fore.GREEN + ">>> LangChain: Model is processing...")
        response = model.invoke(formatted_prompt)
        print(Fore.GREEN + ">>> LangChain: Response received successfully!")
        print(Fore.GREEN + f">>> LangChain: Response type: {type(response).__name__}")
        print(Fore.GREEN + f">>> LangChain: Response content length: {len(response.content)} characters")
        print(Fore.GREEN + "=" * 60 + Style.RESET_ALL)
        
        # Parse the JSON response
        response_text = response.content.strip()
        print(f"DEBUG: First 500 chars of response: {response_text[:500]}")
        
        # Clean up the response (remove markdown formatting if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text.split("```")[1]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Fix newlines in JSON strings - extract JSON block and properly escape newlines
        import re
        # Find the JSON object (from first { to last })
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_content = response_text[json_start:json_end]
            # Use a state machine to properly escape newlines in string values
            # Iterate through and replace newlines that are inside string values
            result_chars = []
            in_string = False
            escape_next = False
            i = 0
            while i < len(json_content):
                char = json_content[i]
                if escape_next:
                    result_chars.append(char)
                    escape_next = False
                elif char == '\\' and in_string:
                    result_chars.append(char)
                    escape_next = True
                elif char == '"' and not escape_next:
                    in_string = not in_string
                    result_chars.append(char)
                elif char == '\n' and in_string:
                    result_chars.append('\\n')
                elif char == '\r' and in_string:
                    result_chars.append('\\r')
                else:
                    result_chars.append(char)
                i += 1
            json_content = ''.join(result_chars)
            response_text = response_text[:json_start] + json_content + response_text[json_end:]
        
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
        print(f"ERROR: Error type: {type(e)}")
        import traceback
        print(f"ERROR: Full traceback:")
        traceback.print_exc()
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
