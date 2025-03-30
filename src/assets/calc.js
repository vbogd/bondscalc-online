window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        calculate: function(
            commission,
            tax,
            coupon,
            par_value,
            buy_date,
            buy_price,
            sell_date,
            sell_price,
            till_maturity,
        ) {
            commission = commission / 100.0
            tax = tax / 100.0
            coupon = coupon / 100.0
            buy_price = buy_price / 100.0
            sell_price = sell_price / 100.0
            const _sell_date = Date.parse(sell_date)
            const _buy_date = Date.parse(buy_date)
            const _till_maturity = till_maturity === "maturity"

            const days = _days_between(_buy_date, _sell_date)
            var commission_fixed = commission
            if (_till_maturity) commission_fixed = commission / 2.0

            const income = (
                // ((C13 * C8) - (C10 * C8))
                (sell_price * par_value - buy_price * par_value) +
                // ((C8*C7)/365)*РАЗНДАТ(C11;C14;"d")
                par_value * coupon / 365 * days -
                // (((C13 * C8) + (C10 * C8)) * C5)
                (sell_price * par_value + buy_price * par_value) * commission_fixed
            ) * (1 - tax)

            const profitability = (
                // =((C16 / (РАЗНДАТ(C11;C14;"d"))) * 365) / (C10 * C8 + ((C13 * C8) + (C10 * C8)) * C5)
                (income * 365 / days) /
                (buy_price * par_value + (sell_price + buy_price) * par_value * commission_fixed) * 100
            )

            const current_yield = coupon / buy_price * 100 * (1 - tax)

            return [
                format_number(profitability.toFixed(2)),
                format_number(current_yield.toFixed(2)),
                format_number(income.toFixed(2)),
                format_number(days)
            ]
        }
    }
});

function _days_between(start, end) {
    const oneDay = 24 * 60 * 60 * 1000;
    return Math.round(Math.abs((end - start) / oneDay));
}

function format_number(num) {
    return isNaN(num) ? '-' : num.toLocaleString()
}