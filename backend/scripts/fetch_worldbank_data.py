"""
Fetch real World Bank data for ASEAN countries
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
from app.database import CountryData, SessionLocal
from datetime import datetime

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

# World Bank indicator codes
INDICATORS = {
    "SP.POP.TOTL": "population",           # Total population
    "SP.URB.TOTL.IN.ZS": "urbanization",  # Urban population (% of total)
    "NY.GDP.PCAP.CD": "gdp_per_capita",   # GDP per capita (current US$)
    "SP.DYN.CBRT.IN": "birth_rate",       # Birth rate (per 1,000 people)
    "SP.DYN.CDRT.IN": "death_rate",       # Death rate (per 1,000 people)
    "SP.DYN.LE00.IN": "life_expectancy",  # Life expectancy at birth
    "NY.HEA.HLTH.CE.ZS": "healthcare_spending",  # Health expenditure (% of GDP)
}

def fetch_country_data(country_code, country_name, year):
    """Fetch data for a specific country and year"""
    try:
        country_data = {
            "country_code": country_code,
            "country_name": country_name,
            "year": year,
        }
        
        # Fetch each indicator separately
        for indicator_code, field_name in INDICATORS.items():
            time.sleep(0.05)  # Be nice to API
            
            url = f"https://api.worldbank.org/v2/country/{country_code}/indicators/{indicator_code}"
            
            params = {
                "date": f"{year}:{year}",
                "format": "json",
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Response format: [metadata, [records]]
            if len(data) > 1 and data[1] and len(data[1]) > 0:
                record = data[1][0]
                if record and 'value' in record and record['value'] is not None:
                    try:
                        country_data[field_name] = float(record['value'])
                    except (ValueError, TypeError):
                        pass
        
        return country_data
    
    except Exception as e:
        print(f"  Error fetching {country_name} {year}: {e}")
        return None

def fetch_worldbank_data():
    """Fetch data from World Bank API for all ASEAN countries"""
    print("Fetching World Bank data for ASEAN countries...")
    print(f"Countries: {', '.join(ASEAN_COUNTRIES.values())}\n")
    
    db = SessionLocal()
    fetched_count = 0
    
    try:
        for country_code, country_name in ASEAN_COUNTRIES.items():
            print(f"\n{country_name} ({country_code}):")
            
            # Fetch data for recent years (2015-2025)
            for year in range(2025, 2014, -1):  # Most recent first
                # Be nice to API - add delay
                time.sleep(0.1)
                
                country_data = fetch_country_data(country_code, country_name, year)
                
                if not country_data or len(country_data) < 5:
                    print(f"  {year}: No complete data")
                    continue
                
                # Check if record already exists
                existing = db.query(CountryData).filter(
                    CountryData.country_code == country_code,
                    CountryData.year == year
                ).first()
                
                if existing:
                    # Update existing record
                    for key, value in country_data.items():
                        if key not in ["country_code", "country_name", "year"] and value is not None:
                            setattr(existing, key, value)
                    db.commit()
                    print(f"  {year}: Updated")
                else:
                    # Create new record
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
                    )
                    db.add(record)
                    db.commit()
                    fetched_count += 1
                    print(f"  {year}: Added")
        
        print(f"\n\n{'='*50}")
        print(f"World Bank data fetch completed!")
        print(f"Records added/updated: {fetched_count}")
        print(f"{'='*50}")
        
    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    from app.database import init_db
    init_db()
    fetch_worldbank_data()
