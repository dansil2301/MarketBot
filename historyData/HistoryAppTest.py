import asyncio
from _decimal import Decimal
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal

from Strategies.StrategyEMA import StrategyEMA
from Strategies.StrategyMA import StrategyMA
from Strategies.StrategyMACD import StrategyMACD
from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from Strategies.StrategyRSI import StrategyRSI
from historyData.HistoryData import HistoryData


class FakeCandle:
    def __init__(self, close):
        self.close = close


class HistoryAppTest:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.historyData = HistoryData()
        self.action = ActionEnum.KEEP
        self.sum = 100
        self.bought_at = None

    async def get_historical_candles_period(self, period=None):
        if not period:
            candles = (await self.historyData.GetAllData())
            for i in range(len(candles)):
                candles[i] = FakeCandle(decimal_to_quotation(Decimal(candles[i]["close"])))
            return candles

        candles = (await self.historyData.GetAllData())[:period]
        for i in range(len(candles)):
            candles[i] = FakeCandle(decimal_to_quotation(Decimal(candles[i]["close"])))
        return candles

    async def trade(self) -> None:
        self.strategy.initialize_moving_avg_container((await self.get_historical_candles_period(35))) # this var is manual
        candles = await self.get_historical_candles_period()
        for candle in candles:
            self.action = await self.strategy.trade_logic(candle)
            self.take_action(candle)

    def take_action(self, candle):
        if self.action == ActionEnum.BUY:
            print("bought ", candle.close)
            self.bought_at = float(quotation_to_decimal(candle.close))
        elif self.action == ActionEnum.SELL:
            if self.bought_at:
                current_sum = float(quotation_to_decimal(candle.close))
                percent = 1 - (current_sum / self.bought_at)
                self.sum += self.sum * percent
                print(f"sold: ", self.sum, candle.close)


if __name__ == "__main__":
    test = HistoryAppTest(StrategyMACD())
    asyncio.run(test.trade())
