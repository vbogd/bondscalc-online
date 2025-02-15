# -*- coding: utf-8 -*-

import dash
from dash import Dash, html
import dash_bootstrap_components as dbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], use_pages=True)
server = app.server

# dbc.Label(
#     dcc.Link(
#         "надежные-облигации.рус",
#         href="https://надежные-облигации.рус/",
#         target="_blank",
#         className="card-subtitle, text-decoration-none"
#     ),
# )

app.layout = dbc.Container([
    dash.page_container
])

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, host='0.0.0.0', port=8050)
    # app.run(host='0.0.0.0', port=8050)
