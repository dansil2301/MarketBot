""" Example - How to set/get balance for sandbox account.
    How to get/close all sandbox accounts.
    How to open new sandbox account. """

import logging
import os
from datetime import datetime
from decimal import Decimal
from tinkoff.invest import (
    Client,
    InstrumentIdType,
    StopOrderDirection,
    StopOrderExpirationType,
    StopOrderType, InvestError,
)
from tinkoff.invest import MoneyValue
from tinkoff.invest.sandbox.client import SandboxClient
from tinkoff.invest.utils import decimal_to_quotation, quotation_to_decimal

from tokenData.TokenData import TokenData

TOKEN = TokenData().GetToken("SANDBOX_TOKEN")

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)


def add_money_sandbox(client, account_id, money, currency="rub"):
    """Function to add money to sandbox account."""
    money = decimal_to_quotation(Decimal(money))
    return client.sandbox.sandbox_pay_in(
        account_id=account_id,
        amount=MoneyValue(units=money.units, nano=money.nano, currency=currency),
    )


def main():
    with SandboxClient(TOKEN) as client:
        sandbox_accounts = client.users.get_accounts()
        # account, *_ = response.accounts
        # account_id = account.id

        #close all sandbox accounts
        for sandbox_account in sandbox_accounts.accounts:
            client.sandbox.close_sandbox_account(account_id=sandbox_account.id)

        #open new sandbox account
        sandbox_account = client.sandbox.open_sandbox_account()
        print(sandbox_account.account_id)

        account_id = sandbox_account.account_id

        print(add_money_sandbox(client=client, account_id=account_id, money=100000))
        logger.info(
            "positions: %s", client.operations.get_positions(account_id=account_id)
        )
        print(
            "money: ",
            float(
                quotation_to_decimal(
                    client.operations.get_positions(account_id=account_id).money[0]
                )
            ),
        )


if __name__ == "__main__":
    main()
