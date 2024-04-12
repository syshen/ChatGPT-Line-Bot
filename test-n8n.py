from dotenv import load_dotenv

load_dotenv(".env")
import os

from src.n8n import N8N

n8n = N8N(api_key=os.getenv("N8N_API_KEY"))

print(
    n8n.identifyOrders("42838139ad12", "詠鑠生活 x 古箏餐廳 - B0803", "我要芥花油三箱")
)
