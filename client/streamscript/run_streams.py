import time
import os
import pandas as pd
from datetime import datetime
import requests
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import okx.MarketData as MarketData
import csv
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

colorama_init()

csv_file_path = 'client\streamscript\streams\STREAM_ethusdt.csv'
class DataStream:
    def __init__(self, symbol, filename):
        self.symbol = symbol
        self.filename = filename

    def fetch_data(self):
        url = f"https://api.kraken.com/0/public/OHLC?pair={self.symbol}&interval=15"
        response = requests.get(url)
        response.raise_for_status()
        klines = response.json()['result'][self.symbol]
        kline_data = []

        for kline in klines:
            kline_data.append({
                'time': datetime.fromtimestamp(int(kline[0])),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
            })

        df = pd.DataFrame(kline_data, columns=[
            'time', 'high', 'low', 'close'])
        df = df.iloc[:-1]
        last_row = None

        if os.path.isfile(self.filename):
            last_row = pd.read_csv(self.filename).tail(1)
        latest_row = df.iloc[-1:]

        if last_row is None:
            df.to_csv(self.filename, mode='w', header=True, index=False)
            return f"◉ {Fore.LIGHTBLUE_EX}Fetched data for {Style.BRIGHT}{self.symbol}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}"

        elif latest_row['close'].values[0] == last_row['close'].values[0]:
            return f"○ {Fore.LIGHTBLUE_EX}No new data, row already exists"

        else:
            latest_row.to_csv(self.filename, mode='a',
                              header=False, index=False)
            return f"◉ {Fore.LIGHTBLUE_EX}Fetched data for {Style.BRIGHT}{self.symbol}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}"

    def run(self):
        print(
            f"{Fore.BLUE}{Style.BRIGHT}︙ ―――――――――― Streams ――――――――― ︙{Style.RESET_ALL}")
        print(self.fetch_data())


class Streams:
    def __init__(self):
        pass

    def run(self):
        eth_stream = DataStream(
            'ETHUSDT', r'client/streamscript/streams/STREAM_ethusdt.csv')
        eth_stream.run()

if __name__ == '__main__': # debug only
    try:
        while True:
            datastream = Streams()
            datastream.run()
            time.sleep(10) # sam was here :>

    except KeyboardInterrupt:
        os.remove(csv_file_path)
        print(f"{Fore.LIGHTRED_EX}Shutting down datastream...{Style.RESET_ALL}")
        exit()

# completely stripped this of threading/multiprocessing as it can be
# used whenever you call these functions instead.
# ~ sam