from Graph.graph import Graph

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