import argparse
import pandas as pd
import os


def calculate_premium(base_premium, risk_score):
    """
    Adjusts the base premium using the risk score.
    Example formula:
        - low-risk drivers get discounts
        - high-risk drivers pay more
    """
    # Cap risk between 0 and 1
    risk_score = max(0, min(1, risk_score))

    # Example dynamic multiplier:
    #  - Safe drivers (score < 0.3): up to 20% discount
    #  - Risky drivers (score > 0.7): up to 50% increase
    if risk_score < 0.3:
        multiplier = 1 - (0.2 * (0.3 - risk_score) / 0.3)
    elif risk_score > 0.7:
        multiplier = 1 + (0.5 * (risk_score - 0.7) / 0.3)
    else:
        multiplier = 1.0  # Neutral zone

    return round(base_premium * multiplier, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV with driver features + risk_score")
    parser.add_argument("--out", default="../data/premiums.csv", help="Output CSV with premiums")
    parser.add_argument("--base", type=float, default=500.0, help="Base premium ($)")
    parser.add_argument("--multiplier", type=float, default=1.5, help="Risk multiplier")
    args = parser.parse_args()

    # Load scored features
    df = pd.read_csv(args.input)

    # Ensure risk_score column exists
    if 'risk_score' not in df.columns:
        raise ValueError("Input CSV must contain 'risk_score' column. Run eval.py first.")

    # Calculate premiums
    df['premium'] = df['risk_score'].apply(lambda x: calculate_premium(args.base, x))

    # Keep only relevant columns for output
    out_df = df[['driver_id', 'risk_score', 'premium']]

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    # Save
    out_df.to_csv(args.out, index=False)
    print(f"Saved premiums to {args.out}")

if __name__ == "__main__":
    main()

