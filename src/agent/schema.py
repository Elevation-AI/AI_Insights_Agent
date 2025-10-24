from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class InsightType(str, Enum):
    """Types of insights that can be generated"""
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    ACTION = "action"
    ALERT = "alert"
    SUMMARY = "summary"


class InsightCard(BaseModel):
    """Individual insight card containing analysis and recommendations"""
    title: str = Field(..., description="Clear, concise title for the insight")
    insight_type: InsightType = Field(..., description="Type of insight (risk, opportunity, action, alert, summary)")
    description: str = Field(..., description="Detailed description of the insight")
    impact: str = Field(..., description="Assessment of potential impact (high, medium, low)")
    confidence: str = Field(..., description="Confidence level in the insight (high, medium, low)")
    recommendation: str = Field(..., description="Specific actionable recommendation")
    supporting_data: List[str] = Field(..., description="Key data points that support this insight")
    priority: int = Field(..., ge=1, le=5, description="Priority level from 1 (highest) to 5 (lowest)")


class InsightResponse(BaseModel):
    """Complete response containing all generated insights"""
    insights: List[InsightCard] = Field(..., description="List of all generated insight cards")
    summary: str = Field(..., description="Executive summary of all insights")
    total_insights: int = Field(..., description="Total number of insights generated")
    analysis_timestamp: str = Field(..., description="Timestamp when analysis was performed")
