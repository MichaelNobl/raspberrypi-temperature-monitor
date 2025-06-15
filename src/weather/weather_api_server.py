from flask import Flask, jsonify
from weather.weather_data import WeatherData

class WeatherAPIServer:
    def __init__(self):
        self.app = Flask(__name__)
        self._latest_weather = WeatherData(temp=0, feels_like=0, humidity=0, temp_min=0, temp_max=0, pressure=0)

        # Set up routes
        self.app.add_url_rule("/weather", "weather", self.get_weather)

    def get_weather(self):
        return jsonify({
            "temp": self._latest_weather.temp,
            "feels_like": self._latest_weather.feels_like,
            "humidity": self._latest_weather.humidity
        })

    def update_weather(self, weather_data: WeatherData):
        self._latest_weather = weather_data

    def run(self, host="0.0.0.0", port=5000):
        print(f"🌦️  Starting Flask weather server on port {port}")
        self.app.run(host=host, port=port)
