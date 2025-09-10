import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

# --------------------
# CONFIG
# --------------------
st.set_page_config(page_title="Live India Weather + Prediction", page_icon="🌤", layout="centered")
API_KEY = "7bf5c5a62213c2be1199c5e8caefb547"  # <<< Replace with your actual API key
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
ONECALL_URL = "https://api.openweathermap.org/data/2.5/onecall/timemachine"

# --------------------
# HELPER: Get city coordinates
# --------------------
def get_city_coordinates(city_name):
    params = {"q": f"{city_name},IN", "limit": 1, "appid": API_KEY}
    r = requests.get(GEOCODE_URL, params=params)
    if r.status_code == 200 and r.json():
        data = r.json()[0]
        return data["lat"], data["lon"]
    return None, None

# --------------------
# HELPER: Fetch historical temperature (last N days)
# --------------------
def fetch_historical_weather(lat, lon, days=5):
    records = []
    for d in range(days, 0, -1):
        dt = int((datetime.utcnow() - timedelta(days=d)).timestamp())
        params = {"lat": lat, "lon": lon, "dt": dt, "appid": API_KEY, "units": "metric"}
        r = requests.get(ONECALL_URL, params=params)
        if r.status_code == 200:
            data = r.json()
            temps = [h["temp"] for h in data.get("hourly", [])]
            if temps:
                avg_temp = np.mean(temps)
                records.append({"date": datetime.utcfromtimestamp(dt).date(), "temp": avg_temp})
            else:
                st.warning(f"⚠ No hourly data for {datetime.utcfromtimestamp(dt).date()}. Trying fallback...")
                # Fallback: use current temp if available
                fallback_temp = data.get("current", {}).get("temp")
                if fallback_temp is not None:
                    records.append({"date": datetime.utcfromtimestamp(dt).date(), "temp": fallback_temp})
                else:
                    st.warning(f"❌ No fallback data available for {datetime.utcfromtimestamp(dt).date()}")
        else:
            st.warning(f"❌ API error on day {d}: {r.status_code}")
    return pd.DataFrame(records)

# --------------------
# HELPER: Predict temperature using selected model
# --------------------
def predict_temperature(df, model_type="Linear", days_ahead=1):
    X = np.arange(len(df)).reshape(-1, 1)
    y = df["temp"].values

    if model_type == "Linear":
        model = LinearRegression()
        model.fit(X, y)
        pred = model.predict(np.array([[len(df) + days_ahead - 1]]))[0]

    elif model_type == "Polynomial":
        poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
        poly_model.fit(X, y)
        pred = poly_model.predict(np.array([[len(df) + days_ahead - 1]]))[0]

    elif model_type == "Moving Average":
        pred = np.mean(y[-3:])  # Simple average of last 3 days

    elif model_type == "Exponential Smoothing":
        model = SimpleExpSmoothing(y).fit(smoothing_level=0.6, optimized=False)
        pred = model.forecast(days_ahead)[-1]

    else:
        pred = None

    return pred

# --------------------
# UI
# --------------------
st.title("🌦 Live Indian Weather + Multi-Model Prediction")
st.markdown("Select an Indian city to get current weather and forecast temperatures using different models.")

indian_cities = [
    "Delhi", "Mumbai", "Bengaluru", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
]
city = st.selectbox("🏙 Select City", indian_cities)

model_choice = st.selectbox("📈 Choose Prediction Model", ["Linear", "Polynomial", "Moving Average", "Exponential Smoothing"])
days_ahead = st.slider("📅 Days Ahead to Predict", 1, 5, 1)

if st.button("Get Weather & Predict"):
    if not API_KEY or API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        st.error("⚠ Please set your OpenWeatherMap API key in the code.")
        st.stop()

    lat, lon = get_city_coordinates(city)
    if lat is None:
        st.error("❌ Could not find the city coordinates. Try another city.")
        st.stop()

    # Current weather
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric"
    r = requests.get(current_url)
    if r.status_code != 200:
        st.error("❌ API error fetching current weather.")
        st.stop()
    current_data = r.json()

    # Display live data
    st.subheader(f"📍 Current Weather in {city}")
    icon_code = current_data["weather"][0]["icon"]
    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
    st.image(icon_url, width=100)
    st.metric("🌡 Temperature (°C)", f"{current_data['main']['temp']:.1f}")
    st.metric("💧 Humidity (%)", current_data["main"]["humidity"])
    st.metric("💨 Wind Speed (m/s)", current_data["wind"]["speed"])
    st.metric("🌥 Condition", current_data["weather"][0]["description"].title())

    # Historical fetch + Prediction
    df_hist = fetch_historical_weather(lat, lon, days=5)
    if df_hist.empty:
        st.error("⚠ Not enough historical data available for prediction.")
    else:
        predicted_temp = predict_temperature(df_hist, model_type=model_choice, days_ahead=days_ahead)
        future_date = df_hist["date"].max() + timedelta(days=days_ahead)

        st.success(f"🔮 {model_choice} Prediction for {future_date.strftime('%A, %d %b')}: **{predicted_temp:.2f} °C**")

        # Plotting
        fig, ax = plt.subplots()
        ax.plot(df_hist["date"], df_hist["temp"], marker="o", label="Historical Temp", color="blue")
        ax.plot(future_date, predicted_temp, marker="x", color="red", label=f"{model_choice} Prediction")
        ax.set_title(f"Temperature Trend - {city}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Temperature (°C)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Pandas, NumPy, scikit-learn, Matplotlib, and OpenWeatherMap API")
