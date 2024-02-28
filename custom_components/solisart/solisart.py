"""All Solisart related logic."""

import base64

from lxml import etree
import requests

from homeassistant.core import HomeAssistant

from .const import SOLISART_ID, URL, URL_DATA


def encodeXML(values: list[list[int, str]]) -> str:
    xml = "<valeurs>"
    for value in values:
        xml += '<valeur donnee="'
        xml += str(value[0])
        xml += '" valeur="'
        xml += base64.b64encode(bytes(value[1], "utf-8")).decode("utf-8")
        xml += '" />'
    xml += "</valeurs>"
    return base64.b64encode(bytes(xml, "utf-8")).decode("utf-8")


class Solisart:
    """Encapsulates logic for retrieving data from Solisart."""

    def __init__(
        self, user: str, password: str, hass: HomeAssistant, session: requests.Session
    ):
        self._username = user
        self._password = password
        self._hass = hass
        self._session = session

    async def log_in_to_get_cookie(self) -> bool:
        """Log in to renew the cookie."""

        payload = {
            "id": self._username,
            "pass": self._password,
            "ihm": "admin",
            "connexion": "Se connecter",
        }
        files = []
        headers = {}

        session = self._session
        response = await self._hass.async_add_executor_job(
            lambda: session.request(
                "POST", URL, headers=headers, data=payload, files=files
            )
        )

        # TODO: Parse response in case it didn't work
        # TODO: Get solisart ID from the call

        return True

    async def fetch_data(self) -> dict[str, any]:
        """Fetch data from Solisart."""

        await (
            self.log_in_to_get_cookie()
        )  # TODO: Only relog in when needed (fetching fails)

        payload = {"id": SOLISART_ID, "heure": "0", "periode": "0"}
        files = []
        headers = {
            # 'Accept': 'application/xml, text/xml, */*; q=0.01',
            # 'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'Connection': 'keep-alive',
            # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Origin': 'https://my.solisart.fr',
            # 'Referer': 'https://my.solisart.fr/admin/?page=installation&id=SC1M20234001',
            # 'Sec-Fetch-Dest': 'empty',
            # 'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            # 'X-Requested-With': 'XMLHttpRequest',
            # 'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            # 'sec-ch-ua-mobile': '?0',
            # 'sec-ch-ua-platform': '"Windows"'
        }

        session = self._session
        response = await self._hass.async_add_executor_job(
            lambda: session.request(
                "POST", URL_DATA, headers=headers, data=payload, files=files
            )
        )

        # TODO: Check if there's an error and if so, log in and retry

        data = {}
        xmlRoot = etree.fromstring("\n".join(response.text.split("\n")[1:]))  # noqa: S320
        for value in xmlRoot.iter("valeur"):
            # print(value.get("donnee"),base64.b64decode(value.get("valeur")))
            data[int(value.get("donnee"))] = base64.b64decode(
                value.get("valeur")
            ).decode("utf-8")

        return data
