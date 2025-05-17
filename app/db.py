import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()  # This loads environment variables from .env

class Database:
    def __init__(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,
            dbname="djdb",
            user="djdb_owner",
            password=os.getenv("DB_PASSWORD"),
            host="ep-snowy-dust-a1pxcpyg-pooler.ap-southeast-1.aws.neon.tech",
            port="5432",
            sslmode="require"
        )

    def get_db(self):
        return self.pool.getconn()

    def put_db(self, conn):
        self.pool.putconn(conn)

db = Database()
