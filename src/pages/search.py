from typing import Any

import dash
from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc
import logging

from data import moex_bonds_db_search, BasicBondInfo

dash.register_page(
    __name__,
    path='/',
    title='BondsCalc | поиск'
)

logger = logging.getLogger(__name__)

_perpetual_mat_date = html.Span("Бессрочно", className="text-danger")

def currency_str(curr: str) -> str:
    if curr == 'SUR': return '₽'
    elif curr == 'USD': return '$'
    elif curr == 'EUR': return '€'
    elif curr == 'CNY': return '¥'
    else: return curr

def _get_calc_link(bond: BasicBondInfo):
    if bond.coupon_percent:
        coupon_str = f'{bond.coupon_value} {currency_str(bond.face_unit)} | {bond.coupon_percent} %'
    else: coupon_str = "-"

    def col(children: Any):
        return dbc.Col(children)
    def auto_col(children: Any):
        return dbc.Col(children, width="auto")

    return dbc.ListGroupItem(
        [
            dbc.Row([
                auto_col(html.H5(bond.shortname, className="card-title")),
                # dbc.Col(html.Span("•", className="text-muted"), className="p-0", width="auto"),
                col(html.Small(bond.isin, className="text-muted")),
                auto_col(
                    dbc.Badge(
                        bond.list_level,
                        pill=True,
                        color="warning" if (int(bond.list_level) >= 3) else "success",
                        className="me-1",
                    ),
                ),
            ]),

            dbc.Row([
                col(html.Span("Погашение", className="text-muted")),
                auto_col(bond.mat_date or _perpetual_mat_date)
            ]),
            #
            # dbc.Row([
            #     dbc.Col(html.Span("НКД", className="text-muted")),
            #     dbc.Col(f'{bond.nkd} {currency_str(bond.face_unit)}', width="auto")
            # ]),

            dbc.Row([
                col(html.Span("Выплата купона", className="text-muted")),
                auto_col(bond.coupon_date)
            ]),

            dbc.Row([
                col(html.Span("Купон", className="text-muted")),
                auto_col(coupon_str)
            ]),
        ],
        href=f"calc/{bond.secid}"
    )

@callback(
    Output("isin_search_result", "children"),
    Input("isin_search", "value"),
)
def search_isin(isin: str):
    if len(isin) < 3:
        return html.Span("Введите минимум 3 символа")
    logger.info(f"Search bonds for query: '{isin}' ...")
    bonds = moex_bonds_db_search(isin)
    logger.info(f"Search bonds for query: '{isin}' - found {len(bonds)} bond(s)")
    if len(bonds) == 0:
        return html.Span("Ничего не найдено"),
    try:
        return [_get_calc_link(bond) for bond in bonds]
    except Exception as e:
        logger.exception("Failed to process search query: " + isin, e)
        return html.Span("Внутреннаая ошибка", className="text-danger")

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
        dbc.Row(dbc.Col(
            dbc.ListGroup(
                id="isin_search_result",
                flush=True,
            ),
        ), className="g-1 pt-1 m-2",),
    ]
