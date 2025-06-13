import requests

from weather.weather_constants import CITY, COUNTRY
from weather.weather_data import WeatherData


class WeatherAPI:
    def __init__(self, api_key):
        self.api_url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={CITY},{COUNTRY}&units=metric&appid={api_key}"
        )

    def get_weather_temp(self) -> WeatherData | None:
        try:
            response = requests.get(self.api_url, timeout=5)
            data = response.json()
            return WeatherData.from_dict(data["main"])
        except Exception as e:
            print(f"API error: {e}")
            return None
