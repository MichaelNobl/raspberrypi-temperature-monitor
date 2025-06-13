import requests


class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.chat_id = chat_id

        self.url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

    def send_notification(self, message: str):
        payload = {
            'chat_id': self.chat_id,
            'text': message
        }

        requests.post(self.url, data=payload)
