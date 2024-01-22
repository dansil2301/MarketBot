import sqlite3
from datetime import timedelta
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.utils import now
from tokenData.TokenData import TokenData
import asyncio


class HistoryData:
    def __init__(self):
        tokenData = TokenData()
        self.TOKEN = tokenData.GetToken("TOKEN")
        print(self.TOKEN)

    async def SaveHistoryData(self):
        async with AsyncClient(self.TOKEN) as client:
            async for candle in client.get_all_candles(
                    figi="BBG004730N88",
                    from_=now() - timedelta(days=365),
                    interval=CandleInterval.CANDLE_INTERVAL_HOUR,
            ):
                print(candle)


test = HistoryData()
asyncio.run(test.SaveHistoryData())