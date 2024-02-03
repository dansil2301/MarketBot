from tinkoff.invest.utils import now

from App.StreamService import StreamService
from Strategies.StrategyMA import StrategyAM


class App:
    def __init__(self):
        self.strategy = StrategyAM()
        self.streamService = StreamService()

    async def trade(self):
        minuteChecker = now().minute
        async for candle in self.streamService.streamCandle():
            if candle and minuteChecker != candle.time.minute:
                minuteChecker = candle.time.minute