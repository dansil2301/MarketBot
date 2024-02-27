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

    async def trade(self) -> None:
        all_candles_period = await self.historyData.get_tinkoff_server_data(
            self.startTime, self.endTime, self.candle_interval)

        if self.strategy.__class__.__name__ != "StrategyRandomForest":
            period_candles = all_candles_period[:self.strategy.history_candles_length]
            self.strategy.initialize_moving_avg_container(period_candles)
        else:
            period = timedelta(days=20)
            candles = await HistoryData().get_tinkoff_server_data(end=self.startTime, start=self.startTime - period,
                                                                  interval=self.candle_interval)
            self.strategy.initialize_moving_avg_container(candles)

        for i in range(self.strategy.history_candles_length, len(all_candles_period)):
            if datetime.strptime(str(all_candles_period[i].time).replace('+00:00', ''), '%Y-%m-%d %H:%M:%S').weekday() in [5, 6]:
                continue
            self.action = await self.strategy.trade_logic(all_candles_period[i])
            self.take_action(all_candles_period[i])
        print(self.profit_loss)

    def take_action(self, candle):
        if not candle:
            return
        if self.action == ActionEnum.BUY:
            self.twice_in_row += 1
            if (self.bought_at == 0.1 or not self.bought_at) and self.twice_in_row > 1: #and self.twice_in_row > 2
                print("bought ", candle.close, candle.time)
                self.bought_at = float(quotation_to_decimal(candle.close))
                self.sum -= self.bought_at * 3
                self.sum -= self.bought_at * 3 * self.commission
        elif self.bought_at:
            self.twice_in_row = 0
            current_percent = (float(quotation_to_decimal(candle.close)) / self.bought_at - 1) * 100
            if current_percent > Settings().percent_up or current_percent < -Settings().percent_down: #current_percent > Settings().percent_up or current_percent < -Settings().percent_down

                if self.bought_at != 0.1 and self.bought_at:
                    if current_percent > Settings().percent_up:
                        self.profit_loss["profit"] += 1
                    elif current_percent < -Settings().percent_down:
                        self.profit_loss["loss"] += 1

                    current_sum = float(quotation_to_decimal(candle.close))
                    #percent = (current_sum / self.bought_at) - 1
                    self.sum += current_sum * 3
                    self.sum -= current_sum * 3 * self.commission
                    self.bought_at = 0.1
                    print(f"sold: ", self.sum, candle.close, candle.time)


if __name__ == "__main__":
    candle_interval = CandleInterval.CANDLE_INTERVAL_1_MIN
    # big drop
    date_start = datetime(2022, 2, 1)
    end_date = datetime(2022, 3, 1)

    # small up
    # date_start = datetime(2023, 2, 1)
    # end_date = datetime(2023, 3, 1)

    # new small up
    # date_start = datetime(2024, 2, 1)
    # end_date = datetime(2024, 2, 25)

    # big up
    # date_start = datetime(2023, 3, 1)
    # end_date = datetime(2023, 4, 1)

    test = HistoryAppTest(StrategyRandomForest(candle_interval), candle_interval, date_start, end_date)
    asyncio.run(test.trade())
