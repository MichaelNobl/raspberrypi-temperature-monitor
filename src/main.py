import os
from typing import Tuple

from dotenv import load_dotenv

from listener.telegram_listener import TelegramListener
from monitoring.temperature_monitor import TemperatureMonitor
from notifier.pushover_notifier import PushoverNotifier
from notifier.telegram_notifier import TelegramNotifier
from weather.weather_api import WeatherAPI


def main():
    load_environment()

    telegram_notifier, pushover_notifier = init_notifiers()
    weather_api = init_weather_api()

    init_telegram_listener(weather_api)

    monitor = TemperatureMonitor(
        weather_api=weather_api,
        telegram_notifier=telegram_notifier,
        pushover_notifier=pushover_notifier
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


def init_telegram_listener(weather_api: WeatherAPI):
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    telegram_listener = (
        TelegramListener(bot_token=telegram_token, chat_id=telegram_chat_id, weather_api=weather_api)
        if telegram_token and telegram_chat_id else None
    )

    if telegram_listener is not None:
        telegram_listener.run()


def init_weather_api() -> WeatherAPI:
    return WeatherAPI(api_key=os.getenv("WEATHER_API_KEY"))


def load_environment():
    load_dotenv()

if __name__ == "__main__":
    main()
