from datetime import datetime
from tinkoff.invest.grpc.common_pb2 import Quotation


class DataCovert:
    def ConvertTinkoffMoneyToFloat(self, money: Quotation) -> float:
        floatMoney = money.units
        floatMoney += money.nano / 10**9
        return floatMoney
