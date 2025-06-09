#!/usr/bin/env python3
from RPLCD.i2c import CharLCD
from weather_data import WeatherData
from constants import THRESHOLD_HOT, THRESHOLD_COLD, TOLERANCE, WEATHER_UPDATE_INTERVAL, DISPLAY_ROTATE_INTERVAL, DISPLAY_WIDTH, ZONE_INFO, CITY, COUNTRY
from display_mode import DisplayMode
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import http.client
import urllib.parse
import requests
import time
import os

class TemperatureMonitor:
    def __init__(self, api_key, pushover_token, pushover_user):
        self.city = CITY
        self.country = COUNTRY
        self.api_key = api_key
        self.pushover_token = pushover_token
        self.pushover_user = pushover_user
        self.lcd = CharLCD('PCF8574', 0x27)
        self.alert_sent = False
        self.last_weather_update = 0
        self.last_temp = None
        self.display_mode = DisplayMode.CITY
        self.last_display_switch = 0
        self.last_weather_data = None
        self.scroll_index = 0

        self.api_url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={self.city},{self.country}&units=metric&appid={self.api_key}"
        )

    def get_weather_temp(self):
        try:
            response = requests.get(self.api_url, timeout=5)
            data = response.json()
            return WeatherData.from_dict(data["main"])
        except Exception as e:
            print(f"API error: {e}")
            return None

    def get_local_time_str(self):
        now = datetime.now(ZoneInfo(ZONE_INFO))
        return now.strftime("%H:%M:%S")

    def get_local_date_str(self):
        now = datetime.now(ZoneInfo(ZONE_INFO))
        return now.strftime("%d.%m.%Y")

    def send_pushover(self, message):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": self.pushover_token,
                "user": self.pushover_user,
                "message": message,
                "priority": 1
            }), {
                "Content-type": "application/x-www-form-urlencoded"
            }
        )
        conn.getresponse()

    def send_pushover_hot(self, temp):
        time_str = self.get_local_time_str()
        date_str = self.get_local_date_str()
        message = f"🔥 Hot outside: {temp:.1f}°C\n{date_str} {time_str}"
        self.send_pushover(message)

    def send_pushover_cold(self, temp):
        time_str = self.get_local_time_str()
        date_str = self.get_local_date_str()
        message = f"❄️ Cold outside: {temp:.1f}°C\n{date_str} {time_str}"
        self.send_pushover(message)

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
                    weather = self.get_weather_temp()
                    if weather:
                        self.last_weather_data = weather
                        if(weather.temp > THRESHOLD_HOT + TOLERANCE):
                            if not self.alert_sent:
                                self.send_pushover_hot(weather.temp)
                                self.alert_sent = True
                        elif(weather.temp < THRESHOLD_COLD - TOLERANCE):
                            if not self.alert_sent:
                                self.send_pushover_cold(weather.temp)
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


if __name__ == "__main__":
    load_dotenv()

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    PUSHOVER_TOKEN = os.getenv("PUSHOVER_TOKEN")
    PUSHOVER_USER = os.getenv("PUSHOVER_USER")

    monitor = TemperatureMonitor(api_key=WEATHER_API_KEY, pushover_token=PUSHOVER_TOKEN, pushover_user=PUSHOVER_USER)
    monitor.run()
