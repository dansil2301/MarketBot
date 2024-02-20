import asyncio
from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyBB(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.MA_period = 20
        self.D = 2
        self.moving_avg_container = dict()
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.MA_period
        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.history_candles_length)
        else:
            period = timedelta(hours=self.history_candles_length)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)
        self.moving_avg_container = {
            "avr_period": candles,
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        self.moving_avg_container = {
            "avr_period": candles,
        }

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        self.moving_avg_container["avr_period"].append(new_candle)
        self.moving_avg_container["avr_period"].pop(0)

        middle_line = self.calc_helper.MA_calc(self.moving_avg_container["avr_period"])
        upper_line = middle_line + (self.D * self.calc_helper.std_dev(middle_line, self.moving_avg_container["avr_period"]))
        lower_line = middle_line - (self.D * self.calc_helper.std_dev(middle_line, self.moving_avg_container["avr_period"]))
        return [middle_line, upper_line, lower_line]

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        return self._param_calculation(new_candle)

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        current_price = float(quotation_to_decimal(new_candle.close))
        middle_line, upper_line, lower_line = self.get_candle_param(new_candle)

        if current_price >= upper_line:
            return ActionEnum.SELL
        elif current_price <= lower_line:
            return ActionEnum.BUY
        else:
            return ActionEnum.KEEP
