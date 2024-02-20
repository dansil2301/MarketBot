import asyncio
from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from Strategies.Utils.CalcHelper import CalcHelper
from historyData.HistoryData import HistoryData


class StrategyEMA(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.longTerm = 200  # minutes
        self.shortTerm = 20  # minutes
        self.longA = 2 / (self.longTerm + 1)
        self.shortA = 2 / (self.shortTerm + 1)
        self.moving_avg_container = dict()
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.longTerm
        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.longTerm)
        else:
            period = timedelta(hours=self.longTerm)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)
        self.moving_avg_container = {
            "long": self.calc_helper.MA_calc(candles),
            "short": self.calc_helper.MA_calc(candles[len(candles) - self.shortTerm:])
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        self.moving_avg_container = {
            "long": self.calc_helper.MA_calc(candles),
            "short": self.calc_helper.MA_calc(candles[len(candles) - self.shortTerm:])
        }

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        current_price = float(quotation_to_decimal(new_candle.close))

        prev_long = self.moving_avg_container["long"]
        prev_short = self.moving_avg_container["short"]

        current_long = self.calc_helper.EMA_calc(prev_long, self.longA, current_price)
        current_short = self.calc_helper.EMA_calc(prev_short, self.shortA, current_price)

        self.moving_avg_container["long"] = current_long
        self.moving_avg_container["short"] = current_short

        return [prev_long, prev_short, current_long, current_short]

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        prev_long, prev_short, current_long, current_short = self._param_calculation(new_candle)
        return [prev_long - prev_short, current_long - current_short]

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        prev_long, prev_short, current_long, current_short = self._param_calculation(new_candle)

        if prev_long > prev_short and current_long <= current_short:
            return self.action.BUY
        elif prev_long < prev_short and current_long >= current_short:
            return self.action.SELL
        else:
            return self.action.KEEP
