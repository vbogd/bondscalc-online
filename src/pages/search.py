import dash
from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc
import logging

from data import moex_search

dash.register_page(
    __name__,
    path='/',
    title='BondsCalc | поиск'
)

logger = logging.getLogger(__name__)

def _get_calc_link(bond: dict):
    secid = bond['secid']
    shortname = bond['shortname']
    isin = bond['isin']
    return dbc.ListGroupItem(
        [
            html.P(shortname, className="mb-0"),
            html.Small(isin, className="text-muted")
        ],
        href=f"calc/{secid}"
    )

@callback(
    Output("isin_search_result", "children"),
    Input("isin_search", "value"),
)
def search_isin(isin: str):
    if len(isin) < 3:
        return dbc.ListGroupItem("Введите минимум 3 символа")
    logger.info(f"Search bonds for query: '{isin}' ...")
    bonds = moex_search(isin)
    logger.info(f"Search bonds for query: '{isin}' - found {len(bonds)} bond(s)")
    if len(bonds) == 0:
        return dbc.ListGroupItem("Ничего не найдено")
    return [_get_calc_link(bond) for bond in bonds]

def layout(**kwargs):
    return [
        dbc.Row(
            [
                # dbc.Col(
                #     dbc.Button(html.I(className="bi bi-arrow-left"), outline=True, href="/"),
                #     width="auto",
                #     # style=None if show_search else hidden_style,
                # ),
                dbc.Col(
                    dbc.Input(
                        id="isin_search",
                        type="search",
                        value="",
                        minlength=3,
                        placeholder="Название или isin",
                        persistence=True,
                        debounce=1000,
                        size="lg",
                    ),
                ),
            ],
            className="g-1 pt-1 m-2",
        ),
        dbc.ListGroup(
            id="isin_search_result",
            flush=True,
        ),
    ]
