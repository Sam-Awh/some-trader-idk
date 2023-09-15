import time
from colorama import Style
from colorama import Fore
from colorama import init as colorama_init
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from keras.optimizers import RMSprop
from keras.layers import LSTM, Bidirectional, Dense, Dropout
from keras.models import Sequential
import sys
sys.path.append('client\streamscript')
from run_streams import Streams
import os

colorama_init()

def load_data(file_path, value):
    try:
        data = pd.read_csv(file_path)
        data = data[[value]].values
        scaler = MinMaxScaler()
        data = scaler.fit_transform(data)
        x = data[:-1]
        y = data[1:]
        x = np.reshape(x, (x.shape[0], x.shape[1], 1))
        return x, y, scaler
    except Exception as e:
        print("Exception while loading data in model_refresh.py load_data() method.")
        print(e)


def create_model():
    try:
        model = Sequential()
        model.add(Bidirectional(
            LSTM(units=256, activation='tanh'), input_shape=(None, 1)))
        model.add(Dropout(0.2))
        model.add(Dense(units=1, activation='relu'))
        optimizer = RMSprop(learning_rate=0.0001)
        model.compile(optimizer=optimizer, loss='mean_squared_error')
        return model
    except Exception as e:
        print("Exception while creating model in model_refresh.py create_model() method.")
        print(e)


def train_model(model, x_train, y_train, type):
    try:
        print(f"◍ {Fore.GREEN}Training the {Style.BRIGHT}{type}{Style.RESET_ALL} {Fore.GREEN}model{Style.RESET_ALL}")
        model.fit(x_train, y_train, batch_size=256, epochs=250, verbose=0)
        return model
    except Exception as e:
        print("Exception while training model in model_refresh.py train_model() method.")
        print(e)


def test_model(model, scaler, file_path, value):
    try:
        data = pd.read_csv(file_path)
        price = data[[value]].values
        inputs = price
        inputs = scaler.transform(inputs)
        inputs = np.reshape(inputs, (inputs.shape[0], inputs.shape[1], 1))
        predicted = model.predict(inputs, verbose=0)
        predicted = scaler.inverse_transform(predicted)
        plt.plot(price, color='red', label='Real Market ' + value)
        plt.plot(predicted, color='blue', label='Predicted Market ' + value)
        plt.title(value + " Prediction Results")
        plt.xlabel('Days')
        plt.ylabel('Market ' + value)
        plt.legend()
        plt.show()
        rmse = math.sqrt(mean_squared_error(price, predicted))
        error = rmse/np.mean(price)
        print(f'◌ {Fore.GREEN}RMSE: {Style.BRIGHT}{rmse}{Style.RESET_ALL}')
        print(f'◌ {Fore.GREEN}Mean error: {Style.BRIGHT}{error}{Style.RESET_ALL}')
    except Exception as e:
        print("Exception while testing model in model_refresh.py test_model() method.")
        print(e)


def model_close():
    try:
        file_path = 'ETHUSDT_Kline_Data.csv'
        x_train, y_train, scaler = load_data(file_path, "close")
        model = create_model()
        trained_model = train_model(model, x_train, y_train, "close")
        test_model(trained_model, scaler, file_path, "close")
        trained_model.save('out/close.h5')
    except Exception as e:
        print("Exception while training model in model_refresh.py model_close() method.")
        print(e)


def model_low():
    try:
        file_path = 'ETHUSDT_Kline_Data.csv'
        x_train, y_train, scaler = load_data(file_path, "low")
        model = create_model()
        trained_model = train_model(model, x_train, y_train, "low")
        test_model(trained_model, scaler, file_path, "low")
        trained_model.save('out/low.h5')
    except Exception as e:
        print("Exception while training model in model_refresh.py model_low() method.")
        print(e)


def model_high():
    try:
        file_path = 'ETHUSDT_Kline_Data.csv'
        x_train, y_train, scaler = load_data(file_path, "high")
        model = create_model()
        trained_model = train_model(model, x_train, y_train, "high")
        test_model(trained_model, scaler, file_path, "high")
        trained_model.save('out/high.h5')
    except Exception as e:
        print("Exception while training model in model_refresh.py model_high() method.")
        print(e)


if __name__ == '__main__':
    try:
        StreamProcess = multiprocessing.Process(target=Streams().run)
        StreamProcess.start()
        time.sleep(5)
        print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}︙ ――――――――― Training ――――――――― ︙{Style.RESET_ALL}")
        model_close()
        model_high()
        model_low()
        print(f"{Fore.GREEN}{Style.BRIGHT}︙ ―――――――― Done ―――――――― ︙{Style.RESET_ALL}")
    except KeyboardInterrupt:
        print(f"{Fore.LIGHTRED_EX}Stopping datastream...{Style.RESET_ALL}")
        Streams().stop()
        time.sleep(2)
        print(f"{Fore.LIGHTRED_EX}Training Module shutting down...{Style.RESET_ALL}")
        exit()
