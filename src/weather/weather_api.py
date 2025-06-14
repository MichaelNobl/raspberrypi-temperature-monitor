import requests

from weather.weather_constants import CITY, COUNTRY
from weather.weather_data import WeatherData
from flask import Flask, jsonify


class WeatherAPI:
    def __init__(self, api_key):
        self.api_url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={CITY},{COUNTRY}&units=metric&appid={api_key}"
        )

        self.weather_data = None

    def get_weather_temp(self) -> WeatherData | None:
        try:
            response = requests.get(self.api_url, timeout=5)
            data = response.json()
            self.weather_data = WeatherData.from_dict(data["main"])
            return self.weather_data
        except Exception as e:
            print(f"API error: {e}")
            return None

    