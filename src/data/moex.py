from datetime import date
from dateutil.parser import parse
from typing import NamedTuple

import requests
from .util import write_date

_moex_options = 'iss.json=compact&iss.meta=off&iss.dp=dot'


def load_bond_info(secid: str) -> dict:
    columns = 'marketdata.columns=SECID,BOARDID,LAST&securities.columns=BOARDID,MATDATE,OFFERDATE,SHORTNAME,COUPONPERCENT,FACEVALUE,PREVPRICE,FACEUNIT'
    url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/securities/{secid}.json?{_moex_options}&{columns}'
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
    coupon_percent: float | None
    # MOEX: LISTLEVEL
    # values: 1, 2 or 3
    list_level: int
    # MOEX: COUPONVALUE
    # 0 if unknown
    coupon_value: str
    # MOEX: NEXTCOUPON
    coupon_date: date
    # MOEX: ACCRUEDINT, НКД на дату расчетов, в валюте расчетов
    nkd: str
    # MOEX: CURRENCYID, Валюта, в которой проводятся расчеты по сделкам
    currency_id: str
    # MOEX: FACEUNIT, Валюта номинала
    face_unit: str
    # MOEX: FACEVALUE
    face_value: str
    # MOEX: COUPONPERIOD, Длительность купона
    coupon_period: str
    # MOEX: ISSUESIZE, Объем выпуска, штук
    issue_size: str
    # MOEX: OFFERDATE, may be ''
    offer_date: date | None


def load_moex_bonds() -> list[BasicBondInfo]:
    columns = 'SECID,ISIN,SHORTNAME,STATUS,BOARDID,MATDATE,COUPONPERCENT,LISTLEVEL,COUPONVALUE,NEXTCOUPON,ACCRUEDINT,CURRENCYID,FACEUNIT,FACEVALUE,COUPONPERIOD,ISSUESIZE,OFFERDATE'
    url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json?iss.only=securities&securities.columns={columns}'
    j = requests.get(url).json()
    data = _to_dict(j['securities'], columns.split(sep=','))
    data = [
        BasicBondInfo(
            b['SHORTNAME'],
            b['SECID'],
            b['ISIN'],
            _to_optional_date(b['MATDATE']),
            b['COUPONPERCENT'],
            b['LISTLEVEL'],
            b['COUPONVALUE'],
            _to_date(b['NEXTCOUPON']),
            b['ACCRUEDINT'],
            b['CURRENCYID'],
            b['FACEUNIT'],
            b['FACEVALUE'],
            b['COUPONPERIOD'],
            b['ISSUESIZE'],
            _to_optional_date(b['OFFERDATE']),
        )
        for b in data
        # there are bonds with zeroes in 'NEXTCOUPON' field, f.e. RU000A109K81
        if (b['BOARDID'] != 'SPOB' and b['NEXTCOUPON'] != '0000-00-00')
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
    if date_str and date_str != '0000-00-00':
        return write_date(parse(date_str))
    else:
        return ''

def _to_optional_date(date_str: str) -> date | None:
    if date_str and date_str != '0000-00-00':
        return date.fromisoformat(date_str)
    else: return None

def _to_date(date_str: str) -> date:
    return date.fromisoformat(date_str)
