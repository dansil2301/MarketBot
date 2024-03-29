import asyncio
from abc import ABC, abstractmethod

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval

from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.Utils.CalcHelper import CalcHelper


class Strategy(ABC):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        self.interval = interval
        self.history_candles_length = int()
        self.calc_helper = CalcHelper()

    @abstractmethod
    async def _initialize_moving_avg_container(self) -> None:
        pass

    @abstractmethod
    def initialize_moving_avg_container(self, candles: list) -> None:
        pass

    @abstractmethod
    def _param_calculation(self, new_candle: Candle) -> list[float]:
        pass

    @abstractmethod
    def get_candle_param(self, new_candle: Candle) -> dict:
        pass

    @abstractmethod
    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        pass
