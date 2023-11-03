import os
import time
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
from Graph.graph_utils import get_tree_node_pos

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
        return "Plans" in self.raw_json
    
class Graph:
    def __init__(self, query_json:dict, raw_query:str):
        self.graph = nx.DiGraph()
        self.root = Node(query_json)
        self._construct_graph(self.root)
        self.raw_query = raw_query

    def _construct_graph(self, curr_node:Node):
        self.graph.add_node(curr_node)
        if curr_node.has_children():
            for child in curr_node.raw_json["Plans"]:
                child_node = Node(child)
                self.graph.add_edge(curr_node, child_node)
                self._construct_graph(child_node)

    def serialize_graph_operation(self) -> str:
        node_list = [self.root.node_type]
        for start, end in nx.edge_bfs(self.graph, self.root):
            node_list.append(end.node_type)
        return "#".join(node_list)

    def calculate_total_cost(self):
        return sum([x.cost for x in self.graph.nodes])

    def calculate_plan_rows(self):
        return sum([x.plan_rows for x in self.graph.nodes])

    def calculate_num_nodes(self, node_type: str):
        node_count = 0
        for node in self.graph.nodes:
            if node.node_type == node_type:
                node_count += 1
        return node_count
    
    def save_graph_file(self):
        graph_name = f"graph_{str(time.time())}.png"
        filename = os.path.join("plots", graph_name)
        plot_formatter_position = get_tree_node_pos(self.graph, self.root)
        node_labels = {x: str(x) for x in self.graph.nodes}
        nx.draw(
            self.graph,
            plot_formatter_position,
            with_labels=True,
            labels=node_labels,
            font_size=6,
            node_size=300,
            node_color="skyblue",
            node_shape="s",
            alpha=1,
        )
        plt.savefig(filename)
        plt.clf()
        return filename

    def create_explanation(self, node: Node):
        if not node.has_children:
            return [node.explanation]
        else:
            result = []
            for child in self.graph[node]:
                result += self.create_explanation(child)
            result += [node.explanation]
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