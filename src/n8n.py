import requests
from src.logger import logger
import os


class N8N:
    def __init__(self, api_key: str):
        self.api_key = api_key
        n8n_env = os.getenv("N8N_ENV")
        self.base_url = f"https://n8n.jidou.xyz/webhook{n8n_env}/"

    def identifyOrders(self, message_id, group_name, message):
        return self._request(
            "POST",
            "orders/identify",
            body={
                "message": message,
                "message_id": message_id,
                "group_name": group_name,
            },
        )

    def confirmOrder(self, order_id):
        return self._request(
            "POST",
            "orders/confirm",
            body={"order_id": order_id},
        )

    def cancelOrder(self, order_id):
        return self._request("POST", "orders/cancel", body={"order_id": order_id})

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
