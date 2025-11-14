"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/population_db")
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/population_db")
    
    # GenAI APIs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
    USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"
    
    # Model paths
    MODEL_DIR = os.getenv("MODEL_DIR", "./models")
    XGBOOST_MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_model.pkl")
    
    # RAG settings
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_db")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Data sources
    WORLD_BANK_API_URL = "https://api.worldbank.org/v2/country"
    UN_DATA_API_URL = "https://population.un.org/wpp/Download/Standard/CSV/"
    
    # Training settings
    XGBOOST_PARAMS = {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42
    }
    
    # Data pipeline
    DATA_UPDATE_SCHEDULE = os.getenv("DATA_UPDATE_SCHEDULE", "monthly")  # daily, weekly, monthly
    
settings = Settings()


