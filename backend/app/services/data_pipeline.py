"""
Data Pipeline for automated data collection from UN/World Bank API
All data fetching is handled by scripts/fetch_un_api_data.py
"""
from typing import Dict, List
from datetime import datetime
from app.database import CountryData, SessionLocal

class DataPipeline:
    """Data pipeline - now simplified as data comes from UN API script"""
    
    def __init__(self):
        # Data is now fetched via fetch_un_api_data.py script
        pass
    
    def scrape_country_data(self, country_code: str, country_name: str) -> Dict:
        """
        Legacy method - data fetching now handled by fetch_un_api_data.py
        Returns placeholder message
        """
        return {
            'country_code': country_code,
            'country_name': country_name,
            'message': 'Data fetching handled by UN API script on startup. See scripts/fetch_un_api_data.py'
        }
    
    def save_to_database(self, country_data: Dict):
        """Legacy method - kept for compatibility"""
        print(f"Note: Data saving is now handled by fetch_un_api_data.py script")
        print(f"Received data for: {country_data.get('country_name', 'Unknown')}")
    
    def update_all_countries(self, country_list: List[Dict]):
        """
        Legacy method - data updates now handled by fetch_un_api_data.py
        """
        print(f"Note: Data updates are now handled by the UN API fetch script")
        print(f"Please run: python scripts/fetch_un_api_data.py")
        print(f"Or restart the backend server to trigger automatic data fetch")
