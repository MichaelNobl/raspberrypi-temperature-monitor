from temperature_monitor import TemperatureMonitor
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
    PUSHOVER_USER = os.getenv("PUSHOVER_USER")

    monitor = TemperatureMonitor(api_key=WEATHER_API_KEY, pushover_token=PUSHOVER_TOKEN, pushover_user=PUSHOVER_USER)
    monitor.run()
