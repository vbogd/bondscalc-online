from datetime import date
from typing import Any

import dash
from dash import html, callback, Input, Output
import dash_bootstrap_components as dbc
import logging

from data import moex_bonds_db_search, BasicBondInfo, write_date, currency_str

dash.register_page(
    __name__,
    path='/',
    title='BondsCalc | поиск'
)

logger = logging.getLogger(__name__)

_perpetual_mat_date = html.Span("Бессрочно", className="text-danger")

def _get_calc_link(bond: BasicBondInfo):
    if bond.coupon_percent is not None:
        coupon_str = f'{bond.coupon_percent} %'
        coupon_left_suffix = f'• {bond.coupon_value} {currency_str(bond.face_unit)}'
    else:
        coupon_str = "-"
        coupon_left_suffix = ""

    if bond.coupon_percent is not None and bond.prev_price is not None and bond.prev_price != 0:
        cur_yield = f'{round(bond.coupon_percent / bond.prev_price * 100, 2)} %'
    else:
        cur_yield = "-"

    def col(children: Any):
        return dbc.Col(children)
    def auto_col(children: Any):
        return dbc.Col(children, width="auto")

    return dbc.ListGroupItem(
        [
            dbc.Row([
                auto_col(html.H5(bond.shortname, className="card-title")),
                # dbc.Col(html.Span("•", className="text-muted"), className="p-0", width="auto"),
                dbc.Col(html.Small(bond.isin, className="text-muted"), className="p-0"),
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
                auto_col(write_optional_date(bond.mat_date) or _perpetual_mat_date)
            ]),
            #
            # dbc.Row([
            #     dbc.Col(html.Span("НКД", className="text-muted")),
            #     dbc.Col(f'{bond.nkd} {currency_str(bond.face_unit)}', width="auto")
            # ]),

            dbc.Row([
                col(html.Span("Выплата купона", className="text-muted")),
                auto_col(write_date(bond.coupon_date))
            ]),

            dbc.Row([
                col(html.Span(
                    f'Купон {coupon_left_suffix}',
                    className="text-muted")
                ),
                auto_col(coupon_str)
            ]),

            dbc.Row([
                col(html.Span("Тек. доходность", className="text-muted")),
                auto_col(html.B(cur_yield)),
            ]),

            dbc.Row([
                col(html.Span("Цена", className="text-muted")),
                auto_col(html.Span(
                    bond.prev_price,
                    className="text-danger" if ((bond.prev_price or 0) > 100) else ""
                )),
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

def write_optional_date(v: date | None) -> str | None:
    return None if v is None else write_date(v)
