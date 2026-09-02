# System Limitations & Future Scope

## 1. Known Limitations

1. **Synthetic Data Reliance**: The model is trained on synthetic data created with statistical distributions. Real-world payment fraud involves complex evolving attack patterns (e.g. distributed botnets, SIM swapping) not fully mirrored in synthetic data.
2. **Offline Velocity Metrics**: Velocity scores in the demo rely on provided transaction history payloads rather than live real-time Redis sliding window counters.
3. **Static Thresholds**: Risk thresholds (LOW < 0.30, HIGH >= 0.70) are currently fixed in environment settings rather than dynamically calibrated based on real-time fraud trends.

## 2. Recommended Future Enhancements

1. **Feature Store Integration**: Implement a real-time feature store (such as Feast) for low-latency state tracking.
2. **Model Concept Drift Monitoring**: Deploy automated Population Stability Index (PSI) tracking to detect model decay.
3. **Active Learning Feedback Loop**: Allow manual risk analysts to submit ground truth feedback from manual reviews back into the training pipeline.
