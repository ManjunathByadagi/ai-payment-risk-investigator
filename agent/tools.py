import pandas as pd
import numpy as np
import os
from typing import Dict, Any, List, Optional

class RiskTools:
    def __init__(self, data_path: str = "data/raw/synthetic_transactions.csv"):
        self.data_path = data_path
        self._df = None

    def _get_df(self) -> pd.DataFrame:
        if self._df is None:
            if os.path.exists(self.data_path):
                self._df = pd.read_csv(self.data_path)
            else:
                self._df = pd.DataFrame()
        return self._df

    def get_customer_history(self, customer_id: str, current_txn: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        df = self._get_df()
        benchmark_amount = round(float(current_txn.get("average_customer_amount", 150.0)), 2) if current_txn else None

        if df.empty or customer_id not in df["customer_id"].values:
            return {
                "customer_id": customer_id,
                "found": False,
                "average_amount": 150.0,
                "declared_benchmark_amount": benchmark_amount,
                "recent_transaction_count": 1,
                "previous_risk_flags": 0,
                "home_country": "IN",
                "account_age_days": 30
            }
        
        cust_df = df[df["customer_id"] == customer_id]
        return {
            "customer_id": customer_id,
            "found": True,
            "total_historical_transactions": int(len(cust_df)),
            "average_amount": round(float(cust_df["amount"].mean()), 2),
            "declared_benchmark_amount": benchmark_amount,
            "max_amount": round(float(cust_df["amount"].max()), 2),
            "previous_risk_flags": int(cust_df["label"].sum()),
            "home_country": str(cust_df["customer_country"].iloc[0]),
            "account_age_days": int(cust_df["customer_account_age_days"].iloc[0])
        }

    def get_merchant_statistics(self, merchant_id: str) -> Dict[str, Any]:
        df = self._get_df()
        if df.empty or merchant_id not in df["merchant_id"].values:
            return {
                "merchant_id": merchant_id,
                "found": False,
                "risk_score": 0.05,
                "total_transactions": 50,
                "dispute_rate": 0.01
            }
        
        merch_df = df[df["merchant_id"] == merchant_id]
        total_txns = len(merch_df)
        risky_txns = int(merch_df["label"].sum())
        dispute_rate = round(float(risky_txns / total_txns), 4) if total_txns > 0 else 0.0
        
        return {
            "merchant_id": merchant_id,
            "found": True,
            "total_transactions": total_txns,
            "merchant_risk_score": round(float(merch_df["merchant_risk_score"].iloc[0]), 4),
            "dispute_rate": dispute_rate
        }

    def get_transaction_velocity(self, customer_id: str, current_txn: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        txns_10m = current_txn.get("transactions_last_10_minutes", 1) if current_txn else 1
        txns_1h = current_txn.get("transactions_last_1_hour", 1) if current_txn else 1
        txns_24h = current_txn.get("transactions_last_24_hours", 1) if current_txn else 1
        failed_24h = current_txn.get("failed_transactions_last_24_hours", 0) if current_txn else 0
        
        velocity_score = round(float((txns_10m * 3.0 + txns_1h * 1.5 + txns_24h * 0.5) / 10.0), 4)
        
        return {
            "customer_id": customer_id,
            "transactions_last_10_minutes": txns_10m,
            "transactions_last_1_hour": txns_1h,
            "transactions_last_24_hours": txns_24h,
            "failed_transactions_last_24_hours": failed_24h,
            "velocity_score": velocity_score,
            "velocity_status": "HIGH" if velocity_score > 1.2 else "NORMAL"
        }

    def get_device_activity(self, device_id: str, current_txn: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        is_new = current_txn.get("device_new", 0) == 1 if current_txn else False
        ip_risk = current_txn.get("ip_risk_score", 0.1) if current_txn else 0.1
        
        return {
            "device_id": device_id,
            "is_new_device": is_new,
            "ip_risk_score": ip_risk,
            "device_risk_level": "HIGH" if (is_new and ip_risk > 0.5) else ("MEDIUM" if is_new else "LOW")
        }

    def check_geographic_consistency(self, customer_id: str, transaction_country: str, current_txn: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        home_country = current_txn.get("customer_country", "IN") if current_txn else "IN"
        mismatch = transaction_country != home_country
        
        return {
            "customer_id": customer_id,
            "home_country": home_country,
            "transaction_country": transaction_country,
            "geographic_mismatch": mismatch,
            "geo_risk_level": "HIGH" if mismatch else "LOW"
        }

    def get_recent_related_transactions(self, customer_id: str, merchant_id: str) -> Dict[str, Any]:
        df = self._get_df()
        if df.empty:
            return {"customer_id": customer_id, "merchant_id": merchant_id, "related_count": 0}
        
        related = df[(df["customer_id"] == customer_id) & (df["merchant_id"] == merchant_id)]
        return {
            "customer_id": customer_id,
            "merchant_id": merchant_id,
            "related_count": len(related),
            "recent_flagged_count": int(related["label"].sum()) if not related.empty else 0
        }
