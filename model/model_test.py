import time
from colorama import Style
from colorama import Fore
from colorama import init as colorama_init
from datetime import datetime
from sklearn.metrics import mean_squared_error
import pandas as pd
import multiprocessing
import time
import math
import requests
import pandas as pd
import numpy as np
import okx.MarketData as MarketData
import matplotlib.pyplot as plt
import os
import csv
import dotenv
import sys

sys.path.append('client\streamscript')
from run_streams import Streams
sys.path.insert(1, '')
from predict import Predictor
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

realtime_data = 'client\streamscript\streams\STREAM_ethusdt.csv'
predicted_data = 'client\streamscript\streams\TEST_ethusdt.csv'

epochs = 10 # tests model 10 times, 10 x 15 = 150 minutes, 2.5 hours of testing.
sleep_time = 900 # tests model on realtime data every 15 minutes, change if required.

def fetch_prediction():
    try:
        predictor = Predictor(realtime_data)
        Predictor.load_data(
            self=Predictor, file_path=realtime_data)

        pred_timestamp = Predictor.data.iloc[-1]["time"]
        pred_high = predictor.get_high()
        high_data = Predictor.data.iloc[-1]["high"]
        pred_low = predictor.get_low()
        low_data = Predictor.data.iloc[-1]["low"]
        pred_close = predictor.get_close()
        close_data = Predictor.data.iloc[-1]["close"]

        # write predictions to another csv
        if not os.path.exists(predicted_data):
            with open(predicted_data, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['time', 'high', 'low', 'close'])

        # if path already exists, and if data is already in csv, don't write it again
        elif os.path.exists(predicted_data):
            with open(predicted_data, mode='r') as file:
                reader = csv.reader(file)
                rows = list(reader)
                if len(rows) > 1:
                    if rows[-1][0] == pred_timestamp:
                        pass
                    
        # save data to csv
        with open(predicted_data, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([pred_timestamp, pred_high, pred_low, pred_close])

        print(
            f"◉ {Fore.LIGHTYELLOW_EX}Fetched predictions for {Style.BRIGHT}ETH-USDT{Style.RESET_ALL}{Fore.LIGHTYELLOW_EX} at {Style.BRIGHT}{datetime.now()}{Style.RESET_ALL}")
        print(
            f"◉ {Fore.LIGHTYELLOW_EX}15m Predicted high ↪ {Fore.CYAN}{Style.BRIGHT}{str(pred_high)}{Style.RESET_ALL}")
        print(
            f"◉ {Fore.LIGHTYELLOW_EX}15m Predicted low ↪ {Fore.CYAN}{Style.BRIGHT}{str(pred_low)}{Style.RESET_ALL}")
        print(
            f"◉ {Fore.LIGHTYELLOW_EX}15m Predicted close ↪ {Fore.CYAN}{Style.BRIGHT}{str(pred_close)}{Style.RESET_ALL}")
    except Exception as e:
        print("Exception while predicting in model_test.py get_prediction() method.")
        print(e)

def fetch_result(realtime_csv, predicted_csv, value):
    try:
        # Read real-time data and predicted data
        raw = pd.read_csv(realtime_csv)
        formatted = raw.tail(epochs) # number of rows to be preserved = number of epochs.
        formatted.to_csv(realtime_csv, index=False)
        real_data = pd.read_csv(realtime_csv)
        predicted_data = pd.read_csv(predicted_csv)
        
        # Extract the real and predicted values
        real_values = real_data[value].values
        predicted_values = predicted_data[value].values
        
        # Create a time index for the x-axis (assuming there's a 'Date' column)
        time_index = pd.to_datetime(real_data['time'])
        
        # Plot real values and predicted values
        plt.plot(time_index, real_values, color='red', label='Real ' + value)
        plt.plot(time_index, predicted_values, color='blue', label='Predicted ' + value)
        plt.title(value + " Prediction Results")
        plt.xlabel('Date')
        plt.ylabel(value)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        # Calculate and print RMSE
        rmse = math.sqrt(mean_squared_error(real_values, predicted_values))
        error = rmse/np.mean(real_values)
        print(f'◌ {Fore.GREEN}RMSE: {Style.BRIGHT}{rmse}{Style.RESET_ALL}')
        print(f'◌ {Fore.GREEN}Mean error: {Style.BRIGHT}{error}{Style.RESET_ALL}')
    except Exception as e:
        print("Exception while visualizing accuracy in model_test.py result() method.")
        print(e)

if __name__ == '__main__':
    print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}︙ ――――――――― Testing Model ――――――――― ︙{Style.RESET_ALL}")
    for i in range(0, epochs):
        stream = Streams()
        stream.run()
        time.sleep(6)
        fetch_prediction()
        time.sleep(sleep_time)

    high_result = fetch_result(realtime_data, predicted_data, "high")
    high_thread = multiprocessing.Process(target=high_result)
    high_thread.start()
    low_result = fetch_result(realtime_data, predicted_data, "low")
    low_thread = multiprocessing.Process(target=low_result)
    low_thread.start()
    close_result = fetch_result(realtime_data, predicted_data, "close")
    close_thread = multiprocessing.Process(target=close_result)
    close_thread.start()

    print(
        f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}︙ ――――――――――― Done ――――――――――― ︙{Style.RESET_ALL}")
    input(
        f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}◌ Press enter to exit{Style.RESET_ALL}")
    os.remove(realtime_data)
    os.remove(predicted_data)
    exit()

# ~ ong helo mof ~