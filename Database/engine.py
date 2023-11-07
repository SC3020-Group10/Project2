import os
import psycopg2
from sql_metadata import Parser
from collections import Counter
from ast import literal_eval
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
        self.conn = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor()

    def get_query_plan(self, raw_query:str) -> dict:
        self.cursor.execute(f"EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT JSON) {raw_query}")
        result = self.cursor.fetchone()[0]
        return result[0]
    
    def get_block_size(self):
        self.cursor.execute("show block_size")
        result = self.cursor.fetchone()[0]
        return result
    
    def get_tables(self, raw_query:str):
        parser = Parser(raw_query)
        return parser.tables
    
    def get_table_aliases(self, raw_query:str):
        parser = Parser(raw_query)
        return parser.tables_aliases
    
    def get_blocks(self, raw_query:str, table_idx=0):
        table_name = self.get_tables(raw_query)[table_idx]
        table_aliases = self.get_table_aliases(raw_query)

        try:
            for alias, tb_name in table_aliases.items():
                if table_name == tb_name:
                    table_name = alias
                    break

            raw_query_lowercase = raw_query.lower()
            raw_query = raw_query[:7] + f"{table_name}.ctid " + raw_query[raw_query_lowercase.find("from"):]

            raw_query_lowercase = raw_query.lower()
            if "group by" not in raw_query_lowercase:            
                if "order by" not in raw_query_lowercase:
                    if raw_query_lowercase[-1] == ";":
                        raw_query = raw_query[:-1] + f" ORDER BY {table_name}.ctid;"
                    else:
                        raw_query += f" ORDER BY {table_name}.ctid;"

                else:
                    raw_query = raw_query[:raw_query_lowercase.find("order by")] + f"ORDER BY {table_name}.ctid;"

            else:
                raw_query = raw_query[:raw_query_lowercase.find("group by")] + f"ORDER BY {table_name}.ctid;"

            self.cursor.execute(raw_query)
            ctids = self.cursor.fetchall()
        
        except:
            self.conn.rollback()
            self.cursor = self.conn.cursor()
            table_name = self.get_tables(raw_query)[table_idx]

            raw_query_lowercase = raw_query.lower()
            raw_query = raw_query[:7] + f"{table_name}.ctid " + raw_query[raw_query_lowercase.find("from"):]

            raw_query_lowercase = raw_query.lower()
            if "group by" not in raw_query_lowercase:            
                if "order by" not in raw_query_lowercase:
                    if raw_query_lowercase[-1] == ";":
                        raw_query = raw_query[:-1] + f" ORDER BY {table_name}.ctid;"
                    else:
                        raw_query += f" ORDER BY {table_name}.ctid;"

                else:
                    raw_query = raw_query[:raw_query_lowercase.find("order by")] + f"ORDER BY {table_name}.ctid;"

            else:
                raw_query = raw_query[:raw_query_lowercase.find("group by")] + f"ORDER BY {table_name}.ctid;"

            self.cursor.execute(raw_query)
            ctids = self.cursor.fetchall()

        ctids = [literal_eval(c[0])[0] for c in ctids]
        return ctids