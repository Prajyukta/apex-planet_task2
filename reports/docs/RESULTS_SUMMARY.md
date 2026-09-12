Telco Customer Churn — Initial Findings

Dataset: `data/processed/telco_cleaned.csv` (7,043 rows × 35 columns)

Top 3 insights:
1. Overall churn rate is ~26.5% (1,869 churned customers).
2. Customers on `Month-to-month` contracts have much higher churn (~42.7%) compared with `One year` (~11.3%) and `Two year` (~2.8%).
3. Top reported churn reasons include: `Attitude of support person`, `Competitor offered higher download speeds`, and `Competitor offered more data` — indicating support experience and competitive offers are major drivers.

Modeling summary:
- Logistic regression (simple baseline) trained after removing churn-like leak columns.
- Results on test set: Accuracy ~0.7346, Precision ~0.50, Recall ~0.369, ROC AUC ~0.758.
- Model indicates reasonable discrimination (AUC), but recall is low — implies many churners are missed by this simple baseline.

Artifacts:
- Cleaned data: `data/processed/telco_cleaned.csv`
- Visuals & report: `reports/telco_report.pdf` and `reports/*.png`
- Trained model: `models/logistic_telco.pkl`
- Notebooks: `notebooks/02_EDA_Telco.ipynb`

Suggested next steps:
- Feature engineering (tenure buckets, interaction terms, CLTV normalization).
- Try tree-based models (RandomForest, XGBoost) with class weighting or resampling to improve recall.
- Generate SHAP explanations and feature importances for model interpretability.
- Produce a short slide deck summarizing the findings for stakeholders.
