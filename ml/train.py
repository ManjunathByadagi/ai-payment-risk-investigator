import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib
from ml.preprocess import Preprocessor, FEATURE_COLUMNS

def train_and_save_models():
    raw_data_path = "data/raw/synthetic_transactions.csv"
    if not os.path.exists(raw_data_path):
        from ml.generate_dataset import generate_synthetic_transactions
        print("Dataset not found. Generating synthetic dataset...")
        df = generate_synthetic_transactions(25000)
        os.makedirs("data/raw", exist_ok=True)
        df.to_csv(raw_data_path, index=False)
    else:
        df = pd.read_csv(raw_data_path)

    print(f"Loaded dataset with shape: {df.shape}")

    # Separate input features and target label to prevent data leakage
    X_df = df[FEATURE_COLUMNS + ["customer_country", "transaction_country"]].copy()
    y = df["label"].values

    # Stratified Train/Test Split
    X_train_df, X_test_df, y_train, y_test = train_test_split(
        X_df, y, test_size=0.20, random_state=42, stratify=y
    )

    # Fit Preprocessor on Train set only
    preprocessor = Preprocessor()
    X_train = preprocessor.fit_transform(X_train_df)
    X_test = preprocessor.transform(X_test_df)

    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("ml/model", exist_ok=True)

    preprocessor.save("ml/model/preprocessor.joblib")
    np.save("data/processed/X_train.npy", X_train)
    np.save("data/processed/X_test.npy", X_test)
    np.save("data/processed/y_train.npy", y_train)
    np.save("data/processed/y_test.npy", y_test)
    X_test_df.to_csv("data/processed/X_test_df.csv", index=False)

    print("Training Logistic Regression baseline...")
    lr_model = LogisticRegression(random_state=42, max_iter=1000)
    lr_model.fit(X_train, y_train)
    joblib.dump(lr_model, "ml/model/logistic_regression.joblib")

    print("Training Random Forest model...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    joblib.dump(rf_model, "ml/model/random_forest.joblib")

    print("Training XGBoost Classifier...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_model.fit(X_train, y_train)
    joblib.dump(xgb_model, "ml/model/xgboost_model.joblib")
    
    # Save the primary model (XGBoost) as the default serving model
    joblib.dump(xgb_model, "ml/model/risk_model.joblib")
    print("All models successfully trained and persisted in ml/model/")

if __name__ == "__main__":
    train_and_save_models()
