from datetime import date, datetime

_date_format = '%d.%m.%Y'

def write_date(v: date) -> str:
    return v.strftime(_date_format)

def parse_date(v: str) -> date:
    return datetime.strptime(v, _date_format)
