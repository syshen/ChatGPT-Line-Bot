from dotenv import load_dotenv

load_dotenv(".env")
from src.orders import Order


order = Order({"orders": [], "total": 100})
order.createNewOrder()
