import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests

# API endpoint
API_URL = "http://127.0.0.1:8000"

# List of driver IDs for dropdown (you can fetch this dynamically from API too)
DRIVER_IDS = [f"driver_{i:04d}" for i in range(10)]  # example: first 10 drivers

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Telematics Insurance Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Telematics Insurance Dashboard"),
    html.Label("Select Driver:"),
    dcc.Dropdown(
        id="driver-dropdown",
        options=[{"label": d, "value": d} for d in DRIVER_IDS],
        value="driver_0001"
    ),
    html.Br(),
    html.Div(id="premium-output"),
    html.Br(),
    html.Div(id="risk-output")
])

# Function to fetch data from API
def get_driver_premium(driver_id):
    try:
        resp = requests.get(f"{API_URL}/premium/{driver_id}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

# Callback to update dashboard
@app.callback(
    Output("premium-output", "children"),
    Output("risk-output", "children"),
    Input("driver-dropdown", "value")
)
def update_dashboard(driver_id):
    data = get_driver_premium(driver_id)
    if data and "premium" in data:
        premium_text = f"Premium: ${data['premium']:.2f}"
        risk_text = f"Risk Score: {data['risk_score']:.3f}"
    else:
        premium_text = "Premium: N/A"
        risk_text = "Risk Score: N/A"
    return premium_text, risk_text

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, host="127.0.0.1", port=8050)
