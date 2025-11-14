"""
Initialize database with World Bank data + sample demographic rates
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import time
from app.database import CountryData, SessionLocal, init_db
from app.config import settings

# ASEAN country codes for World Bank API
ASEAN_COUNTRIES = {
    "VN": "Việt Nam",
    "TH": "Thái Lan",
    "MY": "Malaysia",
    "SG": "Singapore",
    "PH": "Philippines",
    "ID": "Indonesia",
    "KH": "Campuchia",
    "LA": "Lào",
    "MM": "Myanmar",
    "BN": "Brunei",
}

# Estimated demographic rates (World Bank style estimates for recent years)
# These are realistic based on official sources and UN data
DEMOGRAPHIC_RATES = {
    "VN": {"birth": 14.8, "death": 7.2, "fertility": 2.0, "life_expectancy": 75.4},
    "TH": {"birth": 10.5, "death": 8.8, "fertility": 1.4, "life_expectancy": 77.1},
    "MY": {"birth": 15.3, "death": 5.0, "fertility": 2.0, "life_expectancy": 76.6},
    "SG": {"birth": 9.0, "death": 5.7, "fertility": 1.05, "life_expectancy": 83.7},
    "PH": {"birth": 19.2, "death": 6.2, "fertility": 2.58, "life_expectancy": 71.7},
    "ID": {"birth": 17.5, "death": 6.3, "fertility": 2.3, "life_expectancy": 71.8},
    "KH": {"birth": 20.5, "death": 6.8, "fertility": 2.55, "life_expectancy": 71.0},
    "LA": {"birth": 22.5, "death": 6.4, "fertility": 2.8, "life_expectancy": 71.7},
    "MM": {"birth": 17.8, "death": 7.5, "fertility": 2.2, "life_expectancy": 67.6},
    "BN": {"birth": 16.5, "death": 3.8, "fertility": 1.87, "life_expectancy": 75.3},
}

# World Bank indicator codes
INDICATORS = {
    "SP.POP.TOTL": "population",
    "NY.GDP.PCAP.CD": "gdp_per_capita",
    "SP.URB.TOTL.IN.ZS": "urbanization",
}

def fetch_indicator_data(country_code, indicator_code, year):
    """Fetch single indicator from World Bank API"""
    try:
        url = f"https://api.worldbank.org/v2/country/{country_code}/indicators/{indicator_code}"
        params = {"date": f"{year}:{year}", "format": "json"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if len(data) > 1 and data[1] and len(data[1]) > 0:
            record = data[1][0]
            if record and 'value' in record and record['value'] is not None:
                return float(record['value'])
    except Exception:
        pass
    
    return None

def init_database():
    """Initialize database with World Bank data + demographic estimates"""
    print("\n" + "="*60)
    print("🌍 Initializing Database with World Bank + Demographic Data")
    print("="*60 + "\n")
    
    db = SessionLocal()
    total_added = 0
    
    try:
        for country_code, country_name in ASEAN_COUNTRIES.items():
            print(f"📍 {country_name} ({country_code}):")
            
            # Get demographic rates for this country
            demo_rates = DEMOGRAPHIC_RATES.get(country_code, {})
            
            # Fetch data for years 2015-2024 (10 years of data)
            for year in range(2024, 2014, -1):
                country_data = {
                    "country_code": country_code,
                    "country_name": country_name,
                    "year": year,
                }
                
                # Fetch core indicators from World Bank
                for indicator_code, field_name in INDICATORS.items():
                    time.sleep(0.02)  # Be nice to API
                    
                    value = fetch_indicator_data(country_code, indicator_code, year)
                    if value is not None:
                        country_data[field_name] = value
                
                # Add demographic rates (estimated/fixed)
                country_data["birth_rate"] = demo_rates.get("birth")
                country_data["death_rate"] = demo_rates.get("death")
                country_data["fertility_rate"] = demo_rates.get("fertility")
                country_data["life_expectancy"] = demo_rates.get("life_expectancy")
                
                # Check if we have meaningful data
                if "population" in country_data:
                    # Check if record exists
                    existing = db.query(CountryData).filter(
                        CountryData.country_code == country_code,
                        CountryData.year == year
                    ).first()
                    
                    if not existing:
                        record = CountryData(
                            country_code=country_data["country_code"],
                            country_name=country_data["country_name"],
                            year=country_data["year"],
                            population=country_data.get("population"),
                            birth_rate=country_data.get("birth_rate"),
                            death_rate=country_data.get("death_rate"),
                            gdp_per_capita=country_data.get("gdp_per_capita"),
                            urbanization=country_data.get("urbanization"),
                            life_expectancy=country_data.get("life_expectancy"),
                            healthcare_spending=country_data.get("healthcare_spending"),
                            fertility_rate=country_data.get("fertility_rate"),
                        )
                        db.add(record)
                        print(f"  ✅ {year}: Added")
                        total_added += 1
                    else:
                        print(f"  ⏭️  {year}: Already exists")
                else:
                    print(f"  ⏭️  {year}: No World Bank data")
                
                db.commit()
        
        print(f"\n{'='*60}")
        print(f"✅ Database initialized!")
        print(f"📝 Total records added: {total_added}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    init_database()



