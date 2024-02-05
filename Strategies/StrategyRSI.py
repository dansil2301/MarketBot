from tinkoff.invest.grpc.marketdata_pb2 import Candle

from Strategies.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy


class StrategyRSI(Strategy):
    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        pass
    