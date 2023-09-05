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
# import imp
# import ctypes
# import _thread
# import win32api

# # --------------------------------------------
# # Just something i copypasted off of stackoverflow to
# # patch the stupid fortran error.
# basepath = imp.find_module('numpy')[1]
# ctypes.CDLL(os.path.join(basepath, 'core', 'libmmd.dll'))
# ctypes.CDLL(os.path.join(basepath, 'core', 'libifcoremd.dll'))

# # Now set our handler for CTRL_C_EVENT. Other control event 
# # types will chain to the next handler.
# def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
#     if dwCtrlType == 0: # CTRL_C_EVENT
#         hook_sigint()
#         return 1 # don't chain to the next handler
#     return 0 # chain to the next handler

# win32api.SetConsoleCtrlHandler(handler, 1)
# # --------------------------------------------
# pls ignore this i tried fixing the stoobid fortran error but im too dumb for that.

dotenv.load_dotenv()
colorama_init()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
API_PASSPHRASE = os.getenv("PASS_PHRASE")
flag = "1"

# OKEx API endpoints
BASE_URL = 'https://www.okx.com/api/v5'

# Always Trust The Model.
def balance():
    try:
        # Get account balance
        AccountAPI = Account.AccountAPI(api_key=API_KEY, api_secret_key=API_SECRET, passphrase=API_PASSPHRASE, use_server_time=False, flag="1")
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

def get_price():
    try:
        MarketDataAPI = MarketData.MarketAPI(api_key=API_KEY, api_secret_key=API_SECRET, passphrase=API_PASSPHRASE, use_server_time=False, flag="1")
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

class AutoTrade:
    def __init__(self):
        pass

    def order(self, tpTriggerPx):
        try:
            AutoTradeAPI = Trade.TradeAPI(api_key=API_KEY, api_secret_key=API_SECRET, passphrase=API_PASSPHRASE, use_server_time=False, flag="1")

            # create a market buy order
            randInt = random.randint(10000, 99999999)
            orderId = str(f"ALGO{randInt}")
            algo_order = AutoTradeAPI.place_algo_order(
                instId="ETH-USDT",
                tdMode="cash",
                side="buy",
                ordType="conditional",
                sz="20",
                tpTriggerPx=f'{tpTriggerPx}',
                tpOrdPx=f'-1' # -1 means market price
            )
            # print the balance after placing the order.
            balance()
            print(algo_order)
        except Exception as e:
            print(f"{Fore.LIGHTRED_EX}Exception while running trader in trader.py run_trader() method.{Style.RESET_ALL}")
            print(e)

# ! message from sam
# so i didnt know where to start with fixing this shit after cooking all of that
# useless shit in model\model_test.py to test the model's accuracy in realtime as
# supposed to just downloading historical data from the past 7 days and running
# predictions on that. the tests take 2.5 hours to finish 10 epochs and 15 minute intervals.
# but hey it makes a nice graph and i personally buss to graphs. #! (pls help idk wtf im doing)
