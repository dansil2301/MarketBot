from abc import ABC, abstractmethod

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval

from Strategies.Utils.ActionEnum import ActionEnum


class Strategy(ABC):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        self.interval = interval

    @abstractmethod
    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        pass

    @abstractmethod
    def initialize_moving_avg_container(self, candles: list) -> None:
        pass
