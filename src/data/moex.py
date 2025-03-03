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
    # format: YYYY-MM-DD; may be '' for perpetual bonds
    mat_date: str
    # MOEX: COUPONPERCENT
    # empty string if unknown
    coupon_percent: str
    # MOEX: LISTLEVEL
    # values: 1, 2 or 3
    list_level: str
    # COUPONVALUE
    # 0 if unknown
    coupon_value: str
    # NEXTCOUPON
    # format: YYYY-MM-DD
    coupon_date: str
    # ACCRUEDINT, НКД на дату расчетов, в валюте расчетов
    nkd: str
    # FACEUNIT, Валюта номинала
    face_unit: str


def load_moex_bonds() -> list[BasicBondInfo]:
    columns = 'SECID,ISIN,SHORTNAME,STATUS,BOARDID,MATDATE,COUPONPERCENT,LISTLEVEL,COUPONVALUE,NEXTCOUPON,ACCRUEDINT,FACEUNIT'
    url = f'http://iss.moex.com/iss/engines/stock/markets/bonds/securities.json?iss.only=securities&securities.columns={columns}'
    j = requests.get(url).json()
    data = _to_dict(j['securities'], columns.split(sep=','))
    data = [
        BasicBondInfo(
            b['SHORTNAME'],
            b['SECID'],
            b['ISIN'],
            _fix_zeroes_in_date(b['MATDATE']),
            b['COUPONPERCENT'],
            b['LISTLEVEL'],
            b['COUPONVALUE'],
            b['NEXTCOUPON'],
            b['ACCRUEDINT'],
            b['FACEUNIT']
        )
        for b in data
        if b['BOARDID'] != 'SPOB'
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
    if date_str and date_str != '0000-00-00':
        return write_date(parse(date_str))
    else:
        return ''

def _fix_zeroes_in_date(date_str: str) -> str:
    if date_str != '0000-00-00': return date_str
    else: return ''
