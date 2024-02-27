import asyncio
from _decimal import Decimal
from datetime import datetime, timedelta

from tinkoff.invest import SubscriptionInterval
from tinkoff.invest.grpc.marketdata_pb2 import CandleInterval
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal

from AppLogic.Settings import Settings
from Strategies.StrategyAroon import StrategyAroon
from Strategies.StrategyBB import StrategyBB
from Strategies.StrategyEMA import StrategyEMA
from Strategies.StrategyMA import StrategyMA
from Strategies.StrategyMACD import StrategyMACD
from Strategies.StrategyOBV import StrategyOBV
from Strategies.StrategyRandomForest import StrategyRandomForest
from Strategies.StrategyST import StrategyST
from Strategies.StrategyStochRSI import StrategyStochRSI
from Strategies.Utils.ActionEnum import ActionEnum
from Strategies.StrategyABS import Strategy
from Strategies.StrategyRSI import StrategyRSI
from historyData.HistoryData import HistoryData


class FakeCandle:
    def __init__(self, close):
        self.close = close


class HistoryAppTest:
    def __init__(self, strategy: Strategy, candleInterval: CandleInterval, startTime: datetime, endTime: datetime):
        self.strategy = strategy
        self.historyData = HistoryData()
        self.action = ActionEnum.KEEP
        self.sum = 1000
        self.commission = 0.0005
        self.bought_at = None
        self.candle_interval = candleInterval

        self.startTime = startTime
        self.endTime = endTime

        self.profit_loss = {"profit": 0, "loss": 0}
        self.twice_in_row = 0
        self.bought = list()

    async def get_year_candles(self, year: int):
        all_candles = []
        for i in range(6):
            candles = await HistoryData().get_tinkoff_server_data(end=datetime(year, i + 3, 1),
                                                                  start=datetime(year, i + 2, 2),
                                                                  interval=self.candle_interval)
            all_candles.extend(candles)
        return all_candles

    async def init_candles_for_new_day(self, current_date: datetime):
        self.strategy = StrategyRandomForest(self.candle_interval)
        period = timedelta(days=20)
        candles = await HistoryData().get_tinkoff_server_data(end=current_date, start=current_date - period,
                                                              interval=self.candle_interval)
        new_candles = []
        for filtered_candles in candles:
            if datetime.strptime(str(filtered_candles.time).replace('+00:00', ''),
                                 '%Y-%m-%d %H:%M:%S').weekday() in [5, 6]:
                continue
            new_candles.append(filtered_candles)
        self.strategy.initialize_moving_avg_container(new_candles)

    async def trade(self) -> None:
        # await self.historyData.get_tinkoff_server_data(self.startTime, self.endTime, self.candle_interval)
        # await self.get_year_candles(2023)
        all_candles_period = await self.historyData.get_tinkoff_server_data(self.startTime, self.endTime, self.candle_interval)
        date_candle = datetime.strptime(str(all_candles_period[self.strategy.history_candles_length].time).replace('+00:00', ''), '%Y-%m-%d %H:%M:%S')

        if self.strategy.__class__.__name__ != "StrategyRandomForest":
            period_candles = all_candles_period[:self.strategy.history_candles_length]
            self.strategy.initialize_moving_avg_container(period_candles)
        else:
            await self.init_candles_for_new_day(date_candle)

        day = date_candle.day
        for i in range(self.strategy.history_candles_length, len(all_candles_period)):
            date_candle = datetime.strptime(str(all_candles_period[i].time).replace('+00:00', ''), '%Y-%m-%d %H:%M:%S')
            if date_candle.weekday() in [5, 6]:
                continue
            # if day != date_candle.day:
            #     day = date_candle.day
            #     await self.init_candles_for_new_day(date_candle)
            self.action = await self.strategy.trade_logic(all_candles_period[i])
            self.take_action(all_candles_period[i])

        if self.bought != 0:
            for b in self.bought:
                print(b)
                self.sum += float(quotation_to_decimal(all_candles_period[i].close))
        print(f"Final sum: {self.sum}")
        print(self.profit_loss)

    def take_action(self, candle):
        if not candle:
            return
        if self.action == ActionEnum.BUY:
            self.twice_in_row += 1
            # if (self.bought_at == 0.1 or not self.bought_at) and self.twice_in_row > 1: #and self.twice_in_row > 2
            #     print("bought ", candle.close, candle.time)
            #     self.bought_at = float(quotation_to_decimal(candle.close))
            #     self.sum -= self.bought_at * 3
            #     self.sum -= self.bought_at * 3 * self.commission
            safe_counter = 0
            if self.sum - float(quotation_to_decimal(candle.close)) - float(quotation_to_decimal(candle.close)) * self.commission > 0 and self.twice_in_row > safe_counter:  #and self.twice_in_row > 2
                print("bought ", candle.close, candle.time)
                self.bought_at = float(quotation_to_decimal(candle.close))
                self.sum -= self.bought_at
                self.sum -= self.bought_at * self.commission
                self.bought.append({"bought": self.bought_at})
        if self.bought:
            for i, bought_at in enumerate(self.bought):
                current_percent = (float(quotation_to_decimal(candle.close)) / bought_at["bought"] - 1) * 100
                if current_percent > Settings().percent_up or current_percent < -Settings().percent_down: #current_percent > Settings().percent_up or current_percent < -Settings().percent_down
                    self.twice_in_row = 0

                    if bought_at["bought"] != 0.1 and bought_at["bought"]:
                        if current_percent > Settings().percent_up:
                            self.profit_loss["profit"] += 1
                        elif current_percent < -Settings().percent_down:
                            self.profit_loss["loss"] += 1

                        current_sum = float(quotation_to_decimal(candle.close))
                        #percent = (current_sum / self.bought_at) - 1
                        self.sum += current_sum
                        self.sum -= current_sum * self.commission
                        self.bought_at = 0.1
                        self.bought.pop(i)
                        print(f"sold: ", self.sum, candle.close, candle.time)


if __name__ == "__main__":
    candle_interval = CandleInterval.CANDLE_INTERVAL_5_MIN
    # big drop
    # date_start = datetime(2022, 2, 1)
    # end_date = datetime(2022, 3, 1)

    # small up
    # date_start = datetime(2023, 2, 1)
    # end_date = datetime(2023, 3, 1)

    # new small up
    date_start = datetime(2024, 2, 1)
    end_date = datetime(2024, 2, 27)

    # big up
    # date_start = datetime(2023, 3, 1)
    # end_date = datetime(2023, 4, 1)

    # small down
    # date_start = datetime(2023, 9, 1)
    # end_date = datetime(2023, 10, 1)

    test = HistoryAppTest(StrategyRandomForest(candle_interval), candle_interval, date_start, end_date)
    asyncio.run(test.trade())
