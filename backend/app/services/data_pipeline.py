"""
Data Pipeline for automated data collection from World Bank and UN
"""
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import time
from app.config import settings
from app.database import CountryData, SessionLocal

class DataPipeline:
    """Automated data collection pipeline"""
    
    def __init__(self):
        self.world_bank_url = settings.WORLD_BANK_API_URL
        self.un_data_url = settings.UN_DATA_API_URL
    
    def fetch_world_bank_data(self, country_code: str, indicators: List[str]) -> Dict:
        """
        Fetch data from World Bank API
        Args:
            country_code: ISO country code (e.g., 'VN', 'US')
            indicators: List of indicator codes
        Returns:
            Dictionary with country data
        """
        data = {}
        
        for indicator in indicators:
            try:
                url = f"{self.world_bank_url}/{country_code}/indicator/{indicator}?format=json&date=2000:2025"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                json_data = response.json()
                if len(json_data) > 1 and json_data[1]:
                    # Get latest value
                    latest = json_data[1][0] if json_data[1] else None
                    if latest and 'value' in latest:
                        data[indicator] = latest['value']
                
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Error fetching {indicator} for {country_code}: {e}")
        
        return data
    
    def fetch_un_data(self, country_name: str) -> Dict:
        """
        Fetch data from UN Population Division
        Note: UN API may require authentication, this is a simplified version
        Args:
            country_name: Country name
        Returns:
            Dictionary with UN data
        """
        # This is a placeholder - actual UN API may require different approach
        # You might need to scrape from https://population.un.org/wpp/Download/
        data = {}
        
        try:
            # Example: Fetch from UN API if available
            # This would need to be customized based on actual UN API structure
            pass
        except Exception as e:
            print(f"Error fetching UN data for {country_name}: {e}")
        
        return data
    
    def scrape_country_data(self, country_code: str, country_name: str) -> Dict:
        """
        Scrape country demographic data from multiple sources
        Args:
            country_code: ISO country code
            country_name: Country name
        Returns:
            Combined country data dictionary
        """
        # Define World Bank indicators
        indicators = {
            'SP.POP.TOTL': 'population',
            'SP.DYN.CBRT.IN': 'birthRate',
            'SP.DYN.CDRT.IN': 'deathRate',
            'NY.GDP.PCAP.CD': 'gdpPerCapita',
            'SP.URB.TOTL.IN.ZS': 'urbanization',
            'SP.DYN.TFRT.IN': 'fertilityRate',
            'SP.DYN.LE00.IN': 'lifeExpectancy'
        }
        
        # Fetch from World Bank
        wb_data = self.fetch_world_bank_data(country_code, list(indicators.keys()))
        
        # Transform data
        country_data = {
            'country_code': country_code,
            'country_name': country_name,
            'year': datetime.now().year,
            'population': wb_data.get('SP.POP.TOTL'),
            'birthRate': wb_data.get('SP.DYN.CBRT.IN'),
            'deathRate': wb_data.get('SP.DYN.CDRT.IN'),
            'gdpPerCapita': wb_data.get('NY.GDP.PCAP.CD'),
            'urbanization': wb_data.get('SP.URB.TOTL.IN.ZS'),
            'fertilityRate': wb_data.get('SP.DYN.TFRT.IN'),
            'lifeExpectancy': wb_data.get('SP.DYN.LE00.IN')
        }
        
        # Calculate derived metrics
        if country_data['birthRate'] is not None and country_data['deathRate'] is not None:
            country_data['growthRate'] = country_data['birthRate'] - country_data['deathRate']
        
        # Determine demographic stage
        country_data['stage'] = self._determine_stage(
            country_data.get('birthRate'),
            country_data.get('deathRate'),
            country_data.get('growthRate')
        )
        
        return country_data
    
    def _determine_stage(self, birth_rate: float, death_rate: float, growth_rate: float) -> int:
        """Determine demographic transition stage"""
        if birth_rate is None or death_rate is None or growth_rate is None:
            return 3
        if birth_rate > 30 and death_rate > 20:
            return 1  # Pre-transition
        elif birth_rate > 30 and death_rate < 20:
            return 2  # Early transition
        elif 20 < birth_rate < 30 and death_rate < 15:
            return 3  # Late transition
        elif birth_rate < 20 and death_rate < 10:
            return 4  # Post-transition
        elif birth_rate < death_rate:
            return 5  # Declining
        else:
            return 3  # Default
    
    def save_to_database(self, country_data: Dict):
        """Save country data to database"""
        try:
            db = SessionLocal()
            mapped_data = {
                "country_code": country_data.get("country_code"),
                "country_name": country_data.get("country_name"),
                "year": country_data.get("year"),
                "population": country_data.get("population"),
                "birth_rate": country_data.get("birthRate"),
                "death_rate": country_data.get("deathRate"),
                "gdp_per_capita": country_data.get("gdpPerCapita"),
                "urbanization": country_data.get("urbanization"),
                "education_index": country_data.get("educationIndex"),
                "healthcare_spending": country_data.get("healthcareSpending"),
                "fertility_rate": country_data.get("fertilityRate"),
                "median_age": country_data.get("medianAge"),
                "life_expectancy": country_data.get("lifeExpectancy"),
                "growth_rate": country_data.get("growthRate"),
                "stage": country_data.get("stage"),
            }
            
            # Check if record exists
            existing = db.query(CountryData).filter(
                CountryData.country_code == mapped_data['country_code'],
                CountryData.year == mapped_data['year']
            ).first()
            
            if existing:
                # Update existing record
                for key, value in mapped_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
            else:
                # Create new record
                new_record = CountryData(**mapped_data)
                db.add(new_record)
            
            db.commit()
            db.close()
            print(f"Saved data for {country_data['country_name']} ({country_data['year']})")
        except Exception as e:
            print(f"Error saving to database: {e}")
    
    def update_all_countries(self, country_list: List[Dict]):
        """
        Update data for all countries
        Args:
            country_list: List of {code, name} dictionaries
        """
        print(f"Starting data update for {len(country_list)} countries...")
        
        for i, country in enumerate(country_list, 1):
            print(f"Processing {i}/{len(country_list)}: {country['name']}")
            
            try:
                country_data = self.scrape_country_data(
                    country['code'],
                    country['name']
                )
                
                self.save_to_database(country_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {country['name']}: {e}")
        
        print("Data update completed!")
    
    def collect_news_articles(self, country_code: str, country_name: str, max_articles: int = 10):
        """
        Collect news articles related to population/demographics
        This is a placeholder - actual implementation would use news APIs or web scraping
        Args:
            country_code: Country code
            country_name: Country name
            max_articles: Maximum number of articles to collect
        """
        # This would integrate with news APIs like:
        # - NewsAPI
        # - Google News RSS
        # - Web scraping from news sites
        
        query = f"{country_name} dân số nhân khẩu chính sách khuyến sinh"
        
        # Placeholder - actual implementation needed
        articles = []
        
        return articles
