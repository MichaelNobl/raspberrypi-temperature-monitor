from temperature_monitor import TemperatureMonitor
from dotenv import load_dotenv
import os

def main():
    load_dotenv()

    weather_api_key = os.getenv("WEATHER_API_KEY")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    pushover_user = os.getenv("PUSHOVER_USER")

    monitor = TemperatureMonitor(api_key=weather_api_key, pushover_token=pushover_token, pushover_user=pushover_user)
    monitor.run()

if __name__ == "__main__":
    main()
