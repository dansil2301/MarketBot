from tinkoff.invest.grpc.marketdata_pb2 import Candle

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum


class StrategyAroon(Strategy):
    async def _initialize_moving_avg_container(self) -> None:
        pass

    def initialize_moving_avg_container(self, candles: list) -> None:
        pass

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        pass

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        pass

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        pass