"""
Main FastAPI application for Population Dynamics AI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from app.routers import predict, ai_insights, chat, data_pipeline, train, countries
from app.database import init_db

app = FastAPI(
    title="Population Dynamics AI API",
    description="Backend API cho hệ thống dự báo dân số với AI",
    version="1.0.0"
)

# CORS middleware để cho phép frontend React gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predict.router, prefix="/api", tags=["Prediction"])
app.include_router(ai_insights.router, prefix="/api", tags=["AI Insights"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(data_pipeline.router, prefix="/api", tags=["Data Pipeline"])
app.include_router(train.router, prefix="/api", tags=["Training"])
app.include_router(countries.router, prefix="/api", tags=["Countries"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("You may need to set up PostgreSQL first.")

@app.get("/")
async def root():
    return {
        "message": "Population Dynamics AI API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/api/predict",
            "ai_insights": "/api/ai-insights",
            "chat": "/api/chat",
            "train": "/api/train",
            "data_pipeline": "/api/data-pipeline"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


