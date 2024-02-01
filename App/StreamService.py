import asyncio

from tinkoff.invest.strategies.base.models import Candle

from tokenData.TokenData import TokenData

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
    CandleInterval,
)


class StreamService:
    def __init__(self):
        tokenData = TokenData()
        self.TOKEN = tokenData.GetToken("SANDBOX_TOKEN")

    async def streamIterator(self) -> None:
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

    async def streamCandle(self) -> Candle:
        '''
        iterator that streams a Candle
        :return: Candle
        '''
        async with AsyncClient(self.TOKEN) as client:
            async for marketdata in client.market_data_stream.market_data_stream(
                    self.streamIterator()
            ):
                yield marketdata.candle
