# Raspberry Pi Temperature Monitor

A simple Raspberry Pi project that fetches local weather data from OpenWeatherMap and displays temperature, feels-like
temperature, humidity, and city name on an I2C LCD display. The display cycles through different weather information. It
also sends notifications via Pushover and also Telegram when temperatures are critically hot or cold.

## Features

- Fetches live weather data for a specified city using OpenWeatherMap API
- Displays temperature, feels-like temperature, humidity, and city name on a 16x2 I2C LCD (PCF8574)
- Sends push notifications for extreme temperatures using Pushover and Telegram Bot
- Runs continuously on a Raspberry Pi with graceful shutdown handling
- Uses `.env` file for secure API key and token management

## Requirements

- Raspberry Pi with I2C enabled
- 16x2 I2C LCD display (using PCF8574 backpack)
- Python 3.7+
- Libraries:
  - `RPLCD`
  - `requests`
  - `python-dotenv`

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
    sudo apt install python3-smbus i2c-tools
    ```

3. Create a `.env` file in the project root with your API keys:

    ```env
    WEATHER_API_KEY=your_openweathermap_api_key

    # Pushover credentials
    PUSHOVER_TOKEN=your_pushover_app_token
    PUSHOVER_USER=your_pushover_user_key

    # Telegram credentials (optional)
    TELEGRAM_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    ```

4. Enable I2C on your Raspberry Pi if not already done:

    ```bash
    sudo raspi-config
    # Navigate to Interface Options -> I2C -> Enable
    ```

5. Run the monitor script:

    ```bash
    python3 main.py
    ```

## Configuration

- Change city and country in `weather_constants.py`
- Adjust temperature thresholds in `weather_constants.py`
- Adjust display rotation interval in `constants.py`

## Usage

The display cycles through:
- City name
- Temperature
- Feels-like temperature
- Humidity

Push notifications are sent when temperature exceeds configured hot or cold thresholds.
Notifications are sent via:

- Pushover (if PUSHOVER_TOKEN and PUSHOVER_USER are set)

- Telegram Bot (if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are set)

## License

This project is licensed under the MIT License.

---

*Feel free to contribute or raise issues on GitHub!*

