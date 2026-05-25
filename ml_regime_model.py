import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

class RegimeForecastingModel:
    def __init__(self, model_path="regime_model.pkl"):
        self.model_path = model_path
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)

    def generate_historical_data(self, days=1000):
        np.random.seed(42)
        gex = np.random.normal(loc=0.5, scale=2.0, size=days) 
        vix = np.clip(np.random.normal(loc=18, scale=5.0, size=days), 10, 80) 
        sentiment = np.random.uniform(-1, 1, size=days)
        
        # Sprint 2: Historical Memory Features
        vix_velocity = np.random.normal(loc=0, scale=2.0, size=days) # Daily change in VIX
        prev_regime = np.random.choice([0, 1], size=days, p=[0.7, 0.3]) # T-1 Regime
        
        df = pd.DataFrame({
            'net_gex': gex, 'vix': vix, 'macro_sentiment': sentiment,
            'vix_velocity': vix_velocity, 'prev_regime': prev_regime
        })
        
        # Target logic now respects inertia: Harder to break out of chop if yesterday was chop
        conditions = (df['net_gex'] < 0) & (df['vix'] > 20) & (df['prev_regime'] == 1) | (df['vix_velocity'] > 2)
        df['regime_target'] = np.where(conditions, 1, 0)
        
        return df

    def train_model(self, df):
        X = df[['net_gex', 'vix', 'macro_sentiment', 'vix_velocity', 'prev_regime']]
        y = df['regime_target']
        self.model.fit(X, y)
        joblib.dump(self.model, self.model_path)
        print("Production ML Model trained and saved with Regime Memory capabilities.")

    def predict_today(self, features_dict):
        model = joblib.load(self.model_path)
        features = pd.DataFrame([features_dict])
        return round(model.predict_proba(features)[0][1] * 100, 2)

if __name__ == "__main__":
    ml = RegimeForecastingModel()
    ml.train_model(ml.generate_historical_data())