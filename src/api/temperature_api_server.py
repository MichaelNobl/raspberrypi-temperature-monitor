from flask import Flask, jsonify
from weather.weather_data import WeatherData
from sensor.room_data import RoomData

class TemperatureApiServer:
    def __init__(self):
        self.app = Flask(__name__)
        self._latest_weather = WeatherData(temp=0, feels_like=0, humidity=0, temp_min=0, temp_max=0, pressure=0)
        self._latest_room_data = WeatherData(temp=0, feels_like=0, humidity=0, temp_min=0, temp_max=0, pressure=0)

        # Set up routes
        self.app.add_url_rule("/weather", "weather", self.get_weather)
        self.app.add_url_rule("/room", "room", self.get_room_data)

    def get_weather(self):
        return jsonify({
            "temp": self._latest_weather.temp,
            "feels_like": self._latest_weather.feels_like,
            "humidity": self._latest_weather.humidity
        })

    def get_room_data(self):
        return jsonify({
            "temp": self._latest_room_data.temp,
            "humidity": self._latest_room_data.humidity
        })

    def update_weather(self, weather_data: WeatherData):
        self._latest_weather = weather_data

    def update_room_data(self, room_data: WeatherData):
        self._latest_room_data = room_data

    def run(self, host="0.0.0.0", port=5000):
        print(f"🌦️  Starting Flask weather server on port {port}")
        self.app.run(host=host, port=port)
