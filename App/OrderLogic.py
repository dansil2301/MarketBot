import asyncio
from asyncio import sleep

from _decimal import Decimal
from tinkoff.invest.grpc.operations_pb2 import GetOperationsByCursorRequest, PositionsResponse
from tinkoff.invest.grpc.operations_pb2_grpc import OperationsService
from tinkoff.invest.logging import logger
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal

from tokenData.TokenData import TokenData

from tinkoff.invest import (
    Client,
    OrderDirection,
    OrderExecutionReportStatus,
    OrderType,
    PostOrderResponse,
    StopOrderDirection,
    StopOrderExpirationType,
    StopOrderType, AsyncClient, InvestError,
)


class OrderLogic:
    def __init__(self):
        self.TOKEN = TokenData().GetToken("SANDBOX_TOKEN")
        self.figi = "BBG004730N88"
        self.percent_down = -5
        self.purchasedLots = dict()

    async def buy_request(self):
        with SandboxClient(self.TOKEN) as client:
            response = client.users.get_accounts()
            account, *_ = response.accounts
            account_id = account.id

            order_type = OrderType.ORDER_TYPE_MARKET
            direction = OrderDirection.ORDER_DIRECTION_BUY
            try:
                response = client.orders.post_order(
                    figi=self.figi, quantity=1,
                    direction=direction, order_type=order_type,
                    account_id=account_id,
                )
                self.purchasedLots[response.order_id] = response.lots_requested
            except InvestError as error:
                print("oops")

    async def sell_request(self):
        with SandboxClient(self.TOKEN) as client:
            response = client.users.get_accounts()
            account, *_ = response.accounts
            account_id = account.id

            order_type = OrderType.ORDER_TYPE_MARKET
            direction = OrderDirection.ORDER_DIRECTION_SELL
            try:
                response = client.orders.post_order(
                    figi=self.figi, quantity=1,
                    direction=direction, order_type=order_type,
                    account_id=account_id,
                )
                self.purchasedLots = dict()
            except InvestError as error:
                print("oops")

    async def get_account_details(self) -> PositionsResponse:
        with SandboxClient(self.TOKEN) as client:
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
