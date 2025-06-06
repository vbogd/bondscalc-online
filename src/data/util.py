from datetime import date, datetime

_date_format = '%d.%m.%Y'

def write_date(v: date) -> str:
    return v.strftime(_date_format)

def write_optional_date(v: date | None) -> str | None:
    return None if v is None else write_date(v)

def parse_date(v: str) -> date:
    return datetime.strptime(v, _date_format)

def currency_str(curr: str) -> str:
    if curr == 'SUR': return '₽'
    elif curr == 'USD': return '$'
    elif curr == 'EUR': return '€'
    elif curr == 'CNY': return '¥'
    else: return curr
