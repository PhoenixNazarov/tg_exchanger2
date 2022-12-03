from decimal import Decimal

from database.enums import Currency


class Calculate:
    def __init__(self, currency_in: Currency, currency_out: Currency, amount_in: float = None, amount_out: float = None,
                 rate: float = None):
        self.currency_in = currency_in
        self.currency_out = currency_out
        self.amount_in = amount_in
        self.amount_out = amount_out
        self.rate = rate

        self.type_in = True

    def get_main_currency(self) -> Currency:
        currency_m = Currency.THB

        if self.currency_in == Currency.USDC:
            currency_m = Currency.USDC
        elif self.currency_in == Currency.USDT:
            currency_m = Currency.USDT

        elif self.currency_out == Currency.USDC:
            currency_m = Currency.USDC
        elif self.currency_out == Currency.USDT:
            currency_m = Currency.USDT

        elif self.currency_in == Currency.THB:
            currency_m = Currency.THB
        elif self.currency_out == Currency.THB:
            currency_m = Currency.THB

        return currency_m

    def get_main_amount(self):
        _currency = self.get_main_currency()
        if _currency == self.currency_in:
            return self.amount_in
        return self.amount_out

    def set_amount(self, amount: float, currency: Currency):
        match self.currency_in, self.currency_out, currency:
            case (Currency.THB, Currency.RUB, Currency.THB):
                self.amount_in = amount
                self.amount_out = amount * self.rate
            case (Currency.THB, Currency.RUB, Currency.RUB):
                self.amount_in = amount * self.rate
                self.amount_out = amount
                self.type_in = False

            case (Currency.RUB, Currency.THB, Currency.RUB):
                self.amount_in = amount
                self.amount_out = amount / self.rate
            case (Currency.RUB, Currency.THB, Currency.THB):
                self.amount_in = amount * self.rate
                self.amount_out = amount
                self.type_in = False

            case (Currency.USDT | Currency.USDC, Currency.THB, Currency.USDT | Currency.USDC):
                self.amount_in = amount
                self.amount_out = amount * self.rate
            case (Currency.USDT | Currency.USDC, Currency.THB, Currency.THB):
                self.amount_in = amount / self.rate
                self.amount_out = amount
                self.type_in = False

            case (Currency.THB, Currency.USDT | Currency.USDC, Currency.USDT | Currency.USDC):
                self.amount_in = amount * self.rate
                self.amount_out = amount
                self.type_in = False
            case (Currency.THB, Currency.USDT | Currency.USDC, Currency.THB):
                self.amount_in = amount
                self.amount_out = amount / self.rate


def normalize(text: str, _in: Currency, _out: Currency, rate: float) -> Calculate:
    text = text.lower()
    _currency = None
    normal = {
        'thb': Currency.THB,
        'usdt': Currency.USDT,
        'usdc': Currency.USDC,
        'rub': Currency.RUB
    }
    for k, v in normal.items():
        if k in text:
            _currency = v
            text = text.replace(k, '')
            break
    else:
        if 'usd' in text:
            text = text.replace('usd', '')
            if _in == Currency.USDT or _out == Currency.USDT:
                _currency = Currency.USDT
            elif _in == Currency.USDC or _out == Currency.USDC:
                _currency = Currency.USDC

    if not _currency:
        if _in == Currency.USDT or _out == Currency.USDT:
            _currency = Currency.USDT
        elif _in == Currency.USDC or _out == Currency.USDC:
            _currency = Currency.USDC
        else:
            _currency = Currency.THB

    text = text.replace(' ', '').replace(',', '.')
    try:
        amount = float(text)
        rate = float(rate)
        calc = Calculate(_in, _out, rate = rate)
        calc.set_amount(amount, _currency)
    except:
        raise ValueError

    return calc
