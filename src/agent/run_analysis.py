#!/usr/bin/env python3
"""
AI Insights Agent - Main Analysis Script
This script loads mock data, initializes the Gemini model via LangChain,
and generates structured insights using Pydantic schemas.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

from colorama import Fore, Style, init
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import ValidationError

from src.agent.schema import InsightResponse
from src.agent.rules_engine import run_all_rules
from prompts.prompts import V1_HYBRID_SYSTEM_PROMPT

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


def load_mock_data(file_path: str = "input/mock_data.json") -> Dict[str, Any]:
    """Load the mock financial data from JSON file"""
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    print(f"SUCCESS: Successfully loaded mock data from {file_path}")
    return data
    


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


def create_analysis_messages(findings: str):
    """Create the analysis messages directly (avoiding template formatting issues with JSON)"""
    # Create system message using the Hybrid prompt
    system_message = SystemMessage(content=V1_HYBRID_SYSTEM_PROMPT)
    
    # Create human message content directly (no template, so no formatting issues)
    human_message_content = "Here are the facts you must summarize: " + findings + "\n\nProvide your analysis as a JSON object matching the InsightResponse schema."
    human_message = HumanMessage(content=human_message_content)
    
    return [system_message, human_message]


def run_analysis() -> Optional[InsightResponse]:
    """Main analysis function that orchestrates the entire process"""
    print("Starting AI Insights Agent Analysis...")
    print("=" * 50)
    
    # Step 1: Load mock data
    print("\n[Step 1] Loading financial data...")
    financial_context_object = load_mock_data()
    
    # Step 2: Rules Engine (The Quant)
    print("\n[Step 2] Running Rules Engine (The Quant)...")
    all_findings = run_all_rules(financial_context_object)
    
    # Check if no findings
    if not all_findings:
        print("No issues found.")
        return None
    
    print(f"SUCCESS: Rules Engine found {len(all_findings)} issues")
    
    # Step 3: Initialize Gemini model
    print("\n[Step 3] Initializing AI model...")
    model = initialize_gemini_model()
    
    # Step 4: Create analysis messages using Hybrid prompt
    print("\n[Step 4] Preparing analysis messages...")
    findings_json = json.dumps(all_findings, indent=2)
    messages = create_analysis_messages(findings_json)
    
    # Create output parser for structured output
    output_parser = PydanticOutputParser(pydantic_object=InsightResponse)
    
    # Step 5: Run the analysis (LLM Call)
    print("\n[Step 5] Running financial analysis...")
    print(Fore.GREEN + "=" * 60)
    print(Fore.GREEN + ">>> LangChain: Invoking model with messages...")
    try:
        
        # Generate response using LangChain
        print(Fore.GREEN + ">>> LangChain: Sending request to Gemini model...")
        print(Fore.GREEN + ">>> LangChain: Model is processing...")
        try:
            response = model.invoke(messages)
            print(Fore.GREEN + ">>> LangChain: Response received successfully!")
            print(Fore.GREEN + f">>> LangChain: Response type: {type(response).__name__}")
            
            # Extract response content
            if hasattr(response, 'content'):
                response_text = response.content.strip()
            elif isinstance(response, str):
                response_text = response.strip()
            else:
                response_text = str(response).strip()
            
            print(Fore.GREEN + f">>> LangChain: Response content length: {len(response_text)} characters")
            print(Fore.GREEN + "=" * 60 + Style.RESET_ALL)
        except Exception as e:
            print(f"ERROR: Failed to invoke model: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
        
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
        if json_start == -1 or json_end <= json_start:
            raise ValueError(f"No valid JSON object found in response. Response text: {response_text[:500]}")
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
        
        # Ensure required fields are present
        insights_count = len(response_data.get('insights', []))
        
        if 'summary' not in response_data:
            # Generate summary from insights if missing
            response_data['summary'] = f"Analysis identified {insights_count} key insights requiring attention."
        
        if 'total_insights' not in response_data:
            response_data['total_insights'] = insights_count
        
        if 'analysis_timestamp' not in response_data:
            response_data['analysis_timestamp'] = datetime.now().isoformat()
        
        result = InsightResponse(**response_data)
        
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
        print(f"Response text (first 1000 chars): {response_text[:1000] if 'response_text' in locals() else 'N/A'}")
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
        
        # Check if no findings were found
        if insights is None:
            print("\nAnalysis complete! No issues found.")
            return 0
        
        # Print results
        print_insights(insights)
        
        # Save results
        save_results(insights)
        
        print("\nAnalysis complete! Check the results above and the saved JSON file.")
        
    except Exception as e:
        print(f"\nAnalysis failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure you have set GOOGLE_API_KEY in your .env file or environment variables")
        print("2. Check that all required packages are installed: pip install -r requirements.txt")
        print("3. Verify your Google Cloud credentials and permissions")
        print("4. Make sure your .env file is in the project root directory")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
