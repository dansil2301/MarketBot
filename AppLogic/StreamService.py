import asyncio
from typing import AsyncGenerator

from tinkoff.invest.grpc.marketdata_pb2 import Candle, CandleInterval

from Settings import Settings

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)


class StreamService:
    def __init__(self):
        self.settings = Settings()

    async def streamIterator(self, interval: SubscriptionInterval) -> None:
        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=[
                    CandleInstrument(
                        figi=self.settings.figi,
                        interval=interval,
                    )
                ],
            )
        )
        while True:
            await asyncio.sleep(1)

    async def streamCandle(self, interval: SubscriptionInterval) -> AsyncGenerator[Candle, None]:
        '''
        iterator that streams a Candle
        :return: Candle
        '''
        async with AsyncClient(self.settings.TOKEN) as client:
            async for marketdata in client.market_data_stream.market_data_stream(
                    self.streamIterator(interval)
            ):
                yield marketdata.candle
