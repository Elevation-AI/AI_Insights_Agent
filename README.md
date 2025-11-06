# AI Insights Agent 

A sophisticated AI-powered financial Insights analysis agent that fetches real data from Plaid and generates actionable insights using Google's Gemini AI.

##  Project Structure

```
AI_Insights_agent_mvp/
├── src/
│   └── agent/                    # Core agent functionality
│       ├── __init__.py
│       ├── run_analysis.py       # Mock data analysis
│       ├── run_analysis_with_plaid.py  # Real Plaid data analysis
│       ├── plaid_data_fetcher.py       # Plaid data fetching (full version)
│       ├── plaid_data_fetcher_simple.py # Plaid data fetching (simplified)
│       ├── plaid_data_transformer.py   # Data format conversion
│       └── schema.py             # Pydantic data models
├── prompts/                      # AI prompts and templates
│   ├── __init__.py
│   ├── prompts.py               # Main V1 system prompt
│   └── prompt_2.py             # Alternative "Aperture" prompt
├── output/                      # Generated results and data
│   ├── analysis_results_mock.json
│   ├── analysis_results_plaid.json
│   ├── plaid_data.json
│   └── transformed_plaid_data.json
├── test/                        # Test files
│   ├── __init__.py
│   └── test_structure.py        # Structure validation tests
├── main.py                      # Main entry point with menu
├── access.py                    # Plaid token creation
├── mock_data.json              # Sample financial data
├── requirements.txt             # Python dependencies
├── setup.py                    # Automated setup script
└── README.md                   # This file
```

##  Quick Start

### Option 1: Interactive Menu (Recommended)
```bash
python main.py
```

### Option 2: Direct Script Execution
```bash
# Fetch Plaid data
python src/agent/plaid_data_fetcher_simple.py

# Transform data
python src/agent/plaid_data_transformer.py

# Run analysis
python src/agent/run_analysis_with_plaid.py
```

##  Features

###  **Completed Features**
- **Plaid Integration**: Real-time data fetching from Plaid sandbox
- **Data Transformation**: Convert Plaid format to family office schema
- **AI Analysis**: Generate insights using Gemini 2.0 Flash
- **Dual Data Sources**: Support for both mock and real data
- **Structured Output**: Pydantic-validated JSON responses
- **Error Handling**: Robust retry logic and error management
- **Organized Structure**: Clean separation of concerns

###  **Data Pipeline**
1. **Fetch**: Get real financial data from Plaid sandbox
2. **Transform**: Convert to family office format
3. **Analyze**: Generate AI-powered insights
4. **Output**: Save structured results

###  **Analysis Capabilities**
- **Risk Assessment**: Concentration, liquidity, compliance risks
- **Opportunity Identification**: Portfolio optimization opportunities
- **Action Items**: Immediate and strategic recommendations
- **Alerts**: Critical issues requiring attention
- **Data Quality**: Connection status and data freshness

##  Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key_here
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
```

### 3. Run Setup (Optional)
```bash
python setup.py
```

##  Usage Examples

### Fetch and Analyze Real Data
```python
from src.agent.plaid_data_fetcher_simple import PlaidDataFetcher
from src.agent.plaid_data_transformer import PlaidDataTransformer
from src.agent.run_analysis_with_plaid import run_analysis_with_data

# Fetch data
fetcher = PlaidDataFetcher()
public_token = fetcher.create_public_token()
data = fetcher.fetch_basic_data(public_token)

# Transform data
transformer = PlaidDataTransformer()
transformed_data = transformer.transform_to_family_office_format(data)

# Analyze
insights = run_analysis_with_data(transformed_data, "plaid")
```

### Custom Analysis
```python
from src.agent.schema import InsightResponse
from prompts.prompts import V1_SYSTEM_PROMPT

# Use custom prompt
custom_prompt = f"{V1_SYSTEM_PROMPT}\n\nAnalyze this data..."
```

##  Output Files

### `output/` Directory Contents:
- **`plaid_data.json`**: Raw Plaid API response
- **`transformed_plaid_data.json`**: Converted family office format
- **`analysis_results_mock.json`**: Mock data insights
- **`analysis_results_plaid.json`**: Real data insights

### Sample Output Structure:
```json
{
  "insights": [
    {
      "title": "High Tech Sector Concentration Risk",
      "insight_type": "risk",
      "description": "Portfolio heavily concentrated in tech sector...",
      "impact": "high",
      "confidence": "high",
      "recommendation": "Diversify across sectors...",
      "supporting_data": ["MSFT: $500K", "GOOG: $700K"],
      "priority": 1
    }
  ],
  "summary": "Executive summary...",
  "total_insights": 5,
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔧 Configuration

### Prompts
- **`prompts/prompts.py`**: Main comprehensive analyst prompt
- **`prompts/prompt_2.py`**: Alternative "Aperture" prompt with specific thresholds

### Models
- **Gemini 2.0 Flash**: Primary AI model
- **Temperature**: 0.1 (low for consistent results)
- **Max Tokens**: 4096

### Plaid Settings
- **Environment**: Sandbox
- **Products**: Transactions, Investments
- **Retry Logic**: 3 attempts with 5-second delays

##  Testing

```bash
# Run structure tests
python test/test_structure.py

# Test individual components
python src/agent/plaid_data_fetcher_simple.py
python src/agent/plaid_data_transformer.py
```

##  Next Steps

### Production Readiness
1. **Database Integration**: Replace JSON files with proper database
2. **API Endpoints**: Create REST API for external access
3. **Authentication**: Implement user authentication
4. **Real-time Updates**: Add webhook handling
5. **Advanced Analytics**: Implement sophisticated risk metrics

### Enhancements
- **Multi-user Support**: Handle multiple family offices
- **Custom Prompts**: User-defined analysis criteria
- **Visualization**: Dashboard for insights
- **Alerts**: Real-time notifications
- **Reporting**: PDF report generation

##  Support

For issues or questions:
1. Check the troubleshooting section in individual scripts
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Review the output logs for specific error messages

---

**Status**:  Fully functional MVP with real Plaid integration
**Last Updated**: October 2024
