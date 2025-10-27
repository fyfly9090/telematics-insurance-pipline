"""
Evaluate / score driver risk using trained model.

Input:
  - Driver-level features CSV (from data_processor.py)
  - Trained model (from train_model.py)

Output:
  - CSV with driver_id, features, and predicted risk_score
"""
import argparse
import pandas as pd
import joblib
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Driver-level features CSV")
    parser.add_argument("--model", required=True, help="Trained risk model (.joblib)")
    parser.add_argument("--out", default="../data/features_scored.csv", help="Output CSV with risk scores")
    args = parser.parse_args()

    # Load features
    df = pd.read_csv(args.input)

    # Load trained model
    model = joblib.load(args.model)

    # Prepare feature matrix (drop driver_id and risk_label if present)
    X = df.drop(columns=['driver_id', 'risk_label'], errors='ignore')

    # Predict risk scores
    df['risk_score'] = model.predict(X)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Save scored results
    df.to_csv(args.out, index=False)
    print(f"Saved scored driver risk CSV to {args.out}")

if __name__ == "__main__":
    main()