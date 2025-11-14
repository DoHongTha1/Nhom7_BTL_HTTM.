"""
Utility functions
"""
from typing import Dict, List

def convert_countries_data_to_training_format(countries_data: Dict) -> List[Dict]:
    """
    Convert frontend countries data format to training format
    Args:
        countries_data: Dictionary from frontend (countries.js format)
    Returns:
        List of country data dictionaries in training format
    """
    training_data = []
    
    for country_key, country_data in countries_data.items():
        # Extract historical data
        historical_data = []
        for hist in country_data.get('historicalData', []):
            historical_data.append({
                'year': hist['year'],
                'pop': hist['pop'] * 1000 if hist['pop'] < 100000 else hist['pop'],
                'birth': hist.get('birth', 0),
                'death': hist.get('death', 0),
                'gdp': hist.get('gdp', 0)
            })
        
        # Convert to training format
        training_data.append({
            'name': country_data.get('name', ''),
            'country_code': country_key.upper()[:2] if len(country_key) >= 2 else country_key,
            'population': country_data.get('population', 0),
            'birthRate': country_data.get('birthRate', 0),
            'deathRate': country_data.get('deathRate', 0),
            'gdpPerCapita': country_data.get('gdpPerCapita', 0),
            'urbanization': country_data.get('urbanization', 0),
            'educationIndex': country_data.get('educationIndex', 0),
            'healthcareSpending': country_data.get('healthcareSpending', 0),
            'fertilityRate': country_data.get('fertilityRate', 0),
            'medianAge': country_data.get('medianAge', 0),
            'lifeExpectancy': country_data.get('lifeExpectancy', 0),
            'growthRate': country_data.get('growthRate', 0),
            'stage': country_data.get('stage', 3),
            'historicalData': historical_data
        })
    
    return training_data

