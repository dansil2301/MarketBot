import asyncio

from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.Utils.CalcHelper import CalcHelper
from historyData.HistoryData import HistoryData


class StrategyMACD(Strategy):
    def __init__(self):
        self.calc_helper = CalcHelper()
        self.longTerm = 26  # minutes
        self.shortTerm = 12  # minutes
        self.signal = 9  # signal step

        self.longA = 2 / (self.longTerm + 1)
        self.shortA = 2 / (self.shortTerm + 1)
        self.signalA = 2 / (self.signal + 1)

        self.MACD_parameters = dict()
        self.action = ActionEnum.KEEP
        asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        candles = await HistoryData().GetTinkoffServerHistoryData(self.longTerm + self.signal)
        long, short, signal = self._init_helper(candles)
        self.MACD_parameters = {
            "long": long,
            "short": short,
            "signal": signal
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        long, short, signal = self._init_helper(candles)
        self.MACD_parameters = {
            "long": long,
            "short": short,
            "signal": signal
        }

    def _init_helper(self, candles: list[Candle]):
        long = self.calc_helper.MA_calc(candles[:len(candles) - self.signal])
        short = self.calc_helper.MA_calc(candles[len(candles) - self.shortTerm - self.signal:len(candles) - self.signal])
        signal_saver = list()
        for i in range(len(candles) - self.signal, len(candles)):
            current_price = float(quotation_to_decimal(candles[i].close))
            long = self.calc_helper.EMA_calc(long, self.longA, current_price)
            short = self.calc_helper.EMA_calc(short, self.shortA, current_price)

            signal_saver.append(short - long)

        return long, short, sum(signal_saver) / len(signal_saver)

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        current_price = float(quotation_to_decimal(new_candle.close))

        prev_MCAD = self.MACD_parameters["short"] - self.MACD_parameters["long"]
        prev_signal = self.MACD_parameters["signal"]

        short = self.calc_helper.EMA_calc(self.MACD_parameters["short"], self.shortA, current_price)
        long = self.calc_helper.EMA_calc(self.MACD_parameters["long"], self.longA, current_price)

        current_MCAD = short - long
        current_signal = self.calc_helper.EMA_calc(prev_signal, self.signalA, current_MCAD)

        self.MACD_parameters["short"] = short
        self.MACD_parameters["long"] = long
        self.MACD_parameters["signal"] = current_signal

        if prev_MCAD < prev_signal and current_MCAD >= current_signal:
            return self.action.BUY
        elif prev_MCAD > prev_signal and current_MCAD <= current_signal:
            return self.action.SELL
        else:
            return self.action.KEEP
