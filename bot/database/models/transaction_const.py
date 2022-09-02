from strenum import StrEnum
import enum

__all__ = ['Currency', 'TransGet', 'TransStatus']


def _(t): return t


class Currency(StrEnum):
    BAT = 'THB'
    RUB = 'RUB'
    USDT = 'USDT'
    USDC = 'USDC'

    @staticmethod
    def all():
        return [str(Currency.USDT), str(Currency.USDC), str(Currency.RUB), str(Currency.BAT)]

    @staticmethod
    def fiat():
        return [str(Currency.USDT), str(Currency.USDC), str(Currency.RUB)]

    @staticmethod
    def non_stable():
        return [Currency.BAT]


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

    def exchange(self):
        return [self.in_exchange, self.wait_good_user]


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
