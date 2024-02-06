import asyncio

from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from historyData.HistoryData import HistoryData


class StrategyRSI(Strategy):
    def __init__(self):
        self.EMA_period = 200  # minutes
        self.gain_loss_container = list()
        self.prev_candle_saver = float
        self.action = ActionEnum.KEEP

        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        candles = await HistoryData().GetTinkoffServerHistoryData(self.EMA_period + 1)
        self.prev_candle_saver = float(quotation_to_decimal(candles[len(candles) - 1].close))
        self.EMA_period = len(candles) # to get rid of api bug
        self.gain_loss_container = candles

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        self.prev_candle_saver = float(quotation_to_decimal(candles[len(candles) - 1].close))
        self.gain_loss_container = candles

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

    def _move_candles(self, candles: list[Candle], candle: Candle) -> list[Candle]:
        new_candles = candles
        new_candles.pop(0)
        new_candles.append(candle)
        return new_candles

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        prev_gain = self._candles_avr_loss_gain(self.gain_loss_container, "gain")
        prev_loss = self._candles_avr_loss_gain(self.gain_loss_container, "loss")
        prev_RS = prev_gain / prev_loss
        prev_RSI = 100 - 100 / (1 + prev_RS)

        self._move_candles(self.gain_loss_container, new_candle)

        current_gain = self._candles_avr_loss_gain(self.gain_loss_container, "gain")
        current_loss = self._candles_avr_loss_gain(self.gain_loss_container, "loss")

        current_RS = current_gain / current_loss
        current_RSI = 100 - 100 / (1 + current_RS)

        if prev_RSI < 50 <= current_RSI:
            return self.action.BUY
        elif prev_RSI > 50 >= current_RSI:
            return self.action.SELL
        else:
            return self.action.KEEP
    