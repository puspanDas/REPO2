import streamlit as st
import requests
import json

st.title("Disease Prediction System")

# Backend URL
API_URL = "http://localhost:5000"

# Check backend status
try:
    status = requests.get(f"{API_URL}/status").json()
    if status["model_ready"]:
        st.success("✅ Model is ready")
    else:
        st.warning("⚠️ No model found")
except:
    st.error("❌ Backend not running. Start backend.py first")
    st.stop()

# Train model section
st.header("Model Training")
if st.button("Train New Model"):
    with st.spinner("Training model..."):
        try:
            response = requests.post(f"{API_URL}/train", json={"csv_path": "diseases.csv"})
            result = response.json()
            if result["status"] == "success":
                st.success(f"Model trained! Accuracy: {result['accuracy']:.3f}")
            else:
                st.error(f"Training failed: {result['message']}")
        except Exception as e:
            st.error(f"Error: {e}")

# Prediction section
st.header("Make Prediction")
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", 0, 120, 50)
    bmi = st.number_input("BMI", 10.0, 50.0, 25.0)
    glucose = st.number_input("Glucose", 50.0, 200.0, 100.0)
    blood_pressure = st.number_input("Blood Pressure", 80.0, 200.0, 120.0)
    cholesterol = st.number_input("Cholesterol", 100.0, 300.0, 200.0)
    insulin = st.number_input("Insulin", 0.0, 200.0, 50.0)

with col2:
    skin_thickness = st.number_input("Skin Thickness", 0.0, 50.0, 20.0)
    pregnancies = st.number_input("Pregnancies", 0, 20, 0)
    smoking_status = st.selectbox("Smoking Status", [0, 1])
    exercise_mins = st.number_input("Exercise Minutes/Week", 0.0, 500.0, 150.0)
    family_history = st.selectbox("Family History", [0, 1])

if st.button("Predict Disease Risk"):
    data = [age, bmi, glucose, blood_pressure, cholesterol, insulin, 
            skin_thickness, pregnancies, smoking_status, exercise_mins, family_history]
    
    try:
        response = requests.post(f"{API_URL}/predict", json={"data": data})
        result = response.json()
        
        if "prediction" in result:
            risk = result["risk"]
            prob = max(result["probability"])
            
            if risk == "High":
                st.error(f"🚨 {risk} Risk (Confidence: {prob:.2f})")
            else:
                st.success(f"✅ {risk} Risk (Confidence: {prob:.2f})")
        else:
            st.error(f"Prediction failed: {result['message']}")
    except Exception as e:
        st.error(f"Error: {e}")