import os
import pandas as pd
from datetime import datetime
import time
import requests
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

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
            return f"◉ {Fore.LIGHTBLUE_EX}Fetched data for {Style.BRIGHT}{self.symbol}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}"

        elif latest_row['close'].values[0] == last_row['close'].values[0]:
            return f"○ {Fore.LIGHTBLUE_EX}No new data, row already exists"

        else:
            latest_row.to_csv(self.filename, mode='a',
                              header=False, index=False)
            return f"◉ {Fore.LIGHTBLUE_EX}Fetched data for {Style.BRIGHT}{self.symbol}{Style.RESET_ALL}{Fore.LIGHTBLUE_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}"

    def run(self):
        while not self.stop_flag:
            print(
                f"{Fore.BLUE}{Style.BRIGHT}︙ ―――――――――――― Streams ――――――――――― ︙{Style.RESET_ALL}")
            print(self.fetch_data())
            time.sleep(900)


btc_stream = CryptoStream(
    'XETHZUSD', r'client/streamscript/streams/STREAM_ethusd.csv')


class Streams:
    def __init__(self):
        self.streams = []

    def run(self):
        btc_stream = CryptoStream(
            'XETHZUSD', r'client/streamscript/streams/STREAM_ethusd.csv')
        self.streams.append(btc_stream)
        btc_stream.run()

    def stop(self):
        for stream in self.streams:
            stream.stop()
            # file_path = "client/streamscript/streams/STREAM_ethusd.csv"
            # os.remove(file_path)


if __name__ == '__main__':
    try:
        datastream = Streams()
        datastream.run()

    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Shutting down datastream...{Style.RESET_ALL}")
        datastream.stop()
        exit()
