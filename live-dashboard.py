"""
Smart Study Area Climate Dashboard (MQTT) — Version 14.2 
By: Jonathan Mishayel

"""

import random
import threading
import traceback
from datetime import datetime, timedelta
from collections import deque
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import paho.mqtt.client as mqtt

# -----------------------------
# MQTT CONFIGURATION
# -----------------------------
BROKER = "test.mosquitto.org"
TOPIC = "jtown/study_area/data"
UPDATE_INTERVAL_MS = 2000
MAX_POINTS = 1500
buffer, lock = deque(maxlen=MAX_POINTS), threading.Lock()

def safe_append(t, h):
    with lock:
        buffer.append({"ts": datetime.utcnow(), "temperature": float(t), "humidity": float(h)})

def on_message(_, __, msg):
    try:
        t, h = map(float, msg.payload.decode().split(",")[:2])
        if -10 < t < 60 and 0 <= h <= 100:
            safe_append(t, h)
    except Exception as e:
        print("⚠️ Parse error:", e)

# Attempt MQTT connection
client = mqtt.Client()
try:
    client.on_message = on_message
    client.connect(BROKER, 1883, 60)
    client.subscribe(TOPIC)
    client.loop_start()
    MQTT = True
except Exception:
    MQTT = False

# -----------------------------
# SIMULATION THREAD
# -----------------------------
stop_evt = None
def simulate():
    while not stop_evt.is_set():
        safe_append(29 + random.uniform(-0.5, 0.5), 80 + random.uniform(-0.5, 0.5))
        stop_evt.wait(UPDATE_INTERVAL_MS / 1000)

# -----------------------------
# DASH SETUP
# -----------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
server = app.server

def df_buf(mins):
    with lock:
        rows = list(buffer)
    if not rows:
        return pd.DataFrame(columns=["ts", "temperature", "humidity"])
    df = pd.DataFrame(rows)
    df["ts"] = pd.to_datetime(df["ts"])
    if mins > 0:
        df = df[df["ts"] > datetime.utcnow() - timedelta(minutes=mins)]
    return df.sort_values("ts")

# -----------------------------
# HELPERS
# -----------------------------
def safe_range(lo, hi, expand=0.1):
    try:
        if pd.isna(lo) or pd.isna(hi):
            return (0.0, 1.0)
        if hi <= lo:
            v = float(lo)
            return (v - expand, v + expand)
        return (float(lo), float(hi))
    except Exception:
        return (0.0, 1.0)

def gauge(val, lo, hi, title, color):
    lo, hi = safe_range(lo, hi, expand=0.1)
    ticks = [round(lo + i * (hi - lo) / 5, 2) for i in range(6)]
    g = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val if pd.notna(val) else 0,
        title={"text": f"<b>{title}</b>", "font": {"size": 20, "color": "#333"}},
        number={"font": {"size": 28, "color": "#000"}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [lo, hi], "tickvals": ticks, "ticktext": [f"{x:.2f}" for x in ticks]},
            "bar": {"color": color, "thickness": 0.15},
            "bgcolor": "white",
            "bordercolor": "#ddd",
            "borderwidth": 1
        }
    ))
    g.update_layout(height=300, margin=dict(t=30, b=20, l=20, r=20), paper_bgcolor="white")
    return g

def line_fig(df, y, title, clr, step, y_label):
    if df.empty or y not in df.columns or df[y].dropna().empty:
        f = go.Figure().update_layout(template="plotly_white", title=f"{title} (No data yet)", height=400)
        return f

    lo, hi = safe_range(df[y].min() - (step or 0.01), df[y].max() + (step or 0.01))
    y_dtick = step if step and step > 0 else max((hi - lo) / 8.0, 0.01)

    fig = go.Figure(go.Scatter(
        x=df["ts"], y=df[y],
        mode="lines+markers",
        name=y_label,
        line=dict(color=clr, width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 22, "color": "black"}},
        template="plotly_white",
        height=500,
        legend=dict(font=dict(size=16, color="black"), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(
            title={"text": y_label, "font": {"size": 18, "color": "black"}},
            tickformat=".2f",
            dtick=y_dtick,
            range=[lo, hi],
            showgrid=True,
            tickfont=dict(size=14, color="black")
        ),
        xaxis=dict(
            title={"text": "Time (HH:MM:SS)", "font": {"size": 18, "color": "black"}},
            tickformat="%H:%M:%S",
            dtick=30000,
            showgrid=True,
            tickfont=dict(size=14, color="black")
        )
    )
    return fig

# -----------------------------
# LAYOUT
# -----------------------------
app.layout = dbc.Container([
    dbc.Row([dbc.Col(html.H2("Smart Study Area Climate Dashboard",
                        style={"textAlign": "center", "color": "#FFD580", "fontWeight": "bold"}))], className="my-3"),

    dbc.Row([
        dbc.Col(html.Small(id="status-mqtt", style={"color": "#80D8FF", "fontWeight": "bold", "fontSize": "16px"}), md=6),
        dbc.Col(html.Small(f"MQTT Broker: {BROKER}", style={"color": "#ccc", "fontSize": "14px"}), md=6)
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardHeader("Controls & Filters"),
            dbc.CardBody([
                html.Label("Time window:"),
                dcc.Dropdown(id="window", value=5, clearable=False,
                             options=[{"label": f"Last {m} minutes", "value": m} for m in [1,5,15,60]] + [{"label":"All data","value":0}]),
                html.Br(),
                html.Label("Smoothing (seconds):"),
                dcc.Slider(id="smooth", min=0, max=20, step=1, value=0, marks={i:str(i) for i in [0,5,10,15,20]}),
                html.Br(),
                dbc.Checklist(id="opts", value=[], inline=True, options=[{"label":"Show markers","value":"mark"},{"label":"Simulate data","value":"sim"}]),
                html.Br(),
                dbc.Button("Pause", id="pause", color="warning", className="me-2"),
                dbc.Button("Resume", id="resume", color="success", className="me-2"),
                dbc.Button("Export CSV", id="export", color="primary"),
                html.Div(id="export-msg")
            ])
        ]), md=4),

        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardHeader(html.H5("Temperature Gauge", style={"fontWeight":"bold"})),
                                  dbc.CardBody(dcc.Graph(id="t_g", style={"height":"300px"}))]), md=6),
                dbc.Col(dbc.Card([dbc.CardHeader(html.H5("Humidity Gauge", style={"fontWeight":"bold"})),
                                  dbc.CardBody(dcc.Graph(id="h_g", style={"height":"300px"}))]), md=6)
            ]),
            dbc.Row([dbc.Col(dbc.Card(dbc.CardBody([html.H5("📊 Data Summary (Visible Window)", style={"color":"#FFD580","fontWeight":"bold"}),
                                                    html.Div(id="stats", style={"color":"#E0E0E0","fontSize":"20px"})])), md=12, className="mt-2")])
        ], md=8)
    ], className="mb-3"),

    dbc.Row([dbc.Col(dbc.Card(dcc.Graph(id="t_line", style={"height":"600px"})), md=6),
             dbc.Col(dbc.Card(dcc.Graph(id="h_line", style={"height":"600px"})), md=6)], className="mb-3"),

    dbc.Row([dbc.Col(dbc.Card([dbc.CardHeader(html.H5("Correlation Between Temperature and Humidity", style={"fontWeight":"bold","fontSize":"20px","color":"black"})),
                               dbc.CardBody(dcc.Graph(id="corr", style={"height":"400px"}))]), md=12)]),

    dcc.Interval(id="intv", interval=UPDATE_INTERVAL_MS, n_intervals=0),

    html.Footer([html.Hr(), html.Small("© 2025 Smart Study Area IoT Dashboard — Created by Jonathan Mishayel", style={"color":"#888"})], style={"textAlign":"center","marginTop":"25px"})
], fluid=True, style={"background":"linear-gradient(180deg,#001F33,#002B40)","minHeight":"100vh","paddingBottom":"20px"})

