"""
AI Insights API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from app.services.genai_service import GenAIService

router = APIRouter()
genai_service = GenAIService()

class InsightsRequest(BaseModel):
    model_metrics: Dict
    forecast_data: Dict
    country_data: Dict

@router.post("/ai-insights")
async def get_ai_insights(request: InsightsRequest):
    """
    Generate AI insights based on model results
    """
    try:
        insights = genai_service.generate_ai_insights(
            request.model_metrics,
            request.forecast_data,
            request.country_data
        )
        
        return {
            "insights": insights,
            "timestamp": "2025-01-01T00:00:00Z"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

