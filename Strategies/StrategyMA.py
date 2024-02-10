import asyncio
from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from Strategies.Utils.CalcHelper import CalcHelper
from historyData.HistoryData import HistoryData


class StrategyMA(Strategy):
    def __init__(self):
        self.calc_helper = CalcHelper()
        self.longTerm = 50  # steps
        self.shortTerm = 5  # steps
        self.moving_avg_container = dict()
        self.action = ActionEnum.KEEP

        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        interval = CandleInterval.CANDLE_INTERVAL_1_MIN
        if CandleInterval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.longTerm)
        else:
            period = timedelta(hours=self.longTerm)
        candles = await HistoryData().GetTinkoffServerHistoryData(period=period, interval=interval)
        self.moving_avg_container = {
            "long": candles,
            "short": candles[len(candles) - self.shortTerm:]
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        self.moving_avg_container = {
            "long": candles,
            "short": candles[len(candles) - self.shortTerm:]
        }

    def _move_candles(self, candle: Candle) -> None:
        for name in self.moving_avg_container:
            self.moving_avg_container[name].pop(0)
            self.moving_avg_container[name].append(candle)

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        prev_long = self.calc_helper.MA_calc(self.moving_avg_container["long"])
        prev_short = self.calc_helper.MA_calc(self.moving_avg_container["short"])

        self._move_candles(new_candle)

        current_long = self.calc_helper.MA_calc(self.moving_avg_container["long"])
        current_short = self.calc_helper.MA_calc(self.moving_avg_container["short"])

        if prev_long > prev_short and current_long <= current_short:
            return self.action.BUY
        elif prev_long < prev_short and current_long >= current_short:
            return self.action.SELL
        else:
            return self.action.KEEP

