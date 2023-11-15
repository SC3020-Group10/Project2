import dash
import dash_daq as daq
from dash import dcc, html
import plotly.express as px
from igraph import Graph as IG
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from explore import QueryPlan, Graph, Node, Engine

# Initialize the app frontend and database engine.
app = dash.Dash(__name__)
engine = Engine()

# Creates traces for drawing the graph
def create_plotly_traces(pos:dict, graph:Graph):
    nt_x = []
    nt_y = []
    nt_t = []
    et_x = []
    et_y = []

    for node_id, position in pos.items():
        nt_x.append(position[0])
        nt_y.append(position[1])
        node:Node = graph.nodes[node_id]
        nt_t.append(f"{node.node_type}<br>Cost:{node.cost}")

    for start_node, end_node in graph.edges:
        start_position = pos[start_node]
        end_position = pos[end_node]
        et_x += [start_position[0], end_position[0], None]
        et_y += [start_position[1], end_position[1], None]
    edge_trace = go.Scatter(x=et_x, y=et_y, line=dict(width=0.5, color='#888'), hoverinfo='none', mode='lines')
    node_trace = go.Scatter(x=nt_x, y=nt_y, text=nt_t, mode='markers+text', hoverinfo='text', marker=dict(showscale=False, color=[], size=10, line_width=2))

    return edge_trace, node_trace


# Creates histogram of the number of tuples accessed per data block.
def generate_histogram(blocks):
    heatmap = px.histogram(
        blocks, 
        range_y=[0, engine.get_block_size()],
        title="Number of tuples accessed per data block"
    )
    heatmap.update_layout(
        xaxis_title="Data Blocks",
        yaxis_title="Number of tuples"
    )
    return heatmap

# Creates query execution plan information
def generate_qep_info(graph, q_plan):
    return html.Div([
        html.H1("Information about Query"),
        html.Div(
            style={
                'display': 'flex',
                'gap': '50px',
            },
            children=[
                html.Div([
                    html.H2('Block Size'),
                    html.P(f"{engine.get_block_size()} bytes")
                ]),
                html.Div([
                    html.H2('Planning Time'),
                    html.P(f"{q_plan.planning_time} milliseconds")
                ]),
                html.Div([
                    html.H2('Execution Time'),
                    html.P(f"{q_plan.execution_time} milliseconds")
                ]),
                html.Div([
                    html.H2('Estimated Cost'),
                    html.P(f"{graph.root.cost}")
                ]),
            ]
        )
    ])

# Creates switches to toggle between whether Seq scan, Index scan and Bitmap scan
# should be considered.
def generate_boolean_switches():
    return html.Div(
        style={'display': 'flex', 'gap': '20px', 'padding': "20px 50px"},
        children=[
            daq.BooleanSwitch(
                id='seq-scan',
                label='Sequential Scan',
                labelPosition='bottom',
                on=True
            ),
            daq.BooleanSwitch(
                id='index-scan',
                label='Index Scan',
                labelPosition='bottom',
                on=True
            ),
            daq.BooleanSwitch(
                id='bitmap-scan',
                label='Bitmap Scan',
                labelPosition='bottom',
                on=True
            )
        ]
    )

app.layout = html.Div([
    html.H2("Toggle to disable scans!"),
    generate_boolean_switches(),
    html.P("Note: If no other scans are possible, DBMS will still choose the disabled scan"),
    dcc.Textarea(id='sql-input', style={'width': '100%', 'height': 100}),
    html.Button('Parse SQL', id='parse-button', n_clicks=0),
    html.Div(id='parsed-output'),
    dcc.Graph(id='graph-visual'),
    html.Div(id='query-info'),
    html.H2("Select table to visualize data blocks"),
    dcc.Dropdown(value=0, id='table-dropdown'),
    dcc.Graph(id='data-blocks-histogram')
])

# Main function to parse SQL to be executed when the parse SQL function is
# pressed.
@app.callback(
    [Output('parsed-output', 'children'),
     Output('graph-visual', 'figure'),
     Output('query-info', 'children'),
     Output('table-dropdown', 'options'),
     Output('data-blocks-histogram', 'figure')],
    [Input('parse-button', 'n_clicks'),
     Input('table-dropdown', 'value')],
    [dash.dependencies.State('seq-scan', 'on'),
    dash.dependencies.State('index-scan', 'on'),
    dash.dependencies.State('bitmap-scan', 'on'),
    dash.dependencies.State('sql-input', 'value')]
)
def parse_sql(n_clicks, table_idx, enable_seqscan, enable_indexscan, enable_bitmapscan, value):
    if n_clicks > 0:
        try:
            q_plan = QueryPlan(engine.get_query_plan(value, enable_seqscan, enable_indexscan, enable_bitmapscan))     
        except Exception as e:
            print(e)
            engine.conn.rollback()
            return [
                dcc.Markdown('<h2>There was a problem with executing your query. Please try again with a different query.</h2>', dangerously_allow_html=True),
                go.Figure(), 
                html.Div(''), 
                [],
                go.Figure()
            ]
        block_size = engine.get_block_size()
        print(f"enable_seqscan: {enable_seqscan}")
        print(f"enable_indexscan: {enable_indexscan}")
        print(f"enable_bitmapscan: {enable_bitmapscan}")
        tables_name = engine.get_tables(value)

        # Query Explanation
        graph = q_plan.graph
        explanation = graph.create_explanation(graph.root)
        exp_f = ""
        for i, e in enumerate(explanation):
            exp_f += f"{i+1}) {e}\n\n"

        # Query Execution Plan
        ig = IG()
        for node in graph.nodes:
            ig.add_vertex(node)
        for start_node, end_node in graph.edges:
            ig.add_edge(start_node, end_node)
        layout = ig.layout("tree", 0)
        pos = {i: layout[i] for i, _ in enumerate(graph.nodes)}
        edge_trace, node_trace = create_plotly_traces(pos, graph)
        layout = go.Layout(showlegend=False, hovermode='closest',
                            margin=dict(b=20,l=5,r=5,t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))

        # QEP Tree
        fig = go.Figure(data=[edge_trace, node_trace], layout=layout)

        # Information about Query
        query_info = generate_qep_info(graph, q_plan)
        # Histogram
        try:
            blocks = engine.get_blocks(value, table_idx)
            heatmap = generate_histogram(blocks)

            fig = go.Figure(data=[edge_trace, node_trace], layout=layout)
            return [
                dcc.Markdown(exp_f, dangerously_allow_html=True), 
                fig, 
                query_info, 
                [{'label': name, 'value': i} for i, name in enumerate(tables_name)], 
                heatmap
            ]
        except Exception as e:
            exp_f = "<h2>There was an error in the estimation of block usage</h2>\n" + exp_f
            return [
                dcc.Markdown(exp_f, dangerously_allow_html=True), 
                go.Figure(), 
                query_info,
                [],
                go.Figure()
            ]

    return [
        html.Div(''), 
        go.Figure(), 
        html.Div(''), 
        [],
        go.Figure()
    ]
    