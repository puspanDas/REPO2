# app.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import streamlit as st
import plotly.express as px

# --------------------
# Streamlit Page Setup
# --------------------
st.set_page_config(
    page_title="Weather Prediction App",
    page_icon="🌤",
    layout="wide"
)

# --------------------
# Load Dataset
# --------------------
DATA_PATH = "weather_data.csv"  # Place your Kaggle CSV here
try:
    data = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error(f"CSV file '{DATA_PATH}' not found! Please add it to your project folder.")
    st.stop()

# Clean column names
data.columns = [col.strip() for col in data.columns]

# Convert date column
date_col = 'Formatted Date'
if date_col not in data.columns:
    st.error(f"Date column '{date_col}' not found!")
    st.stop()

data[date_col] = pd.to_datetime(data[date_col], errors='coerce')

# Encode categorical cols
categorical_cols = ['Summary', 'Precip Type', 'Daily Summary']
label_encoders = {}
for col in categorical_cols:
    if col in data.columns:
        le = LabelEncoder()
        data[col] = data[col].astype(str)
        data[col] = le.fit_transform(data[col])
        label_encoders[col] = le

# --------------------
# Select Target Variable
# --------------------
st.markdown("## 🌦 Minimalistic Weather Prediction App")
st.markdown("Get predictions based on historical weather patterns, powered by scikit-learn and Streamlit.")

target_col = st.selectbox(
    "🎯 Select Target Variable",
    [col for col in data.columns if col != date_col],
    index=3  # Default: "Temperature (C)" usually
)

# Prepare features & target
X = data.drop(columns=[target_col, date_col], errors='ignore')
y = data[target_col]
X = X.fillna(method='ffill').select_dtypes(include=[np.number])

# --------------------
# Train Model
# --------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

# --------------------
# UI Layout: Two Columns
# --------------------
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Input Features")
    date_input = st.date_input("📅 Select Date")
    input_data = {}

    for feature in X.columns:
        if feature in label_encoders:
            le = label_encoders[feature]
            selected_class = st.selectbox(f"{feature}", le.classes_)
            input_data[feature] = le.transform([selected_class])[0]
        else:
            default_val = float(data[feature].mean())
            input_data[feature] = st.number_input(feature, value=default_val)

    if st.button("🔮 Predict"):
        features_array = np.array(list(input_data.values())).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        st.markdown(
            f"""
            <div style='background:#f0f0f5; padding:15px; border-radius:10px; font-size:18px; text-align:center'>
            ✅ Predicted <b>{target_col}</b> for <b>{date_input}</b>:
            <span style='color:green; font-size:22px;'>{prediction:.2f}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

with col2:
    st.subheader(f"📈 Historical Trend - {target_col}")
    fig = px.line(
        data,
        x=date_col,
        y=target_col,
        title=f"{target_col} Over Time",
        template="plotly_white"
    )
    fig.update_traces(line=dict(color="#4A90E2", width=2))
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Pandas, scikit-learn, and Plotly")
