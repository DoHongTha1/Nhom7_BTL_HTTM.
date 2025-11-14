"""
Scheduler script for automated data pipeline updates
"""
import schedule
import time
import sys
import os
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_pipeline import DataPipeline
from app.config import settings
from app.models.xgboost_model import PopulationXGBoostModel
from app.routers import predict
from app.database import SessionLocal, CountryData

# Country list for data updates
COUNTRY_LIST = [
    {"code": "VN", "name": "Việt Nam"},
    {"code": "JP", "name": "Nhật Bản"},
    {"code": "NG", "name": "Nigeria"},
    {"code": "US", "name": "Hoa Kỳ"},
    {"code": "DE", "name": "Đức"},
    {"code": "TH", "name": "Thái Lan"},
    {"code": "MY", "name": "Malaysia"},
    {"code": "SG", "name": "Singapore"},
    {"code": "PH", "name": "Philippines"},
    {"code": "ID", "name": "Indonesia"},
    {"code": "KH", "name": "Campuchia"},
    {"code": "LA", "name": "Lào"},
    {"code": "MM", "name": "Myanmar"},
    {"code": "BN", "name": "Brunei"},
    # Add more countries as needed
]

def run_data_update():
    """Run data pipeline update"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting data update...")
    pipeline = DataPipeline()
    
    try:
        pipeline.update_all_countries(COUNTRY_LIST)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data update completed!")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error in data update: {e}")

def run_model_training():
    """Retrain XGBoost model after data update"""
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting model training...")
    try:
        session = SessionLocal()
        country_records = defaultdict(list)
        for record in session.query(CountryData).order_by(CountryData.year).all():
            country_records[record.country_code].append(record)
        session.close()

        countries = []
        for code, records in country_records.items():
            latest = records[-1]
            historical = [
                {
                    "year": rec.year,
                    "pop": rec.population,
                    "birth": rec.birth_rate,
                    "death": rec.death_rate,
                    "gdp": rec.gdp_per_capita
                }
                for rec in records
            ]
            countries.append({
                "name": latest.country_name,
                "country_code": latest.country_code,
                "population": latest.population,
                "birthRate": latest.birth_rate,
                    "deathRate": latest.death_rate,
                "gdpPerCapita": latest.gdp_per_capita,
                "urbanization": latest.urbanization,
                "educationIndex": latest.education_index or 0,
                "healthcareSpending": latest.healthcare_spending or 0,
                "fertilityRate": latest.fertility_rate or 0,
                "medianAge": latest.median_age or 0,
                "lifeExpectancy": latest.life_expectancy or 0,
                "historicalData": historical
            })

        if not countries:
            print("No training data available.")
            return
        model = PopulationXGBoostModel()
        metrics = model.train(countries, save_model=True)
        predict._model_instance = model
        print(f"Training completed. Val R²: {metrics.get('val_r2'):.3f}")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error in training: {e}")

def setup_scheduler():
    """Setup scheduler based on config"""
    schedule_type = settings.DATA_UPDATE_SCHEDULE.lower()
    
    if schedule_type == "daily":
        schedule.every().day.at("02:00").do(run_data_update)
        print("Scheduler set to run daily at 02:00")
    elif schedule_type == "weekly":
        schedule.every().monday.at("02:00").do(run_data_update)
        print("Scheduler set to run weekly on Monday at 02:00")
    elif schedule_type == "monthly":
        schedule.every().month.do(run_data_update)
        print("Scheduler set to run monthly on the 1st at 02:00")
    else:
        # Default: daily
        schedule.every().day.at("02:00").do(run_data_update)
        print("Scheduler set to run daily at 02:00 (default)")

if __name__ == "__main__":
    print("Starting data pipeline scheduler...")
    setup_scheduler()
    
    # Run once immediately
    run_data_update()
    
    # Then run on schedule
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

