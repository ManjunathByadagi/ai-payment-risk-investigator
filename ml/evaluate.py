import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

def evaluate_all_models():
    os.makedirs("evaluation/results", exist_ok=True)

    X_test = np.load("data/processed/X_test.npy")
    y_test = np.load("data/processed/y_test.npy")

    models = {
        "LogisticRegression": joblib.load("ml/model/logistic_regression.joblib"),
        "RandomForest": joblib.load("ml/model/random_forest.joblib"),
        "XGBoost": joblib.load("ml/model/xgboost_model.joblib")
    }

    false_positive_cost_unit = 50.0  # Configurable unit cost per false positive in USD/INR
    results = {}

    for name, model in models.items():
        y_probs = model.predict_proba(X_test)[:, 1]
        y_preds = (y_probs >= 0.50).astype(int)

        acc = float(accuracy_score(y_test, y_preds))
        prec = float(precision_score(y_test, y_preds, zero_division=0))
        rec = float(recall_score(y_test, y_preds, zero_division=0))
        f1 = float(f1_score(y_test, y_preds, zero_division=0))
        roc_auc = float(roc_auc_score(y_test, y_probs))

        cm = confusion_matrix(y_test, y_preds)
        tn, fp, fn, tp = cm.ravel()

        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0
        est_fp_cost = float(fp * false_positive_cost_unit)

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": {
                "true_negative": int(tn),
                "false_positive": int(fp),
                "false_negative": int(fn),
                "true_positive": int(tp)
            },
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
            "estimated_false_positive_cost": est_fp_cost,
            "cost_per_fp_unit": false_positive_cost_unit
        }

    results_file = "evaluation/results/evaluation_metrics.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Evaluation completed. Metrics written to {results_file}")
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    evaluate_all_models()
