import time
from datetime import datetime
import os
from predict import Predictor
from client.streamscript.run_streams import Streams
from client.trade_functions import AutoTrade
import threading
import math
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
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

colorama_init()

trading_client = AutoTrade()
LAST_TIMESTAMP_FILE = "last_timestamp.txt"


def run_trader():
    try:
        global predictor
        predictor = Predictor("client\streamscript\streams\STREAM_ethusdt.csv")

        if os.path.exists(LAST_TIMESTAMP_FILE):
            with open(LAST_TIMESTAMP_FILE, "r") as f:
                last_timestamp_str = f.read().strip()
                last_timestamp = datetime.strptime(
                    last_timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp()
        else:
            last_timestamp = int(time.time())

        while True: # actually do shit
            time.sleep(1) # DONT REMOVE THIS. trading client needs to wait for datastream csv to be created to use the csv's data.
            Predictor.load_data(
                self=Predictor, file_path="client\streamscript\streams\STREAM_ethusdt.csv")
            if Predictor.data.iloc[-1]["time"] != last_timestamp:
                last_timestamp = Predictor.data.iloc[-1]["time"]
                predicted_close = predictor.get_close()
                live_price = Predictor.data.iloc[-1]["close"]
                signal = ""

                if float(predicted_close) > float(live_price):
                    signal = "Buy"
                elif float(predicted_close) < float(live_price):
                    signal = "Hold"
                else:
                    pass

                print(
                    f"{Fore.LIGHTYELLOW_EX}︙ ―――――――― {Fore.RED}{Style.BRIGHT}Pyre{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}Trader {Fore.LIGHTYELLOW_EX}―――――――― ︙{Style.RESET_ALL}")
                print(
                    f"✚ {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Playing with those numbers, give me a second ︙ {time.ctime()}.{Style.RESET_ALL}")
                print(
                    f"◉ {Fore.LIGHTYELLOW_EX}15m Current close (LR) ↪ {Fore.CYAN}{Style.BRIGHT}{str(live_price)}{Style.RESET_ALL}")
                print(
                    f"◉ {Fore.LIGHTYELLOW_EX}15m Predicted close (PC) ↪ {Fore.CYAN}{Style.BRIGHT}{str(predicted_close)}{Style.RESET_ALL}")
                if signal == "Buy":
                    print(
                        f'◌ {Fore.LIGHTYELLOW_EX}Signal ︙ {Fore.GREEN}{Style.BRIGHT}{signal}{Style.RESET_ALL}')
                elif signal == "Hold":
                    print(
                        f'◌ {Fore.LIGHTYELLOW_EX}Signal ︙ {Fore.RED}{Style.BRIGHT}{signal}{Style.RESET_ALL}')

                if signal == "Buy":
                    floor_pred_close = math.floor(predicted_close)
                    floor_live_price = math.floor(live_price)
                    try:
                        trading_client.order(
                            price=floor_live_price,
                            take_profit=floor_pred_close,
                        )
                        print(
                            f'◌ {Fore.LIGHTGREEN_EX}BUY Signal Executed! ︙ {Fore.CYAN}{Style.BRIGHT}10USDT{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}of ETH{Style.RESET_ALL}')
                        pass
                    except Exception as e:
                        print(e)
                        exit()
                else:
                    pass

                print(
                    f"◍ {Fore.LIGHTYELLOW_EX}Bravo six going{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{Style.BRIGHT}dark{Style.RESET_ALL}{Fore.LIGHTYELLOW_EX}...{Style.RESET_ALL}")
                time.sleep(10)

                with open(LAST_TIMESTAMP_FILE, "w") as f:
                    f.write(str(last_timestamp))
            else:
                pass
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        time.sleep(1)
        print(f"{Fore.LIGHTRED_EX}Retinal Engine shutting down...{Style.RESET_ALL}")
        Streams().stop()
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
        time.sleep(1)
        exit()


if __name__ == "__main__":
    try:
        stream_thread = threading.Thread(target=Streams().run)
        stream_thread.start()
        trader_thread = threading.Thread(target=run_trader)
        trader_thread.start()
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        Streams().stop()
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
        time.sleep(2)
        print(f"{Fore.LIGHTRED_EX}Retinal Engine shutting down...{Style.RESET_ALL}")
        time.sleep(2)
        exit()
