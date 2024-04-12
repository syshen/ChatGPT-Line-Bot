import json
from src.psqldb import posgresdb
from src.logger import logger
from psycopg2 import sql

customer_id = "B0794"


class Customer:
    @classmethod
    def getCustomerById(self, customer_id):
        try:
            query = sql.SQL("SELECT * FROM customers WHERE customer_id = %s")
            rows = posgresdb.execute(query, values=[customer_id])
            return rows
        except Exception as e:
            logger.error("DB error", e)

    @classmethod
    def setCustomerLineId(self, customer_id, line_id):
        try:
            query = sql.SQL("UPDATE customers SET line_id = %s WHERE customer_id = %s")
            posgresdb.execute(query, values=[line_id, customer_id])
        except Exception as e:
            logger.error("DB error", e)
