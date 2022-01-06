import requests
from typing import Union

from loguru import logger

from config import TOKEN, EMAIL

# NOTE API DOCS: https://zvukogram.com/node/api/


class ZvukogramApiError(Exception):
    def __init__(self, error, *args: object) -> None:
        super().__init__(error, *args)
        self.error = error

    def __str__(self) -> str:
        return self.error


class Zvukogram:
    API_URL = "https://zvukogram.com/index.php?r=api/text"

    def __init__(self, token=None, email=None) -> None:
        self.token = token or TOKEN
        self.email = email or EMAIL

    def _check_response(self, response: requests.Response):
        # TODO check response content-type
        try:
            response_data = response.json()
        except Exception as e:
            raise ZvukogramApiError("No JSON response")
        if response_data["status"] == -1:
            raise ZvukogramApiError(response_data["error"])

    @staticmethod
    def _save_file(fileurl, filename=None) -> Union[str, bytes]:
        response = requests.get(fileurl)
        assert response.headers["content-type"] in ("audio/mpeg",), "Wrong content-type"
        if filename:
            open(filename, "wb").write(response.content)
            return filename
        else:
            return response.content

    def from_text(self, text, voice="Светлана", filename=None):
        # TODO class of request params
        if len(text) <= 300:
            return self.fast_voice_acting(text, voice, filename)
        else:
            # TODO write long voice acting
            raise ValueError("Length of text more 300 symbols")

    def fast_voice_acting(self, text, voice="Светлана", filename=None):
        params = {
            "token": self.token,
            "email": self.email,
            "voice": voice,
            "text": text,
        }
        response = requests.post(self.API_URL, params=params)
        self._check_response(response)
        response_data = response.json()
        fileurl = response_data["file"]
        return self._save_file(fileurl, filename)


def test_from_text():
    z_api = Zvukogram()
    return z_api.from_text("Привет, Максим!", filename="test.mp3")
