import asyncio
import datetime
import time

from tinkoff.invest.grpc.marketdata_pb2 import Candle, SubscriptionInterval
from tinkoff.invest.utils import now

from OrderLogic import OrderLogic
from Strategies.StrategyABS import Strategy
from Strategies.StrategyEMA import StrategyEMA
from Strategies.StrategyMA import StrategyMA
from Strategies.StrategyMACD import StrategyMACD
from StreamService import StreamService
from Strategies.Utils.ActionEnum import ActionEnum


class App:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.streamService = StreamService()
        self.orderLogic = OrderLogic()
        self.action = ActionEnum.KEEP

    async def trade(self) -> None:
        interval = SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE
        time_checker = now()
        async for candle in self.streamService.streamCandle(interval):
            if candle and time_checker != candle.time:
                self.action = await self.strategy.trade_logic(candle)
                await self.take_action(candle)
            time_checker = candle.time if candle else time_checker

    async def take_action(self, candle: Candle) -> None:
        if self.action == ActionEnum.BUY:
            await self.orderLogic.buy_request()
            print("bought ", candle.close)
        elif self.action == ActionEnum.SELL:
            await self.orderLogic.sell_request()
            print(f"sold: {(await self.orderLogic.get_account_details()).money} ", candle.close)
        else:
            print("the sum is being kept ", candle.close)


if __name__ == "__main__":
    app = App(StrategyMA())  # testing
    asyncio.run(app.trade())
