# -*- coding: utf-8 -*-

import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)
server = app.server

app.layout = html.Div([
    # html.Div(
    #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #     ),
    # html.Div([
    #     html.Div(
    #         dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
    #     ) for page in dash.page_registry.values()
    # ]),
    dash.page_container
])

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=8050)
    # app.run(host='0.0.0.0', port=8050)
