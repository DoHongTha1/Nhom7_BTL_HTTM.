"""
Prediction API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.models.xgboost_model import PopulationXGBoostModel
from app.services.rag_service import RAGService

router = APIRouter()

# Initialize model and services
_model_instance = None
_rag_service = None

def get_model():
    """Get or create model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = PopulationXGBoostModel()
        try:
            _model_instance.load_model()
        except:
            print("No existing model found. Please train model first.")
    return _model_instance

def get_rag_service():
    """Get or create RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

class PredictionRequest(BaseModel):
    country_data: Dict
    years: int = 10
    use_rag: bool = False

class PredictionResponse(BaseModel):
    forecast: List[Dict]
    metrics: Optional[Dict] = None
    rag_adjustments: Optional[Dict] = None

@router.post("/predict", response_model=PredictionResponse)
async def predict_population(request: PredictionRequest):
    """
    Predict population growth for a country
    """
    model = get_model()
    rag_service = get_rag_service()
    
    if not model.is_trained:
        raise HTTPException(
            status_code=400,
            detail="Model chưa được huấn luyện. Vui lòng train model trước."
        )
    
    try:
        # Apply RAG adjustments if requested
        adjusted_features = request.country_data.copy()
        rag_adjustments = None
        
        if request.use_rag:
            country_code = request.country_data.get('country_code', '')
            country_name = request.country_data.get('name', '')
            
            adjustments = rag_service.generate_contextual_adjustments(
                country_code,
                country_name,
                request.country_data
            )
            
            if adjustments.get('adjustments'):
                # Apply adjustments
                for key, value in adjustments['adjustments'].items():
                    if key in adjusted_features:
                        adjusted_features[key] += value
                
                rag_adjustments = adjustments
        
        # Generate forecast
        forecast = model.forecast(adjusted_features, years=request.years)
        
        return PredictionResponse(
            forecast=forecast,
            metrics=model.training_metrics,
            rag_adjustments=rag_adjustments
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/status")
async def model_status():
    """Get model status"""
    model = get_model()
    return {
        "is_trained": model.is_trained,
        "metrics": model.training_metrics if model.is_trained else None,
        "feature_importance": model.feature_importance if model.is_trained else None
    }

