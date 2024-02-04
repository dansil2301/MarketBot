from abc import ABC, abstractmethod

from tinkoff.invest.grpc.marketdata_pb2 import Candle

from Strategies.ActionEnum import ActionEnum


class Strategy(ABC):
    @abstractmethod
    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        pass
