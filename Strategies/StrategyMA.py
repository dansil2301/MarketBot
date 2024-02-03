import asyncio
from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import now, quotation_to_decimal
from tinkoff.invest import (
    AsyncClient,
    CandleInterval,
)

from App.OrderLogic import OrderLogic
from App.StreamService import StreamService
from historyData.HistoryData import HistoryData
from tokenData.TokenData import TokenData


class StrategyAM:
    def __init__(self):
        self.TOKEN = TokenData().GetToken("SANDBOX_TOKEN")
        self.streamService = StreamService()
        self.orderLogic = OrderLogic()
        self.longTerm = 50  # minutes
        self.shortTerm = 5  # minutes
        self.figi = "BBG004730N88"
        self.testSum = 100
        self.boughtAt = None

    async def getLongShortTermPeriod(self) -> dict:
        candles = await HistoryData().GetTinkoffServerHistoryData(self.longTerm)
        return {"long": candles, "short": candles[len(candles) - self.shortTerm:]}

    async def trade(self):
        minuteChecker = now().minute
        long_short = await self.getLongShortTermPeriod()
        async for candle in self.streamService.streamCandle():
            if candle and minuteChecker != candle.time.minute:
                minuteChecker = candle.time.minute
                long_short = await self.buySellDecision(long_short, candle)

    def candles_avr_counter(self, candles: list[Candle]) -> float:
        avg = sum(float(quotation_to_decimal(candle.close))
                  for candle in candles) / len(candles)
        return avg

    async def buySellDecision(self, long_short: dict, newCandle: Candle):
        prev_long = self.candles_avr_counter(long_short["long"])
        prev_short = self.candles_avr_counter(long_short["short"])

        long_short["long"].append(newCandle)
        long_short["short"].append(newCandle)
        long_short["long"].pop(0)
        long_short["short"].pop(0)

        new_long = self.candles_avr_counter(long_short["long"])
        new_short = self.candles_avr_counter(long_short["short"])

        candleClose = float(quotation_to_decimal(newCandle.close))
        if prev_long > prev_short and new_long <= new_short:
            self.boughtAt = candleClose
            await self.orderLogic.buy_request()
            print(f"buy, current sum: {self.boughtAt}")
        elif prev_long < prev_short and new_long >= new_short:
            if self.boughtAt:
                await self.orderLogic.sell_request()
                balance = await self.orderLogic.get_account_details()
                print(f"sell, current_balance: {balance.money}"
                      f"current sum: {candleClose}")
            else:
                print("couldn't sell ", candleClose)
        else:
            print("wait", candleClose)

        return long_short


if __name__ == "__main__":
    test = StrategyAM()
    asyncio.run(test.trade())

