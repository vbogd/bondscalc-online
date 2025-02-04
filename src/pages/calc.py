from datetime import date, timedelta
import dash
from dash import html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import logging

from data import calculate, write_date, parse_date, load_bond_info as moex_load_bond_info

dash.register_page(__name__, path_template="/calc/<secid>")

logger = logging.getLogger(__name__)

def col_input(
        type: str,
        id: str,
        placeholder: str,
        value: str = "",
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

result_card = dbc.Card(
    [
        dbc.CardHeader("результаты"),
        dbc.CardBody(
            [
                # html.H4("Card title", className="card-title"),
                dbc.Row([
                    dbc.Col(html.Div("доходность, год", className="card-text")),
                    dbc.Col(html.Div("", className="card-text", id="result_profitability"), width="auto")
                ], justify="between"),
                dbc.Row([
                    dbc.Col(html.Div("тек. доходность", className="card-text")),
                    dbc.Col(html.Div("", className="card-text", id="result_current_yield"), width="auto")
                ], justify="between"),
                dbc.Row([
                    dbc.Col(html.Div("прибыль", className="card-text")),
                    dbc.Col(html.Div("", className="card-text", id="result_income"), width="auto")
                ], justify="between"),
                dbc.Row([
                    dbc.Col(html.Div("срок, дней", className="card-text")),
                    dbc.Col(html.Div("", className="card-text", id="result_days"), width="auto")
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
    if offer_date:
        return offer_date
    else:
        return mat_date

def get_sell_type_options(offer_date):
    has_offer = offer_date != ''
    res = [
        {"label": "до погашения", "value": "maturity"},
        {"label": "продажа", "value": "sell"},
    ]
    if has_offer:
        res.insert(0, {"label": "до оферты", "value": "offer"})
    return res

@callback(
    Output('load_bond_info', 'children'),
    Output('ticker', 'value'),
    Output('coupon', 'value'),
    Output('par_value', 'value'),
    Output('buy_price', 'value'),
    Output('sell_date', 'value'),
    Output('sell_type', 'options'),
    Output('sell_type', 'value'),
    Output('mat_date', 'children'),
    Output('offer_date', 'children'),
    Input('location', 'pathname'),
    Input('load_bond_info', 'children'),
)
def load_bond_info(
    url: str,
    load_bond_info: str,
):
    if load_bond_info != '1': raise PreventUpdate
    secid = url[url.rfind('/') + 1:]
    logger.info(f"Loading info for secid {secid} ...")
    bond_info = moex_load_bond_info(secid)
    if bond_info:
        logger.info(f"Loaded info for secid {secid}: {bond_info}")
    else:
        logger.error(f"Loading info for secid {secid} failed")
    mat_date = bond_info.get('MATDATE', '')
    offer_date = bond_info.get('OFFERDATE', '')
    sell_type_options = get_sell_type_options(offer_date)
    return (
        '0',
        bond_info.get('SHORTNAME', 'не найдено'),
        bond_info.get('COUPONPERCENT', ''),
        bond_info.get('FACEVALUE', ''),
        bond_info.get('LAST', '') or bond_info.get('PREVPRICE', ''),
        get_sell_date(mat_date, offer_date),
        sell_type_options,
        sell_type_options[0]['value'],
        mat_date,
        offer_date,
    )

@callback(
    Output('sell_date', 'value', allow_duplicate=True),
    Output('sell_price', 'value', allow_duplicate=True),
    Input('sell_type', 'value'),
    Input('sell_price', 'value'),
    Input('sell_date', 'value'),
    Input('mat_date', 'children'),
    Input('offer_date', 'children'),
    Input('buy_date', 'value'),
    prevent_initial_call=True,
)
def switch_sell_type(sell_type, sell_price, sell_date, mat_date, offer_date, buy_date):
    if sell_type == 'maturity':
        sell_date = mat_date
        sell_price = 100
    elif sell_type == 'offer':
        sell_date = offer_date
        sell_price = 100
    else:
        sell_date = write_date(parse_date(buy_date) + timedelta(days=1))
    return sell_date, sell_price

@callback(
Output('result_profitability', 'children'),
    Output('result_current_yield', 'children'),
    Output('result_income', 'children'),
    Output('result_days', 'children'),
    Input('load_bond_info', 'children'),
    Input('commission', 'value'),
    Input('tax', 'value'),
    Input('coupon', 'value'),
    Input('par_value', 'value'),
    Input('buy_date', 'value'),
    Input('buy_price', 'value'),
    Input('sell_date', 'value'),
    Input('sell_price', 'value'),
    Input('sell_type', 'value'),
    prevent_initial_call=True,
)
def run_calculator(
    load_bond_info: str,
    *args
):
    if load_bond_info != '0': raise PreventUpdate
    print("args:", args)
    result = calculate(args)
    if result:
        return (
            f"{round(result['profitability'], 2)} %",
            f"{round(result['current_yield'], 2)} %",
            f"{round(result['income'], 2)} ₽",
            f"{result['days']:,}".replace(',',' '),
        )
    else:
        return '', '', '', ''

def layout(secid="", **kwargs):
    return dbc.Container(
        [
            dcc.Location(id='location'),
            dbc.Label('BondsCalc Online'),
            html.Div(children="1", id="load_bond_info", hidden=True),
            dbc.Row(
                [
                    dbc.FormFloating(
                        [
                            dbc.Input(type="text", placeholder="isin", id="ticker", readonly=True),
                            dbc.Label("Тикер"),
                        ]
                    ),
                ],
                className="g-1 pt-1",
            ),
            layout_row(
                col_input(type="number", id="commission", placeholder="комиссия", value='0.05', persistence=True),
                col_input(type="number", id="tax", placeholder="налог", value='13', persistence=True)
            ),
            layout_row(
                col_input(type="number", id="par_value", placeholder="номинал"),
                col_input(type="number", id="coupon", placeholder="купон")
            ),
            layout_row(
                dbc.Label("покупка")
            ),
            layout_row(
                col_input(type="text", id="buy_date", placeholder="дата", value=write_date(date.today())),
                col_input(type="number", id="buy_price", placeholder="цена")
            ),
            layout_row(
                dbc.RadioItems(
                    options=get_sell_type_options(''),
                    value="maturity",
                    id="sell_type",
                    inline=True,
                )
            ),
            html.Div(children="", id="mat_date", hidden=True),
            html.Div(children="", id="offer_date", hidden=True),
            layout_row(
                col_input(type="text", id="sell_date", placeholder="дата"),
                col_input(type="number", id="sell_price", placeholder="цена", value='100')
            ),
            result_card,
        ],
        # className="p-5",
    )
    # return html.Div(
    #     f"calc secid: {secid}."
    # )