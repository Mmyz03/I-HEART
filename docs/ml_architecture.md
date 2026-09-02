# Machine Learning Architecture

## 1. High-Level Architectural Flow

The system employs a **Unified Patient Input Architecture** that branches into **two independent Machine Learning pipelines** before re-converging into a unified risk dashboard:

```mermaid
graph TD
    A[User / Healthcare Practitioner] -->|Single Form Input| B[Unified Patient Profile]
    B -->|POST /api/analyze| C[FastAPI Gateway]
    
    subgraph Diabetes Subsystem
        C --> D1[Diabetes Feature Mapper]
        D1 --> E1[Fitted ColumnTransformer]
        E1 --> F1[Trained Diabetes Classifier]
        F1 --> G1[Diabetes Risk & Probability]
    end
    
    subgraph Cardiovascular Subsystem
        C --> D2[CVD Feature Mapper]
        D2 --> E2[Fitted ColumnTransformer]
        E2 --> F2[Trained CVD Classifier]
        F2 --> G2[CVD Risk & Probability]
    end
    
    G1 --> H[Unified Response Aggregator]
    G2 --> H
    H --> I[Unified Results Dashboard]
```

## 2. Core Architectural Principles

1. **Single Intake Contract**: The user enters patient information exactly once. There are no separate forms for diabetes and CVD.
2. **Strict Feature Isolation**: Each disease pipeline extracts and processes *only* the specific features required by its mathematical model.
3. **Reproducibility & Serialization**: Both pipelines use scikit-learn `Pipeline` and `ColumnTransformer` objects serialized via `joblib`, ensuring exact training-time preprocessing transforms are applied at inference time without duplicate code.
4. **Data Leakage Immunity**: Feature imputation, scaling, and categorical encoding are fitted strictly on training data splits.
5. **Calibrated Model Risk Estimates**: Models output probability scores (`predict_proba`) converted to standard clinical screening risk bands (`Low`, `Moderate`, `High`).
