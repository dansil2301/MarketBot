import os
import sqlite3
from datetime import timedelta, datetime
from tinkoff.invest import CandleInterval, AsyncClient, Client
from tinkoff.invest.grpc.marketdata_pb2 import HistoricCandle
from tinkoff.invest.utils import now, quotation_to_decimal

from AppLogic.Settings import Settings
import asyncio


class HistoryData:
    def __init__(self):
        script_path = os.path.abspath(__file__)
        self.db_path = os.path.join(os.path.dirname(script_path), 'HistoryData.db')
        self.settings = Settings()

    async def GetTinkoffServerHistoryData(self, period: timedelta, interval: CandleInterval) -> list[HistoricCandle]:
        async with AsyncClient(self.settings.TOKEN) as client:
            candles = list()
            async for candle in client.get_all_candles(
                    figi=self.settings.figi,
                    from_=now() - period,
                    interval=interval,
            ):
                candles.append(candle)
        return candles

    def _get_table_name(self, interval: CandleInterval):
        if interval == CandleInterval.CANDLE_INTERVAL_1_MIN:
            return "historyData1Minute"
        elif interval == CandleInterval.CANDLE_INTERVAL_5_MIN:
            return "historyData5Minutes"
        elif interval == CandleInterval.CANDLE_INTERVAL_10_MIN:
            return "historyData10Minutes"
        elif interval == CandleInterval.CANDLE_INTERVAL_15_MIN:
            return "historyData15Minutes"
        elif interval == CandleInterval.CANDLE_INTERVAL_HOUR:
            return "historyDataHour"

    async def SaveHistoryData(self, interval: CandleInterval) -> None:
        with Client(self.settings.TOKEN) as client:
            for candle in client.get_all_candles(
                    instrument_id="BBG004730N88",
                    from_=datetime(2023, 1, 1),
                    to=datetime(2023, 2, 1),
                    interval=interval,
            ):
                await self.AddData(candle, self._get_table_name(interval=interval))
                print(f"Saved: {candle}")

    async def AddData(self, candle: HistoricCandle, table_name: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {table_name} (open, close, high, low, volume, time, is_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (float(quotation_to_decimal(candle.open)),
                  float(quotation_to_decimal(candle.close)),
                  float(quotation_to_decimal(candle.high)),
                  float(quotation_to_decimal(candle.low)),
                  candle.volume, candle.time, candle.is_complete))

    async def GetAllData(self, interval: CandleInterval) -> list[dict]:
        return_data = list()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT `open`, `close`, `high`, `low`, `volume`, `time`, `is_completed` "
                           f"FROM `{self._get_table_name(interval)}`")

            for row in cursor.fetchall():
                info = dict(row)
                return_data.append(info)

        return return_data


if __name__ == "__main__":
    test = HistoryData()
    asyncio.run(test.SaveHistoryData(interval=CandleInterval.CANDLE_INTERVAL_1_MIN))
    asyncio.run(test.SaveHistoryData(interval=CandleInterval.CANDLE_INTERVAL_5_MIN))
    asyncio.run(test.SaveHistoryData(interval=CandleInterval.CANDLE_INTERVAL_10_MIN))
    asyncio.run(test.SaveHistoryData(interval=CandleInterval.CANDLE_INTERVAL_15_MIN))
    asyncio.run(test.SaveHistoryData(interval=CandleInterval.CANDLE_INTERVAL_HOUR))
    # a = asyncio.run(test.GetTinkoffServerHistoryData(200))
    # print(a)
