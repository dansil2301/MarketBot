import os
import sqlite3
from datetime import timedelta
from tinkoff.invest import CandleInterval, AsyncClient
from tinkoff.invest.grpc.marketdata_pb2 import HistoricCandle
from tinkoff.invest.utils import now

from App.Settings import Settings
from tokenData.TokenData import TokenData
from Utils.DataConvert import DataCovert
import asyncio


class HistoryData:
    def __init__(self):
        script_path = os.path.abspath(__file__)
        self.db_path = os.path.join(os.path.dirname(script_path), 'HistoryData.db')
        self.Converter = DataCovert()
        self.settings = Settings()

    async def GetTinkoffServerHistoryData(self, periodMinutes: int) -> list[HistoricCandle]:
        async with AsyncClient(self.settings.TOKEN) as client:
            candles = list()
            async for candle in client.get_all_candles(
                    figi=self.settings.figi,
                    from_=now() - timedelta(minutes=periodMinutes),
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
            ):
                candles.append(candle)
        return candles

    async def SaveHistoryData(self) -> None:
        async with AsyncClient(self.settings.TOKEN) as client:
            async for candle in client.get_all_candles(
                    figi="BBG004730N88",
                    from_=now() - timedelta(days=30),
                    interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
            ):
                await self.AddData(candle)
                print(f"Saved: {candle}")

    async def AddData(self, candle: HistoricCandle):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO historyData (open, close, high, low, volume, time, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.Converter.ConvertTinkoffMoneyToFloat(candle.open),
                  self.Converter.ConvertTinkoffMoneyToFloat(candle.close),
                  self.Converter.ConvertTinkoffMoneyToFloat(candle.high),
                  self.Converter.ConvertTinkoffMoneyToFloat(candle.low),
                  candle.volume, candle.time, candle.is_complete))

    async def GetAllData(self) -> list[dict]:
        return_data = list()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT `open`, `close`, `high`, `low`, `volume`, `time`, `is_completed` FROM `historyData`")

            for row in cursor.fetchall():
                info = dict(row)
                return_data.append(info)

        return return_data


if __name__ == "__main__":
    test = HistoryData()
    a = asyncio.run(test.SaveHistoryData())
    print(a)
