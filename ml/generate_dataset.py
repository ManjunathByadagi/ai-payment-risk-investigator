import numpy as np
import pandas as pd
import os
import random
from datetime import datetime, timedelta, timezone

def generate_synthetic_transactions(num_records: int = 25000, seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    random.seed(seed)
    
    countries = ["IN", "US", "GB", "AE", "SG", "CA", "DE", "FR", "JP", "BR"]
    high_risk_countries = ["XX", "YY", "ZZ", "BR", "AE"]
    
    num_customers = 3500
    num_merchants = 900
    num_devices = 4500
    
    customers = [f"CUST_{i:05d}" for i in range(1, num_customers + 1)]
    merchants = [f"MERCH_{i:04d}" for i in range(1, num_merchants + 1)]
    devices = [f"DEV_{i:05d}" for i in range(1, num_devices + 1)]
    
    # Pre-assign realistic customer profiles
    customer_profiles = {}
    for c in customers:
        is_frequent_traveler = np.random.rand() < 0.15
        is_high_net_worth = np.random.rand() < 0.10
        base_avg = float(np.random.exponential(scale=500 if is_high_net_worth else 120) + 15)
        
        customer_profiles[c] = {
            "home_country": np.random.choice(countries, p=[0.52, 0.18, 0.08, 0.05, 0.05, 0.04, 0.03, 0.02, 0.02, 0.01]),
            "primary_device": np.random.choice(devices),
            "avg_amount": round(base_avg, 2),
            "account_age_days": int(np.random.randint(1, 1200)),
            "is_frequent_traveler": is_frequent_traveler,
            "is_high_net_worth": is_high_net_worth,
            "risk_tolerance": float(np.random.uniform(0.1, 0.9))
        }
        
    merchant_profiles = {}
    for m in merchants:
        merchant_profiles[m] = {
            "risk_score": round(float(np.clip(np.random.beta(a=0.5, b=6.0), 0.01, 0.95)), 4),
            "category": np.random.choice(["retail", "travel", "digital_goods", "crypto_gaming", "luxury"])
        }

    records = []
    start_time = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    for i in range(1, num_records + 1):
        txn_id = f"TXN_{i:07d}"
        cust_id = np.random.choice(customers)
        cust_prof = customer_profiles[cust_id]
        merch_id = np.random.choice(merchants)
        merch_prof = merchant_profiles[merch_id]
        
        # Determine archetype scenario:
        # 1. Normal routine transaction (75%)
        # 2. Legitimate anomaly e.g. legitimate travel, luxury purchase, new device upgrade (13%)
        # 3. Fraud / Suspicious attack scenario (12%)
        scenario_roll = np.random.rand()
        
        if scenario_roll < 0.75:
            # Routine legitimate transaction
            amount = round(float(np.clip(np.random.lognormal(mean=np.log(cust_prof["avg_amount"]), sigma=0.4), 3.0, cust_prof["avg_amount"] * 2.8)), 2)
            txn_country = cust_prof["home_country"]
            device_id = cust_prof["primary_device"]
            device_new = 0
            txns_last_10m = int(np.random.choice([0, 1], p=[0.92, 0.08]))
            txns_last_1h = int(txns_last_10m + np.random.choice([0, 1, 2], p=[0.85, 0.12, 0.03]))
            txns_last_24h = int(txns_last_1h + np.random.choice([0, 1, 2, 3], p=[0.70, 0.20, 0.08, 0.02]))
            failed_txns_last_24h = int(np.random.choice([0, 1], p=[0.94, 0.06]))
            ip_risk = round(float(np.random.uniform(0.01, 0.25)), 4)
            unusual_time = 1 if np.random.rand() < 0.10 else 0
            cust_prev_risk = int(np.random.choice([0, 1], p=[0.92, 0.08]))
            is_suspicious_base = 0
            
        elif scenario_roll < 0.88:
            # Legitimate anomaly scenario (Benign noise / benign edge cases)
            anomaly_type = np.random.choice(["travel", "device_upgrade", "big_purchase"])
            if anomaly_type == "travel" and cust_prof["is_frequent_traveler"]:
                txn_country = np.random.choice([c for c in countries if c != cust_prof["home_country"]])
                device_id = cust_prof["primary_device"]
                device_new = 0
                amount = round(float(cust_prof["avg_amount"] * np.random.uniform(1.2, 3.5)), 2)
            elif anomaly_type == "device_upgrade":
                txn_country = cust_prof["home_country"]
                device_id = np.random.choice(devices)
                device_new = 1
                amount = round(float(cust_prof["avg_amount"] * np.random.uniform(0.8, 2.0)), 2)
            else: # big purchase
                txn_country = cust_prof["home_country"]
                device_id = cust_prof["primary_device"]
                device_new = 0
                amount = round(float(cust_prof["avg_amount"] * np.random.uniform(3.5, 7.0)), 2)
                
            txns_last_10m = int(np.random.choice([0, 1, 2], p=[0.80, 0.15, 0.05]))
            txns_last_1h = int(txns_last_10m + np.random.choice([0, 1, 2], p=[0.75, 0.20, 0.05]))
            txns_last_24h = int(txns_last_1h + np.random.choice([1, 2, 4], p=[0.60, 0.30, 0.10]))
            failed_txns_last_24h = int(np.random.choice([0, 1, 2], p=[0.80, 0.15, 0.05]))
            ip_risk = round(float(np.random.uniform(0.10, 0.45)), 4)
            unusual_time = 1 if np.random.rand() < 0.30 else 0
            cust_prev_risk = int(np.random.choice([0, 1, 2], p=[0.85, 0.10, 0.05]))
            is_suspicious_base = 0

        else:
            # Fraud Attack Scenario (Targeted anomaly)
            attack_type = np.random.choice(["account_takeover", "card_testing_velocity", "cross_border_bot"])
            if attack_type == "account_takeover":
                device_id = np.random.choice(devices)
                device_new = 1
                txn_country = np.random.choice(high_risk_countries)
                amount = round(float(cust_prof["avg_amount"] * np.random.uniform(5.0, 16.0) + 800), 2)
                txns_last_10m = int(np.random.randint(2, 6))
                txns_last_1h = int(txns_last_10m + np.random.randint(3, 8))
                txns_last_24h = int(txns_last_1h + np.random.randint(4, 12))
                failed_txns_last_24h = int(np.random.randint(1, 4))
                ip_risk = round(float(np.random.uniform(0.65, 0.99)), 4)
            elif attack_type == "card_testing_velocity":
                device_id = np.random.choice(devices)
                device_new = 1 if np.random.rand() < 0.7 else 0
                txn_country = cust_prof["home_country"]
                amount = round(float(np.random.uniform(1.0, 25.0)), 2) # Small test amounts rapidly
                txns_last_10m = int(np.random.randint(4, 9))
                txns_last_1h = int(txns_last_10m + np.random.randint(6, 15))
                txns_last_24h = int(txns_last_1h + np.random.randint(10, 25))
                failed_txns_last_24h = int(np.random.randint(2, 6))
                ip_risk = round(float(np.random.uniform(0.55, 0.95)), 4)
            else: # cross_border_bot
                device_id = np.random.choice(devices)
                device_new = 1
                txn_country = np.random.choice(high_risk_countries)
                amount = round(float(cust_prof["avg_amount"] * np.random.uniform(2.5, 8.0)), 2)
                txns_last_10m = int(np.random.randint(1, 4))
                txns_last_1h = int(txns_last_10m + np.random.randint(2, 6))
                txns_last_24h = int(txns_last_1h + np.random.randint(3, 10))
                failed_txns_last_24h = int(np.random.randint(1, 4))
                ip_risk = round(float(np.random.uniform(0.70, 0.98)), 4)

            unusual_time = 1 if np.random.rand() < 0.70 else 0
            cust_prev_risk = int(np.random.choice([0, 1, 2, 3], p=[0.4, 0.3, 0.2, 0.1]))
            is_suspicious_base = 1

        geo_mismatch = 1 if txn_country != cust_prof["home_country"] else 0
        amount_dev = round(float(amount / (cust_prof["avg_amount"] + 1e-5)), 4)
        velocity_score = round(float((txns_last_10m * 3.0 + txns_last_1h * 1.5 + txns_last_24h * 0.5) / 10.0), 4)

        # Compute complex non-linear probability of risk with interactive conditions
        # Non-linear term 1: High velocity + new device (Classic credential stuffing / ATO)
        ato_term = 1.0 / (1.0 + np.exp(-3.0 * (velocity_score * device_new - 1.2)))
        
        # Non-linear term 2: Geo mismatch * High Amount Dev (Unusual international drain)
        geo_amount_term = 1.0 / (1.0 + np.exp(-2.5 * (geo_mismatch * np.log1p(amount_dev) - 2.0)))
        
        # Non-linear term 3: Failed transactions + High IP risk + Digital goods merchant
        digital_merchant_flag = 1.0 if merch_prof["category"] in ["digital_goods", "crypto_gaming"] else 0.5
        failed_ip_term = (failed_txns_last_24h >= 2) * (ip_risk > 0.6) * digital_merchant_flag * 0.35

        # Account age protective buffer (Older accounts less prone to sudden false flags unless ATO)
        account_age_decay = np.exp(-cust_prof["account_age_days"] / 365.0)

        raw_prob = (
            0.35 * ato_term +
            0.30 * geo_amount_term +
            0.20 * failed_ip_term +
            0.15 * (merch_prof["risk_score"] > 0.4) +
            0.10 * account_age_decay +
            0.10 * (cust_prev_risk > 1)
        )

        # Baseline scenario influence
        combined_prob = 0.65 * raw_prob + 0.35 * is_suspicious_base
        
        # Add realistic noise/stochasticity (7% stochastic flip bound)
        final_prob = float(np.clip(combined_prob, 0.02, 0.95))
        is_suspicious = int(np.random.rand() < final_prob)
        if np.random.rand() < 0.07:
            is_suspicious = 1 - is_suspicious

        time_offset = timedelta(minutes=i * 2 + random.randint(-30, 30))
        timestamp = (start_time + time_offset).isoformat()

        records.append({
            "transaction_id": txn_id,
            "customer_id": cust_id,
            "merchant_id": merch_id,
            "amount": amount,
            "currency": "INR",
            "timestamp": timestamp,
            "customer_country": cust_prof["home_country"],
            "transaction_country": txn_country,
            "device_id": device_id,
            "device_new": device_new,
            "customer_account_age_days": cust_prof["account_age_days"],
            "transactions_last_10_minutes": txns_last_10m,
            "transactions_last_1_hour": txns_last_1h,
            "transactions_last_24_hours": txns_last_24h,
            "average_customer_amount": cust_prof["avg_amount"],
            "amount_deviation": amount_dev,
            "merchant_risk_score": merch_prof["risk_score"],
            "customer_previous_risk_count": cust_prev_risk,
            "failed_transactions_last_24_hours": failed_txns_last_24h,
            "ip_risk_score": ip_risk,
            "unusual_time": unusual_time,
            "geographic_mismatch": geo_mismatch,
            "velocity_score": velocity_score,
            "label": is_suspicious
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/sample", exist_ok=True)
    
    print("Generating 25,000 synthetic payment transactions with non-linear risk interactions...")
    df = generate_synthetic_transactions(num_records=25000, seed=42)
    
    raw_path = "data/raw/synthetic_transactions.csv"
    df.to_csv(raw_path, index=False)
    print(f"Saved dataset to {raw_path}")
    print(f"Total transactions: {len(df)}")
    print(f"Suspicious transactions: {df['label'].sum()} ({df['label'].mean()*100:.2f}%)")
    
    sample_path = "data/sample/sample_transactions.json"
    df.head(10).to_json(sample_path, orient="records", indent=2)
    print(f"Saved sample transactions to {sample_path}")
