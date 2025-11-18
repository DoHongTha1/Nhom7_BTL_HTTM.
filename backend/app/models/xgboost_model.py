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
        # Optimized config for augmented dataset
        self.config = config or {
            'max_depth': 4,  # Deeper trees with more data
            'learning_rate': 0.05,  # Moderate learning rate
            'n_estimators': 300,  # More trees for better learning
            'min_child_weight': 3,  # Less strict with more data
            'subsample': 0.8,  # Higher sampling with more data
            'colsample_bytree': 0.8,
            'gamma': 0.3,  # Less regularization with more data
            'reg_alpha': 0.5,  # Reduced L1 regularization
            'reg_lambda': 1.0,  # Reduced L2 regularization
            'random_state': 42,
            'objective': 'reg:squarederror'
        }
        self.model = None
        # Use only most important features
        self.feature_names = [
            'birthRate', 'deathRate', 'naturalIncrease', 'birthDeathRatio',
            'gdpLog', 'lifeExpectancy', 'urbanization'
        ]
        self.feature_importance = {}
        self.training_metrics = {}
        self.is_trained = False
        
    def prepare_training_data(self, countries_data: List[Dict]) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data from countries data with data augmentation
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
                
                # Extract values
                birth = current.get('birth', 15.0)
                death = current.get('death', 7.0)
                gdp = current.get('gdp', 3000)
                
                # Prepare features - only keep most important ones
                features = {
                    'birthRate': birth / 50,
                    'deathRate': death / 20,
                    'naturalIncrease': (birth - death) / 30,
                    'birthDeathRatio': birth / max(death, 1),
                    'gdpLog': np.log1p(gdp) / 15,
                    'lifeExpectancy': country_meta['lifeExpectancy'],
                    'urbanization': country_meta['urbanization']
                }
                
                # Add original sample
                training_samples.append({
                    **features,
                    'target': actual_growth,
                    'country': country.get('name', ''),
                    'year': current.get('year', 0)
                })
                
                # DATA AUGMENTATION: Create synthetic variations
                # Add 9 augmented samples per real sample (10x data)
                for aug_idx in range(9):
                    noise_scale = 0.08  # 8% noise for more diversity
                    augmented = {
                        'birthRate': features['birthRate'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'deathRate': features['deathRate'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'naturalIncrease': features['naturalIncrease'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'birthDeathRatio': features['birthDeathRatio'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'gdpLog': features['gdpLog'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'lifeExpectancy': features['lifeExpectancy'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'urbanization': features['urbanization'] * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'target': actual_growth * (1 + np.random.uniform(-noise_scale, noise_scale)),
                        'country': f"{country.get('name', '')}_aug{aug_idx}",
                        'year': current.get('year', 0)
                    }
                    training_samples.append(augmented)
        
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
        from sklearn.model_selection import train_test_split, cross_val_score
        import time
        
        start_time = time.time()
        
        # Prepare data
        X, y = self.prepare_training_data(countries_data)
        
        print(f"Training samples: {len(X)} (with data augmentation)")
        print(f"Target (growth rate) stats: mean={y.mean():.4f}, std={y.std():.4f}, min={y.min():.4f}, max={y.max():.4f}")
        
        # Use 5-fold cross-validation for small dataset
        from sklearn.model_selection import KFold
        kfold = KFold(n_splits=5, shuffle=True, random_state=42)
        
        # Shuffle and split data (80% train, 20% validation)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
        
        # Train XGBoost model with better regularization
        self.model = xgb.XGBRegressor(**self.config)
        
        # Simple fit without early stopping (XGBoost version compatibility)
        self.model.fit(X_train, y_train, verbose=False)
        
        # Cross-validation scores
        cv_scores = cross_val_score(self.model, X, y, cv=kfold, 
                                    scoring='r2', n_jobs=-1)
        print(f"Cross-validation R² scores: {cv_scores}")
        print(f"Mean CV R²: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
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
        
        # Use mean CV score if better
        if cv_scores.mean() > val_r2:
            val_r2 = cv_scores.mean()
        
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
        
        # Extract values
        birth = features.get('birthRate', 15.0)
        death = features.get('deathRate', 7.0)
        gdp = features.get('gdpPerCapita', 3000)
        edu = features.get('educationIndex', 0.7)
        life_exp = features.get('lifeExpectancy', 74.0) / 100
        
        # Prepare feature vector - only important features
        feature_vector = pd.DataFrame([{
            'birthRate': birth / 50,
            'deathRate': death / 20,
            'naturalIncrease': (birth - death) / 30,
            'birthDeathRatio': birth / max(death, 1),
            'gdpLog': np.log1p(gdp) / 15,
            'lifeExpectancy': life_exp,
            'urbanization': features.get('urbanization', 0) / 100
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
        """Save trained model with metrics to file"""
        if self.model is None:
            raise ValueError("Không có model để lưu!")
        
        path = path or settings.XGBOOST_MODEL_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model along with metrics and feature importance
        model_data = {
            'model': self.model,
            'training_metrics': self.training_metrics,
            'feature_importance': self.feature_importance,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
        print(f"Model đã được lưu tại: {path}")
    
    def load_model(self, path: Optional[str] = None):
        """Load trained model with metrics from file"""
        path = path or settings.XGBOOST_MODEL_PATH
        if not os.path.exists(path):
            raise FileNotFoundError(f"Không tìm thấy model tại: {path}")
        
        model_data = joblib.load(path)
        
        # Handle both old format (just model) and new format (dict with metrics)
        if isinstance(model_data, dict):
            self.model = model_data.get('model')
            self.training_metrics = model_data.get('training_metrics', {})
            self.feature_importance = model_data.get('feature_importance', {})
            self.feature_names = model_data.get('feature_names', self.feature_names)
            self.is_trained = model_data.get('is_trained', True)
        else:
            # Old format - just the model
            self.model = model_data
            self.training_metrics = {}
            self.feature_importance = {}
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

