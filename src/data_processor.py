"""
Feature engineering for telematics events CSV.

Input: simulated telematics CSV with columns:
  driver_id, trip_id, event_id, timestamp, lat, lon, speed_kmh, accel_ms2

Output: driver-level aggregated features CSV
"""
import pandas as pd
import argparse

def extract_features(df):
    # convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Basic temporal features
    df['hour'] = df['timestamp'].dt.hour
    df['is_night'] = ((df['hour'] < 6) | (df['hour'] >= 22)).astype(int)

    # Driving behavior flags
    df['hard_brake'] = ((df['accel_ms2'] < -3.0) & (df['speed_kmh'] > 10)).astype(int)
    df['harsh_accel'] = ((df['accel_ms2'] > 3.0) & (df['speed_kmh'] > 10)).astype(int)

    # Aggregate per driver
    agg = df.groupby('driver_id').agg({
        'speed_kmh': ['mean', 'std', 'max'],
        'hard_brake': 'sum',
        'harsh_accel': 'sum',
        'is_night': 'mean',
        'timestamp': lambda x: (x.max() - x.min()).total_seconds() / 3600.0  # active hours
    })

    # Flatten multi-level columns
    agg.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in agg.columns.values]
    agg = agg.reset_index()

    # Trips per day estimate
    trips_per_driver = df.groupby('driver_id')['trip_id'].nunique()
    agg['trips_per_day_est'] = trips_per_driver.values / (df['timestamp'].dt.date.nunique())

    # Hard brake / harsh accel rates
    agg['hard_brake_rate'] = agg['hard_brake_sum'] / agg['timestamp_<lambda>'].replace(0,1)
    agg['harsh_accel_rate'] = agg['harsh_accel_sum'] / agg['timestamp_<lambda>'].replace(0,1)

    return agg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input simulated telematics CSV")
    parser.add_argument("--out", default="../data/features.csv", help="Output driver-level features CSV")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    features = extract_features(df)
    features.to_csv(args.out, index=False)
    print(f"Wrote driver-level features to {args.out}")

if __name__ == "__main__":
    main()