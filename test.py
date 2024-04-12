from dotenv import load_dotenv

load_dotenv(".env")
from linebot.v3.messaging import (
    FlexContainer,
)
import json
import os
from src.n8n import N8N

message = {
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [{"type": "text", "text": "請問您是要訂購:"}],
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {"type": "text", "text": "沙拉油 x1, 價格: 100"},
            {"type": "text", "text": "葵花籽油 x1, 價格: 200"},
            {"type": "separator"},
            {"type": "text", "text": "總價: 300"},
        ],
    },
    "footer": {
        "type": "box",
        "layout": "horizontal",
        "spacing": "sm",
        "contents": [
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "postback",
                    "label": "確認",
                    "data": "confirm_order",
                },
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {"type": "postback", "label": "取消", "data": "cancel_order"},
            },
        ],
        "flex": 0,
    },
}

message2 = {
    "type": "bubble",
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [{"type": "text", "text": "Brown Cafe"}],
    },
    "footer": {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": [
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "CALL",
                    "uri": "https://linecorp.com",
                },
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                    "type": "uri",
                    "label": "WEBSITE",
                    "uri": "https://linecorp.com",
                },
            },
        ],
        "flex": 0,
    },
}

n8n = N8N(api_key=os.getenv("N8N_API_KEY"))

print(n8n.identifyOrders("test12345", "豆奶6罐，謝謝"))
# print(n8n.confirmOrder("abdc123456"))
# json_str = json.dumps(message)
# print(json_str)
# bubble = FlexContainer.from_json(json_str)
# print(bubble)
