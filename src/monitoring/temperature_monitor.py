#!/usr/bin/env python3
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from RPLCD.i2c import CharLCD

from monitoring.constants import WEATHER_UPDATE_INTERVAL, DISPLAY_ROTATE_INTERVAL, \
    DISPLAY_WIDTH, ZONE_INFO, ROOM_DATA_UPDATE_INTERVAL
from monitoring.display_mode import DisplayMode

from weather.weather_constants import CITY, TOLERANCE, THRESHOLD_HOT, THRESHOLD_COLD
from weather.weather_api import WeatherAPI
from api.temperature_api_server import TemperatureApiServer
from weather.weather_data import WeatherData

from notifier.pushover_notifier import PushoverNotifier
from notifier.telegram_notifier import TelegramNotifier

from sensor.room_data import RoomData 
from sensor.dht_sensor import DHT22Reader 

class TemperatureMonitor:
    def __init__(self, weather_api: WeatherAPI, temperature_api_server : TemperatureApiServer, telegram_notifier: TelegramNotifier | None,
                 pushover_notifier: PushoverNotifier | None, dht_reader : DHT22Reader):
        self.pushover_notifier = pushover_notifier
        self.telegram_notifier = telegram_notifier
        self.weather_api = weather_api
        self.temperature_api_server = temperature_api_server
        self.lcd = CharLCD('PCF8574', 0x27)
        self.alert_sent = False
        self.last_weather_update = 0
        self.last_temp = None
        self.display_mode = DisplayMode.CITY
        self.last_display_switch = 0
        self.last_weather_data = None
        self.scroll_index = 0
        self.last_dht_update = 0
        self.window_alert_sent = False
        self.last_dht_data = None
        self.dht_reader = dht_reader

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

    def send_notification_room(self, message):
        self.alert_notifiers(message)

    def alert_notifiers(self, message):
        if self.pushover_notifier is not None:
            self.pushover_notifier.send_notification(message)

        if self.telegram_notifier is not None:
            self.telegram_notifier.send_notification(message)

    def update_display(self, weather: WeatherData, current_time, room_data : RoomData):
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
        elif self.display_mode == DisplayMode.TEMPOUTDOOR:
            self.lcd.write_string(f"Temp: {weather.temp:.1f}C".ljust(DISPLAY_WIDTH))
        elif self.display_mode == DisplayMode.FEELS_LIKE:
            self.lcd.write_string(f"Feels: {weather.feels_like:.1f}C".ljust(DISPLAY_WIDTH))
        elif self.display_mode == DisplayMode.HUMIDITYOUTDOOR:
            self.lcd.write_string(f"Humidity: {weather.humidity}%".ljust(DISPLAY_WIDTH))
        elif self.display_mode == DisplayMode.HUMIDITYINDOOR:
            self.lcd.write_string(f"Room-Hum: {room_data.humidity}%".ljust(DISPLAY_WIDTH))
        elif self.display_mode == DisplayMode.TEMPINDOOR:
            self.lcd.write_string(f"Room-Temp: {room_data.temp:.1f}C".ljust(DISPLAY_WIDTH))

    def run(self):
        self.lcd.clear()
        try:
            while True:
                current_time = time.time()

                # Update weather every 5 minutes
                if current_time - self.last_weather_update >= WEATHER_UPDATE_INTERVAL:
                    weather = self.weather_api.get_weather_temp()
                    self.temperature_api_server.update_weather(weather)
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

                # Update DHT22 sensor every 10 seconds
                if current_time - self.last_dht_update >= ROOM_DATA_UPDATE_INTERVAL:
                    room_data = self.dht_reader.read()
                    self.temperature_api_server.update_room_data(room_data)

                    if room_data.temp is not None and room_data.humidity is not None:
                        self.last_dht_data = room_data

                        # Trigger notification if air feels humid and warm
                        if room_data.temp > 27 and room_data.humidity > 60:
                            message = (
                                f"🌡️ Warm and humid indoor conditions detected:\n"
                                f"Temperature: {room_data.temp:.1f}°C\n"
                                f"Humidity: {room_data.humidity:.1f}%\n"
                            )
                            if not self.window_alert_sent:
                                self.send_notification_room(message)
                                self.window_alert_sent = True
                        elif room_data.humidity > 70:
                            message = (
                                f"💧 High indoor humidity detected:\n"
                                f"Humidity: {room_data.humidity:.1f}%\n"
                            )
                            if not self.window_alert_sent:
                                self.send_notification_room(message)
                                self.window_alert_sent = True
                        elif room_data.temp > 28:
                            message = (
                                f"🔥 It's quite hot. Time to let some fresh air in!"
                            )
                            if not self.window_alert_sent:
                                self.send_notification_room(message)
                                self.window_alert_sent = True
                        else:
                            self.window_alert_sent = False
                    else:
                        print("⚠️ DHT22 sensor read failed.")

                    self.last_dht_update = current_time

                # Switch display every 10 seconds
                if current_time - self.last_display_switch >= DISPLAY_ROTATE_INTERVAL:
                    self.display_mode = DisplayMode((self.display_mode + 1) % 6)
                    self.last_display_switch = current_time
                    self.scroll_index = 0  # Reset scroll position when mode changes

                time_str = self.get_local_time_str()

                if self.last_weather_data:
                    self.update_display(self.last_weather_data, time_str, self.last_dht_data)
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
