# AI Payment Risk Investigator

A production-quality, student-friendly AI/ML platform designed for payment anomaly risk scoring, evidence gathering, and autonomous agent investigation. Built for the Razorpay AI Builder / AI Risk Manager challenge.

---

## 1. Problem Statement
Payment platforms must evaluate millions of transaction attempts per second to detect fraudulent or risky activities. Traditional static rule engines suffer from high maintenance overhead and high false-positive rates, while relying entirely on Large Language Models (LLMs) for raw transaction scoring introduces severe latency, high cost, and hallucination risks.

---

## 2. The Solution
The **AI Payment Risk Investigator** solves this problem using a hybrid defensive architecture:
1. **Machine Learning Engine**: High-speed, deterministic ML model (XGBoost / Random Forest) scores raw feature inputs in milliseconds to compute exact risk probabilities (`LOW`, `MEDIUM`, `HIGH`).
2. **Deterministic Tooling**: Standard Python tools extract customer history, merchant stats, velocity spikes, device activity, geographic consistency, and recent related transactions.
3. **Autonomous Investigation Agent**: Triggers automatically on `HIGH` risk cases to dynamically plan tool execution (`Planner`), run tools (`Tool Registry`), gather evidence (`Evidence Aggregator`), and generate structured investigation reports with recommended actions (`APPROVE`, `MONITOR`, `MANUAL_REVIEW`).
4. **Optional LLM Integration**: Enhances report narratives when an API key is available, but seamlessly falls back to a deterministic rules engine when offline.

---

## 3. Key Features
- **Non-Linear Synthetic Data Pipeline**: Realistic 25,000 transaction dataset generator with complex interaction features (e.g., ATO velocity + device novelty, geo mismatch + high amount) and noise.
- **Explainable ML Scoring**: Clear risk signal attribution (e.g. amount deviation, geographic mismatch, velocity spikes).
- **Dynamic Bounded Agent**: Tool-calling planner executing up to `MAX_TOOL_CALLS = 4` with early stopping and step-by-step audit logs.
- **Full-Stack Dashboard**: React + Vite frontend dashboard displaying real-time metrics, transaction analysis, preset demos, and audit trails.
- **RESTful API**: FastAPI backend powering health checks, transactions, investigations, and analytics.
- **Automated Test Suite**: 100% passing pytest suite (13/13 tests) validating API endpoints, ML predictions, dynamic agent tool selection, and fallbacks.

---

## 4. Architecture

```mermaid
flowchart TD
    A[Transaction Payload] --> B[FastAPI Backend Engine]
    B --> C[Feature Engineering & Preprocessor]
    C --> D[ML Risk Model: XGBoost]
    D --> E{Risk Score Classification}
    E -->|Low Risk < 0.30| F[APPROVE]
    E -->|Medium Risk 0.30-0.69| G[MONITOR]
    E -->|High Risk >= 0.70| H[Trigger AI Investigation Agent]
    
    subgraph Autonomous Dynamic Agent Loop (Max 4 Calls)
        H --> Planner[Signal & Evidence Planner]
        Planner --> Registry{Tool Registry}
        Registry --> Tool1[Customer History Tool]
        Registry --> Tool2[Merchant Statistics Tool]
        Registry --> Tool3[Velocity Analysis Tool]
        Registry --> Tool4[Device Activity Tool]
        Registry --> Tool5[Geo Consistency Tool]
        Registry --> Tool6[Recent Related Txns Tool]
        
        Tool1 --> Agg[Evidence Aggregator & Audit Logger]
        Tool2 --> Agg
        Tool3 --> Agg
        Tool4 --> Agg
        Tool5 --> Agg
        Tool6 --> Agg
        
        Agg --> Planner
    end

    Agg --> O[Investigation Report Generator]
    O --> P[MANUAL_REVIEW Recommendation]
    P --> Q[SQLite / PostgreSQL Audit Log]
```

---

## 5. Technology Stack
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Uvicorn
- **Machine Learning**: pandas, numpy, scikit-learn, joblib, XGBoost
- **Agent Framework**: Custom lightweight tool-calling agent orchestrator with Planner, Tool Registry, Bounded Execution Loop, and optional OpenAI LLM enhancement
- **Frontend**: React 18, Vite, Tailwind CSS
- **Database**: SQLite (default), PostgreSQL compatible
- **Testing**: pytest, FastAPI TestClient
- **Containerization**: Docker, docker-compose

---

## 6. Actual Evaluation Results (Measured on Held-out 5,000 Test Set)

The following metrics were calculated by running `python ml/evaluate.py`:

| Metric | Logistic Regression | Random Forest | XGBoost (Serving Model) |
|---|---|---|---|
| **Accuracy** | 87.86% | 87.84% | **87.92%** |
| **Precision** | 68.95% | 68.37% | **69.54%** |
| **Recall** | 46.76% | 47.61% | **46.39%** |
| **F1 Score** | 0.5573 | 0.5613 | **0.5565** |
| **ROC-AUC** | 0.7435 | 0.7439 | **0.7512** |
| **False Positive Rate** | 4.11% | 4.30% | **3.97%** |
| **Est. FP Business Cost ($50/unit)** | $8,600.00 | $9,000.00 | **$8,300.00** |

---

## 7. Installation & Quick Start

### 7.1 Local Development Setup

1. **Clone repository and set up environment**:
   ```bash
   git clone https://github.com/your-username/ai-payment-risk-investigator.git
   cd ai-payment-risk-investigator
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Generate Synthetic Data**:
   ```bash
   python ml/generate_dataset.py
   ```

3. **Train ML Models**:
   ```bash
   python ml/train.py
   ```

4. **Run Model Evaluation**:
   ```bash
   python ml/evaluate.py
   ```

5. **Run Automated Test Suite**:
   ```bash
   pytest -v
   ```

6. **Start FastAPI Backend**:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

7. **Start Frontend Dashboard**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 8. Docker Deployment

To run using Docker Compose:
```bash
docker-compose up --build
```

---

## 9. API Reference Summary

- `GET /health` : Backend health check and LLM status.
- `POST /api/v1/transactions/analyze` : Evaluates payload using ML model.
- `GET /api/v1/transactions/{transaction_id}` : Retrieves transaction scoring details.
- `POST /api/v1/investigations/{transaction_id}` : Triggers AI agent investigation for high-risk transactions.
- `GET /api/v1/audit` : Retrieves system audit logs.
- `GET /api/v1/analytics/summary` : Returns high-level metrics for dashboard cards.

---

## 10. Disclaimer
This project uses synthetic data only and is designed purely for educational, student challenge, and technical demonstration purposes. It does not execute real financial payments or integrate with real banking rails.
