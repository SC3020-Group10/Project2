import os
import time
from typing import List
from collections import deque

import matplotlib.pyplot as plt
from Graph.graph_utils import get_tree_node_pos
from igraph import Graph as IGraph

from QueryAnalyzer.explainer import Explainer
from QueryAnalyzer.explainers.default_explain import default_explain
from QueryAnalyzer.utils import get_tree_node_pos


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
    
    @staticmethod
    def create_explanation(query_plan):
        node_type = query_plan["Node Type"]
        explainer = Explainer.explainer_map.get(node_type, default_explain)
        return explainer(query_plan)
    
    def has_children(self):
        return bool(self.children)
    
class Graph:
    def __init__(self, query_json):
        self.root = Node(query_json)
        self.nodes = []
        self.edges = []
        self._construct_graph(self.root, query_json)

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


if __name__ == "__main__":
    from Database.engine import Engine
    engine = Engine()

    raw_query = """
        SELECT * 
        FROM umbrellas AS u, loans AS l
        WHERE u.id = l.umbrella_id
        AND u.location = 3;
    """

    query_json = engine.get_query_plan(raw_query)
    print(query_json)
    graph = Graph(query_json, raw_query)
    explanation = graph.create_explanation(graph.root)

    print(explanation)