from datetime import datetime
import os
import time
from predict import Predictor
from client.streamscript.run_streams import Streams
from client.trade_functions import AutoTrade
import threading
import math
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

trading_client = AutoTrade()
LAST_TIMESTAMP_FILE = "last_timestamp.txt"


def run_predictor():
    try:
        global predictor
        predictor = Predictor("client\streamscript\streams\STREAM_ethusd.csv")

        if os.path.exists(LAST_TIMESTAMP_FILE):
            with open(LAST_TIMESTAMP_FILE, "r") as f:
                last_timestamp_str = f.read().strip()
                last_timestamp = datetime.strptime(
                    last_timestamp_str, '%Y-%m-%d %H:%M:%S').timestamp()
        else:
            last_timestamp = int(time.time())

        while True:

            Predictor.load_data(
                self=Predictor, file_path="client\streamscript\streams\STREAM_ethusd.csv")
            if Predictor.data.iloc[-1]["time"] != last_timestamp:
                last_timestamp = Predictor.data.iloc[-1]["time"]
                predicted_close = predictor.get_close()
                live_price = Predictor.data.iloc[-1]["close"]
                signal = "Hold"

                if float(predicted_close) > float(live_price):
                    signal = "Buy"
                elif float(predicted_close) < float(live_price):
                    signal = "Sell"
                else:
                    pass

                print(
                    f"{Fore.YELLOW}{Style.BRIGHT}︙ ―――――――― Retinal Engine ―――――――― ︙{Style.RESET_ALL}")
                print(
                    f"✚ {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}Playing with those numbers, give me a second ︙ {time.ctime()}.{Style.RESET_ALL}")
                print(
                    f"◉ {Fore.LIGHTYELLOW_EX}15m close (LR) ↩ {Fore.CYAN}{Style.BRIGHT}{str(live_price)}{Style.RESET_ALL}")
                print(
                    f"◉ {Fore.LIGHTYELLOW_EX}15m close (PC) ↩ {Fore.CYAN}{Style.BRIGHT}{str(predicted_close)}{Style.RESET_ALL}")
                if signal == "Buy":
                    print(
                        f'◌ {Fore.LIGHTYELLOW_EX}Signal ︙ {Fore.GREEN}{Style.BRIGHT}{signal}{Style.RESET_ALL}')
                elif signal == "Sell":
                    print(
                        f'◌ {Fore.LIGHTYELLOW_EX}Signal ︙ {Fore.RED}{Style.BRIGHT}{signal}{Style.RESET_ALL}')

                if signal == "Buy":
                    floor_pred_close = math.floor(predicted_close)
                    floor_live_price = math.floor(live_price)
                    qty = 0.018
                    try:
                        trading_client.buy(
                            qty=qty,
                            price=floor_live_price,
                            take_profit=floor_pred_close,
                        )
                        print(
                            f'◌ {Fore.LIGHTGREEN_EX}Bought! ︙ {Fore.CYAN}{Style.BRIGHT}{qty}{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}of BTC{Style.RESET_ALL}')
                        pass
                    except Exception as e:
                        print(e)
                        exit()
                else:
                    pass

                print(
                    f"◍ {Fore.LIGHTYELLOW_EX}Bravo six going{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}{Style.BRIGHT}dark{Style.RESET_ALL}{Fore.LIGHTYELLOW_EX}...{Style.RESET_ALL}")
                time.sleep(900)

                with open(LAST_TIMESTAMP_FILE, "w") as f:
                    f.write(str(last_timestamp))
            else:
                pass
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        time.sleep(1)
        print(f"{Fore.LIGHTRED_EX}Retinal Engine shutting down...{Style.RESET_ALL}")
        Streams().stop()
        time.sleep(1)
        exit()


if __name__ == "__main__":
    try:
        stream_thread = threading.Thread(target=Streams().run)
        stream_thread.start()
        time.sleep(5)
        predictor_thread = threading.Thread(target=run_predictor)
        predictor_thread.start()
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        time.sleep(1)
        print(f"{Fore.LIGHTRED_EX}Retinal Engine shutting down...{Style.RESET_ALL}")
        Streams().stop()
        time.sleep(1)
        exit()
