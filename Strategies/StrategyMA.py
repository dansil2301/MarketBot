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
from tokenData.TokenData import TokenData


class StrategyAM:
    def __init__(self):
        self.TOKEN = TokenData().GetToken("SANDBOX_TOKEN")
        self.streamService = StreamService()
        self.orderLogic = OrderLogic()
        self.longTerm = 20  # minutes
        self.shortTerm = 5  # minutes
        self.figi = "BBG004730N88"
        self.testSum = 100
        self.boughtAt = None

    async def getLongShortTermPeriod(self):
        longTermCandles, shortTermCandles = list(), list()
        async with AsyncClient(self.TOKEN) as client:
            async for candle in client.get_all_candles(
                    figi=self.figi,
                    from_=now() - timedelta(minutes=(self.longTerm)),
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
            ):
                longTermCandles.append(candle)
        return {"long": longTermCandles, "short": longTermCandles[len(longTermCandles) - self.shortTerm:]}

    async def trade(self):
        minuteChecker = now().minute
        long_short = await self.getLongShortTermPeriod()
        async for candle in self.streamService.streamCandle():
            if candle and minuteChecker != candle.time.minute:
                minuteChecker = candle.time.minute
                long_short = await self.buySellDecision(long_short, candle)

    async def buySellDecision(self, long_short: dict, newCandle: Candle):
        prev_long = sum(float(quotation_to_decimal(candle.close))
                        for candle in long_short["long"]) / len(long_short["long"])
        prev_short = sum(float(quotation_to_decimal(candle.close))
                         for candle in long_short["short"]) / len(long_short["short"])

        long_short["long"].append(newCandle)
        long_short["short"].append(newCandle)
        long_short["long"].pop(0)
        long_short["short"].pop(0)

        new_long = sum(float(quotation_to_decimal(candle.close))
                       for candle in long_short["long"]) / len(long_short["long"])
        new_short = sum(float(quotation_to_decimal(candle.close))
                        for candle in long_short["short"]) / len(long_short["short"])

        candleClose = float(quotation_to_decimal(newCandle.close))
        if prev_long > prev_short and new_long <= new_short:
            self.boughtAt = candleClose
            await self.orderLogic.buy_request()
            print(f"buy, current sum: {self.boughtAt}")
        elif prev_long < prev_short and new_long >= new_short:
            if self.boughtAt:
                await self.orderLogic.sell_request()
                balance = await self.orderLogic.get_account_details().money
                print(f"sell, current_balance: {balance}, "
                      f"current sum: {candleClose}")
            else:
                print("couldn't sell ", candleClose)
        else:
            print("wait", candleClose)

        return long_short


if __name__ == "__main__":
    test = StrategyAM()
    asyncio.run(test.trade())

