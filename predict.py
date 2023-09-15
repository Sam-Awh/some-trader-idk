from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from client.streamscript.run_streams import Streams
import numpy as np
import pandas as pd
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
import multiprocessing
import time
import os

colorama_init()

class Predictor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.model = None
        self.scaler = None
        self.high = None
        self.close = None
        self.low = None

    def load_data(self, file_path):
        try:
            with open(file_path) as f:
                self.data = pd.read_csv(f)
        except Exception as e:
            print("Exception while loading data in predict.py load_data() method.")
            print(e)

    def scale_data(self, value):
        try:
            self.scaler = MinMaxScaler()
            self.scaled_data = self.scaler.fit_transform(self.data[[value]])
        except Exception as e:
            print("Exception while scaling data in predict.py scale_data() method.")
            print(e)

    def split_data(self):
        try:
            self.train_data = self.scaled_data[:-1]
            self.test_data = self.scaled_data[-1:]
        except Exception as e:
            print("Exception while splitting data in predict.py split_data() method.")
            print(e)

    def reshape_data(self):
        try:
            self.X_train = np.reshape(
                self.train_data, (self.train_data.shape[0], 1, 1))
            self.X_test = np.reshape(
                self.test_data, (self.test_data.shape[0], 1, 1))
        except Exception as e:
            print("Exception while reshaping data in predict.py reshape_data() method.")
            print(e)

    def load_model(self, filename):
        try:
            self.model = load_model(filename)
        except Exception as e:
            print("Exception while loading model in predict.py load_model() method.")
            print(e)

    def predict(self, value):
        try:
            if value == "high":
                self.high = self.model.predict(self.X_test, verbose=None)
                self.high = self.scaler.inverse_transform(
                    self.high)
                return self.high
            elif value == "close":
                self.close = self.model.predict(self.X_test, verbose=None)
                self.close = self.scaler.inverse_transform(
                    self.close)
                return self.close
            elif value == "low":
                self.low = self.model.predict(self.X_test, verbose=None)
                self.low = self.scaler.inverse_transform(
                    self.low)
                return self.low
            else:
                print("Invalid value passed to predict() method --> ", value)
        except Exception as e:
            print("Exception while predicting data in predict.py predict() method.")
            print(e)

    def get_high(self, file_path="client\streamscript\streams\STREAM_ethusdt.csv"):
        try:
            self.load_data(file_path)
            self.scale_data("high")
            self.split_data()
            self.reshape_data()
            self.load_model("out\high.h5")
            self.predict("high")
            return self.high[0][0]
        except Exception as e:
            print("Exception while predicting high in predict.py get_high() method.")
            print(e)

    def get_close(self, file_path="client\streamscript\streams\STREAM_ethusdt.csv"):
        try:
            self.load_data(file_path)
            self.scale_data("close")
            self.split_data()
            self.reshape_data()
            self.load_model("out\close.h5")
            self.predict("close")
            return self.close[0][0]
        except Exception as e:
            print("Exception while predicting close in predict.py get_close() method.")
            print(e)

    def get_low(self, file_path="client\streamscript\streams\STREAM_ethusdt.csv"):
        try:
            self.load_data(file_path)
            self.scale_data("low")
            self.split_data()
            self.reshape_data()
            self.load_model("out\low.h5")
            self.predict("low")
            return self.low[0][0]
        except Exception as e:
            print("Exception while predicting low in predict.py get_low() method.")
            print(e)


if __name__ == "__main__":
    try:
        stream_process = multiprocessing.Process(target=Streams().run)
        stream_process.start()
        time.sleep(5)
        predictor = Predictor("client\streamscript\streams\STREAM_ethusdt.csv")
        print(
            f"⨯ {Fore.RED}{Style.NORMAL}This script is running in debug mode.{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}{Style.BRIGHT}︙ ―――――――― {Fore.RED}{Style.BRIGHT}Pyre{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}Trader {Fore.GREEN}{Style.BRIGHT}―――――――― ︙{Style.RESET_ALL}")
        print(
            f"✚ {Fore.BLUE}{Style.NORMAL}Playing with those numbers, give me a second.{Style.RESET_ALL}")
        print(
           f"◉ {Fore.GREEN}15m high ↩ {Style.BRIGHT}{predictor.get_high()}{Style.RESET_ALL}")
        print(
            f"◉ {Fore.GREEN}15m close ↩ {Style.BRIGHT}{predictor.get_close()}{Style.RESET_ALL}")
        print(
           f"◉ {Fore.GREEN}15m low ↩ {Style.BRIGHT}{predictor.get_low()}{Style.RESET_ALL}")
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
    except KeyboardInterrupt:
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
        print(f"{Fore.RED}KeyboardInterrupt in predict.py main() method.{Style.RESET_ALL}")
        exit()
    except Exception as e:
        file_path = "client/streamscript/streams/STREAM_ethusdt.csv"
        os.remove(file_path)
        print("Exception while running predict.py main() method.")
        print(e)