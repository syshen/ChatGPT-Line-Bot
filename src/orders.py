import json
from src.psqldb import posgresdb
from src.logger import logger
from psycopg2 import sql


class Order:
    @classmethod
    def createNewOrder(self, customer_id, order_id, orders=None, total=0, line_id=None):
        try:
            orders_json = json.dumps(orders)
            customer_id = "C0A38F95-C8FB-4C62-902C-6379ADC6BC11"
            query = sql.SQL(
                "INSERT INTO orders (total, items, customer_id, order_id, line_id) VALUES (%s, %s, %s, %s, %s)"
            )
            posgresdb.execute(
                query, values=[total, orders_json, customer_id, order_id, line_id]
            )
        except Exception as e:
            logger.error("DB error", e)

    @classmethod
    def confirmOrder(self, order_id):
        try:
            query = sql.SQL(
                "UPDATE orders SET confirmed = true, confirmed_at = now() WHERE order_id = %s"
            )
            posgresdb.execute(query, values=[order_id])
        except Exception as e:
            logger.error("DB error", e)
