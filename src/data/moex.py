import requests
from urllib.parse import quote
from .util import write_date

_moex_options = 'iss.json=compact&iss.meta=off&iss.dp=dot'

def moex_search(query: str) -> list[dict]:
    query = query.lower()
    columns = 'secid,shortname,isin,is_traded,primary_boardid'
    url = f'http://iss.moex.com/iss/securities.json?{_moex_options}&engine=stock&market=bonds&securities.columns={columns}&q=' + quote(query)
    j = requests.get(url).json()
    data = [{k : r[i] for i, k in enumerate(j['securities']['columns'])}
                      for r in j['securities']['data']]
    # TODO: remove duplicates?
    data = [bond for bond in data
             if bond['is_traded'] == 1
             and bond['primary_boardid'] in _valid_boards
             and (query in bond['isin'].lower() or query in bond['shortname'].lower())
    ]
    data.sort(key=lambda bond: bond['shortname'])
    return data
    # df = pd.DataFrame(data)[['secid', 'shortname', 'isin', 'is_traded']]
    # df = df.loc[df['is_traded'] == 1].drop(columns=['is_traded'])
    # # TODO: remove duplicates
    # df.set_index('secid', inplace=True)
    # df.sort_values(by='shortname', inplace=True)
    # return df

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
