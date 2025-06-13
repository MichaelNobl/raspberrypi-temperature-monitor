import os
from typing import Tuple

from dotenv import load_dotenv

from monitoring.temperature_monitor import TemperatureMonitor
from notifications.pushover import PushoverNotifier
from src.weather.weather_api import WeatherAPI


def main():
    load_dotenv()

    test, pushover_notifier = init_notifier()
    weather_api = init_weather_api()

    monitor = TemperatureMonitor(weather_api, pushover_notifier)
    monitor.run()


def init_notifier() -> Tuple[str, PushoverNotifier]:
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")

    pushover_notifier = PushoverNotifier(pushover_token, pushover_user)
    return "test", pushover_notifier


def init_weather_api() -> WeatherAPI:
    weather_api_key = os.getenv("WEATHER_API_KEY")
    return WeatherAPI(weather_api_key)

if __name__ == "__main__":
    main()
