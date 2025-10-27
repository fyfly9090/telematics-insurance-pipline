from typing import List
from fastapi import FastAPI, HTTPException
import pandas as pd
import os

# Paths setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "premiums.csv")

# Initialize app
app = FastAPI(
    title="Telematics Insurance API",
    description="API providing driver risk scores and insurance premiums.",
    version="1.0.0",
)

# Load precomputed premiums
premium_df = pd.read_csv(DATA_PATH)

def load_premiums():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Premium data not found: {DATA_PATH}")
    return pd.read_csv(DATA_PATH)

@app.get("/", summary="Root endpoint")
def root():
    return {
        "message": "🚗 Telematics Insurance API running.",
        "usage": "Try /drivers or /premium/{driver_id}"
    }

@app.get("/drivers", response_model=List[str], summary="List all driver IDs")
def list_drivers():
    df = load_premiums()
    return df["driver_id"].tolist()

@app.get("/premium/{driver_id}", summary="Get premium & risk score for a driver")
def get_premium(driver_id: str):
    df = load_premiums()
    row = df.loc[df["driver_id"] == driver_id]

    if row.empty:
        raise HTTPException(status_code=404, detail=f"Driver {driver_id} not found")

    record = row.iloc[0]
    return {
        "driver_id": driver_id,
        "risk_score": float(record["risk_score"]),
        "premium": float(record["premium"])
    }


