"""
Training API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from app.models.xgboost_model import PopulationXGBoostModel

router = APIRouter()

_model_instance = None

def get_model():
    """Get or create model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = PopulationXGBoostModel()
    return _model_instance

class TrainingRequest(BaseModel):
    countries_data: List[Dict]

class TrainingResponse(BaseModel):
    metrics: Dict
    message: str

@router.post("/train", response_model=TrainingResponse)
async def train_model(request: TrainingRequest):
    """
    Train XGBoost model with provided data
    """
    model = get_model()
    
    try:
        if len(request.countries_data) < 2:
            raise HTTPException(
                status_code=400,
                detail="Cần ít nhất 2 quốc gia để huấn luyện mô hình."
            )
        
        metrics = model.train(request.countries_data, save_model=True)

        try:
            from app.routers import predict
            predict._model_instance = model
        except Exception as sync_error:
            print(f"Warning: Unable to sync trained model with prediction router: {sync_error}")
        
        return TrainingResponse(
            metrics=metrics,
            message="Model đã được huấn luyện thành công!"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/train/status")
async def training_status():
    """Get training status"""
    model = get_model()
    return {
        "is_trained": model.is_trained,
        "metrics": model.training_metrics if model.is_trained else None
    }

