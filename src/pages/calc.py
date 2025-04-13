import dash
from dash import html, callback, Output, Input, State, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
import logging

from datetime import date, timedelta
from typing import Any
from data import moex_bonds_db_get, currency_str, write_optional_date


def _title(secid=""):
    return f"BondsCalc | {secid}"

dash.register_page(
    __name__,
    path_template="/calc/<secid>",
    title=_title,
)

logger = logging.getLogger(__name__)

def header(
        ticker: str,
        isin: str,
        show_search: bool = True
):
    hidden_style = {'display': 'none'}
    return dbc.Row([
            dbc.Col(
                html.H3([
                        ticker,
                        # html.Small(isin, className="text-muted")
                    ],
                    className="card-title"
                ),
                width="auto",
            ),
            dbc.Col(
                html.Span(isin, className="text-muted"),
                className="gx-4"
            ),
            dbc.Col(
                dbc.Button(html.I(className="bi bi-search"), outline=True, href="/"),
                width="auto",
                style=None if show_search else hidden_style,
            ),
        ],
        justify="between",
        className="g-1 pt-1",
    )

def col_input(
        type: str,
        id: str,
        placeholder: str,
        value: Any,
        persistence: bool = False,
):
    return dbc.Col(
        dbc.FormFloating([
            dbc.Input(
                type=type, id=id, placeholder=placeholder, value=value, persistence=persistence
            ),
            dbc.Label(placeholder),
        ]),
        width=6,
    )

def result_card(
        face_unit: str,
):
    face_unit_str = currency_str(face_unit)
    return dbc.Card(
        [
            dbc.CardHeader("результаты"),
            dbc.CardBody(
                [
                    # html.H4("Card title", className="card-title"),
                    dbc.Row([
                        dbc.Col(html.Span("доходность, год", className="card-text")),
                        dbc.Col([
                            html.Span("", className="card-text", id="result_profitability"),
                            html.Span("%", className="card-text ms-1")
                        ], width="auto")
                    ], justify="between"),
                    dbc.Row([
                        dbc.Col(html.Span("тек. доходность", className="card-text")),
                        dbc.Col([
                            html.Span("", className="card-text", id="result_current_yield"),
                            html.Span("%", className="card-text ms-1")
                        ], width="auto")
                    ], justify="between"),
                    dbc.Row([
                        dbc.Col(html.Span("прибыль", className="card-text")),
                        dbc.Col([
                            html.Span("", className="card-text", id="result_income"),
                            html.Span(face_unit_str, className="card-text ms-1")
                        ], width="auto")
                    ], justify="between"),
                    dbc.Row([
                        dbc.Col(html.Span("срок, дней", className="card-text")),
                        dbc.Col(html.Span("", className="card-text", id="result_days"), width="auto")
                    ], justify="between"),
                ]
            ),
        ],
        className="mt-1"
        # style={"width": "18rem"},
    )

def layout_row(*arg):
    return dbc.Row(
        children=list(arg),
        className="g-1 pt-1",
    )

def get_sell_date(mat_date, offer_date):
    return offer_date or mat_date

def get_sell_type_options(offer_date: date | None):
    has_offer = offer_date is not None
    res = [
        {"label": "до погашения", "value": "maturity"},
        {"label": "продажа", "value": "sell"},
    ]
    if has_offer:
        res.insert(0, {"label": "до оферты", "value": "offer"})
    return res

@callback(
    Output('sell_date', 'value', allow_duplicate=True),
    Output('sell_price', 'value', allow_duplicate=True),
    Input('sell_type', 'value'),
    State('sell_price', 'value'),
    Input('mat_date', 'children'),
    Input('offer_date', 'children'),
    Input('buy_date', 'value'),
    prevent_initial_call=True,
)
def switch_sell_type(sell_type, sell_price, mat_date, offer_date, buy_date):
    if sell_type == 'maturity':
        sell_date = mat_date
        sell_price = 100
    elif sell_type == 'offer':
        sell_date = offer_date
        sell_price = 100
    else:
        sell_date = date.fromisoformat(buy_date) + timedelta(days=1)
    return sell_date, sell_price

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='calculate'
    ),
    Output('result_profitability', 'children'),
    Output('result_current_yield', 'children'),
    Output('result_income', 'children'),
    Output('result_days', 'children'),
    Input('commission', 'value'),
    Input('tax', 'value'),
    Input('coupon', 'value'),
    Input('par_value', 'value'),
    Input('buy_date', 'value'),
    Input('buy_price', 'value'),
    Input('sell_date', 'value'),
    Input('sell_price', 'value'),
    Input('sell_type', 'value'),
)

