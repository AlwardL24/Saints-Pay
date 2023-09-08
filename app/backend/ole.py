import requests
import urllib.parse
import re


class OLE:
    class Error(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

        pass

    username = None
    password = None
    cookie = None

    def __init(self, username: str, password: str):
        self.username = username
        self.password = password

        self.login()

    def get_headers(self):
        return {
            "Accept": "text/html, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 SaintsPayBot/1.0 (+https://saintspay.lucasalward.com/bot)",
            "Cookie": self.cookie,
        }.copy()

    def login(self):
        # Post request to /api/session
        # Request body
        # form data encoded
        # username: username
        # password: password

        url = "https://ole.saintkentigern.com/api/session"

        payload = {
            "username": self.username,
            "password": self.password,
        }

        headers = self.get_headers()
        headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
        )

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 400:
            raise OLE.Error(f"{response.text}")
        elif response.status_code not in [200, 302]:
            raise OLE.Error("An unknown error occurred while logging in.")

        self.cookie = response.headers["Set-Cookie"]
