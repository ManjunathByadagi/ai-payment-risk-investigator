# Technical Interview Preparation Guide

This guide equips students to defend the technical architecture during engineering interviews.

---

## 1. Machine Learning & Data Science

### Q: Why did you choose supervised ML over an LLM for risk scoring?
**A**: Risk scoring requires low latency (<20ms), deterministic scoring consistency, high throughput, and cost efficiency. Supervised models (like XGBoost or Random Forests) excel at tabular numerical risk pattern detection, whereas LLMs are suited for narrative summarization and unstructured reasoning.

### Q: Why prioritize Precision and Recall over Accuracy?
**A**: Payment risk datasets are highly imbalanced (~19% positive in our dataset, <1% in production). A naive model predicting all normal transactions achieves ~81%+ accuracy while missing 100% of risky transactions. Precision measures how many flagged cases are truly risky, while Recall measures how many total risky transactions were caught.

### Q: How did you prevent data leakage?
**A**: The dataset split (80/20 train/test) was performed *before* any feature scaling or transformation. All preprocessor scalers were fitted strictly on the training set and applied to the test set using `.transform()`. Target labels were completely excluded from the feature inputs.

---

## 2. Agentic AI & Systems Design

### Q: How do you prevent LLM hallucinations in risk reports?
**A**: 
1. The LLM is restricted to narrative formatting; numerical risk probabilities are calculated by the ML model.
2. The agent prompt grounds the LLM strictly within JSON evidence retrieved by deterministic tools.
3. If an LLM API error occurs or the API key is missing, the system seamlessly falls back to a deterministic python-based evidence compiler.

### Q: How does the system handle high transaction throughput?
**A**: Feature extraction and model scoring run in memory in FastAPI in milliseconds. The heavy agent investigation workflow is executed asynchronously only for HIGH risk transactions (~10-15% of traffic), keeping system response times fast.

---

## 3. Backend & Full-Stack Architecture

### Q: Why use FastAPI and Pydantic?
**A**: FastAPI offers high performance (built on Starlette & ASGI), automatic OpenAPI documentation (`/docs`), type checking, and native async support. Pydantic ensures strong payload validation.

### Q: How is database migration handled between SQLite and PostgreSQL?
**A**: Through SQLAlchemy ORM abstraction. By changing the `DATABASE_URL` environment variable from `sqlite:///...` to `postgresql://...`, the backend connects to PostgreSQL without requiring application code changes.
