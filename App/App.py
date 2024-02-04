import asyncio

from tinkoff.invest.utils import now

from OrderLogic import OrderLogic
from Strategies.StrategyABS import Strategy
from StreamService import StreamService
from Strategies.ActionEnum import ActionEnum
from Strategies.StrategyMA import StrategyAM


class App:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.streamService = StreamService()
        self.orderLogic = OrderLogic()
        self.action = ActionEnum.KEEP

    async def trade(self):
        minuteChecker = now().minute
        async for candle in self.streamService.streamCandle():
            print(candle)
            if candle and minuteChecker != candle.time.minute:
                self.action = await self.strategy.trade_logic(candle)
                await self.take_action()

    async def take_action(self):
        if self.action == ActionEnum.BUY:
            await self.orderLogic.buy_request()
            print("bought")
        elif self.action == ActionEnum.SELL:
            await self.orderLogic.sell_request()
            print(f"sold: {(await self.orderLogic.get_account_details()).money}")
        else:
            print("the sum is being kept")


if __name__ == "__main__":
    app = App(StrategyAM()) # testing AM
    asyncio.run(app.trade())
