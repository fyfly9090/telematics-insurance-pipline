"""
Train a driver risk scoring model from driver-level telematics features.

Input: features CSV (from data_processor.py)
Output: trained model saved as .joblib
"""
import argparse
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Driver-level features CSV")
    parser.add_argument("--out", default="../models/baseline_rf.joblib", help="Output trained model path")
    args = parser.parse_args()

    # Load features
    df = pd.read_csv(args.input)

    # Check if risk_label exists; if not, create a synthetic label for POC
    if 'risk_label' not in df.columns:
        # Higher mean speed, more hard brakes and harsh accel → higher risk
        df['risk_label'] = (
            0.4 * df['speed_kmh_mean'] +
            3.0 * df['hard_brake_sum'] +
            2.0 * df['harsh_accel_sum']
        )
        # Normalize to 0-1
        df['risk_label'] = (df['risk_label'] - df['risk_label'].min()) / (df['risk_label'].max() - df['risk_label'].min())

    # Features (drop ID and target)
    X = df.drop(columns=['driver_id', 'risk_label'])
    y = df['risk_label']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print("RMSE:", rmse)
    print(f"Model trained. RMSE on test set: {rmse:.4f}")

    # Ensure model output directory exists
    import os
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Save model
    joblib.dump(model, args.out)
    print(f"Saved model to {args.out}")

if __name__ == "__main__":
    main()