import asyncio
from historyData.HistoryData import HistoryData


class TestingMA:
    def __init__(self):
        self.testing_sum = 100
        self.historyData = HistoryData()
        self.longTerm = 50 #days, hours, minutes
        self.shortTerm = 5 #days, hours, minutes
        self.startingPoint = self.longTerm # where should testing data start

    async def sell_buy_decision(self):
        candles = await self.historyData.GetAllData()
        start_sum = self.testing_sum
        sum_bought = 0

        longTermLst, shortTerm = list(), list()
        for i in range(len(candles) - self.longTerm + 1):
            longTermLst.append(self.get_long_term_MA(candles))
            shortTerm.append(self.get_short_term_MA(candles))
            self.startingPoint += 1

            if i != 0 and longTermLst[i] <= shortTerm[i] and longTermLst[i - 1] > shortTerm[i - 1]:
                print("buy", candles[i + self.longTerm - 1]["close"])
                sum_bought = candles[i + self.longTerm - 1]["close"]
            if i != 0 and longTermLst[i] >= shortTerm[i] and longTermLst[i - 1] < shortTerm[i - 1]:
                if sum_bought == 0:
                    continue
                print("sell", candles[i + self.longTerm - 1]["close"])
                percent = 1 - sum_bought / candles[i + self.longTerm - 1]["close"]
                self.testing_sum += self.testing_sum * percent

        print(f"starting sum: {start_sum}, final sum: {self.testing_sum}, "
              f"percent: {round((self.testing_sum - start_sum) / start_sum * 100, 2)}")

    def get_short_term_MA(self, candles):
        candelCloseSum = 0
        for i in range(self.startingPoint - self.longTerm, self.startingPoint):
            candelCloseSum += candles[i]["close"]

        candleAvg = candelCloseSum / self.longTerm
        return candleAvg

    def get_long_term_MA(self, candles):
        candelCloseSum = 0
        for i in range(self.startingPoint - self.shortTerm, self.startingPoint):
            candelCloseSum += candles[i]["close"]

        candleAvg = candelCloseSum / self.shortTerm
        return candleAvg


if __name__ == "__main__":
    test = TestingMA()
    asyncio.run(test.sell_buy_decision())