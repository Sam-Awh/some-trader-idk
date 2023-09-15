import requests
import json
import csv
from datetime import datetime, timedelta

# Binance API URL
url = "https://api.binance.com/api/v1/klines"

# Symbol (ETHUSDT) and Interval (30m)
symbol = "ETHUSDT"
interval = "30m"

# Calculate the start and end timestamps for the past month
end_time = int(datetime.now().timestamp() * 1000)
start_time = int((datetime.now() - timedelta(days=21)).timestamp() * 1000)

# Parameters for the API request
params = {
    "symbol": symbol,
    "interval": interval,
    "startTime": start_time,
    "endTime": end_time,
    "limit": 1000,  # Maximum limit per request
}

# Send the GET request to Binance API
response = requests.get(url, params=params)

if response.status_code == 200:
    kline_data = json.loads(response.text)
    # kline_data is a list of lists containing OHLCV data
    # Each entry is [timestamp, open, high, low, close, volume, close_time, quote_asset_volume, trades, taker_buy_base, taker_buy_quote, ignore]

    # Create and open a CSV file for writing
    with open("ETHUSDT_Kline_Data.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write the header row
        csv_writer.writerow(
            ["time", "open", "high", "low", "close", "volume"])

        # Write K-line data to the CSV file
        for kline in kline_data:
            # Extract relevant data
            timestamp = datetime.utcfromtimestamp(
                kline[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            open_price = kline[1]
            high_price = kline[2]
            low_price = kline[3]
            close_price = kline[4]
            volume = kline[5]

            # Write data to CSV
            csv_writer.writerow(
                [timestamp, open_price, high_price, low_price, close_price, volume])

    print("K-line data has been written to ETHUSDT_Kline_Data.csv")
else:
    print(f"Error: {response.status_code}")
