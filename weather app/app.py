import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
import plotly.graph_objects as go

# --------------------
# CONFIG
# --------------------
st.set_page_config(page_title="Global Weather + Forecast", page_icon="🌤", layout="centered")
API_KEY = "7bf5c5a62213c2be1199c5e8caefb547"  # <<< Replace with your actual API key
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
ONECALL_URL = "https://api.openweathermap.org/data/2.5/onecall/timemachine"
AQI_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# --------------------
# HELPER: Get city coordinates
# --------------------
def get_city_coordinates(city_name):
    params = {"q": city_name, "limit": 1, "appid": API_KEY}
    r = requests.get(GEOCODE_URL, params=params)
    if r.status_code == 200 and r.json():
        data = r.json()[0]
        return data["lat"], data["lon"]
    return None, None

# --------------------
# HELPER: Fetch historical weather
# --------------------
def fetch_historical_weather(lat, lon, days=5):
    records = []
    for d in range(days, 0, -1):
        dt = int((datetime.utcnow() - timedelta(days=d)).timestamp())
        params = {"lat": lat, "lon": lon, "dt": dt, "appid": API_KEY, "units": "metric"}
        r = requests.get(ONECALL_URL, params=params)
        if r.status_code == 200:
            data = r.json()
            hourly = data.get("hourly", [])
            temps = [h["temp"] for h in hourly]
            humidity = [h["humidity"] for h in hourly]
            wind = [h["wind_speed"] for h in hourly]
            if temps:
                records.append({
                    "date": datetime.utcfromtimestamp(dt).date(),
                    "temp": np.mean(temps),
                    "humidity": np.mean(humidity),
                    "wind": np.mean(wind)
                })
    return pd.DataFrame(records)

# --------------------
# UI
# --------------------
st.title("🌦 Global Weather + Multi-Day Forecast")
st.markdown("Enter any city to get current weather, air quality, and 3-day predictions using multiple models.")

city = st.text_input("🌍 Enter City Name", "Kolkata")
model_type = st.selectbox("📈 Choose Prediction Model", ["Linear Regression", "Polynomial Regression", "Moving Average", "Exponential Smoothing"])

if st.button("Get Weather & Forecast"):
    if not API_KEY or API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        st.error("⚠ Please set your OpenWeatherMap API key in the code.")
        st.stop()

    with st.spinner("Fetching weather data..."):
        lat, lon = get_city_coordinates(city)
        if lat is None:
            st.error("❌ Could not find the city coordinates. Try another city.")
            st.stop()

        # Current weather
        current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(current_url)
        if r.status_code != 200:
            st.error("❌ API error fetching current weather.")
            st.stop()
        current_data = r.json()

        st.subheader(f"📍 Current Weather in {city.title()}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌡 Temperature (°C)", f"{current_data['main']['temp']:.1f}")
            st.metric("🤒 Feels Like (°C)", f"{current_data['main']['feels_like']:.1f}")
            st.metric("💧 Humidity (%)", current_data["main"]["humidity"])
            st.metric("🌫 Visibility (km)", f"{current_data.get('visibility', 0)/1000:.1f}")
        with col2:
            st.metric("🌥 Condition", current_data["weather"][0]["description"].title())
            st.metric("💨 Wind Speed (km/h)", f"{current_data['wind']['speed'] * 3.6:.1f}")
            st.metric("📈 Pressure (mb)", current_data["main"]["pressure"])
            dew_point = current_data["main"].get("dew_point", "N/A")
            st.metric("🧊 Dew Point (°C)", f"{dew_point}")

        # Smart alerts
        if current_data["main"]["humidity"] > 85:
            st.warning("🌧 Very humid day ahead. Stay hydrated!")
        if "rain" in current_data["weather"][0]["description"].lower():
            st.info("🌦 Scattered rain showers expected. Carry an umbrella!")

        # Air Quality Index
        aqi_params = {"lat": lat, "lon": lon, "appid": API_KEY}
        aqi_response = requests.get(AQI_URL, params=aqi_params)
        if aqi_response.status_code == 200:
            aqi_data = aqi_response.json()
            aqi_index = aqi_data["list"][0]["main"]["aqi"]
            aqi_map = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
            st.metric("🌬 Air Quality Index", f"{aqi_index} - {aqi_map.get(aqi_index, 'Unknown')}")

        # Forecasted conditions
        forecast_response = requests.get(FORECAST_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
        if forecast_response.status_code == 200:
            forecast_data = forecast_response.json()
            st.subheader("🌤 Forecast Conditions (Next 3 Days)")
            for i in range(3):
                entry = forecast_data["list"][i * 8]  # every 8th entry ≈ 24 hours
                date = datetime.utcfromtimestamp(entry["dt"]).date()
                condition = entry["weather"][0]["description"].title()
                st.write(f"📅 {date}: {condition}")

        # Historical fetch + Prediction
        df_hist = fetch_historical_weather(lat, lon, days=5)
        if df_hist.empty:
            st.warning("⚠ Not enough historical data available for prediction.")
        else:
            X = np.arange(len(df_hist)).reshape(-1, 1)
            y_temp = df_hist["temp"].values
            y_humidity = df_hist["humidity"].values
            y_wind = df_hist["wind"].values

            future_days = 3
            future_indices = np.arange(len(df_hist), len(df_hist) + future_days).reshape(-1, 1)

            def predict_series(y, model_type):
                if model_type == "Linear Regression":
                    model = LinearRegression().fit(X, y)
                    return model.predict(future_indices), model.predict(X)
                elif model_type == "Polynomial Regression":
                    poly = PolynomialFeatures(degree=2)
                    X_poly = poly.fit_transform(X)
                    model = LinearRegression().fit(X_poly, y)
                    return model.predict(poly.transform(future_indices)), model.predict(X_poly)
                elif model_type == "Moving Average":
                    return [np.mean(y[-3:])] * future_days, y
                elif model_type == "Exponential Smoothing":
                    alpha = 0.5
                    smoothed = y[0]
                    for val in y[1:]:
                        smoothed = alpha * val + (1 - alpha) * smoothed
                    return [smoothed] * future_days, y

            pred_temp, temp_fit = predict_series(y_temp, model_type)
            pred_humidity, _ = predict_series(y_humidity, model_type)
            pred_wind, _ = predict_series(y_wind, model_type)

            # Confidence interval
            rmse = np.sqrt(mean_squared_error(y_temp, temp_fit))
            st.info(f"📊 Temperature Prediction Confidence: ±{rmse:.2f} °C")

            # Display predictions
            st.subheader("📅 3-Day Forecast")
            for i in range(future_days):
                day = df_hist["date"].max() + timedelta(days=i+1)
                st.write(f"**{day}**")
                st.metric("🌡 Temp (°C)", f"{pred_temp[i]:.2f}")
                st.metric("💧 Humidity (%)", f"{pred_humidity[i]:.0f}")
                st.metric("💨 Wind Speed (km/h)", f"{pred_wind[i]*3.6:.1f}")

            # Plotly chart
            future_dates = [df_hist["date"].max() + timedelta(days=i+1) for i in range(future_days)]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_hist["date"], y=df_hist["temp"], mode="lines+markers", name="Historical Temp"))