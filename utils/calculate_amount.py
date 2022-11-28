from database.models.transaction_const import Currency


def calculate_get_amount(have_currency: Currency, get_currency: Currency, amount: float, rate: float) -> float:
    c = Currency

    match have_currency, get_currency:
        # 1.36
        case c.THB, c.RUB:
            return round(amount * rate, 2)
        case c.RUB, c.THB:
            return round(amount / rate, 2)

        # 36
        case c.THB, c.USDC | c.USDT:
            return round(amount / rate, 2)
        case c.USDC | c.USDT, c.THB:
            return round(amount * rate, 2)

        case _, _:
            raise Exception(f"pair {have_currency} -> {get_currency} not allowed")  # todo exception
