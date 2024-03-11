import requests
from src.logger import logger


class N8N:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://n8n.jidou.xyz/webhook/"

    def identifyOrders(self, message_id, message):
        return self._request(
            "POST",
            "orders/identify",
            body={"message": message, "message_id": message_id},
        )

    def _request(self, method, endpoint, body=None, files=None):
        self.headers = {"HTMM_KEY": self.api_key}
        try:
            if method == "GET":
                r = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
            elif method == "POST":
                if body:
                    self.headers["Content-Type"] = "application/json"
                logger.info(body)
                r = requests.post(
                    f"{self.base_url}{endpoint}",
                    headers=self.headers,
                    json=body,
                    files=files,
                )
            r = r.json()
            if r.get("error"):
                return False, None, r.get("error", {}).get("message")
            else:
                return True, r, None
        except Exception as e:
            logger.error(e)
            return False, None, "N8N 系統不穩定，請稍後再試"
