# Trading Strategy Backtesting with Gradient Boosting Classifier

## Introduction:
This Jupyter Notebook contains Python code for backtesting a trading strategy using a Gradient Boosting Classifier. The strategy is based on predicting the direction of future price movements in the EUR/USD exchange rate. The code involves data retrieval, preprocessing, feature engineering, model training, testing, and performance analysis.

## Libraries Used:
- `datetime`: For handling date and time information.
- `numpy`: For numerical operations.
- `pandas`: For data manipulation and analysis.
- `yfinance`: For fetching historical financial data from Yahoo Finance.
- `matplotlib` and `seaborn`: For data visualization.
- `IPython.core.display`: For enhancing display capabilities.

## Data Retrieval:
1. **Ticker Symbol**: 'EURUSD=X' is used for EUR/USD exchange rate.
2. **Date Range**: Data is fetched for the period from July 25, 2023, to September 21, 2023.
3. **Interval**: Data is collected at 30-minute intervals using the `yfinance` library.

## Data Preprocessing and Visualization:
1. Data is fetched and displayed in a DataFrame.
2. Close prices are plotted to visualize the EUR/USD exchange rate.
3. Data is inverted and plotted to visualize the inverted exchange rate.
4. Returns are normalized and plotted to visualize the normalized returns.

## Feature Engineering:
1. Labels are created based on whether the price will rise (1) or fall (0).
2. Features are constructed using a sliding window of historical returns.

## Model Training:
1. A Gradient Boosting Classifier is used for predicting price movements.
2. 95% of the data is used for training, and the last 5% is used for testing.

## Backtesting and Equity Calculation:
1. Predictions are made on the test data.
2. Equity is calculated based on the trading strategy's performance.
3. Trades, profits, and equity are visualized through plots.
4. A summary of trades is provided, including net profit, number of winning and losing trades, and other performance metrics.

## Conclusion:
The notebook demonstrates the process of developing, training, testing, and backtesting a trading strategy. Users can modify parameters, extend data ranges, or experiment with different classifiers to further enhance the strategy.

**Note**: Ensure that all required libraries are installed before running the code. An error message will be displayed if any issues occur during data retrieval or processing.