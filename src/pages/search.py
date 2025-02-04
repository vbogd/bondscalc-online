import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import logging

from data import moex_search

dash.register_page(__name__, path='/')
logger = logging.getLogger(__name__)

def _get_calc_link(bond: dict):
    secid = bond['secid']
    shortname = bond['shortname']
    return html.Div(
            dcc.Link(shortname, href=f"calc/{secid}")
        )

@callback(
    Output("isin_search_result", "children"),
    Input("isin_search", "value"),
    # prevent_initial_call=True,
)
def search_isin(isin: str):
    if len(isin) < 3:
        return dbc.Label("Введите минимум 3 символа")
    logger.info(f"Search bonds for query: '{isin}' ...")
    bonds = moex_search(isin)
    logger.info(f"Search bonds for query: '{isin}' - found {len(bonds)} bond(s)")
    if len(bonds) == 0:
        return dbc.Label("Ничего не найдено")
    return [_get_calc_link(bond) for bond in bonds]

def layout(**kwargs):
    return dbc.Container([
        html.H4("BondsCalc Online", className="card-title"),
        dbc.Label(
            dcc.Link("надежные-облигации.рус", href="https://надежные-облигации.рус/", target="_blank"),
            className="card-subtitle"
        ),
        dbc.Row(
            [
                dbc.Input(
                    id="isin_search",
                    type="text",
                    value="",
                    placeholder="Название или isin",
                    persistence=True,
                    debounce=True,
                ),
            ],
            className="g-1 pt-1",
        ),
        html.Div(id="isin_search_result")
    ])

    # return  html.Div([
    #     html.Div("поиск"),
    #     _get_calc_link("SU26233RMFS5"),
    #     _get_calc_link("RU000A104JQ3"),
    # ])
