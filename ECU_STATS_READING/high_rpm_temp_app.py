import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import time

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🚗 Vehicle Diagnostics & Playback Dashboard",
                   layout="wide",
                   initial_sidebar_state="expanded")

# ------------------- FUNCTIONS -------------------
def load_data(file):
    return pd.read_csv(file, parse_dates=["Timestamp"]).sort_values("Timestamp")

def temp_status(temp, warn, critical):
    if temp >= critical:
        return "Critical", "red"
    elif temp >= warn:
        return "Caution", "orange"
    else:
        return "Normal", "green"

def detect_anomalies(df, col, threshold=2):
    mean = df[col].mean()
    std = df[col].std()
    return df[(df[col] > mean + threshold*std) | (df[col] < mean - threshold*std)]

def gauge_chart(value, title, min_val, max_val, steps):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'steps': steps
        }
    )).update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))

def correlation_heatmap(df):
    corr = df.corr(numeric_only=True)
    return px.imshow(corr, text_auto=True, title="Correlation Heatmap",
                     color_continuous_scale="RdBu_r", zmin=-1, zmax=1)

# ------------------- SIDEBAR SETTINGS -------------------
st.sidebar.header("⚙️ Settings")
uploaded_file = st.sidebar.file_uploader("Upload Vehicle CSV", type=["csv"])
warn_temp = st.sidebar.slider("Warning Temp °C", 70, 200, 120)
critical_temp = st.sidebar.slider("Critical Temp °C", 80, 300, 100)
speed_limit_overrev = st.sidebar.slider("Over-Rev Low Speed (km/h)", 0, 90, 20)
rpm_limit_overrev = st.sidebar.slider("Over-Rev High RPM", 4000, 18000, 8000)
playback_speed = st.sidebar.slider("Playback Speed (sec/frame)", 0.1, 2.0, 0.3)