def layout(secid="", **kwargs):
    logger.info(f"Loading info for secid {secid} ...")
    bond_info = moex_bonds_db_get(secid)
    if bond_info:
        logger.info(f"Loaded info for secid {secid}: {bond_info}")
    else:
        logger.error(f"Loading info for secid {secid} failed")

    buy_price = None
    ticker = 'не найдено'
    isin = ''
    coupon = None
    par_value = None
    mat_date = None
    offer_date = None
    coupon_date = None
    face_unit = ''
    today = date.today()

    if bond_info:
        ticker = bond_info.shortname
        isin = bond_info.isin
        coupon = bond_info.coupon_percent
        par_value = bond_info.face_value
        mat_date = bond_info.mat_date
        offer_date = bond_info.offer_date
        coupon_date = bond_info.coupon_date
        buy_price = bond_info.prev_price
        face_unit = bond_info.face_unit

    sell_date = get_sell_date(mat_date, offer_date)
    sell_type_options = get_sell_type_options(offer_date)
    sell_type_value = sell_type_options[0]['value']

    return [
        header(ticker, isin),
        # layout_row(
        #     dbc.Col("Погашение", className="text-muted"),
        #     dbc.Col(f"{_days_between(today, mat_date)} дн."),
        #     dbc.Col(write_optional_date(mat_date), width="auto")
        # ) if mat_date else None,
        # layout_row(
        #     dbc.Col("Оферта", className="text-muted"),
        #     dbc.Col(f"{_days_between(today, offer_date)} дн."),
        #     dbc.Col(write_optional_date(offer_date), width="auto")
        # ) if offer_date else None,
        # layout_row(
        #     dbc.Col("Выплата купона", className="text-muted"),
        #     dbc.Col(f"{_days_between(today, coupon_date)} дн."),
        #     dbc.Col(write_optional_date(coupon_date), width="auto")
        # ) if coupon_date else None,
        # layout_row(
        #     dbc.Col("НКД и купон", className="text-muted"),
        #     dbc.Col(f"{round(bond_info.nkd, 2)} {currency_str(bond_info.currency_id)}"),
        #     dbc.Col(f"{bond_info.coupon_value or '-'} {currency_str(bond_info.face_unit)} • {bond_info.coupon_percent}%", width="auto")
        # ) if bond_info else None,
        layout_row(
            col_input(type="number", id="par_value", placeholder="номинал", value=par_value),
            col_input(type="number", id="coupon", placeholder="купон", value=coupon)
        ),
        layout_row(
            col_input(type="number", id="commission", placeholder="комиссия", value='0.05', persistence=True),
            col_input(type="number", id="tax", placeholder="налог", value='13', persistence=True)
        ),
        layout_row(
            dbc.Label("покупка")
        ),
        layout_row(
            col_input(type="date", id="buy_date", placeholder="дата", value=today),
            col_input(type="number", id="buy_price", placeholder="цена", value=buy_price)
        ),
        layout_row(
            dbc.RadioItems(
                options=get_sell_type_options(offer_date),
                value=sell_type_value,
                id="sell_type",
                inline=True,
            )
        ),
        html.Div(children=mat_date, id="mat_date", hidden=True),
        html.Div(children=offer_date, id="offer_date", hidden=True),
        layout_row(
            col_input(type="date", id="sell_date", placeholder="дата", value=sell_date),
            col_input(type="number", id="sell_price", placeholder="цена", value='100')
        ),
        result_card(face_unit),
    ]


def _days_between(start: date, end: date) -> int:
    return (end - start).days
