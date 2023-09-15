import time
import os
from client.streamscript.run_streams import Streams
from trader import PyreTrader
import multiprocessing
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()

if __name__ == "__main__":
    trigger = True
    try:
        while trigger == True:
            data_stream_process = multiprocessing.Process(target=Streams().run)
            trader_process = multiprocessing.Process(target=PyreTrader.run_trader)

            data_stream_process.start()
            time.sleep(1)
            trader_process.start()

            data_stream_process.join()
            trader_process.join()
            time.sleep(900)

    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        trigger = False
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
        time.sleep(2)
        print(f"{Fore.LIGHTRED_EX}Shutting down...{Style.RESET_ALL}")
        time.sleep(2)
        exit()
    except Exception as e:
        print(f"{Fore.LIGHTRED_EX}Exception in the main process.{Style.RESET_ALL}")
        print(e)
