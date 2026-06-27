"""
Harness Inspector — chain-aware extension of message_inspector.py
Port: 8011 (leave 8010 for original single-turn inspector)
Shows: node sequence, state delta per node, token consumption per node.
"""

import json
import sys

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html

sys.path.insert(0, "..")
from deepvoxel.application.runner import run_engagement

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = dbc.Container(
    [
        html.H3("deepVoxel Harness Inspector", className="mt-3 mb-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Engagement Slug"),
                        dcc.Input(id="slug-input", value="liponexus", style={"width": "100%"}),
                        dbc.Button("Run Chain", id="run-btn", color="primary", className="mt-2"),
                    ],
                    width=3,
                ),
                dbc.Col(
                    [
                        html.Label("Chain Summary"),
                        html.Div(
                            id="chain-summary",
                            style={
                                "background": "#2a2a2a",
                                "padding": "10px",
                                "height": "150px",
                                "overflow": "auto",
                                "fontFamily": "monospace",
                                "fontSize": "12px",
                            },
                        ),
                    ],
                    width=9,
                ),
            ]
        ),
        html.Hr(),
        html.H5("Node Detail"),
        dcc.Dropdown(id="node-selector", placeholder="Select node to inspect..."),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Messages In"),
                        dcc.Textarea(
                            id="messages-in",
                            style={
                                "width": "100%",
                                "height": "350px",
                                "fontFamily": "monospace",
                                "fontSize": "11px",
                            },
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Label("Response Out"),
                        dcc.Textarea(
                            id="response-out",
                            style={
                                "width": "100%",
                                "height": "350px",
                                "fontFamily": "monospace",
                                "fontSize": "11px",
                            },
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dcc.Store(id="state-store"),
    ],
    fluid=True,
)


@app.callback(
    Output("state-store", "data"),
    Output("chain-summary", "children"),
    Output("node-selector", "options"),
    Input("run-btn", "n_clicks"),
    State("slug-input", "value"),
    prevent_initial_call=True,
)
def run_chain(n_clicks, slug):
    if not slug:
        return {}, "No slug provided.", []
    state = run_engagement(slug)
    state_dict = state.__dict__
    lines = [
        f"Engagement: {state.engagement_id}",
        f"API calls:  {len(state.call_log)}",
        f"Technology: {state.technology_description[:120]}",
        f"Personnel:  {state.named_personnel}",
        "",
    ] + [
        f"  [{c['node']}]  in={c['usage']['input_tokens']}  out={c['usage']['output_tokens']}"
        for c in state.call_log
    ]
    options = [{"label": c["node"], "value": i} for i, c in enumerate(state.call_log)]
    return state_dict, html.Pre("\n".join(lines)), options


@app.callback(
    Output("messages-in", "value"),
    Output("response-out", "value"),
    Input("node-selector", "value"),
    State("state-store", "data"),
    prevent_initial_call=True,
)
def show_node(node_idx, state_data):
    if node_idx is None or not state_data:
        return "", ""
    call = state_data["call_log"][node_idx]
    return json.dumps(call["messages_in"], indent=2), call["response_text"]


if __name__ == "__main__":
    app.run(debug=True, port=8011)