# ------------------- MAIN -------------------
if uploaded_file:
    df = load_data(uploaded_file)

    # Latest readings
    latest_temp = df["Engine_Temperature_C"].iloc[-1]
    latest_rpm = df["RPM"].iloc[-1]
    latest_speed = df["Vehicle_Speed_kmh"].iloc[-1]
    latest_throttle = df["Throttle_Position_Percent"].iloc[-1]
    temp_label, temp_color = temp_status(latest_temp, warn_temp, critical_temp)

    # ---------------- LIVE GAUGES ----------------
    st.subheader("📟 Live Gauges")
    c1, c2, c3, c4 = st.columns(4)
    c1.plotly_chart(gauge_chart(latest_rpm, "RPM", 0, 16000,
                                [{'range': [0, rpm_limit_overrev], 'color': "lightgreen"},
                                 {'range': [rpm_limit_overrev, 16000], 'color': "red"}]), use_container_width=True)
    c2.plotly_chart(gauge_chart(latest_temp, "Temp °C", 0, 130,
                                [{'range': [0, warn_temp], 'color': "lightgreen"},
                                 {'range': [warn_temp, critical_temp], 'color': "orange"},
                                 {'range': [critical_temp, 130], 'color': "red"}]), use_container_width=True)
    c3.plotly_chart(gauge_chart(latest_speed, "Speed km/h", 0, 200,
                                [{'range': [0, 120], 'color': "lightgreen"},
                                 {'range': [120, 200], 'color': "orange"}]), use_container_width=True)
    c4.plotly_chart(gauge_chart(latest_throttle, "Throttle %", 0, 100,
                                [{'range': [0, 60], 'color': "lightgreen"},
                                 {'range': [60, 85], 'color': "orange"},
                                 {'range': [85, 100], 'color': "red"}]), use_container_width=True)

    # ---------------- CORRELATION ----------------
    st.subheader("📌 Correlation Matrix of Vehicle Parameters")
    st.plotly_chart(correlation_heatmap(df), use_container_width=True)

    # ---------------- OVER-REV DETECTION ----------------
    df["OverRev"] = (df["Vehicle_Speed_kmh"] <= speed_limit_overrev) & (df["RPM"] >= rpm_limit_overrev)
    st.subheader("🏎 RPM vs Speed (red = over-revving)")
    overrev_fig = px.scatter(df, x="Vehicle_Speed_kmh", y="RPM", color="OverRev",
                             color_discrete_map={True: "red", False: "blue"},
                             hover_data=["Timestamp"])
    st.plotly_chart(overrev_fig, use_container_width=True)

    # ---------------- THROTTLE vs TEMP ----------------
    st.subheader("⛽ Throttle vs Temperature")
    st.plotly_chart(px.scatter(df, x="Throttle_Position_Percent", y="Engine_Temperature_C",
                               color="Engine_Temperature_C", color_continuous_scale="Turbo"), use_container_width=True)

    # ---------------- O2 SENSOR ----------------
    st.subheader("🛠 Oxygen Sensor Voltage Over Time")
    st.plotly_chart(px.line(df, x="Timestamp", y="Oxygen_Sensor_Voltage_V"), use_container_width=True)

    # ---------------- ANOMALY DETECTION ----------------
    st.subheader("🔍 Anomaly Detection & Event Log")
    events = []
    for _, row in df.iterrows():
        if row["Engine_Temperature_C"] >= critical_temp:
            events.append(("Critical Temp", row["Timestamp"], row["Engine_Temperature_C"]))
        elif row["Engine_Temperature_C"] >= warn_temp:
            events.append(("Warning Temp", row["Timestamp"], row["Engine_Temperature_C"]))
    for _, row in df[df["OverRev"]].iterrows():
        events.append(("Over-Revving", row["Timestamp"], row["RPM"]))
    for col in ["RPM", "Vehicle_Speed_kmh", "Oxygen_Sensor_Voltage_V", "Throttle_Position_Percent"]:
        for _, row in detect_anomalies(df, col).iterrows():
            events.append((f"{col} Anomaly", row["Timestamp"], row[col]))

    event_log_df = pd.DataFrame(events, columns=["Event Type", "Timestamp", "Value"]).drop_duplicates()
    st.dataframe(event_log_df, use_container_width=True)
    st.download_button("📥 Download Event Log CSV", event_log_df.to_csv(index=False), "event_log.csv")

    # ---------------- PLAYBACK MODE ----------------
    st.subheader("🎬 Trip Playback Mode")
    if st.button("▶ Start Playback"):
        placeholder_g1 = st.empty()
        placeholder_g2 = st.empty()
        placeholder_g3 = st.empty()
        placeholder_g4 = st.empty()
        for i in range(len(df)):
            row = df.iloc[i]
            placeholder_g1.plotly_chart(gauge_chart(row["RPM"], "RPM", 0, 16000,
                                                    [{'range': [0, rpm_limit_overrev], 'color': "lightgreen"},
                                                     {'range': [rpm_limit_overrev, 16000], 'color': "red"}]),
                                       use_container_width=True, key=f"g1_{i}")
            placeholder_g2.plotly_chart(gauge_chart(row["Engine_Temperature_C"], "Temp °C", 0, 130,
                                                    [{'range': [0, warn_temp], 'color': "lightgreen"},
                                                     {'range': [warn_temp, critical_temp], 'color': "orange"},
                                                     {'range': [critical_temp, 130], 'color': "red"}]),
                                       use_container_width=True, key=f"g2_{i}")
            placeholder_g3.plotly_chart(gauge_chart(row["Vehicle_Speed_kmh"], "Speed km/h", 0, 200,
                                                    [{'range': [0, 120], 'color': "lightgreen"},
                                                     {'range': [120, 200], 'color': "orange"}]),
                                       use_container_width=True, key=f"g3_{i}")
            placeholder_g4.plotly_chart(gauge_chart(row["Throttle_Position_Percent"], "Throttle %", 0, 100,
                                                    [{'range': [0, 60], 'color': "lightgreen"},
                                                     {'range': [60, 85], 'color': "orange"},
                                                     {'range': [85, 100], 'color': "red"}]),
                                       use_container_width=True, key=f"g4_{i}")
            time.sleep(playback_speed)
else:
    st.info("⬅ Upload your vehicle dataset to see diagnostics.")
