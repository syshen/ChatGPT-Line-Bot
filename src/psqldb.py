import os
import psycopg2
import pandas as pd
from src.logger import logger


class PostgreSQL:
    """
    Initializes the database connection parameters.

    Args:
        dbname (str): The name of the database. Defaults to the value of the environment variable PSQL_DB_DBNAME.
        user (str): The username for the database connection. Defaults to the value of the environment variable PSQL_DB_USER.
        password (str): The password for the database connection. Defaults to the value of the environment variable PSQL_DB_PWD.
        host (str): The host address of the database server. Defaults to the value of the environment variable PSQL_DB_HOST.
        port (str): The port number of the database server. Defaults to the value of the environment variable PSQL_DB_PORT.
    """

    def __init__(self, dbname=None, user=None, password=None, host=None, port=None):
        self.dbname = dbname or os.getenv("PSQL_DB_DBNAME")
        self.user = user or os.getenv("PSQL_DB_USER")
        self.password = password or os.getenv("PSQL_DB_PWD")
        self.host = host or os.getenv("PSQL_DB_HOST")
        self.port = port or os.getenv("PSQL_DB_PORT")
        self.conn = None

    def connect(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = psycopg2.connect(
            database=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def execute(self, query, values=None):
        if self.conn is None or self.conn.closed != 0:
            self.connect()
        with self.conn.cursor() as curs:
            logger.info(f"DB execute: {query}")
            curs.execute(query, values)
            self.conn.commit()
            logger.info("DB committed")


posgresdb = PostgreSQL()
