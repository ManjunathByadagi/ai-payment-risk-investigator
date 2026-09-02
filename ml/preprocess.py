import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib
import os

FEATURE_COLUMNS = [
    "amount",
    "device_new",
    "customer_account_age_days",
    "transactions_last_10_minutes",
    "transactions_last_1_hour",
    "transactions_last_24_hours",
    "average_customer_amount",
    "amount_deviation",
    "merchant_risk_score",
    "customer_previous_risk_count",
    "failed_transactions_last_24_hours",
    "ip_risk_score",
    "unusual_time",
    "geographic_mismatch",
    "velocity_score"
]

NUMERICAL_FEATURES = [
    "amount",
    "customer_account_age_days",
    "transactions_last_10_minutes",
    "transactions_last_1_hour",
    "transactions_last_24_hours",
    "average_customer_amount",
    "amount_deviation",
    "merchant_risk_score",
    "customer_previous_risk_count",
    "failed_transactions_last_24_hours",
    "ip_risk_score",
    "velocity_score"
]

class Preprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_names = FEATURE_COLUMNS
        self.is_fitted = False

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        df_clean = df.copy()
        
        # Ensure calculated features exist
        if "amount_deviation" not in df_clean.columns:
            df_clean["amount_deviation"] = df_clean["amount"] / (df_clean["average_customer_amount"] + 1e-5)
        if "geographic_mismatch" not in df_clean.columns:
            df_clean["geographic_mismatch"] = (df_clean["transaction_country"] != df_clean["customer_country"]).astype(int)
        if "velocity_score" not in df_clean.columns:
            df_clean["velocity_score"] = (df_clean["transactions_last_10_minutes"] * 3.0 + 
                                          df_clean["transactions_last_1_hour"] * 1.5 + 
                                          df_clean["transactions_last_24_hours"] * 0.5) / 10.0

        # Extract numerical & binary features matrix
        X_num = df_clean[NUMERICAL_FEATURES].values
        X_scaled = self.scaler.fit_transform(X_num)
        
        # Combine scaled numerical with unchanged binary features
        binary_features = ["device_new", "unusual_time", "geographic_mismatch"]
        X_bin = df_clean[binary_features].values
        
        X_processed = np.hstack((X_scaled, X_bin))
        self.is_fitted = True
        return X_processed

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet.")
            
        df_clean = df.copy()
        if "amount_deviation" not in df_clean.columns:
            df_clean["amount_deviation"] = df_clean["amount"] / (df_clean["average_customer_amount"] + 1e-5)
        if "geographic_mismatch" not in df_clean.columns:
            df_clean["geographic_mismatch"] = (df_clean["transaction_country"] != df_clean["customer_country"]).astype(int)
        if "velocity_score" not in df_clean.columns:
            df_clean["velocity_score"] = (df_clean["transactions_last_10_minutes"] * 3.0 + 
                                          df_clean["transactions_last_1_hour"] * 1.5 + 
                                          df_clean["transactions_last_24_hours"] * 0.5) / 10.0

        X_num = df_clean[NUMERICAL_FEATURES].values
        X_scaled = self.scaler.transform(X_num)
        
        binary_features = ["device_new", "unusual_time", "geographic_mismatch"]
        X_bin = df_clean[binary_features].values
        
        return np.hstack((X_scaled, X_bin))

    def save(self, filepath: str):
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str):
        return joblib.load(filepath)
