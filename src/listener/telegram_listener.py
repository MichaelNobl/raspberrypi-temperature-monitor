from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from weather.weather_api import WeatherAPI


class TelegramListener:
    def __init__(self, bot_token: str, chat_id: str, weather_api: WeatherAPI):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.weather_api = weather_api
        self.app = ApplicationBuilder().token(bot_token).build()

        # Register command handlers
        self.app.add_handler(CommandHandler("weather", self.handle_weather))
        self.app.add_handler(CommandHandler("help", self.handle_help))

    def is_authorized(self, update: Update) -> bool:
        return str(update.effective_chat.id) == self.chat_id

    async def handle_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update):
            await update.message.reply_text("Unauthorized")
            return

        try:
            if self.weather_api.weather_data is not None:
                weather_data = (
                    f"Temp: {self.weather_api.weather_data.temp}"
                    f"Feels: {self.weather_api.weather_data.feels_like}"
                    f"Humidity: {self.weather_api.weather_data.humidity}"
                )
                await update.message.reply_text(weather_data)
            else:
                await update.message.reply_text(f"Currently no weather data available")
        except Exception as e:
            await update.message.reply_text(f"Error reading temp: {e}")

    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.is_authorized(update):
            await update.message.reply_text("Unauthorized")
            return

        help_text = (
            "Available commands:\n"
            "/weather - Show current weather data\n"
            "/help - Show this message"
        )
        await update.message.reply_text(help_text)

    def run(self):
        print("Bot is running...")
        self.app.run_polling()
