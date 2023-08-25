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

colorama_init()

API_KEY="7fb3cdca-5e17-424f-8070-7a0e6aa2ec7b"
API_SECRET="B46A417BC31279F5D465DC658C150D67"
PASS_PHRASE="JARASjaras6969$demoapi"
flag = "1"

MarketDataAPI = MarketData.MarketAPI(API_KEY, API_SECRET, PASS_PHRASE, False, flag)
ticker = MarketDataAPI.get_ticker(instId="ETH-USDT")

timestamp = datetime.fromtimestamp(int(ticker['data'][0]['ts']) / 1000).strftime('%Y-%m-%d %H:%M:%S')
high = ticker['data'][0]['high24h']
low = ticker['data'][0]['low24h']
close = ticker['data'][0]['last']

csv_file_path = 'client\streamscript\streams\STREAM_ethusdt.csv'
class CryptoStream:
    def __init__(self, symbol, filename):
        self.symbol = symbol
        self.filename = filename
        self.stop_flag = False

    def stop(self):
        self.stop_flag = True

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
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, high, low, close])
            return f"◉ {Fore.LIGHTBLUE_EX}Fetched data for {Style.BRIGHT}{self.symbol}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}"

        elif latest_row['close'].values[0] == last_row['close'].values[0]:
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, high, low, close])
            return f"○ {Fore.LIGHTBLUE_EX}No new data, row already exists"

        else:
            latest_row.to_csv(self.filename, mode='a',
                              header=False, index=False)
            with open(csv_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, high, low, close])
            return f"◉ {Fore.LIGHTBLUE_EX}Fetched data for {Style.BRIGHT}{self.symbol}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}"

    def run(self):
        while not self.stop_flag:
            print(
                f"{Fore.BLUE}{Style.BRIGHT}︙ ―――――――――― Streams ――――――――― ︙{Style.RESET_ALL}")
            print(self.fetch_data())
            time.sleep(8)


btc_stream = CryptoStream(
    'XETHZUSD', r'client/streamscript/streams/STREAM_ethusdt.csv')


class Streams:
    def __init__(self):
        self.streams = []

    def run(self):
        eth_stream = CryptoStream(
            'ETHUSDT', r'client/streamscript/streams/STREAM_ethusdt.csv')
        self.streams.append(eth_stream)
        eth_stream.run()
    def stop(self):
        for stream in self.streams:
            stream.stop()
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)

if __name__ == '__main__':
    try:
        datastream = Streams()
        datastream.run()

    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Shutting down datastream...{Style.RESET_ALL}")
        datastream.stop()
        exit()
