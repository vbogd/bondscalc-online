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
    return [
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
    ]
