from datetime import timedelta

from joblib import load
from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval

from Strategies.StrategyABS import Strategy
from Strategies.StrategyAroon import StrategyAroon
from Strategies.StrategyBB import StrategyBB
from Strategies.StrategyEMA import StrategyEMA
from Strategies.StrategyMACD import StrategyMACD
from Strategies.StrategyOBV import StrategyOBV
from Strategies.StrategyRSI import StrategyRSI
from Strategies.StrategyST import StrategyST
from Strategies.StrategyStochRSI import StrategyStochRSI
from Strategies.Utils.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyRandomForest:
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        self.interval = interval
        self.history_candles_length = 30

        self.param_container = dict()

        self.strategies = [StrategyEMA(), StrategyRSI(), StrategyMACD(),
                           StrategyBB(), StrategyST(), StrategyStochRSI(),
                           StrategyAroon(), StrategyOBV()]
        # asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_param_container(self) -> None:
        period = timedelta(days=self.history_candles_length)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        pass

    def initialize_moving_avg_container(self, candles: list) -> None:
        pass

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        pass

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        pass

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        pass