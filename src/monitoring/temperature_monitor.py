#!/usr/bin/env python3
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from RPLCD.i2c import CharLCD

from src.monitoring.constants import WEATHER_UPDATE_INTERVAL, DISPLAY_ROTATE_INTERVAL, \
    DISPLAY_WIDTH, ZONE_INFO
from src.monitoring.display_mode import DisplayMode
from src.weather.weather_constants import CITY, TOLERANCE, THRESHOLD_HOT, THRESHOLD_COLD
from ..notifier.pushover_notifier import PushoverNotifier
from ..notifier.telegram_notifier import TelegramNotifier
from ..weather.weather_api import WeatherAPI
from ..weather.weather_data import WeatherData


class TemperatureMonitor:
    def __init__(self, weather_api: WeatherAPI, telegram_notifier: TelegramNotifier | None,
                 pushover_notifier: PushoverNotifier | None):
        self.pushover_notifier = pushover_notifier
        self.telegram_notifier = telegram_notifier
        self.weather_api = weather_api
        self.lcd = CharLCD('PCF8574', 0x27)
        self.alert_sent = False
        self.last_weather_update = 0
        self.last_temp = None
        self.display_mode = DisplayMode.CITY
        self.last_display_switch = 0
        self.last_weather_data = None
        self.scroll_index = 0

    @staticmethod
    def get_local_time_str():
        now = datetime.now(ZoneInfo(ZONE_INFO))
        return now.strftime("%H:%M:%S")

    @staticmethod
    def get_local_date_str():
        now = datetime.now(ZoneInfo(ZONE_INFO))
        return now.strftime("%d.%m.%Y")

    def send_notification_hot(self, temp):
        time_str = TemperatureMonitor.get_local_time_str()
        date_str = TemperatureMonitor.get_local_date_str()
        message = f"🔥 Hot outside: {temp:.1f}°C\n{date_str} {time_str}"
        self.alert_notifiers(message)

    def send_notification_cold(self, temp):
        time_str = TemperatureMonitor.get_local_time_str()
        date_str = TemperatureMonitor.get_local_date_str()
        message = f"❄️ Cold outside: {temp:.1f}°C\n{date_str} {time_str}"
        self.alert_notifiers(message)

    def alert_notifiers(self, message):
        if self.pushover_notifier is not None:
            self.pushover_notifier.send_notification(message)

        if self.telegram_notifier is not None:
            self.telegram_notifier.send_notification(message)

    def update_display(self, weather: WeatherData, current_time):
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(f"Time: {current_time}".ljust(DISPLAY_WIDTH))

        self.lcd.cursor_pos = (0, 0)
        if self.display_mode == DisplayMode.CITY:
            if len(CITY) <= DISPLAY_WIDTH:
                self.lcd.write_string(CITY.ljust(DISPLAY_WIDTH))
            else:
                # Scroll the text
                scroll_text = CITY + " "  # Add a space for cleaner loop
                start = self.scroll_index
                end = start + DISPLAY_WIDTH
                self.lcd.write_string(scroll_text[start:end].ljust(DISPLAY_WIDTH))

                self.scroll_index = (self.scroll_index + 1) % len(scroll_text)
        elif self.display_mode == DisplayMode.TEMP:
            self.lcd.write_string(f"Temp: {weather.temp:.1f}C".ljust(DISPLAY_WIDTH))
        elif self.display_mode == DisplayMode.FEELS_LIKE:
            self.lcd.write_string(f"Feels: {weather.feels_like:.1f}C".ljust(DISPLAY_WIDTH))
        elif self.display_mode == DisplayMode.HUMIDITY:
            self.lcd.write_string(f"Humidity: {weather.humidity}%".ljust(DISPLAY_WIDTH))

    def run(self):
        self.lcd.clear()
        try:
            while True:
                current_time = time.time()

                # Update weather every 5 minutes
                if current_time - self.last_weather_update >= WEATHER_UPDATE_INTERVAL:
                    weather = self.weather_api.get_weather_temp()
                    if weather is not None:
                        self.last_weather_data = weather
                        if weather.temp > THRESHOLD_HOT + TOLERANCE:
                            if not self.alert_sent:
                                self.send_notification_hot(weather.temp)
                                self.alert_sent = True
                        elif weather.temp < THRESHOLD_COLD - TOLERANCE:
                            if not self.alert_sent:
                                self.send_notification_cold(weather.temp)
                                self.alert_sent = True
                        else:
                            self.alert_sent = False
                    self.last_weather_update = current_time

                # Switch display every 10 seconds
                if current_time - self.last_display_switch >= DISPLAY_ROTATE_INTERVAL:
                    self.display_mode = DisplayMode((self.display_mode + 1) % 4)
                    self.last_display_switch = current_time
                    self.scroll_index = 0  # Reset scroll position when mode changes

                time_str = self.get_local_time_str()

                if self.last_weather_data:
                    self.update_display(self.last_weather_data, time_str)
                else:
                    self.lcd.cursor_pos = (0, 0)
                    self.lcd.write_string("Weather Error".ljust(DISPLAY_WIDTH))
                    self.lcd.cursor_pos = (1, 0)
                    self.lcd.write_string(f"Time: {time_str}".ljust(DISPLAY_WIDTH))

                time.sleep(1)

        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            print(f"Error: {e}")

    def shutdown(self):
        self.lcd.clear()
        self.lcd.write_string("Temperature")
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string("Monitor Off")
        time.sleep(2)
        self.lcd.clear()
