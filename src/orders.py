import json
from src.psqldb import posgresdb
from src.logger import logger
from psycopg2 import sql


class Order:
    def __init__(self, payload=None):
        self.payload = payload

    def createNewOrder(self):
        json_str = json.dumps(self.payload["orders"])
        customer_id = "C0A38F95-C8FB-4C62-902C-6379ADC6BC11"
        query = sql.SQL(
            "INSERT INTO orders (total, items, customer_id) VALUES (%s, %s, %s)"
        )
        # query = f"INSERT INTO orders (total, items, customer_id) VALUES ('{self.payload['total']}', '{json_str}', 'C0A38F95-C8FB-4C62-902C-6379ADC6BC11')"
        posgresdb.insert(query, values=[self.payload["total"], json_str, customer_id])
