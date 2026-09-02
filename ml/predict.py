import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from ml.preprocess import Preprocessor, FEATURE_COLUMNS, NUMERICAL_FEATURES

class RiskPredictor:
    def __init__(self, model_path: str = "ml/model/risk_model.joblib", preprocessor_path: str = "ml/model/preprocessor.joblib"):
        if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
            # Fallback to train if missing
            from ml.train import train_and_save_models
            train_and_save_models()

        self.model = joblib.load(model_path)
        self.preprocessor = Preprocessor.load(preprocessor_path)

    def predict(self, txn_data: Dict[str, Any], low_threshold: float = 0.30, high_threshold: float = 0.70) -> Dict[str, Any]:
        df = pd.DataFrame([txn_data])

        defaults = {
            "device_new": 0,
            "customer_account_age_days": 30,
            "transactions_last_10_minutes": 0,
            "transactions_last_1_hour": 0,
            "transactions_last_24_hours": 0,
            "average_customer_amount": 150.0,
            "merchant_risk_score": 0.05,
            "customer_previous_risk_count": 0,
            "failed_transactions_last_24_hours": 0,
            "ip_risk_score": 0.1,
            "unusual_time": 0,
        }
        for column, default in defaults.items():
            if column not in df.columns:
                df[column] = pd.Series(default, index=df.index)
        
        # Calculate intermediate engineered features if not supplied
        if "amount_deviation" not in df.columns or pd.isna(df["amount_deviation"].iloc[0]):
            df["amount_deviation"] = df["amount"] / (df.get("average_customer_amount", df["amount"]) + 1e-5)
        if "geographic_mismatch" not in df.columns or pd.isna(df["geographic_mismatch"].iloc[0]):
            if "transaction_country" in df.columns and "customer_country" in df.columns:
                df["geographic_mismatch"] = (
                    df["transaction_country"].fillna("IN") != df["customer_country"].fillna("IN")
                ).astype(int)
            else:
                df["geographic_mismatch"] = pd.Series(0, index=df.index, dtype=int)
        if "velocity_score" not in df.columns or pd.isna(df["velocity_score"].iloc[0]):
            df["velocity_score"] = (
                df.get("transactions_last_10_minutes", 0) * 3.0 + 
                df.get("transactions_last_1_hour", 0) * 1.5 + 
                df.get("transactions_last_24_hours", 0) * 0.5
            ) / 10.0

        X_processed = self.preprocessor.transform(df)
        probabilities = np.asarray(self.model.predict_proba(X_processed))
        classes = list(getattr(self.model, "classes_", []))
        if 1 not in classes:
            raise ValueError("Risk model does not expose a positive class (1).")
        prob = float(probabilities[0, classes.index(1)])

        # Risk Classification
        if prob < low_threshold:
            risk_level = "LOW"
            recommended_action = "APPROVE"
        elif prob < high_threshold:
            risk_level = "MEDIUM"
            recommended_action = "MONITOR"
        else:
            risk_level = "HIGH"
            recommended_action = "MANUAL_REVIEW"

        # Feature signal calculation
        signals = self._extract_risk_signals(df.iloc[0], prob)

        return {
            "risk_probability": round(prob, 4),
            "risk_level": risk_level,
            "decision": recommended_action,
            "risk_signals": signals
        }

    def _extract_risk_signals(self, row: pd.Series, prob: float) -> List[Dict[str, Any]]:
        signals = []

        if row.get("amount_deviation", 1.0) > 3.0:
            signals.append({
                "signal": "amount_deviation",
                "severity": "high",
                "description": f"Transaction amount is {row.get('amount_deviation', 1.0):.1f}x higher than customer's historical average."
            })
        if row.get("device_new", 0) == 1:
            signals.append({
                "signal": "new_device",
                "severity": "medium",
                "description": "Transaction originated from an unrecognized new device."
            })
        if row.get("geographic_mismatch", 0) == 1:
            signals.append({
                "signal": "geographic_mismatch",
                "severity": "high",
                "description": f"Transaction country ({row.get('transaction_country')}) differs from registered home country ({row.get('customer_country')})."
            })
        if row.get("velocity_score", 0) > 1.0 or row.get("transactions_last_10_minutes", 0) >= 3:
            signals.append({
                "signal": "high_velocity",
                "severity": "high",
                "description": f"Abnormal transaction velocity: {row.get('transactions_last_10_minutes', 0)} attempts in last 10 minutes."
            })
        if row.get("failed_transactions_last_24_hours", 0) > 1:
            signals.append({
                "signal": "recent_failures",
                "severity": "medium",
                "description": f"Multiple failed transaction attempts ({row.get('failed_transactions_last_24_hours')} attempts) in past 24 hours."
            })
        if row.get("ip_risk_score", 0.0) > 0.6:
            signals.append({
                "signal": "high_ip_risk",
                "severity": "medium",
                "description": f"IP address risk score is elevated ({row.get('ip_risk_score'):.2f})."
            })
        if row.get("unusual_time", 0) == 1:
            signals.append({
                "signal": "unusual_time",
                "severity": "low",
                "description": "Transaction executed during off-peak historical user activity hours."
            })

        if not signals and prob >= 0.30:
            signals.append({
                "signal": "composite_risk",
                "severity": "low" if prob < 0.70 else "medium",
                "description": "Composite analytical risk scoring indicates anomalous behavior."
            })

        return signals
