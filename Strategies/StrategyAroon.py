from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyAroon(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.MinMax_period = 25

        self.param_container = dict()
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.MinMax_period + self.MinMax_period
        #asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.history_candles_length)
        else:
            period = timedelta(hours=self.history_candles_length)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        self.param_container = {
            "candles": candles
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        self.param_container = {
            "candles": candles
        }

    def find_max_min_index(self, arr: list) -> tuple[int, int]:
        max_val = arr[0]
        min_val = arr[0]
        max_index = 0
        min_index = 0

        for i in range(1, len(arr)):
            if arr[i] > max_val:
                max_val = arr[i]
                max_index = i
            elif arr[i] < min_val:
                min_val = arr[i]
                min_index = i

        return max_index, min_index

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        self.param_container["candles"].append(new_candle)
        self.param_container["candles"].pop(0)

        period_float = [float(quotation_to_decimal(candle.close)) for candle in self.param_container["candles"]]
        high_period, low_period = self.find_max_min_index(period_float)

        aroon_up = (self.MinMax_period - (self.MinMax_period - (high_period + 1))) / self.MinMax_period * 100
        aroon_low = (self.MinMax_period - (self.MinMax_period - (low_period + 1))) / self.MinMax_period * 100

        return [aroon_up, aroon_low]

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        return self._param_calculation(new_candle)

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        aroon_up, aroon_low = self._param_calculation(new_candle)

        if aroon_up > aroon_low:
            return ActionEnum.BUY
        elif aroon_up < aroon_low:
            return ActionEnum.SELL
        else:
            return ActionEnum.KEEP
