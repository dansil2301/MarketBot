import asyncio
from asyncio import sleep

from tinkoff.invest.grpc.operations_pb2 import PositionsResponse
from tinkoff.invest.sandbox.client import SandboxClient

from Settings import Settings

from tinkoff.invest import (
    OrderDirection,
    OrderType,
    InvestError,
)


class OrderLogic:
    def __init__(self):
        self.settings = Settings()
        self.percent_down = -5
        self.purchasedLots = dict()

    async def buy_request(self):
        with SandboxClient(self.settings.TOKEN) as client:
            response = client.users.get_accounts()
            account, *_ = response.accounts
            account_id = account.id

            order_type = OrderType.ORDER_TYPE_MARKET
            direction = OrderDirection.ORDER_DIRECTION_BUY
            try:
                response = client.orders.post_order(
                    figi=self.settings.figi, quantity=1,
                    direction=direction, order_type=order_type,
                    account_id=account_id,
                )
                self.purchasedLots[response.order_id] = response.lots_requested
            except InvestError as error:
                print("oops")

    async def sell_request(self):
        with SandboxClient(self.settings.TOKEN) as client:
            response = client.users.get_accounts()
            account, *_ = response.accounts
            account_id = account.id

            order_type = OrderType.ORDER_TYPE_MARKET
            direction = OrderDirection.ORDER_DIRECTION_SELL
            try:
                client.orders.post_order(
                    figi=self.settings.figi, quantity=1,
                    direction=direction, order_type=order_type,
                    account_id=account_id,
                )
                self.purchasedLots = dict()
            except InvestError as error:
                print("oops")

    async def get_account_details(self) -> PositionsResponse:
        with SandboxClient(self.settings.TOKEN) as client:
            response = client.users.get_accounts()
            account, *_ = response.accounts
            account_id = account.id

            return client.operations.get_positions(account_id=account_id)


if __name__ == "__main__":
    asyncio.run(OrderLogic().buy_request())
    print(asyncio.run(OrderLogic().get_account_details()))
    asyncio.run(sleep(1))
    asyncio.run(OrderLogic().sell_request())
    print(asyncio.run(OrderLogic().get_account_details()))