# -----------------------------
# CALLBACKS
# -----------------------------
@app.callback(Output("status-mqtt", "children"), Input("intv", "n_intervals"))
def status(_):
    return (f" MQTT Connected · Buffer: {len(buffer)} samples" if MQTT
            else f" Simulation Mode · Buffer: {len(buffer)} samples")

@app.callback([Output("t_g","figure"), Output("h_g","figure"),
               Output("t_line","figure"), Output("h_line","figure"),
               Output("stats","children")],
              Input("intv","n_intervals"))
def update(_):
    try:
        df = df_buf(5)

        if df.empty or df["temperature"].dropna().empty or df["humidity"].dropna().empty:
            empty = go.Figure().update_layout(template="plotly_white", height=300)
            return empty, empty, empty, empty, "Waiting for valid data..."

        t = df["temperature"].iloc[-1]
        h = df["humidity"].iloc[-1]

        tg = gauge(t, df["temperature"].min() - 0.1, df["temperature"].max() + 0.1, "Temperature (°C)", "#FF8C00")
        hg = gauge(h, df["humidity"].min() - 0.05, df["humidity"].max() + 0.05, "Humidity (%)", "#00BFFF")

        tl = line_fig(df, "temperature", "Temperature Over Time", "#007AFF", 0.02, "Temperature (°C)")
        hl = line_fig(df, "humidity", "Humidity Over Time", "#00BFFF", 0.05, "Humidity (%)")

        c = df[["temperature","humidity"]].corr()
        if c.shape != (2,2):
            c = pd.DataFrame([[1.0,0.0],[0.0,1.0]], index=["temperature","humidity"], columns=["temperature","humidity"])

        FINAL fixed heatmap
        cf = go.Figure(go.Heatmap(
            z=c.values, x=c.columns, y=c.index,
            colorscale="RdBu_r", zmin=-1, zmax=1,
            colorbar=dict(
                title=dict(
                    text="Correlation",
                    font=dict(size=14, color="black")
                ),
                tickfont=dict(size=12, color="black")
            )
        ))
        cf.update_layout(
            template="plotly_white",
            title={"text": "Correlation Between Temperature and Humidity", "font": {"size": 22, "color": "black"}},
            height=400,
            xaxis=dict(title={"text": "Variables", "font": {"size": 18, "color": "black"}}, tickfont=dict(size=14, color="black")),
            yaxis=dict(title={"text": "Variables", "font": {"size": 18, "color": "black"}}, tickfont=dict(size=14, color="black"))
        )

        stats = (f"Samples: {len(df)}<br>"
                 f"Temp — avg: {df['temperature'].mean():.2f}°C, "
                 f"min: {df['temperature'].min():.2f}, max: {df['temperature'].max():.2f}<br>"
                 f"Hum — avg: {df['humidity'].mean():.2f}%, "
                 f"min: {df['humidity'].min():.2f}, max: {df['humidity'].max():.2f}")

        return tg, hg, tl, hl, stats

    except Exception as e:
        print(" Callback error in update():", e)
        traceback.print_exc()
        empty = go.Figure().update_layout(template="plotly_white", height=300)
        return empty, empty, empty, empty, f"Error generating charts — {e}"

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    if not MQTT:
        print(" MQTT not reachable — using simulated data.")
        stop_evt = threading.Event()
        threading.Thread(target=simulate, daemon=True).start()
    app.run(debug=True, use_reloader=False)
