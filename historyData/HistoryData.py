import sqlite3
from datetime import timedelta
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.grpc.marketdata_pb2 import HistoricCandle
from tinkoff.invest.utils import now
from tokenData.TokenData import TokenData
from Utils.DataConvert import DataCovert
import asyncio


class HistoryData:
    def __init__(self):
        tokenData = TokenData()
        self.TOKEN = tokenData.GetToken("SANDBOX_TOKEN")
        self.Converter = DataCovert()

    async def SaveHistoryData(self) -> None:
        async with AsyncClient(self.TOKEN) as client:
            async for candle in client.get_all_candles(
                    figi="BBG004730N88",
                    from_=now() - timedelta(days=365),
                    interval=CandleInterval.CANDLE_INTERVAL_HOUR,
            ):
                await self.AddData(candle)
                print(f"Saved: {candle}")

    async def AddData(self, candle: HistoricCandle):
        with sqlite3.connect("HistoryData.db") as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO historyData (open, close, high, low, volume, time, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.Converter.ConvertTinkoffMoneyToFloat(candle.open),
                  self.Converter.ConvertTinkoffMoneyToFloat(candle.close),
                  self.Converter.ConvertTinkoffMoneyToFloat(candle.high),
                  self.Converter.ConvertTinkoffMoneyToFloat(candle.low),
                  candle.volume, candle.time, candle.is_complete))


test = HistoryData()
asyncio.run(test.SaveHistoryData())