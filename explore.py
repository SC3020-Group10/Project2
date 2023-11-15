import os
import psycopg2
import sqlparse
from typing import List
from collections import deque
from dotenv import load_dotenv
from sql_metadata import Parser

from explore_helper import Explorer, default_explain

# Environment variables for the connection to the pg database
load_dotenv()
db = os.getenv("DATABASE")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")

# Removes group ordering from the query, since there is a problem with doing ctid
# when groupby is in the query.
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

# Engine for database, connects to database and allows the 
# sending of queries to the database.
class Engine:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)
        self.block_size = None

    # From SQL query sent through UI's textbox, explains the query plan and
    # returns the result of explanation.
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
            self.block_size = int(result)
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

# Node class for the specific node, to be used in the graph display
# to show the cost and other stuff
class Node:
    def __init__(self, query_plan:dict) -> None:
        self.node_type = query_plan["Node Type"]
        self.cost = query_plan["Total Cost"]
        self.parent_relationship = query_plan.get("Parent Relationship")
        self.relation = query_plan.get("Relation Name")
        self.alias = query_plan.get("Alias")
        self.startup_cost = query_plan.get("Startup Cost")
        self.plan_rows = query_plan.get("Plan Rows")
        self.plan_width = query_plan.get("Plan Width")
        self.filter = query_plan.get("Filter")
        self.raw_json = query_plan
        self.children = []
        self.explanation = self.create_explanation(query_plan)

    def __str__(self):
        name_string = f"{self.node_type}\ncost: {self.cost}"
        return name_string
    
    # Given a query plan, creates an explanation for the query plan
    @staticmethod
    def create_explanation(query_plan):
        node_type = query_plan["Node Type"]
        explorer = Explorer.explorer_map.get(node_type, default_explain)
        return explorer(query_plan)
    
    def has_children(self):
        return bool(self.children)

# Main graph that will show the entire node display of the query plan
class Graph:
    def __init__(self, plan):
        self.root = Node(plan)
        self.nodes:List[Node] = []
        self.edges = []
        self._construct_graph(self.root, plan)

    def _construct_graph(self, parent_node, query_plan):
        parent_index = len(self.nodes)
        self.nodes.append(parent_node)
        if "Plans" in query_plan:
            for child_plan in query_plan["Plans"]:
                child_node = Node(child_plan)
                child_index = len(self.nodes)
                self.edges.append((parent_index, child_index))
                parent_node.children.append(child_node)
                self._construct_graph(child_node, child_plan)

    def serialize_graph_operation(self) -> str:
        node_list = [self.root.node_type]
        queue = deque([self.root])
        while queue:
            current_node = queue.popleft()
            for child in current_node.children:
                node_list.append(child.node_type)
                queue.append(child)
        return "#".join(node_list)

    def calculate_total_cost(self):
        return sum(node.cost for node in self.nodes)

    def calculate_plan_rows(self):
        return sum(node.plan_rows for node in self.nodes)

    def calculate_num_nodes(self, node_type: str):
        return sum(1 for node in self.nodes if node.node_type == node_type)

    def save_graph_file(self):
        pass

    def create_explanation(self, node: Node):
        result = []
        if node.children:
            for child in node.children:
                result.extend(self.create_explanation(child))
        result.append(node.explanation)
        return result

# Helper class to organise the results of the query plan better
class QueryPlan:
    def __init__(self, query_plan):
        self.query_plan = query_plan
        self.plan = query_plan['Plan']
        self.planning = query_plan['Planning']
        self.planning_time = query_plan['Planning Time']
        self.triggers = query_plan['Triggers']
        self.execution_time = query_plan['Execution Time']
        self.read_blocks = int(query_plan['Plan']["Shared Read Blocks"])
        self.hit_blocks = int(query_plan['Plan']["Shared Hit Blocks"])
        self.graph = Graph(self.plan)