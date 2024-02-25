from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import CandleInterval, Candle
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyST(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.ATR_period = 15

        self.multi = 3

        self.param_container = dict()
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.ATR_period + 1
        #asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.history_candles_length)
        else:
            period = timedelta(hours=self.history_candles_length)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        ATR, basic_upper, basic_lower = self._init_helper(candles)
        self.param_container = {
            "ATR": ATR,
            "min_max_candles": candles[1:],
            "prev_upper": basic_upper,
            "prev_lower": basic_lower
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        '''
        Used for testing on historical data
        :param candles:
        :return:
        '''
        ATR, basic_upper, basic_lower = self._init_helper(candles)
        self.param_container = {
            "ATR": ATR,
            "min_max_candles": candles[1:],
            "prev_upper": basic_upper,
            "prev_lower": basic_lower
        }

    def _calc_TR(self, current_candle: Candle, prev_candle: Candle) -> float:
        current_high = float(quotation_to_decimal(current_candle.high))
        current_low = float(quotation_to_decimal(current_candle.low))
        prev_close = float(quotation_to_decimal(prev_candle.close))

        current = current_high - current_low + 1 ** -10
        prev_high = abs(current_high - prev_close)
        prev_low = abs(current_low - prev_close)

        return max(prev_high, prev_low, current)

    def _init_helper(self, candles: list[Candle]) -> tuple:
        TR_list = list()

        for i in range(1, len(candles)):
            TR_list.append(self._calc_TR(candles[i], candles[i - 1]))

        ATR = sum(TR_list) / len(TR_list)
        basic_upper = self.calc_helper.cloud_min_max_avg(candles[1:]) + self.multi * ATR
        basic_lower = self.calc_helper.cloud_min_max_avg(candles[1:]) - self.multi * ATR

        return ATR, basic_upper, basic_lower

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        current_price = float(quotation_to_decimal(new_candle.close))
        prev_price = float(quotation_to_decimal(self.param_container["min_max_candles"][-1].close))

        TR = self._calc_TR(new_candle, self.param_container["min_max_candles"][-1])
        current_ATR = (self.param_container["ATR"] * (self.ATR_period - 1) + TR) / self.ATR_period

        basic_upper = self.calc_helper.cloud_min_max_avg(self.param_container["min_max_candles"]) + self.multi * current_ATR
        basic_lower = self.calc_helper.cloud_min_max_avg(self.param_container["min_max_candles"]) - self.multi * current_ATR

        final_upper = basic_upper if basic_upper < self.param_container["prev_upper"] else self.param_container["prev_upper"]
        final_lower = basic_lower if basic_lower > self.param_container["prev_lower"] else self.param_container["prev_lower"]

        self.param_container["min_max_candles"].append(new_candle)
        self.param_container["min_max_candles"].pop(0)

        self.param_container["prev_upper"], self.param_container["prev_lower"] = final_upper, final_lower
        self.param_container["ATR"] = current_ATR

        return [final_upper, final_lower, current_ATR]

    def get_candle_param(self, new_candle: Candle) -> dict:
        final_upper, final_lower, current_ATR = self._param_calculation(new_candle)
        return {"ST_upper": final_upper, "ST_lower": final_lower, "ATR": current_ATR}

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        current_price = float(quotation_to_decimal(new_candle.close))
        final_upper, final_lower = self._param_calculation(new_candle)

        if current_price > final_upper:
            return self.action.BUY
        elif current_price < final_lower:
            return self.action.SELL
        else:
            return self.action.KEEP
