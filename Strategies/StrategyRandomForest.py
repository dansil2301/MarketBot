import asyncio
from datetime import timedelta, datetime

import pandas as pd
import numpy as np
from joblib import load
from sklearn.preprocessing import StandardScaler
from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

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
from Utils.EMAScaler import EMAScaler
from historyData.HistoryData import HistoryData


class StrategyRandomForest(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.model = load("../DataAnalyze/random_forest_model.joblib")
        self.strategies = [StrategyEMA(), StrategyRSI(), StrategyMACD(),
                           StrategyBB(), StrategyST(), StrategyStochRSI(),
                           StrategyAroon(), StrategyOBV()]

        self.interval = interval
        self.history_candles_length = max(strategy.history_candles_length for strategy in self.strategies)

        self.data_for_ss = pd.DataFrame
        #self.standard_scaler = StandardScaler()
        self.EMA_scaler = EMAScaler(288)

        self.param_container = dict()
        #asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        period = timedelta(days=20)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        self.param_container = {"close": [], "volume": [], "open": [], "high": [], "low": []}
        for candle in candles:
            self._init_standard_candle_params(candle)

        for strategy in self.strategies:
            strategy.initialize_moving_avg_container(candles[:strategy.history_candles_length])
            for candle_index in range(strategy.history_candles_length, len(candles)):
                params = strategy.get_candle_param(candles[candle_index])
                for param_name in params:
                    if candle_index == strategy.history_candles_length:
                        self.param_container[param_name] = list()
                        [self.param_container[param_name].append(None) for i in
                         range(strategy.history_candles_length)]
                    self.param_container[param_name].append(params[param_name])

        self.data_for_ss = pd.DataFrame(self.param_container)
        self.data_for_ss = self.data_for_ss.drop(self.data_for_ss.index[:self.history_candles_length])
        self.standard_scaler.fit(self.data_for_ss)
        self.data_for_ss, self.param_container = pd.DataFrame, dict()

    def initialize_moving_avg_container(self, candles: list) -> None:
        self.param_container = {"close": [], "volume": [], "open": [], "high": [], "low": []}
        for candle in candles:
            self._init_standard_candle_params(candle)

        for strategy in self.strategies:
            strategy.initialize_moving_avg_container(candles[:strategy.history_candles_length])
            for candle_index in range(strategy.history_candles_length, len(candles)):
                params = strategy.get_candle_param(candles[candle_index])
                for param_name in params:
                    if candle_index == strategy.history_candles_length:
                        self.param_container[param_name] = list()
                        [self.param_container[param_name].append(None) for i in
                         range(strategy.history_candles_length)]
                    self.param_container[param_name].append(params[param_name])

        self.data_for_ss = pd.DataFrame(self.param_container)
        self.data_for_ss = self.data_for_ss.drop(self.data_for_ss.index[:self.history_candles_length])
        self.EMA_scaler.fit(self.data_for_ss)
        self.data_for_ss, self.param_container = pd.DataFrame, dict()

    def _init_standard_candle_params(self, candle: Candle):
        self.param_container["close"].append(float(quotation_to_decimal(candle.close)))
        self.param_container["open"].append(float(quotation_to_decimal(candle.open)))
        self.param_container["high"].append(float(quotation_to_decimal(candle.high)))
        self.param_container["low"].append(float(quotation_to_decimal(candle.low)))
        self.param_container["volume"].append(candle.volume)

    def _param_calculation(self, new_candle: Candle) -> int:
        self.param_container = {"close": [], "volume": [], "open": [], "high": [], "low": []}
        self._init_standard_candle_params(new_candle)

        for strategy in self.strategies:
            params = strategy.get_candle_param(new_candle)
            for param_name in params:
                self.param_container[param_name] = list()
                self.param_container[param_name].append(params[param_name])

        self.data_for_ss = pd.DataFrame(self.param_container)
        self.EMA_scaler.update_ema(self.data_for_ss)
        scaled_data = np.array(self.EMA_scaler.transform(self.data_for_ss))

        prediction = self.model.predict(scaled_data)
        return prediction[0]

    def get_candle_param(self, new_candle: Candle) -> list[float]:
        pass

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        prediction = self._param_calculation(new_candle)

        if prediction == 1:
            return ActionEnum.BUY
        else:
            return ActionEnum.KEEP
