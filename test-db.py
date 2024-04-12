from dotenv import load_dotenv

load_dotenv(".env")
from src.orders import Order

print(Order.getOrder("503168800570212529"))
