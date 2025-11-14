"""
Data Pipeline API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
from app.services.data_pipeline import DataPipeline

router = APIRouter()
pipeline = DataPipeline()

class UpdateRequest(BaseModel):
    country_list: List[Dict]  # List of {code, name}

@router.post("/data-pipeline/update")
async def update_data(request: UpdateRequest, background_tasks: BackgroundTasks):
    """
    Trigger data update for countries
    """
    try:
        # Run in background
        background_tasks.add_task(
            pipeline.update_all_countries,
            request.country_list
        )
        
        return {
            "message": f"Data update started for {len(request.country_list)} countries",
            "status": "processing"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-pipeline/scrape")
async def scrape_country(country_code: str, country_name: str):
    """
    Scrape data for a single country
    """
    try:
        data = pipeline.scrape_country_data(country_code, country_name)
        pipeline.save_to_database(data)
        
        return {
            "message": f"Data scraped and saved for {country_name}",
            "data": data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

