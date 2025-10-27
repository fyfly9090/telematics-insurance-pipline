"""
Full automated pipeline for Telematics Insurance System
Includes:
- Data generation
- Feature processing
- Model training
- Risk evaluation
- Premium calculation
- Dashboard launch
- API server launch with auto-reload
"""

import subprocess
import os
import time
import sys

# ---------- Directory Setup ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Ensure src directory is in Python path
sys.path.append(SRC_DIR)

# ---------- Config ----------
NUM_DRIVERS = 500
NUM_DAYS = 60
SEED = 42
OPEN_DASHBOARD = True   # True to launch dashboard after pipeline
OPEN_API = True         # True to launch API server after pipeline

# ---------- Paths ----------
TELEMATICS_CSV = os.path.join(DATA_DIR, "simulated_telematics.csv")
FEATURES_CSV = os.path.join(DATA_DIR, "features.csv")
SCORED_FEATURES_CSV = os.path.join(DATA_DIR, "features_scored.csv")
PREMIUMS_CSV = os.path.join(DATA_DIR, "premiums.csv")
MODEL_FILE = os.path.join(MODELS_DIR, "baseline_rf.joblib")

# ---------- Helper ----------
def run_script(script_name, args=[]):
    script_path = os.path.join(SRC_DIR, script_name)
    cmd = ["python", script_path] + args
    print("\nRunning:", " ".join(cmd))
    subprocess.run(cmd, check=True)

# ---------- Pipeline Steps ----------
try:
    # 1. Generate telematics data
    run_script("data_generator.py", [
        "--n-drivers", str(NUM_DRIVERS),
        "--days", str(NUM_DAYS),
        "--out", TELEMATICS_CSV,
        "--seed", str(SEED)
    ])

    # 2. Process features
    run_script("data_processor.py", [
        "--input", TELEMATICS_CSV,
        "--out", FEATURES_CSV
    ])

    # 3. Train model
    run_script("model_trainer.py", [
        "--input", FEATURES_CSV,
        "--out", MODEL_FILE
    ])

    # 4. Evaluate risk
    run_script("risk_scoring_model.py", [
        "--input", FEATURES_CSV,
        "--model", MODEL_FILE,
        "--out", SCORED_FEATURES_CSV
    ])

    # 5. Compute premiums
    run_script("pricing_engine.py", [
        "--input", SCORED_FEATURES_CSV,
        "--out", PREMIUMS_CSV
    ])

    print("\n✅ Pipeline completed successfully!")
    print(f"Generated premiums CSV: {PREMIUMS_CSV}")

    # 6. Launch dashboard
    dashboard_proc = None
    if OPEN_DASHBOARD:
        print("\n📊 Launching dashboard...")
        dashboard_proc = subprocess.Popen([
            "python",
            os.path.join(SRC_DIR, "dashboard.py"),
            "--input", PREMIUMS_CSV
        ])

    # 7. Launch API server with auto-reload
    api_proc = None
    if OPEN_API:
        print("\n🔐 Launching API server with auto-reload...")
        api_proc = subprocess.Popen([
            "python", "-m", "uvicorn",
            "src.api_server:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ])

    # 8. Keep script alive while servers run
    if OPEN_DASHBOARD or OPEN_API:
        print("\n🚀 Pipeline, dashboard, and API server are running.")
        print("   Dashboard: http://127.0.0.1:8050")
        print("   API Server: http://127.0.0.1:8000")
        print("Press Ctrl+C to terminate everything.")
        while True:
            time.sleep(1)

except subprocess.CalledProcessError as e:
    print(f"\n❌ Error running script: {e}")

except KeyboardInterrupt:
    print("\n\n🛑 Stopping dashboard and API server...")
    if 'dashboard_proc' in locals() and dashboard_proc:
        dashboard_proc.terminate()
    if 'api_proc' in locals() and api_proc:
        api_proc.terminate()
    print("All processes terminated.")
