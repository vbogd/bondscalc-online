from datetime import date

_empty_result = {}

def calculate(bond: tuple):
    commission = _get_percent(bond[0])
    tax = _get_percent(bond[1])
    coupon = _get_percent(bond[2])
    par_value = _get_double(bond[3])
    buy_date = _get_date(bond[4])
    buy_price = _get_percent(bond[5])
    sell_date = _get_date(bond[6])
    sell_price = _get_percent(bond[7])
    till_maturity = bond[8] == "maturity"

    if commission is None: return _empty_result
    if tax is None: return _empty_result
    if coupon is None: return _empty_result
    if par_value is None: return _empty_result
    if buy_date is None: return _empty_result
    if buy_price is None: return _empty_result
    if sell_date is None: return _empty_result
    if sell_price is None: return _empty_result
    if till_maturity is None: return _empty_result

    days = _days_between(buy_date, sell_date)
    if till_maturity: commission_fixed = commission / 2
    else: commission_fixed = commission

    income = (
        # ((C13 * C8) - (C10 * C8))
        (sell_price * par_value - buy_price * par_value) +
        # ((C8*C7)/365)*РАЗНДАТ(C11;C14;"d")
        par_value * coupon / 365 * days -
        # (((C13 * C8) + (C10 * C8)) * C5)
        (sell_price * par_value + buy_price * par_value) * commission_fixed
    ) * (1 - tax)

    profitability = (
        # =((C16 / (РАЗНДАТ(C11;C14;"d"))) * 365) / (C10 * C8 + ((C13 * C8) + (C10 * C8)) * C5)
        (income * 365 / days) /
        (buy_price * par_value + (sell_price + buy_price) * par_value * commission_fixed) * 100
    )

    current_yield = coupon / buy_price * 100 * (1 - tax)

    return {
        'profitability': profitability,
        'current_yield': current_yield,
        'income': income,
        'days': days,
    }


def _get_percent(v) -> float | None:
    """
    >>> _get_percent('1')
    0.01
    >>> _get_percent(1)
    0.01
    >>> _get_percent('') is None
    True
    >>> _get_percent(None) is None
    True
    """
    return float(v) / 100 if v else None

def _get_double(v) -> float | None:
    return float(v) if v else None

def _get_date(v: str) -> date | None :
    from .util import parse_date
    return parse_date(v) if (v and len(v) == 10) else None

def _days_between(start: date, end: date) -> int:
    return (end - start).days

if __name__ == '__main__':
    import doctest                 # import the doctest library
    doctest.testmod(verbose=True)
