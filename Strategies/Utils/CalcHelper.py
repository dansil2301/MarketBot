import math

from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import quotation_to_decimal


class CalcHelper:
    def MA_calc(self, candles: list[Candle]) -> float:
        avg = sum(float(quotation_to_decimal(candle.close))
                  for candle in candles) / len(candles)
        return avg

    def EMA_calc(self, prev_ema: float, a_param: float, current_price: float) -> float:
        return a_param * current_price + (1 - a_param) * prev_ema

    def cloud_min_max(self, candles: list[Candle]) -> float:
        min_candle = min(float(quotation_to_decimal(candle.close)) for candle in candles)
        max_candle = max(float(quotation_to_decimal(candle.close)) for candle in candles)
        return (min_candle + max_candle) / 2

    def std_dev(self, avr: float, candles: list[Candle]) -> float:
        power_diff = sum(pow(abs(avr) - float(quotation_to_decimal(candle.close)), 2) for candle in candles)
        return math.sqrt(power_diff / (len(candles) - 1))
