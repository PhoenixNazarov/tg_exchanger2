import enum

from strenum import StrEnum

__all__ = ['Currency', 'TransGet', 'TransStatus']


def _(t): return t


class Currency(StrEnum):
    THB = 'THB'
    RUB = 'RUB'
    USDT = 'USDT'
    USDC = 'USDC'

    @staticmethod
    def all():
        return [str(Currency.USDT), str(Currency.USDC), str(Currency.RUB), str(Currency.THB)]

    @staticmethod
    def change():
        return [str(Currency.THB)]

    @staticmethod
    def fiat():
        return [str(Currency.USDT), str(Currency.USDC), str(Currency.RUB)]

    @staticmethod
    def non_stable():
        return [Currency.RUB]


class TransStatus(enum.Enum):
    in_stack = 0
    in_exchange = 1
    wait_good_user = 2

    canceled = -1
    good_finished = -2

    complain_by_user = -8
    complain_by_merchant = -9

    bad_finished_by_user = -6
    bad_finished_by_merchant = -7

    def __str__(self):
        return {
            TransStatus.in_stack: _('Waiting for a merchant'),
            TransStatus.in_exchange: _('In work'),
            TransStatus.wait_good_user: _('Waiting for a user'),
            TransStatus.good_finished: _('Finished'),
            TransStatus.canceled: _('Canceled')
        }.get(self)

    @classmethod
    def exchange(cls):
        return [cls.in_exchange, cls.wait_good_user]

    @classmethod
    def end(cls):
        return cls.canceled, cls.good_finished, cls.complain_by_user, cls.complain_by_merchant, \
               cls.bad_finished_by_user, cls.bad_finished_by_merchant


class TransGet(StrEnum):
    none = 'none'
    cash = 'cash'
    atm_machine = 'atm_machine'
    bank_balance = 'bank_balance'

    # todo in

    def __str__(self):
        return {
            TransGet.cash: _('Cash'),
            TransGet.atm_machine: _('Cash by code'),
            TransGet.bank_balance: _('Transfer')
        }.get(self)
