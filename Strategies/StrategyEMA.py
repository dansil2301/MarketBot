import asyncio

from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from historyData.HistoryData import HistoryData


class StrategyEMA(Strategy):
    def __init__(self):
        self.longTerm = 200  # minutes
        self.shortTerm = 20  # minutes
        self.longA = 2 / (self.longTerm + 1)
        self.shortA = 2 / (self.shortTerm + 1)
        self.moving_avg_container = dict()
        self.action = ActionEnum.KEEP

        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        candles = await HistoryData().GetTinkoffServerHistoryData(self.longTerm)
        self.moving_avg_container = {
            "long": self._candles_avr_counter(candles),
            "short": self._candles_avr_counter(candles[len(candles) - self.shortTerm:])
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        self.moving_avg_container = {
            "long": self._candles_avr_counter(candles),
            "short": self._candles_avr_counter(candles[len(candles) - self.shortTerm:])
        }

    def _candles_avr_counter(self, candles: list[Candle]) -> float:
        avg = sum(float(quotation_to_decimal(candle.close))
                  for candle in candles) / len(candles)
        return avg

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        current_price = float(quotation_to_decimal(new_candle.close))

        prev_long = self.moving_avg_container["long"]
        prev_short = self.moving_avg_container["short"]

        current_long = self.longA * current_price + (1 - self.longA) * prev_long
        current_short = self.shortA * current_price + (1 - self.shortA) * prev_short

        self.moving_avg_container["long"] = current_long
        self.moving_avg_container["short"] = current_short

        if prev_long > prev_short and current_long <= current_short:
            return self.action.BUY
        elif prev_long < prev_short and current_long >= current_short:
            return self.action.SELL
        else:
            return self.action.KEEP
