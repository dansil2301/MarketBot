import asyncio

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)

from tokenData.TokenData import TokenData


class StrategyAM:
    def __init__(self):
        tokenData = TokenData()
        self.TOKEN = tokenData.GetToken("SANDBOX_TOKEN")
        self.longTerm = 50  # days, hours, minutes
        self.shortTerm = 5  # days, hours, minutes

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
        async with AsyncClient(self.TOKEN) as client:
            async for marketdata in client.market_data_stream.market_data_stream(
                    self.streamIterator()
            ):
                print(marketdata)


if __name__ == "__main__":
    test = StrategyAM()
    asyncio.run(test.asyncStreamClient())