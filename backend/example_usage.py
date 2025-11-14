"""
Example usage of the Population Dynamics AI Backend
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Sample countries data (from frontend)
COUNTRIES_DATA = [
    {
        "name": "Việt Nam",
        "country_code": "VN",
        "population": 98800000,
        "birthRate": 14.8,
        "deathRate": 7.2,
        "gdpPerCapita": 4164,
        "urbanization": 38.2,
        "educationIndex": 0.707,
        "healthcareSpending": 5.3,
        "fertilityRate": 2.0,
        "medianAge": 32.5,
        "lifeExpectancy": 75.4,
        "growthRate": 0.76,
        "stage": 3,
        "historicalData": [
            {"year": 2000, "pop": 77635, "birth": 17.8, "death": 5.4, "gdp": 402},
            {"year": 2005, "pop": 83312, "birth": 16.5, "death": 5.5, "gdp": 638},
            {"year": 2010, "pop": 87411, "birth": 15.8, "death": 6.2, "gdp": 1334},
            {"year": 2015, "pop": 92677, "birth": 15.2, "death": 6.8, "gdp": 2088},
            {"year": 2020, "pop": 97339, "birth": 15.0, "death": 7.0, "gdp": 2786},
            {"year": 2025, "pop": 98800, "birth": 14.8, "death": 7.2, "gdp": 4164}
        ]
    },
    {
        "name": "Nhật Bản",
        "country_code": "JP",
        "population": 123300000,
        "birthRate": 6.9,
        "deathRate": 12.1,
        "gdpPerCapita": 33815,
        "urbanization": 91.8,
        "educationIndex": 0.844,
        "healthcareSpending": 11.1,
        "fertilityRate": 1.3,
        "medianAge": 49.1,
        "lifeExpectancy": 84.8,
        "growthRate": -0.53,
        "stage": 5,
        "historicalData": [
            {"year": 2000, "pop": 126843, "birth": 9.6, "death": 7.7, "gdp": 38532},
            {"year": 2005, "pop": 127773, "birth": 8.4, "death": 8.6, "gdp": 37217},
            {"year": 2010, "pop": 128070, "birth": 8.5, "death": 9.5, "gdp": 44508},
            {"year": 2015, "pop": 127141, "birth": 7.8, "death": 10.3, "gdp": 34524},
            {"year": 2020, "pop": 125502, "birth": 7.0, "death": 11.1, "gdp": 40113},
            {"year": 2025, "pop": 123300, "birth": 6.9, "death": 12.1, "gdp": 33815}
        ]
    }
]

def train_model():
    """Train the XGBoost model"""
    print("Training model...")
    response = requests.post(
        f"{BASE_URL}/api/train",
        json={"countries_data": COUNTRIES_DATA}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Training completed!")
        print(f"R² Score: {result['metrics']['val_r2']:.3f}")
        print(f"RMSE: {result['metrics']['val_rmse']:.3f}%")
        print(f"Feature Importance: {result['metrics']['feature_importance']}")
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

def predict_population():
    """Predict population for Vietnam"""
    print("\nPredicting population for Vietnam...")
    
    country_data = COUNTRIES_DATA[0]
    
    response = requests.post(
        f"{BASE_URL}/api/predict",
        json={
            "country_data": country_data,
            "years": 10,
            "use_rag": False  # Set to True if RAG is configured
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Forecast:")
        for forecast in result['forecast']:
            print(f"  {forecast['year']}: {forecast['population']:,.0f} (growth: {forecast['growthRate']:.2f}%)")
        return result
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def get_ai_insights():
    """Get AI insights"""
    print("\nGetting AI insights...")
    
    country_data = COUNTRIES_DATA[0]
    forecast_result = predict_population()
    
    if forecast_result:
        response = requests.post(
            f"{BASE_URL}/api/ai-insights",
            json={
                "model_metrics": forecast_result.get('metrics', {}),
                "forecast_data": {
                    "years": 10,
                    "growthRate": forecast_result['forecast'][-1]['growthRate'],
                    "finalPopulation": forecast_result['forecast'][-1]['population']
                },
                "country_data": country_data
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("AI Insights:")
            for insight in result['insights']:
                print(f"  • {insight}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

def chat_with_ai():
    """Chat with AI assistant"""
    print("\nChatting with AI...")
    
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "message": "Dân số Việt Nam có xu hướng như thế nào?",
            "context": {
                "country": "Việt Nam"
            }
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"AI Response: {result['response']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def check_model_status():
    """Check model status"""
    print("\nChecking model status...")
    response = requests.get(f"{BASE_URL}/api/model/status")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Model trained: {result['is_trained']}")
        if result['metrics']:
            print(f"R² Score: {result['metrics'].get('val_r2', 0):.3f}")
        return result
    else:
        print(f"Error: {response.status_code}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Population Dynamics AI Backend - Example Usage")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server is not responding correctly")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Please start the server first:")
        print("  python -m app.main")
        exit(1)
    
    # Check model status
    status = check_model_status()
    
    # Train model if not trained
    if not status or not status.get('is_trained'):
        if train_model():
            print("\n✓ Model trained successfully")
        else:
            print("\n✗ Model training failed")
            exit(1)
    
    # Run predictions
    predict_population()
    
    # Get AI insights
    get_ai_insights()
    
    # Chat with AI
    chat_with_ai()
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)

