import asyncio
from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyAM:
    def __init__(self):
        self.longTerm = 50  # minutes
        self.shortTerm = 5  # minutes
        self.moving_avg_container = dict()
        self.action = ActionEnum.KEEP

        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        candles = await HistoryData().GetTinkoffServerHistoryData(self.longTerm)
        self.moving_avg_container = {
            "long": candles,
            "short": candles[len(candles) - self.shortTerm:]
        }

    def _candles_avr_counter(self, candles: list[Candle]) -> float:
        avg = sum(float(quotation_to_decimal(candle.close))
                  for candle in candles) / len(candles)
        return avg

    def _move_candles(self, candles: list[Candle], candle: Candle) -> list[Candle]:
        new_candles = candles
        new_candles.pop(0).append(candle)
        return new_candles

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        prev_long = self._candles_avr_counter(self.moving_avg_container["long"])
        prev_short = self._candles_avr_counter(self.moving_avg_container["short"])

        self._move_candles(self.moving_avg_container["long"], new_candle)
        self._move_candles(self.moving_avg_container["short"], new_candle)

        current_long = self._candles_avr_counter(self.moving_avg_container["long"])
        current_short = self._candles_avr_counter(self.moving_avg_container["short"])

        if prev_long > prev_short and current_long <= current_short:
            return self.action.BUY
        elif prev_long < prev_short and current_long >= current_short:
            return self.action.SELL
        else:
            return self.action.KEEP

