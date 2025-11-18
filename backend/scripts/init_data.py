"""
Initialize database with UN/World Bank API data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db
from fetch_un_api_data import fetch_un_data

def init_database():
    """Initialize database using UN/World Bank API data"""
    print("\n" + "="*60)
    print("Initializing Database with UN/World Bank API")
    print("="*60 + "\n")
    
    try:
        fetch_un_data()
        print("\n" + "="*60)
        print("Database initialized successfully with UN/World Bank API data")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\nError initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()
    init_database()



