"""
Database connection and models
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
import os

Base = declarative_base()

class CountryData(Base):
    """Database model for country demographic data"""
    __tablename__ = "countries"
    __table_args__ = (
        UniqueConstraint("country_code", "year", name="uq_country_year"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String, index=True)
    country_name = Column(String, index=True)
    year = Column(Integer, index=True)
    population = Column(Float)
    birth_rate = Column(Float)
    death_rate = Column(Float)
    gdp_per_capita = Column(Float)
    urbanization = Column(Float)
    education_index = Column(Float)
    healthcare_spending = Column(Float)
    fertility_rate = Column(Float)
    median_age = Column(Float)
    life_expectancy = Column(Float)
    growth_rate = Column(Float)
    stage = Column(Integer)  # Demographic transition stage
    extra_metadata = Column("metadata", JSON)  # Additional data

class ModelMetrics(Base):
    """Database model for storing model training metrics"""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, index=True)
    training_date = Column(Date)
    r2_score = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    feature_importance = Column(JSON)
    training_time = Column(Float)

class NewsArticle(Base):
    """Database model for news articles (RAG system)"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String, index=True)
    title = Column(String)
    content = Column(String)
    source = Column(String)
    published_date = Column(Date)
    embedding = Column(JSON)  # Vector embedding for semantic search

# Create database engine (use SQLite for development if PostgreSQL not available)
try:
    engine = create_engine(settings.DATABASE_URL)
except:
    # Fallback to SQLite for development
    engine = create_engine("sqlite:///./population_db.sqlite", connect_args={"check_same_thread": False})
    
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    os.makedirs(settings.MODEL_DIR, exist_ok=True)
    os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
