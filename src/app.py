# -*- coding: utf-8 -*-
import atexit

import dash
from apscheduler.triggers.interval import IntervalTrigger
from dash import Dash
import dash_bootstrap_components as dbc
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from data import update_local_bonds_db, db_create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], use_pages=True)
server = app.server
scheduler = BackgroundScheduler()

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


def init_app():
    db_create_tables()
    scheduler.start()
    update_local_bonds_db()
    scheduler.add_job(
        func=update_local_bonds_db,
        trigger=IntervalTrigger(hours=1),
        replace_existing=True,
    )
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


init_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
