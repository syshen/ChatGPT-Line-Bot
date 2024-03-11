from dotenv import load_dotenv

load_dotenv(".env")

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    ImageSendMessage,
    AudioMessage,
)
import os
import uuid
import functools

from src.models import OpenAIModel
from src.memory import Memory
from src.logger import logger
from src.n8n import N8N
from src.storage import Storage, FileStorage, MongoStorage
from src.utils import get_role_and_content
from src.service.youtube import Youtube, YoutubeTranscriptReader
from src.service.website import Website, WebsiteReader
from src.mongodb import mongodb
from src.orders import Order


app = Flask(__name__)
n8n = N8N(api_key=os.getenv("N8N_API_KEY"))
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
storage = None
youtube = Youtube(step=4)
website = Website()


memory = Memory(memory_message_count=2)

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise Exception("No OPENAI_API_KEY")
user_model = OpenAIModel(api_key=api_key)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()
    message_id = event.message.id
    logger.info(event)
    logger.info(f"{user_id}: {text}")

    try:
        if text.startswith("/歷史"):
            messages = memory.get(user_id)
            full_history = ""
            for m in messages:
                full_history = full_history + "\n" + m["role"] + ": " + m["content"]
            if full_history == "":
                full_history = "目前沒有任何過去紀錄"
            msg = TextSendMessage(text=full_history)

        elif text.startswith("/清除"):
            memory.remove(user_id)
            msg = TextSendMessage(text="歷史訊息清除成功")

        elif text.startswith("/圖像"):
            prompt = text[3:].strip()
            memory.append(user_id, "user", prompt)
            is_successful, response, error_message = user_model.image_generations(
                prompt
            )
            if not is_successful:
                raise Exception(error_message)
            url = response["data"][0]["url"]
            msg = ImageSendMessage(original_content_url=url, preview_image_url=url)
            memory.append(user_id, "assistant", url)

        else:
            memory.append(user_id, "user", text)
            url = website.get_url_from_text(text)
            if url:
                if youtube.retrieve_video_id(text):
                    is_successful, chunks, error_message = (
                        youtube.get_transcript_chunks(youtube.retrieve_video_id(text))
                    )
                    if not is_successful:
                        raise Exception(error_message)
                    youtube_transcript_reader = YoutubeTranscriptReader(
                        user_model, os.getenv("OPENAI_MODEL_ENGINE")
                    )
                    is_successful, response, error_message = (
                        youtube_transcript_reader.summarize(chunks)
                    )
                    if not is_successful:
                        raise Exception(error_message)
                    role, response = get_role_and_content(response)
                    msg = TextSendMessage(text=response)
                else:
                    chunks = website.get_content_from_url(url)
                    if len(chunks) == 0:
                        raise Exception("無法撈取此網站文字")
                    website_reader = WebsiteReader(
                        user_model, os.getenv("OPENAI_MODEL_ENGINE")
                    )
                    is_successful, response, error_message = website_reader.summarize(
                        chunks
                    )
                    if not is_successful:
                        raise Exception(error_message)
                    role, response = get_role_and_content(response)
                    msg = TextSendMessage(text=response)
            else:
                is_successful, response, error_message = n8n.identifyOrders(
                    message_id, text
                )
                # is_successful, response, error_message = user_model.chat_completions(
                #     memory.get(user_id), os.getenv("OPENAI_MODEL_ENGINE")
                # )
                if not is_successful:
                    raise Exception(error_message)
                logger.info(response)
                if response["total"] == 0:
                    return
                # order = Order(response)
                # order.createNewOrder()
                # role, response = get_role_and_content(response)
                # msg = TextSendMessage(text=response["message"])

                msg = FlexSendMessage(
                    alt_text=response["alt_message"], contents=response["message"]
                )
            # memory.append(user_id, role, response)
    except ValueError as e:
        logger.error(e)
        # msg = TextSendMessage(text="Token 無效，請重新註冊，格式為 /註冊 sk-xxxxx")
    except KeyError as e:
        logger.error(e)
        # msg = TextSendMessage(text="請先註冊 Token，格式為 /註冊 sk-xxxxx")
    except Exception as e:
        memory.remove(user_id)
        logger.error(e)
    line_bot_api.reply_message(event.reply_token, msg)


@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    user_id = event.source.user_id
    audio_content = line_bot_api.get_message_content(event.message.id)
    input_audio_path = f"{str(uuid.uuid4())}.m4a"
    with open(input_audio_path, "wb") as fd:
        for chunk in audio_content.iter_content():
            fd.write(chunk)

    try:
        if not user_model:
            raise ValueError("Invalid API token")
        else:
            is_successful, response, error_message = user_model.audio_transcriptions(
                input_audio_path, "whisper-1"
            )
            if not is_successful:
                raise Exception(error_message)
            memory.append(user_id, "user", response["text"])
            is_successful, response, error_message = user_model.chat_completions(
                memory.get(user_id), "gpt-3.5-turbo"
            )
            if not is_successful:
                raise Exception(error_message)
            role, response = get_role_and_content(response)
            memory.append(user_id, role, response)
            msg = TextSendMessage(text=response)
    except ValueError:
        msg = TextSendMessage(text="請先註冊你的 API Token，格式為 /註冊 [API TOKEN]")
    except KeyError:
        msg = TextSendMessage(text="請先註冊 Token，格式為 /註冊 sk-xxxxx")
    except Exception as e:
        memory.remove(user_id)
        if str(e).startswith("Incorrect API key provided"):
            msg = TextSendMessage(text="OpenAI API Token 有誤，請重新註冊。")
        else:
            msg = TextSendMessage(text=str(e))
    os.remove(input_audio_path)
    line_bot_api.reply_message(event.reply_token, msg)


@app.route("/", methods=["GET"])
def home():
    return "Hello World"


if __name__ == "__main__":
    if os.getenv("USE_MONGO"):
        mongodb.connect_to_database()
        storage = Storage(MongoStorage(mongodb.db))
    else:
        storage = Storage(FileStorage("db.json"))

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
