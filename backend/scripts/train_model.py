"""
Train XGBoost model with data from database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import distinct
from app.database import SessionLocal, CountryData
from app.models.xgboost_model import PopulationXGBoostModel

def fetch_training_data():
    """Fetch training data from database"""
    session = SessionLocal()
    countries_data = []
    
    try:
        # Get all unique country codes
        country_codes = session.query(distinct(CountryData.country_code)).all()
        
        print(f"Found {len(country_codes)} countries in database\n")
        
        for (code,) in country_codes:
            # Get all historical data for this country (sorted by year)
            records = session.query(CountryData).filter(
                CountryData.country_code == code
            ).order_by(CountryData.year).all()
            
            if len(records) < 2:
                print(f"Skipping {code}: Not enough historical data (need at least 2 years)")
                continue
            
            # Build country data structure
            first_record = records[0]
            historical_data = []
            
            for record in records:
                historical_data.append({
                    'year': record.year,
                    'pop': record.population or 0,
                    'birth': record.birth_rate or 15.0,
                    'death': record.death_rate or 7.0,
                    'gdp': record.gdp_per_capita or 3000
                })
            
            country_dict = {
                'name': code,
                'code': code,
                'urbanization': first_record.urbanization or 50.0,
                'educationIndex': first_record.education_index or 0.7,
                'healthcareSpending': first_record.healthcare_spending or 5.0,
                'fertilityRate': first_record.fertility_rate or 2.0,
                'medianAge': first_record.median_age or 32.0,
                'lifeExpectancy': first_record.life_expectancy or 74.0,
                'historicalData': historical_data
            }
            
            countries_data.append(country_dict)
            print(f"{code}: Loaded {len(historical_data)} years of data")
        
    finally:
        session.close()
    
    return countries_data

def main():
    """Main training function"""
    print("="*60)
    print("Training XGBoost Model for Population Forecasting")
    print("="*60)
    print("\n1. Fetching training data from database...\n")
    
    countries_data = fetch_training_data()
    
    if len(countries_data) < 2:
        print("\nERROR: Need at least 2 countries with historical data")
        print("Please run: python scripts/fetch_un_api_data.py")
        return False
    
    print(f"\n2. Training with {len(countries_data)} countries...\n")
    
    # Initialize and train model
    model = PopulationXGBoostModel()
    metrics = model.train(countries_data, save_model=True)
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"\nModel Performance Metrics:")
    print(f"  Validation R² Score:  {metrics['val_r2']:.4f}")
    print(f"  Validation RMSE:      {metrics['val_rmse']:.4f}")
    print(f"  Validation MAE:       {metrics['val_mae']:.4f}")
    print(f"  Training Time:        {metrics['training_time']:.2f}s")
    
    print(f"\nFeature Importance:")
    for feature, importance in sorted(metrics['feature_importance'].items(), 
                                     key=lambda x: x[1], reverse=True):
        bar = "#" * int(importance * 50)
        print(f"  {feature:20s} {bar} {importance:.4f}")
    
    print(f"\nModel saved to: ./models/xgboost_model.pkl")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
