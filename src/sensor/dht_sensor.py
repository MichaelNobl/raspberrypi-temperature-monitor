import adafruit_dht
import board
import time

from sensor.room_data import RoomData

class DHT22Reader:
    def __init__(self, pin=board.D4, retries=5, delay=1):
        self.dht_device = adafruit_dht.DHT22(pin)
        self.retries = retries
        self.delay = delay  # seconds between retries

    def read(self) -> RoomData | None:
        for attempt in range(self.retries):
            try:
                temperature = self.dht_device.temperature
                humidity = self.dht_device.humidity
                if temperature is not None and humidity is not None:
                    return RoomData(temperature, humidity)
                else:
                    print(f"Attempt {attempt+1}: Got None values. Retrying...")
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(self.delay)

        print("❌ Failed to read from DHT22 after multiple attempts.")
        return None
