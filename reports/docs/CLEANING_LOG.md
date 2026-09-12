Cleaning log — Telco Customer Churn

Source file: `Telco_customer_churn.xlsx` (placed at repo root and copied to `data/raw/`).

Transformations applied (scripts/eda_telco.py):
- Copied source Excel to `data/raw/`.
- Loaded Excel into pandas DataFrame.
- Dropped exact duplicate rows.
- Stripped whitespace from column names.
- Converted `Total Charges` / `TotalCharges` to numeric, coercing non-numeric to NaN.
- Converted `Tenure Months` / `tenure` to numeric where present.
- For rows with missing `Total Charges`, estimated as `Monthly Charges * Tenure Months` when those values were present.
- Identified churn-like columns (e.g., `Churn Label`, `Churn Value`, `Churn Score`, `Churn Reason`) and created a normalized `Churn` column where possible; created `ChurnBinary` with 1=churn, 0=no churn.
- Converted non-ID object columns to `category` dtype where appropriate.
- Saved cleaned dataset to `data/processed/telco_cleaned.csv`.

Notes and limitations:
- Several columns (e.g., `Churn Score`, `Churn Reason`) contain information that can leak label for modeling; when training models we explicitly dropped churn-like columns to avoid leakage.
- Some numeric conversions coerced invalid strings to NaN — verify rows with NaN in `Total Charges` after transformations.
- Column names vary in spacing/casing; scripts perform tolerant matching but keep an eye on exact names when adding analyses.

Script references:
- `scripts/eda_telco.py` — initial loading and cleaning.
- `scripts/analysis_telco.py` — visuals, model training (drops churn-like columns before training), and report generation.

Timestamp: 2026-08-12
