from strenum import StrEnum


class Currency(StrEnum):
    THB = "THB"
    RUB = "RUB"
    USDT = 'USDT'
    USDC = "USDC"

    @classmethod
    def all(cls):
        return [cls.THB, cls.RUB, cls.USDT, cls.USDC]


class RequestStatus(StrEnum):
    request_user = '0_request_user'
    request_merchant = '0_request_merchant'

    requisites_merchant = '1_requisites_merchant'
    transfer_user = '1_transfer_user'

    accept_merchant = '2_accept_merchant'
    transfer_merchant = '2_transfer_merchant'

    def prev(self):
        stack = [None, self.request_user, self.request_merchant, self.requisites_merchant, self.transfer_user,
                 self.accept_merchant, self.transfer_merchant]
        return stack[stack.index(self) - 1]
