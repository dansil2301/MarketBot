from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyStochRSI(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.MinMax_period = 14

        self.EMA_period = 5
        self.EMA_A = 2 / (self.EMA_period + 1)

        self.param_container = dict()
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.MinMax_period + self.EMA_period
        #asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.history_candles_length)
        else:
            period = timedelta(hours=self.history_candles_length)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        D, high_low_period = self._init_helper(candles)
        self.param_container = {
            "high_low_period":  high_low_period,
            "%D": D
        }

    def _init_helper(self, candles: list[Candle]):
        list_k = list()
        start_from = 0

        for i in range(self.EMA_period):
            current_price = float(quotation_to_decimal(candles[len(candles) - self.EMA_period - 1 + i].close))
            low, high = self.calc_helper.min_max(candles[i:len(candles) - self.EMA_period + i])
            high += 1 ** -5
            list_k.append((current_price - low) / (high - low) * 100)
            start_from = i

        D = self.calc_helper.MA_calc_list_float(list_k)
        return D, candles[start_from:]

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        D, high_low_period = self._init_helper(candles)
        self.param_container = {
            "high_low_period": high_low_period,
            "%D": D
        }

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        current_price = float(quotation_to_decimal(new_candle.close))

        self.param_container["high_low_period"].append(new_candle)
        self.param_container["high_low_period"].pop(0)
        test = list()

        low, high = self.calc_helper.min_max(self.param_container["high_low_period"])
        high += 1**-5

        K = ((current_price - low) / (high - low) * 100)
        D = self.calc_helper.EMA_calc(self.param_container["%D"], self.EMA_A, K)

        return K, D

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        return self._param_calculation(new_candle)

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        K, D = self._param_calculation(new_candle)

        if K > 80:
            return self.action.SELL
        elif K < 20:
            return self.action.BUY
        else:
            return self.action.KEEP

