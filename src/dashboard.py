"""
Dash dashboard for Telematics-Based Auto Insurance
Automatically reloads when premiums CSV changes.
"""

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import os
import argparse

# ---------- Argument Parsing ----------
parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help="Path to premiums CSV")
args = parser.parse_args()

PREMIUMS_CSV = args.input

# ---------- Dash App ----------
app = dash.Dash(__name__)
app.title = "Telematics Insurance Dashboard"

# Store last modification time
last_mtime = None
df_cached = pd.DataFrame()

# ---------- Layout ----------
app.layout = html.Div([
    html.H1("Telematics Insurance Dashboard"),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # 5 seconds
        n_intervals=0
    ),
    html.Div(id='summary-stats'),
    dcc.Graph(id='premium-risk-scatter'),
])

# ---------- Callback ----------
@app.callback(
    Output('summary-stats', 'children'),
    Output('premium-risk-scatter', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_dashboard(n):
    global last_mtime, df_cached

    # Check if file exists
    if not os.path.exists(PREMIUMS_CSV):
        return html.Div("Premiums CSV not found."), {}

    # Reload only if modified
    mtime = os.path.getmtime(PREMIUMS_CSV)
    if last_mtime != mtime:
        df_cached = pd.read_csv(PREMIUMS_CSV)
        last_mtime = mtime

    df = df_cached

    if df.empty:
        return html.Div("No data available."), {}

    # Summary stats
    avg_premium = df["premium"].mean()
    avg_risk = df["risk_score"].mean()
    stats = html.Div([
        html.P(f"Number of drivers: {len(df)}"),
        html.P(f"Average Premium: ${avg_premium:.2f}"),
        html.P(f"Average Risk Score: {avg_risk:.3f}")
    ])

    # Scatter plot: risk vs premium
    fig = px.scatter(df, x="risk_score", y="premium",
                     hover_data=["driver_id"],
                     labels={"risk_score": "Risk Score", "premium": "Premium ($)"},
                     title="Driver Risk vs Premium")

    return stats, fig

# ---------- Run App ----------
if __name__ == "__main__":
    app.run(port=8050, debug=True)