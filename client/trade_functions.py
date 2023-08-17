import okx.Trade
import pandas as pd
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

api = krakenex.API(
    'xD4LQF39wdRlYhCqjLbCMY2ClGs7hOJXBej5ZPJaNxl6Y9/9YADbs2q9', 'TIpv6kuRmiVXoJq1yUFM3CoGe5I1Li25m2FU41XLPIjOo4R/EQ2FPQWWq/WBcbhThLUx2gtDq8O6QCxHadv0qg==')
k = KrakenAPI(api)


def magic(pc, cp, lr):
    pc = float(pc)
    cp = float(cp)
    lr = float(lr)
    return pc + (cp - lr)


def get_price():
    price = k.get_ticker_information('XXBTZUSD')['c'][0][0]
    print(
        f"◉ {Fore.LIGHTYELLOW_EX}Current Price (CP) ↩ {Fore.CYAN}{Style.BRIGHT}{price}{Style.RESET_ALL}")
    return price


def balance():
    # Get account balance
    balance = k.get_account_balance()

    # Create a list of dictionaries to hold formatted data
    formatted_balance = [{'asset': asset, 'balance': f'{vol:.8f}'}
                         for asset, vol in balance['vol'].items()]

    print(f"◉ {Fore.YELLOW}Fetched current account info:\n")

    # Loop through each row of the formatted_balance dataframe and print the data in the desired format
    for row in formatted_balance:
        print(
            f"↳ {Fore.LIGHTYELLOW_EX}{row['asset']}{Style.RESET_ALL} {Fore.CYAN}--> {Fore.CYAN}{Style.BRIGHT}{row['balance']}{Style.RESET_ALL}")

# Always Trust The Model.


class AutoTrade:
    def __init__(self):
        pass

    def buy(self, qty, price, take_profit):
        cp = get_price()

        buy_order = k.add_standard_order(
            pair='XXBTZUSD',
            type='buy',
            ordertype='limit',
            price=str(cp),
            volume=str(qty),
            close_ordertype="limit",
            close_price=str(magic(pc=take_profit, cp=cp, lr=price) + 10),
            validate=False,
        )

        balance()
        print(buy_order)

    def sell(self, quantity):
        sell_order = k.add_standard_order(
            pair='XXBTZUSD',
            type_='sell',
            ordertype='market',
            volume=str(quantity),
            validate=False,
            userref=None
        )

        balance()
        print(sell_order)
