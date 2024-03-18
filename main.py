from dotenv import load_dotenv

load_dotenv(".env")

from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError

from linebot.v3.messaging import (
    ReplyMessageRequest,
    PushMessageRequest,
    MessagingApi,
    ApiClient,
    Configuration,
    # MessageEvent,
    # TextMessage,
    # TextSendMessage,
    FlexContainer,
    FlexMessage,
    # ImageSendMessage,
    # AudioMessage,
)

from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    TextMessageContent,
    # AudioMessageContent,
    PostbackContent,
)
import os
import json
import uuid
import functools

from src.logger import logger
from src.n8n import N8N
from src.utils import get_role_and_content
from src.orders import Order


app = Flask(__name__)
n8n = N8N(api_key=os.getenv("N8N_API_KEY"))
configuration = Configuration(access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
# line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)
    return "OK"


@handler.add(PostbackEvent)
def handle_postback_message(event):
    user_id = event.source.user_id
    text = event.postback.data
    logger.info(event)
    logger.info(f"{user_id}: {text}")
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            if text.startswith("confirm_order"):
                order_id = text.split(" ")[1]
                is_successful, response, error_message = n8n.confirmOrder(order_id)
                if not is_successful:
                    raise Exception(error_message)

                Order.confirmOrder(order_id)
                bubble = FlexContainer.from_dict(response["message"])
                msg = FlexMessage(alt_text=response["alt_message"], contents=bubble)

                line_bot_api.reply_message(
                    ReplyMessageRequest(reply_token=event.reply_token, messages=[msg])
                )
        except ValueError as e:
            logger.error(e)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    message_id = event.message.id
    logger.info(event)
    logger.info(f"{user_id}: {text}")

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        try:
            is_successful, response, error_message = n8n.identifyOrders(
                message_id, text
            )
            if not is_successful:
                raise Exception(error_message)
            logger.info(response)
            if response["total"] == 0:
                return
                # order = Order(response)
                # order.createNewOrder()
                # role, response = get_role_and_content(response)
                # msg = TextSendMessage(text=response["message"])

            customer_id = "C0A38F95-C8FB-4C62-902C-6379ADC6BC11"
            Order.createNewOrder(
                customer_id,
                message_id,
                orders=response["orders"],
                total=response["total"],
                line_id=user_id,
            )
            bubble = FlexContainer.from_json(json.dumps(response["message"]))
            msg = FlexMessage(alt_text=response["alt_message"], contents=bubble)
            logger.info(msg)
            line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=event.reply_token, messages=[msg])
            )

        except ValueError as e:
            logger.error(e)
            # msg = TextSendMessage(text="Token 無效，請重新註冊，格式為 /註冊 sk-xxxxx")
        except KeyError as e:
            logger.error(e)
            # msg = TextSendMessage(text="請先註冊 Token，格式為 /註冊 sk-xxxxx")
        except Exception as e:
            logger.error(e)


@app.route("/", methods=["GET"])
def home():
    return "Hello World"


@app.route("/push", methods=["POST"])
def push():
    content = request.json
    line_id = content["line_id"]
    message = content["message"]
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        push_message_req = PushMessageRequest.from_dict(
            {"to": line_id, "messages": [{"type": "text", "text": message}]}
        )
        # x_line_retry_key = 'x_line_retry_key_example'
        try:
            resp = line_bot_api.push_message(push_message_req)
        except Exception as e:
            logger.error(e)
    return "Hello World"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
