import asyncio
from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from Strategies.Utils.CalcHelper import CalcHelper
from historyData.HistoryData import HistoryData


class StrategyRSI(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.EMA_period = 200  # minutes
        self.EMA_A = 2 / (self.EMA_period + 1)
        self.gain_loss_container = dict()
        self.prev_candle_saver = float
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.EMA_period
        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.EMA_period + 1)
        else:
            period = timedelta(hours=self.EMA_period + 1)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        self.prev_candle_saver = float(quotation_to_decimal(candles[len(candles) - 1].close))
        self.EMA_period = len(candles)  # to get rid of api bug
        self.gain_loss_container = {
            "gain": self._candles_avr_loss_gain(candles, "gain"),
            "loss": self._candles_avr_loss_gain(candles, "loss"),
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        self.prev_candle_saver = float(quotation_to_decimal(candles[len(candles) - 1].close))
        self.gain_loss_container = {
            "gain": self._candles_avr_loss_gain(candles, "gain"),
            "loss": self._candles_avr_loss_gain(candles, "loss"),
        }

    def _candles_avr_loss_gain(self, candles: list[Candle], gain_loss: str) -> float:
        gain_loss_lst = list()
        for i in range(1, len(candles) - 1):
            prev_candle, current_candle = (float(quotation_to_decimal(candles[i - 1].close)),
                                           float(quotation_to_decimal(candles[i].close)))
            if prev_candle < current_candle and gain_loss == "gain":
                gain_loss_lst.append(current_candle - prev_candle)
            if prev_candle > current_candle and gain_loss == "loss":
                gain_loss_lst.append(prev_candle - current_candle)

        avg = sum(gain_loss_lst) / len(gain_loss_lst)
        return avg

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        current_price = float(quotation_to_decimal(new_candle.close))

        prev_gain = self.gain_loss_container["gain"]
        prev_loss = self.gain_loss_container["loss"]
        prev_RS = prev_gain / prev_loss
        prev_RSI = 100 - 100 / (1 + prev_RS)

        gain_price = current_price - self.prev_candle_saver if current_price >= self.prev_candle_saver else 0
        loss_price = self.prev_candle_saver - current_price if current_price < self.prev_candle_saver else 0
        current_gain = self.calc_helper.EMA_calc(self.gain_loss_container["gain"], self.EMA_A, gain_price)
        current_loss = self.calc_helper.EMA_calc(self.gain_loss_container["loss"], self.EMA_A, loss_price)

        current_RS = current_gain / current_loss
        current_RSI = 100 - 100 / (1 + current_RS)

        self.prev_candle_saver = current_price
        self.gain_loss_container["gain"] = current_gain
        self.gain_loss_container["loss"] = current_loss

        return [prev_RSI, current_RSI]

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        prev_RSI, current_RSI = self._param_calculation(new_candle)
        return [prev_RSI, current_RSI]

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        prev_RSI, current_RSI = self._param_calculation(new_candle)

        if prev_RSI < 50 <= current_RSI:
            return self.action.SELL
        elif prev_RSI > 50 >= current_RSI:
            return self.action.BUY
        else:
            return self.action.KEEP
    