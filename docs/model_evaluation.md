# Model Evaluation & Comparison Report

## 1. Candidate Model Comparison (5-Fold Stratified Cross-Validation on Training Data)

### Diabetes Risk Classification
| Candidate Model | CV Accuracy | CV Precision | CV Recall | CV F1-Score | CV ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Selected)** | **0.7423** | **0.3481** | **0.7530** | **0.4761** | **0.8278** |
| Random Forest | 0.7709 | 0.3731 | 0.6949 | 0.4854 | 0.8204 |
| Gradient Boosting | 0.8625 | 0.6301 | 0.2826 | 0.3900 | 0.8236 |
| HistGradient Boosting | 0.7520 | 0.3556 | 0.7316 | 0.4785 | 0.8224 |

*Rationale for Selection:* In clinical screening, **Recall (Sensitivity)** and **ROC-AUC** are the decisive metrics to minimize False Negatives (missing high-risk diabetic individuals). Logistic Regression with balanced weighting achieved the highest CV ROC-AUC (0.8278) and top Recall (0.7530).

---

### Cardiovascular Disease (CVD) Risk Classification
| Candidate Model | CV Accuracy | CV Precision | CV Recall | CV F1-Score | CV ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression (Selected)** | **0.6858** | **0.5863** | **0.6850** | **0.6318** | **0.7497** |
| Random Forest | 0.6830 | 0.5875 | 0.6525 | 0.6183 | 0.7407 |
| Gradient Boosting | 0.6975 | 0.6513 | 0.4979 | 0.5643 | 0.7430 |
| HistGradient Boosting | 0.6835 | 0.5863 | 0.6647 | 0.6230 | 0.7430 |

*Rationale for Selection:* Logistic Regression achieved the highest CV ROC-AUC (0.7497) and highest Recall (0.6850), providing calibrated linear probability outputs well-suited for subsequent SHAP explainability.

---

## 2. Final Untouched Test Set Evaluation (6,000 Samples Each)

### Diabetes Final Model (`Logistic Regression`, `C=0.01`, `solver='liblinear'`)
- **Test Accuracy:** `0.7455`
- **Test Precision:** `0.3548`
- **Test Recall:** `0.7781`
- **Test F1-Score:** `0.4874`
- **Test ROC-AUC:** `0.8354`
- **Confusion Matrix:**
  ```
                 Predicted 0    Predicted 1
  Actual 0 (No)    3747           1320
  Actual 1 (Yes)   207            726
  ```

### Cardiovascular Disease Final Model (`Logistic Regression`, `C=0.1`, `solver='lbfgs'`)
- **Test Accuracy:** `0.6843`
- **Test Precision:** `0.5854`
- **Test Recall:** `0.6777`
- **Test F1-Score:** `0.6282`
- **Test ROC-AUC:** `0.7470`
- **Confusion Matrix:**
  ```
                 Predicted 0    Predicted 1
  Actual 0 (No)    2506           1133
  Actual 1 (Yes)   761            1600
  ```
