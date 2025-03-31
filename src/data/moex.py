from datetime import date
from dateutil.parser import parse
from typing import NamedTuple

import requests
from .util import write_date

_moex_options = 'iss.json=compact&iss.meta=off&iss.dp=dot'


class BasicBondInfo(NamedTuple):
    shortname: str
    secid: str
    isin: str
    # MOEX: MATDATE
    mat_date: date | None
    # MOEX: COUPONPERCENT
    coupon_percent: float | None
    # MOEX: LISTLEVEL
    # values: 1, 2 or 3
    list_level: int
    # MOEX: COUPONVALUE, 0 if unknown
    coupon_value: float | None
    # MOEX: NEXTCOUPON
    coupon_date: date
    # MOEX: ACCRUEDINT, НКД на дату расчетов, в валюте расчетов
    nkd: float
    # MOEX: CURRENCYID, Валюта, в которой проводятся расчеты по сделкам
    currency_id: str
    # MOEX: FACEUNIT, Валюта номинала
    face_unit: str
    # MOEX: FACEVALUE
    face_value: float
    # MOEX: COUPONPERIOD, Длительность купона
    coupon_period: int
    # MOEX: ISSUESIZE, Объем выпуска, штук
    issue_size: int
    # MOEX: OFFERDATE, may be ''
    offer_date: date | None
    # MOEX: PREVPRICE
    prev_price: float | None
    # MOEX: REGNUMBER
    reg_number: str | None
    # NOTE: update 'select' in db.py when adding more columns


def load_moex_securities() -> list[BasicBondInfo]:
    columns = 'SECID,ISIN,SHORTNAME,STATUS,BOARDID,MATDATE,COUPONPERCENT,LISTLEVEL,COUPONVALUE,NEXTCOUPON,ACCRUEDINT,CURRENCYID,FACEUNIT,FACEVALUE,COUPONPERIOD,ISSUESIZE,OFFERDATE,PREVPRICE,REGNUMBER'
    url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json?{_moex_options}&iss.only=securities&securities.columns={columns}'
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
            # MOEX API: 0 if unknown
            b['COUPONVALUE'] if b['COUPONVALUE'] != 0 else None,
            _to_date(b['NEXTCOUPON']),
            b['ACCRUEDINT'],
            b['CURRENCYID'],
            b['FACEUNIT'],
            b['FACEVALUE'],
            b['COUPONPERIOD'],
            b['ISSUESIZE'],
            _to_optional_date(b['OFFERDATE']),
            float(b['PREVPRICE']) if b['PREVPRICE'] is not None else None,
            b['REGNUMBER'],
        )
        for b in data
        # there are bonds with zeroes in 'NEXTCOUPON' field, f.e. RU000A109K81
        if (b['BOARDID'] != 'SPOB' and b['NEXTCOUPON'] != '0000-00-00')
    ]
    return data

class BondMarketData(NamedTuple):
    secid: str
    last_price: float


def load_moex_marketdata() -> list[BondMarketData]:
    columns = 'BOARDID,SECID,LAST'
    url = f'https://iss.moex.com/iss/engines/stock/markets/bonds/securities.json?{_moex_options}&iss.only=marketdata,dataversion&marketdata.columns={columns}'
    j = requests.get(url).json()
    data = _to_dict(j['marketdata'], columns.split(sep=','))
    return [
        BondMarketData(
            r['SECID'],
            float(r['LAST']),
        )
        for r in data
        if (r['BOARDID'] != 'SPOB' and r['LAST'] is not None)
    ]


def _to_dict(moex_json, columns: list[str]):
    return [
        {k : r[i] for i, k in enumerate(moex_json['columns']) if k in columns}
                  for r in moex_json['data']
    ]


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
