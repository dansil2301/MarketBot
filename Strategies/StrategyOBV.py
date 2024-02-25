from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval
from tinkoff.invest.utils import quotation_to_decimal

from Strategies.StrategyABS import Strategy
from Strategies.Utils.ActionEnum import ActionEnum
from historyData.HistoryData import HistoryData


class StrategyOBV(Strategy):
    def __init__(self, interval: CandleInterval = CandleInterval.CANDLE_INTERVAL_1_MIN):
        super().__init__(interval)
        self.MA_OBV = 15

        self.param_container = dict()
        self.action = ActionEnum.KEEP

        self.history_candles_length = self.MA_OBV + 1
        #asyncio.run(self._initialize_moving_avg_container())

    async def _initialize_moving_avg_container(self) -> None:
        if self.interval != CandleInterval.CANDLE_INTERVAL_HOUR:
            period = timedelta(minutes=self.history_candles_length)
        else:
            period = timedelta(hours=self.history_candles_length)
        candles = await HistoryData().get_tinkoff_server_data_from_now(period=period, interval=self.interval)

        OBV_list, OBV = self._init_helper(candles)
        self.param_container = {
            "OBV": OBV,
            "OBV_list": OBV_list,
            "prev_candle": candles[-1]
        }

    def initialize_moving_avg_container(self, candles: list) -> None:
        OBV_list, OBV = self._init_helper(candles)
        self.param_container = {
            "OBV": OBV,
            "OBV_list": OBV_list,
            "prev_candle": candles[-1]
        }

    def _init_helper(self, candles: list[Candle]) -> tuple:
        OBV_list = list()
        OBV = 0
        for i in range(1, len(candles)):
            prev_candle = float(quotation_to_decimal(candles[i - 1].close))
            current_price = float(quotation_to_decimal(candles[i].close))

            if prev_candle > current_price:
                OBV -= candles[i].volume
            elif prev_candle < current_price:
                OBV += candles[i].volume

            OBV_list.append(OBV)

        return OBV_list, OBV_list[-1]

    def _param_calculation(self, new_candle: Candle) -> list[float]:
        prev_candle = float(quotation_to_decimal(self.param_container["prev_candle"].close))
        current_price = float(quotation_to_decimal(new_candle.close))

        prev_OBV = self.param_container["OBV"]
        if prev_candle > current_price:
            self.param_container["OBV"] -= new_candle.volume
        elif prev_candle < current_price:
            self.param_container["OBV"] += new_candle.volume

        prev_OBV_MA = self.calc_helper.MA_calc_list_float(self.param_container["OBV_list"])
        self.param_container["OBV_list"].append(self.param_container["OBV"])
        self.param_container["OBV_list"].pop(0)
        OBV_MA = self.calc_helper.MA_calc_list_float(self.param_container["OBV_list"])

        self.param_container["prev_candle"] = new_candle

        return [self.param_container["OBV"], OBV_MA]

    def get_candle_param(self, new_candle: Candle) -> dict:
        OBV, OBV_MA = self._param_calculation(new_candle)
        return {"OBV": OBV, "OBV_MA": OBV_MA}

    async def trade_logic(self, new_candle: Candle) -> ActionEnum:
        OBV, prev_OBV, OBV_MA, prev_OBV_MA = self._param_calculation(new_candle)

        if prev_OBV_MA > prev_OBV and OBV_MA <= OBV:
            return self.action.BUY
        elif OBV < prev_OBV and OBV_MA >= OBV:
            return self.action.SELL
        else:
            return self.action.KEEP