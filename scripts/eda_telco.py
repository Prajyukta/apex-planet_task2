"""EDA pipeline for IBM Telco Customer Churn dataset.
Usage: python scripts/eda_telco.py
"""
import os
import shutil
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW_PATH = os.path.join(ROOT, "data", "raw")
PROCESSED_PATH = os.path.join(ROOT, "data", "processed")
RAW_FILE_NAME = "Telco_customer_churn.xlsx"
RAW_FILE_SRC = os.path.join(ROOT, RAW_FILE_NAME)
RAW_FILE = os.path.join(RAW_PATH, RAW_FILE_NAME)
PROCESSED_FILE = os.path.join(PROCESSED_PATH, "telco_cleaned.csv")


def ensure_dirs():
    os.makedirs(RAW_PATH, exist_ok=True)
    os.makedirs(PROCESSED_PATH, exist_ok=True)


def import_raw():
    # If raw file is at repo root, copy to data/raw
    if os.path.exists(RAW_FILE_SRC) and not os.path.exists(RAW_FILE):
        shutil.copy(RAW_FILE_SRC, RAW_FILE)
        print(f"Copied {RAW_FILE_SRC} -> {RAW_FILE}")
    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(f"Telco dataset not found. Place {RAW_FILE_NAME} at repo root or in data/raw/")
    return RAW_FILE


def load_excel(path):
    df = pd.read_excel(path)
    return df


def clean_telco(df: pd.DataFrame) -> pd.DataFrame:
    # Drop duplicates
    df = df.drop_duplicates()

    # Strip whitespace from column names
    df.columns = df.columns.str.strip()

    # Convert TotalCharges to numeric (some rows are empty strings)
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    # Fix tenure to numeric
    if "tenure" in df.columns:
        df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")

    # Fill or drop missing values: if TotalCharges missing and MonthlyCharges present, estimate
    if "TotalCharges" in df.columns and "MonthlyCharges" in df.columns and "tenure" in df.columns:
        missing_tc = df["TotalCharges"].isna()
        if missing_tc.sum() > 0:
            # estimate TotalCharges = MonthlyCharges * tenure
            df.loc[missing_tc, "TotalCharges"] = (df.loc[missing_tc, "MonthlyCharges"] * df.loc[missing_tc, "tenure"]).round(2)

    # Convert churn to binary (case- and whitespace-tolerant)
    # Find any column containing the substring 'churn' (case-insensitive)
    churn_col = next((c for c in df.columns if "churn" in str(c).strip().lower()), None)
    if churn_col is not None:
        # Normalize churn representation
        vals = df[churn_col]
        if pd.api.types.is_numeric_dtype(vals):
            # assume 0/1
            df["Churn"] = vals.astype(int).astype(str)
            df["ChurnBinary"] = vals.astype(int)
        else:
            s = vals.astype(str).str.strip()
            # map common labels
            if set(s.unique()) <= {"0", "1", "0.0", "1.0"}:
                df["ChurnBinary"] = s.astype(float).astype(int)
                df["Churn"] = df["ChurnBinary"].map({1: "Yes", 0: "No"})
            else:
                df["Churn"] = s
                df["ChurnBinary"] = s.map({"Yes": 1, "No": 0})

    # Convert categorical columns to category dtype
    for col in df.select_dtypes(include="object").columns:
        if col not in ["customerID"]:
            df[col] = df[col].astype("category")

    return df


def summarize(df: pd.DataFrame):
    print("Rows, columns:", df.shape)
    # Report churn if present
    if "Churn" in df.columns:
        print("Churn distribution:\n", df["Churn"].value_counts(dropna=False))
        if "ChurnBinary" in df.columns:
            print("Churn rate:", df["ChurnBinary"].mean())
    else:
        # Try to find any churn-like columns
        possible = [c for c in df.columns if "churn" in str(c).lower()]
        if possible:
            print("Found churn-like columns:", possible)
            for c in possible:
                print(c, df[c].value_counts(dropna=False))
        else:
            print("No churn column found in dataframe. Columns:\n", list(df.columns))
    print(df.describe(include="all"))


def save_processed(df: pd.DataFrame):
    df.to_csv(PROCESSED_FILE, index=False)
    print(f"Saved cleaned Telco data to {PROCESSED_FILE}")


def main():
    ensure_dirs()
    raw = import_raw()
    df = load_excel(raw)
    df = clean_telco(df)
    summarize(df)
    save_processed(df)


if __name__ == "__main__":
    main()
