# Raspberry Pi Temperature Monitor

A simple Raspberry Pi project that fetches local weather data from OpenWeatherMap and displays temperature, feels-like
temperature, humidity, and city name on an I2C LCD display. The display cycles through different weather information. It
also reads indoor temperature and humidity using a DHT22 sensor and sends notifications via Pushover and Telegram when
temperatures are critically hot or cold.

## Features

- Fetches **outdoor weather data** from OpenWeatherMap
- Reads **indoor temperature & humidity** via a DHT22 sensor
- Displays all data on a 16x2 I2C LCD (PCF8574)
- Sends push notifications for extreme **indoor or outdoor** temperatures
- Available data over HTTP API (via Flask)
- Telegram bot can provide current readings on request
- Graceful shutdown support and runs continuously

## Requirements

- Raspberry Pi with I2C and GPIO enabled
- 16x2 I2C LCD display (PCF8574 backpack)
- DHT22 temperature/humidity sensor
- Python 3.7+
- Libraries:
  - `RPLCD`
  - `requests`
  - `python-dotenv`
  - `Flask`
  - `adafruit-circuitpython-dht`
  - `RPi.GPIO`

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/YourUsername/raspberrypi-temperature-monitor.git
    cd raspberrypi-temperature-monitor
    ```

2. Install dependencies:

    ```bash
    python3 -m pip install -r requirements.txt
    sudo apt update
    sudo apt install python3-smbus i2c-tools libgpiod2
    ```

3. Enable I2C and GPIO on your Raspberry Pi:

    ```bash
    sudo raspi-config
    # Navigate to Interface Options -> I2C -> Enable
    # Also ensure GPIO is available
    ```

4. Create a `.env` file in the project root:

    ```env
    WEATHER_API_KEY=your_openweathermap_api_key

    # Pushover credentials
    PUSHOVER_TOKEN=your_pushover_app_token
    PUSHOVER_USER=your_pushover_user_key

    # Telegram credentials (optional)
    TELEGRAM_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    ```

5. Run the monitor script:

    ```bash
    python3 src/main.py
    ```

## Configuration

- Change city and country in `weather_constants.py`
- Adjust temperature thresholds (indoor/outdoor) in `weather_constants.py`
- Adjust display rotation interval in `constants.py`
- Set the DHT22 GPIO pin in `dht_sensor.py` (e.g., `board.D4`)

## Wiring the DHT22 Sensor

If your DHT22 module includes a built-in pull-up resistor, use the following wiring:

| DHT22 Pin | Connect to Raspberry Pi |
|----------|--------------------------|
| VCC (+)  | 3.3V (Pin 1)             |
| DATA     | GPIO (e.g. GPIO4 – Pin 7)|
| GND (-)  | GND (e.g. Pin 6)         |

Make sure the sensor is firmly connected to avoid read errors.

## Usage

The LCD display cycles through:
- Outdoor City
- Outdoor Temperature
- Feels-like Temperature
- Outdoor Humidity
- Indoor Room Temperature
- Indoor Room Humidity

Push notifications are sent when temperatures exceed defined thresholds.

### Notifications
- **Pushover** (if PUSHOVER_TOKEN and PUSHOVER_USER are set)
- **Telegram Bot** (if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set)

### API & Telegram Bot

- A small Flask API exposes current readings at:

- You can also request weather and indoor readings through your Telegram bot.

## License

This project is licensed under the MIT License.

---

*Feel free to contribute or raise issues on GitHub!*
