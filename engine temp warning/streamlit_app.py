import streamlit as st
import requests

st.title("Engine Temperature Warning App")

# Input widget for engine temperature
temperature = st.number_input("Enter Engine Temperature (°C)", min_value=0.0, max_value=150.0, step=0.1)

if st.button("Check Warning"):
    if temperature:
        url = "http://127.0.0.1:5000/api/temperature"
        payload = {"temperature": temperature}
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                st.write(f"Temperature Recorded: {data['temperature']} °C")
                if data['warning']:
                    st.error("Warning: Engine temperature too high!")
                else:
                    st.success("Engine temperature is normal.")
            else:
                st.error(f"Error: Received status code {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to backend API. Is the Flask server running?")
    else:
        st.warning("Please enter a temperature value.")
