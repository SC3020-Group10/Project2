import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db = os.getenv("DATABASE")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")
# db = "TPC-H"
# user = "postgres"
# password = "a"
# host = "localhost"
# port = 5432

class Engine:
    def __init__(self) -> None:
        conn = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)
        self.cursor = conn.cursor()

    def get_query_plan(self, raw_query:str) -> dict:
        self.cursor.execute(f"EXPLAIN (FORMAT JSON) {raw_query}")
        result = self.cursor.fetchone()[0]
        return result[0]['Plan']