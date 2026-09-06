import requests

def get_weather():
    latitude = 35.6892
    longitude = 51.3890

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    temperature = data["current"]["temperature_2m"]
    weather_code = data["current"]["weather_code"]

    return temperature, weather_code