import http.client
import urllib.parse


class PushoverNotifier:
    def __init__(self, token: str, user_token: str):
        self.token = token
        self.userToken = user_token

    def send_notification(self, message: str, priority: int = 1):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": self.token,
                         "user": self.userToken,
                         "message": message,
                         "priority": priority
                     }), {
                         "Content-type": "application/x-www-form-urlencoded"
                     }
                     )
        conn.getresponse()
