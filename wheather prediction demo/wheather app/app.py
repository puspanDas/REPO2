import requests

# Your actual API key from OpenWeatherMap
API_KEY = "7bf5c5a62213c2be1199c5e8caefb547"

def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        print("\n--- Current Weather ---")
        print(f"City: {data['name']}")
        print(f"Temperature: {data['main']['temp']}°C")
        print(f"Weather: {data['weather'][0]['description'].title()}")
    else:
        print(f"❌ Error {response.status_code}: {data.get('message', 'Unknown error')}")

def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        print("\n--- Upcoming Forecast ---")
        for item in data["list"][:5]:  # next 5 intervals (3‑hourly)
            time = item["dt_txt"]
            temp = item["main"]["temp"]
            condition = item["weather"][0]["description"].title()
            print(f"{time} | {temp}°C | {condition}")
    else:
        print(f"❌ Error {response.status_code}: {data.get('message', 'Unknown error')}")

if __name__ == "__main__":
    city_name = input("Enter city name: ").strip()
    if city_name:
        get_current_weather(city_name)
        get_forecast(city_name)
    else:
        print("⚠ City name cannot be empty.")
