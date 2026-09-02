# Model Evaluation & Performance Report

## 1. Methodology
- **Synthetic Dataset**: 25,000 synthetic transaction records generated with complex non-linear risk interactions, conditional probabilities, and realistic noise (~16.35% positive class balance).
- **Split Strategy**: 80/20 Stratified Train/Test split (20,000 training, 5,000 test records).
- **Random Seed**: Fixed seed `42` for exact reproducibility.

## 2. Actual Measured Results

| Model Metric | Logistic Regression | Random Forest | XGBoost (Primary Serving) |
|---|---|---|---|
| **Accuracy** | 87.86% | 87.84% | **87.92%** |
| **Precision** | 68.95% | 68.37% | **69.54%** |
| **Recall** | 46.76% | 47.61% | **46.39%** |
| **F1 Score** | 0.5573 | 0.5613 | **0.5565** |
| **ROC-AUC** | 0.7435 | 0.7439 | **0.7512** |
| **False Positive Rate (FPR)** | 4.11% | 4.30% | **3.97%** |
| **False Negative Rate (FNR)** | 53.24% | 52.39% | **53.61%** |
| **Est. FP Business Cost ($50/unit)** | $8,600.00 | $9,000.00 | **$8,300.00** |

## 3. Confusion Matrix Breakdown (XGBoost Test Set = 5,000 items)

- **True Negatives (TN)**: 4,017
- **False Positives (FP)**: 166
- **False Negatives (FN)**: 438
- **True Positives (TP)**: 379

## 4. Key Business Takeaways
1. **Realistic Fraud Modeling**: Non-linear interactions prevent simple linear rule overfitting, producing realistic precision (~70%) and recall (~46%) metrics characteristic of production fraud detection pipelines.
2. **False Positive Cost Calibration**: False positive cost assumes an average customer support review friction cost of $50 per false block ($8,300 FP cost on held-out test data).
