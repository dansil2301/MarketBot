import asyncio
from datetime import timedelta

from tinkoff.invest.grpc.marketdata_pb2 import Candle
from tinkoff.invest.utils import now
from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
    CandleInterval,
)

from Utils.DataConvert import DataCovert
from tokenData.TokenData import TokenData


class StrategyAM:
    def __init__(self):
        tokenData = TokenData()
        self.TOKEN = tokenData.GetToken("SANDBOX_TOKEN")
        self.converter = DataCovert()
        self.longTerm = 50  # minutes
        self.shortTerm = 5  # minutes
        self.testSum = 100
        self.boughtAt = None

    async def getLongShortTermPeriod(self):
        longTermCandles, shortTermCandles = list(), list()
        async with AsyncClient(self.TOKEN) as client:
            async for candle in client.get_all_candles(
                    figi="BBG004730N88",
                    from_=now() - timedelta(minutes=(self.longTerm + 1)),
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
            ):
                longTermCandles.append(candle)
        return {"long": longTermCandles, "short": longTermCandles[len(longTermCandles) - self.shortTerm:]}

    async def streamIterator(self):
        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=[
                    CandleInstrument(
                        figi="BBG004730N88",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    )
                ],
            )
        )
        while True:
            await asyncio.sleep(1)

    async def asyncStreamClient(self):
        minuteChecker = now().minute
        long_short = await self.getLongShortTermPeriod()
        async with AsyncClient(self.TOKEN) as client:
            async for marketdata in client.market_data_stream.market_data_stream(
                    self.streamIterator()
            ):
                if marketdata.candle and minuteChecker != marketdata.candle.time.minute:
                    minuteChecker = marketdata.candle.time.minute
                    long_short = self.buySellDecision(long_short, marketdata.candle)

    def buySellDecision(self, long_short: dict, newCandle: Candle):
        prev_long = sum(self.converter.ConvertTinkoffMoneyToFloat(candle.close)
                        for candle in long_short["long"]) / len(long_short["long"])
        prev_short = sum(self.converter.ConvertTinkoffMoneyToFloat(candle.close)
                         for candle in long_short["short"]) / len(long_short["short"])

        long_short["long"].pop(0)
        long_short["short"].pop(0)
        long_short["long"].append(newCandle)
        long_short["short"].append(newCandle)

        new_long = sum(self.converter.ConvertTinkoffMoneyToFloat(candle.close)
                       for candle in long_short["long"]) / len(long_short["long"])
        new_short = sum(self.converter.ConvertTinkoffMoneyToFloat(candle.close)
                        for candle in long_short["long"]) / len(long_short["long"])

        candleClose = self.converter.ConvertTinkoffMoneyToFloat(newCandle)
        if prev_long > prev_short and new_long <= new_short:
            self.boughtAt = candleClose
            print(f"buy, current sum: {self.boughtAt} {prev_long} {new_long}")
        elif prev_long < prev_short and new_long >= new_short:
            if self.boughtAt:
                percent = 1 - self.boughtAt / candleClose
                self.testSum += self.testSum * percent
                print(f"sell, current_balance: {self.testSum}, current sum: {candleClose}")
            print("couldn't sell")
        else:
            print("wait")

        return long_short


if __name__ == "__main__":
    test = StrategyAM()
    asyncio.run(test.asyncStreamClient())
