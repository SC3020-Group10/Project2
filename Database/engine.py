import os
import psycopg2
from sql_metadata import Parser
import sqlparse
from ast import literal_eval
from dotenv import load_dotenv

load_dotenv()

db = os.getenv("DATABASE")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")

def remove_group_order_from_query(statement:sqlparse.sql.Statement, table_name):
    new_query = ""
    skip = False

    for token in statement.tokens:
        if skip and token.ttype is None:
            skip = False
            continue

        if token.value == "SELECT":
            new_query += f"{token.value} ({table_name}.ctid::text::point)[0]::bigint"
            skip = True
        
        elif token.value == "GROUP BY" or token.value == "ORDER BY":
            skip = True
        
        else:
            new_query += token.value

    return sqlparse.format(new_query, reindent=True, keyword_case='upper')

class Engine:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)
        self.block_size = None

    def get_query_plan(self, raw_query:str, enable_seqscan:bool, enable_indexscan:bool, enable_bitmapscan:bool) -> dict:
        query = f"EXPLAIN (ANALYZE, BUFFERS, COSTS, FORMAT JSON) {raw_query}"
        
        if not enable_seqscan:
            query = "SET LOCAL enable_seqscan = OFF;\n" + query
        if not enable_indexscan:
            query = "SET LOCAL enable_indexscan = OFF;\n" + query
        if not enable_bitmapscan:
            query = "SET LOCAL enable_bitmapscan = OFF;\n" + query

        cursor = self.conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()[0]
        cursor.execute("ROLLBACK;")
        return result[0]
    
    def get_block_size(self):
        if self.block_size is None:
            cursor = self.conn.cursor()
            cursor.execute("show block_size")
            result = cursor.fetchone()[0]
            self.block_size = result
        return self.block_size
    
    def get_tables(self, raw_query:str):
        parser = Parser(raw_query)
        return parser.tables
    
    def get_table_aliases(self, raw_query:str):
        parser = Parser(raw_query)
        return parser.tables_aliases
    
    def get_blocks(self, raw_query:str, table_idx=0):
        table_name = self.get_tables(raw_query)[table_idx]
        table_aliases = self.get_table_aliases(raw_query)

        statement = sqlparse.format(raw_query, reindent=True, keyword_case='upper')
        statement = sqlparse.parse(statement)[0]

        success = False
        for alias, tb_name in table_aliases.items():
            if success:
                break

            if table_name == tb_name:
                try:
                    new_query = remove_group_order_from_query(statement, table_name=alias)
                    cursor = self.conn.cursor()
                    cursor.execute(new_query)
                    success = True
                except:
                    self.conn.rollback()
                    cursor = self.conn.cursor()
                    new_query = remove_group_order_from_query(statement, table_name=table_name)
                    cursor.execute(new_query)
                    success = True

        if not success:
            new_query = remove_group_order_from_query(statement, table_name=table_name)
            cursor = self.conn.cursor()
            cursor.execute(new_query)

        ctids = cursor.fetchall()
        ctids = [c[0] for c in ctids]

        return ctids