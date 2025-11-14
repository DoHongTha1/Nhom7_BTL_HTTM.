"""
XGBoost Model for Population Prediction
"""
import xgboost as xgb
import pandas as pd
import numpy as np
import joblib
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from app.config import settings
from app.database import ModelMetrics, SessionLocal

class PopulationXGBoostModel:
    """XGBoost model for population growth prediction"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or settings.XGBOOST_PARAMS
        self.model = None
        self.feature_names = [
            'birthRate', 'deathRate', 'gdpPerCapita', 'urbanization',
            'educationIndex', 'healthcareSpending', 'fertilityRate',
            'medianAge', 'lifeExpectancy'
        ]
        self.feature_importance = {}
        self.training_metrics = {}
        self.is_trained = False
        
    def prepare_training_data(self, countries_data: List[Dict]) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data from countries data
        Args:
            countries_data: List of country data dictionaries
        Returns:
            X: Features DataFrame
            y: Target Series (population growth rate)
        """
        training_samples = []
        
        for country in countries_data:
            historical_data = country.get('historicalData', [])
            country_meta = {
                'urbanization': country.get('urbanization', 0) / 100,
                'educationIndex': country.get('educationIndex', 0),
                'healthcareSpending': country.get('healthcareSpending', 0) / 20,
                'fertilityRate': country.get('fertilityRate', 0) / 8,
                'medianAge': country.get('medianAge', 0) / 100,
                'lifeExpectancy': country.get('lifeExpectancy', 0) / 100
            }
            
            for i in range(len(historical_data) - 1):
                current = historical_data[i]
                next_year = historical_data[i + 1]
                
                # Calculate actual growth rate
                actual_growth = ((next_year['pop'] - current['pop']) / current['pop']) * 100
                
                # Prepare features
                features = {
                    'birthRate': current.get('birth', 0) / 50,
                    'deathRate': current.get('death', 0) / 20,
                    'gdpPerCapita': np.log1p(current.get('gdp', 0)) / 12,
                    'urbanization': country_meta['urbanization'],
                    'educationIndex': country_meta['educationIndex'],
                    'healthcareSpending': country_meta['healthcareSpending'],
                    'fertilityRate': country_meta['fertilityRate'],
                    'medianAge': country_meta['medianAge'],
                    'lifeExpectancy': country_meta['lifeExpectancy']
                }
                
                training_samples.append({
                    **features,
                    'target': actual_growth,
                    'country': country.get('name', ''),
                    'year': current.get('year', 0)
                })
        
        df = pd.DataFrame(training_samples)
        X = df[self.feature_names]
        y = df['target']
        
        return X, y
    
    def train(self, countries_data: List[Dict], save_model: bool = True) -> Dict:
        """
        Train the XGBoost model
        Args:
            countries_data: List of country data dictionaries
            save_model: Whether to save the trained model
        Returns:
            Dictionary with training metrics
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        import time
        
        start_time = time.time()
        
        # Prepare data
        X, y = self.prepare_training_data(countries_data)
        
        # Split data (80% train, 20% validation)
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Train XGBoost model
        self.model = xgb.XGBRegressor(**self.config)
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Predictions
        y_train_pred = self.model.predict(X_train)
        y_val_pred = self.model.predict(X_val)
        
        # Calculate metrics
        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        val_rmse = np.sqrt(mean_squared_error(y_val, y_val_pred))
        train_mae = mean_absolute_error(y_train, y_train_pred)
        val_mae = mean_absolute_error(y_val, y_val_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        val_r2 = r2_score(y_val, y_val_pred)
        
        # Feature importance
        self.feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_.tolist()
        ))
        
        training_time = time.time() - start_time
        
        self.training_metrics = {
            'train_rmse': float(train_rmse),
            'val_rmse': float(val_rmse),
            'train_mae': float(train_mae),
            'val_mae': float(val_mae),
            'train_r2': float(train_r2),
            'val_r2': float(val_r2),
            'training_time': float(training_time),
            'feature_importance': self.feature_importance
        }
        
        self.is_trained = True
        
        # Save model
        if save_model:
            self.save_model()
            
        # Save metrics to database
        self.save_metrics_to_db()
        
        return self.training_metrics
    
    def predict(self, features: Dict) -> float:
        """
        Predict population growth rate
        Args:
            features: Dictionary with feature values
        Returns:
            Predicted growth rate percentage
        """
        if not self.is_trained:
            raise ValueError("Model chưa được huấn luyện! Vui lòng train model trước.")
        
        # Prepare feature vector
        feature_vector = pd.DataFrame([{
            'birthRate': features.get('birthRate', 0) / 50,
            'deathRate': features.get('deathRate', 0) / 20,
            'gdpPerCapita': np.log1p(features.get('gdpPerCapita', 0)) / 12,
            'urbanization': features.get('urbanization', 0) / 100,
            'educationIndex': features.get('educationIndex', 0),
            'healthcareSpending': features.get('healthcareSpending', 0) / 20,
            'fertilityRate': features.get('fertilityRate', 0) / 8,
            'medianAge': features.get('medianAge', 0) / 100,
            'lifeExpectancy': features.get('lifeExpectancy', 0) / 100
        }])
        
        prediction = self.model.predict(feature_vector)[0]
        return float(prediction)
    
    def forecast(self, initial_data: Dict, years: int = 10) -> List[Dict]:
        """
        Forecast population for multiple years
        Args:
            initial_data: Initial country data
            years: Number of years to forecast
        Returns:
            List of forecasted data points
        """
        if not self.is_trained:
            raise ValueError("Model chưa được huấn luyện!")
        
        forecast_data = []
        current_data = initial_data.copy()
        current_pop = current_data.get('population', 0)
        
        for year in range(1, years + 1):
            # Prepare features for prediction
            features = {
                'birthRate': current_data.get('birthRate', 0),
                'deathRate': current_data.get('deathRate', 0),
                'gdpPerCapita': current_data.get('gdpPerCapita', 0),
                'urbanization': current_data.get('urbanization', 0),
                'educationIndex': current_data.get('educationIndex', 0),
                'healthcareSpending': current_data.get('healthcareSpending', 0),
                'fertilityRate': current_data.get('fertilityRate', 0),
                'medianAge': current_data.get('medianAge', 0),
                'lifeExpectancy': current_data.get('lifeExpectancy', 0)
            }
            
            # Predict growth rate
            growth_rate = self.predict(features)
            
            # Calculate new population
            new_pop = current_pop * (1 + growth_rate / 100)
            
            # Update current data (simple projection - can be enhanced)
            current_data['birthRate'] *= 0.995  # Slight decrease
            current_data['deathRate'] *= 1.01   # Slight increase
            current_data['gdpPerCapita'] *= 1.03  # GDP growth assumption
            current_data['medianAge'] += 0.5     # Aging
            current_data['lifeExpectancy'] += 0.1
            
            forecast_data.append({
                'year': 2025 + year,
                'population': new_pop,
                'growthRate': growth_rate,
                'birthRate': current_data['birthRate'],
                'deathRate': current_data['deathRate']
            })
            
            current_pop = new_pop
        
        return forecast_data
    
    def save_model(self, path: Optional[str] = None):
        """Save trained model to file"""
        if self.model is None:
            raise ValueError("Không có model để lưu!")
        
        path = path or settings.XGBOOST_MODEL_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self.model, path)
        print(f"Model đã được lưu tại: {path}")
    
    def load_model(self, path: Optional[str] = None):
        """Load trained model from file"""
        path = path or settings.XGBOOST_MODEL_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy model tại: {path}")
        
        self.model = joblib.load(path)
        self.is_trained = True
        print(f"Model đã được tải từ: {path}")
    
    def save_metrics_to_db(self):
        """Save training metrics to database"""
        try:
            from app.database import SessionLocal, ModelMetrics
            db = SessionLocal()
            metrics = ModelMetrics(
                model_version=f"v1.0_{datetime.now().strftime('%Y%m%d')}",
                training_date=datetime.now().date(),
                r2_score=self.training_metrics.get('val_r2', 0),
                rmse=self.training_metrics.get('val_rmse', 0),
                mae=self.training_metrics.get('val_mae', 0),
                feature_importance=self.feature_importance,
                training_time=self.training_metrics.get('training_time', 0)
            )
            db.add(metrics)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Lỗi khi lưu metrics vào database: {e}")

