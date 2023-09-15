import okx.Trade as Trade
import okx.Account as Account
import okx.MarketData as MarketData
import pandas as pd
import random
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

import os
import time
import dotenv

dotenv.load_dotenv()
colorama_init()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
PASS_PHRASE = os.getenv("PASS_PHRASE")
flag = "1"


def magic(pc, cp, lr):
    try:
        pc = float(pc)
        cp = float(cp)
        lr = float(lr)
        return pc + (cp - lr)
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Exception while calculating magic number in trader.py magic() method.{Style.RESET_ALL}")
        print(e)


def get_price():
    try:
        MarketDataAPI = MarketData.MarketAPI(
            api_key=API_KEY, api_secret_key=API_SECRET, passphrase=PASS_PHRASE, use_server_time=False, flag="1")
        price = MarketDataAPI.get_ticker(
            instId="ETH-USDT"
        )

        formatted = price['data'][0]['last']
        # print( # debug only
        #      f"◉ {Fore.LIGHTYELLOW_EX}Current Price (CP) ↩ {Fore.CYAN}{Style.BRIGHT}{formatted}{Style.RESET_ALL}")
        return formatted
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Exception while fetching current price in trader.py get_price() method.{Style.RESET_ALL}")
        print(e)


def balance():
    try:
        # Get account balance
        AccountAPI = Account.AccountAPI(
            api_key=API_KEY, api_secret_key=API_SECRET, passphrase=PASS_PHRASE, use_server_time=False, flag="1")
        b_eth = AccountAPI.get_account_balance(ccy="ETH")
        avail_bal_eth = b_eth['data'][0]['details'][0]['availBal']
        b_usdt = AccountAPI.get_account_balance(ccy="USDT")
        avail_bal_usdt = b_usdt['data'][0]['details'][0]['availBal']

        print(f"◉ {Fore.YELLOW}Fetched current account info:\n{Style.RESET_ALL}")
        print(f"{Fore.LIGHTMAGENTA_EX}ETH Balance ↪ {Fore.CYAN}{Style.BRIGHT}{avail_bal_eth}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}USDT Balance ↪ {Fore.CYAN}{Style.BRIGHT}{avail_bal_usdt}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Exception while fetching account balance in trader.py balance() method.{Style.RESET_ALL}")
        print(e)

# Always Trust The Model.


class AutoTrade:
    def __init__(self):
        pass

    def order(self, last_row, predict):
        try:
            AutoTradeAPI = Trade.TradeAPI(
                api_key=API_KEY, api_secret_key=API_SECRET, passphrase=PASS_PHRASE, use_server_time=False, flag="1")
            cp = get_price()

            # create a market buy order
            randint1 = random.randint(10000, 99999999)
            orderId1 = str(f"MARKETBUY{randint1}")
            buy_order = AutoTradeAPI.place_order(
                instId="ETH-USDT",
                tdMode="cash",
                side="buy",
                clOrdId=f"BUY{orderId1}",
                ordType="market",
                sz="10"
            )
            print(buy_order)
            time.sleep(1)

            # create a take profit order
            randint2 = random.randint(10000, 99999999)
            orderId2 = str(f"LIMITSELL{randint2}")
            take_profit_order = AutoTradeAPI.place_order(
                instId="ETH-USDT",
                tdMode="cash",
                clOrdId=f"TP{orderId2}",
                side="sell",
                ordType="limit",
                sz="0.0062",
                px=f"{magic(predict, cp, last_row)}"
            )

            balance()
            # printing this for debug
            print(buy_order)
            print(take_profit_order)
        except Exception as e:
            print(
                f"{Fore.LIGHTRED_EX}Exception while running trader in trader.py run_trader() method.{Style.RESET_ALL}")
            print(e)
