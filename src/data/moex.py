from datetime import date
from typing import NamedTuple

import requests
from .util import write_date

_moex_options = 'iss.json=compact&iss.meta=off&iss.dp=dot'


def load_bond_info(secid: str) -> dict:
    columns = 'marketdata.columns=SECID,BOARDID,LAST&securities.columns=BOARDID,MATDATE,OFFERDATE,SHORTNAME,COUPONPERCENT,FACEVALUE,PREVPRICE,FACEUNIT'
    url = f'http://iss.moex.com/iss/engines/stock/markets/bonds/securities/{secid}.json?{_moex_options}&{columns}'
    j = requests.get(url).json()
    data = [{k : r[i] for i, k in enumerate(j['securities']['columns'])}
                      for r in j['securities']['data']]
    data = _filter_by_board(data)
    fixed_dates = {c : _fix_date(data[c]) for c in ['MATDATE', 'OFFERDATE'] if c in data}
    market_data = _to_dict(j['marketdata'], ['SECID', 'BOARDID', 'LAST'])
    market_data = _filter_by_board(market_data)
    return data | market_data | fixed_dates


class BasicBondInfo(NamedTuple):
    shortname: str
    secid: str
    isin: str
    # MOEX: MATDATE
    mat_date: date
    # MOEX: COUPONPERCENT
    coupon_percent: float
    # MOEX: LISTLEVEL
    list_level: int


def load_moex_bonds() -> list[BasicBondInfo]:
    columns = 'SECID,ISIN,SHORTNAME,STATUS,BOARDID,MATDATE,COUPONPERCENT,LISTLEVEL'
    url = f'http://iss.moex.com/iss/engines/stock/markets/bonds/securities.json?iss.only=securities&securities.columns={columns}'
    j = requests.get(url).json()
    data = _to_dict(j['securities'], columns.split(sep=','))
    data = [
        BasicBondInfo(b['SHORTNAME'], b['SECID'], b['ISIN'], b['MATDATE'], b['COUPONPERCENT'], b['LISTLEVEL'])
        for b in data
        if b['BOARDID'] in _valid_boards
    ]
    return data


def _to_dict(moex_json, columns: list[str]):
    return [
        {k : r[i] for i, k in enumerate(moex_json['columns']) if k in columns}
                  for r in moex_json['data']
    ]


# valid MOEX bonds boards
_valid_boards = ["TQCB", "TQOB", "TQIR"]


def _filter_by_board(data: list[dict]) -> dict:
    return next((bond for bond in data if bond['BOARDID'] in _valid_boards), {})


def _fix_date(date_str: str) -> str:
    from dateutil.parser import parse
    if date_str:
        return write_date(parse(date_str))
    else:
        return ''
