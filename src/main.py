import os
from typing import Tuple

from dotenv import load_dotenv

from monitoring.temperature_monitor import TemperatureMonitor
from notifier.pushover_notifier import PushoverNotifier
from notifier.telegram_notifier import TelegramNotifier
from weather.weather_api import WeatherAPI
from weather.weather_api_server import WeatherAPIServer


def main():
    load_environment()

    telegram_notifier, pushover_notifier = init_notifiers()
    weather_api = init_weather_api()

    weather_api_server = WeatherAPIServer()

    from threading import Thread
    flask_thread = Thread(target=weather_api_server.run, daemon=True)
    flask_thread.start()

    monitor = TemperatureMonitor(
        weather_api=weather_api,
        telegram_notifier=telegram_notifier,
        pushover_notifier=pushover_notifier,
        weather_api_server=weather_api_server
    )  

    monitor.run()


def init_notifiers() -> Tuple[TelegramNotifier | None, PushoverNotifier | None]:

    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    pushover_notifier = (
        PushoverNotifier(pushover_token, pushover_user)
        if pushover_token and pushover_user else None
    )

    telegram_notifier = (
        TelegramNotifier(telegram_token, telegram_chat_id)
        if telegram_token and telegram_chat_id else None
    )

    return telegram_notifier, pushover_notifier

def init_weather_api() -> WeatherAPI:
    return WeatherAPI(api_key=os.getenv("WEATHER_API_KEY"))


def load_environment():
    load_dotenv()

if __name__ == "__main__":
    main()
