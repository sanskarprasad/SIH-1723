import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
from pathlib import Path

class Predict:
    def __init__(self, feature_csv, model_dir="ml_models/models/backward"):
        """
        Initialize the Predict class and load pre-trained models and scalers.
        """
        self.feature_csv = feature_csv
        self.feature_scaler = MinMaxScaler()
        self.model_dir = Path.cwd() / model_dir

        # Load models and scalers dynamically
        self.models = {}
        self.scalers = {}
        self._load_models_and_scalers()

    def _load_models_and_scalers(self):
        """
        Load pre-trained models and scalers dynamically from the specified directory.
        """
        print("Loading models and scalers...")

        for model_file in self.model_dir.glob("xgboost_model_*.joblib"):
            target_name = model_file.stem.split("_", 2)[-1]
            self.models[target_name] = joblib.load(model_file)
            print(f"Loaded model: {target_name}")

        for scaler_file in self.model_dir.glob("target_scaler_*.joblib"):
            target_name = scaler_file.stem.split("_", 2)[-1]
            self.scalers[target_name] = joblib.load(scaler_file)
            print(f"Loaded scaler: {target_name}")

    def load_features(self):
        """
        Load the features from the CSV file and extract the last row.
        """
        print("Loading features...")
        df_features = pd.read_csv(self.feature_csv)
        self.features = df_features.iloc[-1:].values
        return self.features

    def scale_features(self):
        """
        Scale the input features using the feature scaler.
        """
        print("Scaling features...")
        self.features_scaled = self.feature_scaler.fit_transform(self.features)

    def make_predictions(self):
        """
        Make predictions using the pre-trained models.
        """
        print("Making predictions...")
        predictions = {}

        for target, model in self.models.items():
            scaled_prediction = model.predict(self.features_scaled)
            unscaled_prediction = self.scalers[target].inverse_transform(scaled_prediction.reshape(-1, 1)).flatten()[0]
            predictions[target] = unscaled_prediction
            print(f"Prediction for {target}: {unscaled_prediction}")

        return predictions

    def run_pipeline(self):
        """
        Run the entire prediction pipeline: load features, scale them, and make predictions.
        """
        print("Running prediction pipeline...")
        self.load_features()
        self.scale_features()
        predictions = self.make_predictions()
        return predictions

# Example usage:
if __name__ == "__main__":
    feature_csv_path = "data/processed/backward/BAR_TEMP_VAL0_X_test.csv"
    predictor = Predict(feature_csv=feature_csv_path)
    results = predictor.run_pipeline()
    print("Final Predictions:", results)
