import dash
import igraph
from dash import dcc, html
from Graph.graph import Graph
from igraph import Graph as IG
import plotly.graph_objects as go
from Database.engine import Engine
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
engine = Engine()
fig = go.Figure()

def create_plotly_traces(pos, graph):
    nt_x = []
    nt_y = []
    nt_t = []
    et_x = []
    et_y = []

    for node_id, position in pos.items():
        nt_x.append(position[0])
        nt_y.append(position[1])
        nt_t.append(f"{graph.nodes[node_id].raw_json}")

    for start_node, end_node in graph.edges:
        start_position = pos[start_node]
        end_position = pos[end_node]
        et_x += [start_position[0], end_position[0], None]
        et_y += [start_position[1], end_position[1], None]
    edge_trace = go.Scatter(x=et_x, y=et_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    node_trace = go.Scatter(x=nt_x, y=nt_y, text=nt_t, mode='markers+text', hoverinfo='text', marker=dict(showscale=False, color=[], size=10, line_width=2))

    return edge_trace, node_trace

app.layout = html.Div([
    dcc.Textarea(id='sql-input', style={'width': '100%', 'height': 100}),
    html.Button('Parse SQL', id='parse-button', n_clicks=0),
    html.Div(id='parsed-output'),
    dcc.Graph(id='graph-visual')
])

@app.callback(
    [Output('parsed-output', 'children'),
     Output('graph-visual', 'figure')],
    Input('parse-button', 'n_clicks'),
    [dash.dependencies.State('sql-input', 'value')]
)
def parse_sql(n_clicks, value):
    if n_clicks > 0:
        # try:
        q_plan = engine.get_query_plan(value)
        graph = Graph(q_plan)
        explanation = graph.create_explanation(graph.root)
        exp_f = ""
        for i, e in enumerate(explanation):
            exp_f += f"{i+1}) {e}\n\n"
        ig = IG()
        for node in graph.nodes:
            ig.add_vertex(node)
        for start_node, end_node in graph.edges:
            ig.add_edge(start_node, end_node)
        layout = ig.layout('kk')
        pos = {i: layout[i] for i, node in enumerate(graph.nodes)}
        edge_trace, node_trace = create_plotly_traces(pos, graph)
        layout = go.Layout(showlegend=False, hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))

        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
        return [dcc.Markdown(exp_f, dangerously_allow_html=True), fig]
        # except Exception as e:
        #     return [html.Div(f'Error: {str(e)}'), go.Figure()]
    return [html.Div(''), go.Figure()]

if __name__ == "__main__":
    app.run_server(debug=True, threaded=True)