import numpy as np
import pandas as pd
import yfinance as yf
import os
import joblib

# Define the ticker symbol.
ticker_symbol = 'EURUSD=X'

print("Options for ticker interval: 15m, 30m, 1h, 1d")
ticker_interval = input("Enter an interval for signal prediction: ")
if ticker_interval not in ['15m', '30m', '1h', '1d']:
    print("Invalid interval. Defaulting to 15m.")
    ticker_interval = '15m' # i dont even have to fuckging do this but im bored.

if ticker_interval == '1d':
    ticker_period = '1y'
else:
    ticker_period = '1mo'
print(f"Fetching data for {ticker_symbol} with {ticker_interval} interval for the last {ticker_period}.")

try:
    # fetching last 60 days of data with 15min granularity because-
    # i thought it'll be more optimal to train the model on.
    data = yf.download(ticker_symbol, period=ticker_period,
                       interval=ticker_interval, progress=False)

    # Display the first few rows of the data
    # print("[DEBUG] The first few rows of raw data:")
    # display(data.head())

except Exception as e:
    print(f"An error occurred: {str(e)}")


# Put data into Pandas Dataframe
df = pd.DataFrame(data)
df[['Open','High','Low','Close','Adj Close']] = df[['Open','High','Low','Close','Adj Close']].apply(lambda x: 1.0/x)

# Display the first few rows of the DataFrame
# print("[DEBUG] The first few rows of the DataFrame:")
#display(df.head())

# Normalize aclose value and plot 'return' column
df['Return'] = df['Adj Close'] - df['Adj Close'].shift(1)
return_range = df['Return'].max() - df['Return'].min()
df['Return'] = df['Return'] / return_range

# Make label, 1 as rising price, 0 as falling price
df['Label'] = df['Return'].shift(-1)
df['Label'] = df['Label'].apply(lambda x: 1 if x > 0.0 else 0) # WE DONT NEED ANY OF THIS LMFAO

# Display the tail of the DataFrame with labels
# print("[DEBUG] The tail of the DataFrame with labels:")
# df.tail()


# Reset the index of the DataFrame
df.reset_index(drop=True, inplace=True)

n_features = 13  # number of features, has to be 13 because thats what the model accepts as input.

data_x = np.array([]).reshape([-1, n_features])
data_y = np.array([]).reshape([-1, 1])

# Check if 'Label' is in the columns of your DataFrame
if 'Label' not in df.columns:
    print("The 'Label' column does not exist in your DataFrame.") # this is completely unnecessary but idc my brain wanna kms.
else:
    for index, row in df.iterrows():
        i = df.index.get_loc(index)
        if i < n_features:
            continue

        _x = np.array(df[i - n_features + 1:i + 1]['Return']).T.reshape([1, -1])
        _y = df.loc[i, 'Label'] 

        data_x = np.vstack((data_x, _x))
        data_y = np.vstack((data_y, _y))

    # Reshape train_y to 1D array
    data_y = data_y.reshape(-1)

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path to the model file relative to the current directory
model_filename = os.path.join(current_dir, f"../models/{ticker_interval}.h5")

# Load the trained model
clf = joblib.load(model_filename)

# Select the latest row of input data
latest_features = data_x[-1].reshape(1, -1)

# Perform prediction
prediction = clf.predict(latest_features)

# Print the prediction.
# print("[DEBUG] Signal code: ", prediction)

# Interpret the prediction
if prediction == 0:
    print(f"The model predicts that the EUR/USD price will increase for the next {ticker_interval} interval.")
else:
    print(f"The model predicts that the EUR/USD price will decrease for the next {ticker_interval} interval.")