#!/usr/bin/env python3
"""
Phase 1 (Revised): Multi-Source Forex Data Aggregator for EUR/JPY Strategy
==========================================================================

This implementation uses free data-only providers for development and testing,
eliminating geographic restrictions while maintaining full functionality for
strategy development.

Data Sources (in priority order):
1. yfinance (primary) - Yahoo Finance EUR/JPY data
2. Alpha Vantage (backup) - Professional forex API with free tier
3. Twelve Data (tertiary) - Comprehensive financial data API

Features:
- Multi-source failover for reliability
- Real-time and historical EUR/JPY data
- Multi-timeframe aggregation (15M, 30M, 1H, 2H, 4H, Daily, Weekly)
- Data validation and quality checks
- SQLite persistence and crash recovery
- Rate limit handling for free APIs
- Paper trading simulation preparation

Requirements:
pip install yfinance alpha-vantage pandas numpy python-dotenv requests

Setup:
1. Get free API key from Alpha Vantage: https://www.alphavantage.co/support/#api-key
2. Optional: Get Twelve Data API key: https://twelvedata.com/
3. Create .env file with API keys
4. Run: python data_fetch.py
"""

import os
import sys
import time
import pickle
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any
import traceback

import pandas as pd
import numpy as np
import yfinance as yf
import requests
from alpha_vantage.foreignexchange import ForeignExchange
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_fetch.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MultiSourceForexAggregator:
    """
    Multi-source forex data aggregator with failover capabilities.

    Uses multiple free data providers to ensure reliable EUR/JPY data access
    for strategy development and testing.
    """

    def __init__(self):
        """Initialize aggregator with multiple data sources."""
        load_dotenv()

        # API credentials (optional for some sources)
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')

        # Initialize Alpha Vantage client if key available
        self.av_client = None
        if self.alpha_vantage_key:
            self.av_client = ForeignExchange(
                key=self.alpha_vantage_key, output_format="pandas")

        # Data storage
        self.candles_1m = pd.DataFrame()
        self.timeframes = {}

        # Configuration
        self.SYMBOL_YAHOO = 'EURJPY=X'  # Yahoo Finance symbol
        self.SYMBOL_ALPHA = ('EUR', 'JPY')  # Alpha Vantage format
        self.SYMBOL_TWELVE = 'EUR/JPY'  # Twelve Data format

        self.TIMEFRAMES = {
            '15M': '15min',
            '30M': '30min',
            '1H': '1h',
            '2H': '2h',
            '4H': '4h',
            'D': '1D',
            'W': '1W'
        }

        self.BUFFER_SIZES = {
            '1M': 500,
            '15M': 100,
            '30M': 100,
            '1H': 100,
            '2H': 100,
            '4H': 100,
            'D': 100,
            'W': 100
        }

        # Rate limiting
        self.last_api_call = {}
        self.API_DELAYS = {
            'yfinance': 1,      # 1 second between calls
            'alpha_vantage': 12,  # 5 calls per minute = 12 second delay
            'twelve_data': 8     # 8 calls per minute = 7.5 second delay
        }

        # State files
        self.STATE_FILE = 'forex_aggregator_state.pkl'
        self.DB_FILE = 'eurjpy_data.db'

        # Current data source tracking
        self.current_source = None
        self.source_failures = {'yfinance': 0,
                                'alpha_vantage': 0, 'twelve_data': 0}

        self._init_database()
        logger.info("Multi-source forex aggregator initialized")

    def _init_database(self) -> None:
        """Initialize SQLite database for data storage."""
        try:
            conn = sqlite3.connect(self.DB_FILE)
            cursor = conn.cursor()

            # Create tables for each timeframe
            for tf in ['1M'] + list(self.TIMEFRAMES.keys()):
                table_name = f"EURJPY_{tf}"
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        timestamp TEXT PRIMARY KEY,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume INTEGER DEFAULT 0,
                        source TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)

            # Create metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Database initialized")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def _wait_for_rate_limit(self, source: str) -> None:
        """Enforce rate limits for API calls."""
        if source not in self.last_api_call:
            self.last_api_call[source] = 0

        time_since_last = time.time() - self.last_api_call[source]
        required_delay = self.API_DELAYS.get(source, 1)

        if time_since_last < required_delay:
            sleep_time = required_delay - time_since_last
            logger.debug(
                f"Rate limiting {source}: sleeping {sleep_time:.1f} seconds")
            time.sleep(sleep_time)

        self.last_api_call[source] = time.time()

    def fetch_yfinance_data(self, period: str = "7d", interval: str = "1m") -> pd.DataFrame:
        """
        Fetch data from Yahoo Finance using yfinance.

        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        """
        try:
            self._wait_for_rate_limit('yfinance')
            logger.info(f"Fetching Yahoo Finance data: {period}, {interval}")

            # Download data
            data = yf.download(
                tickers=self.SYMBOL_YAHOO,
                period=period,
                interval=interval,
                progress=False,
                rounding=False,  # Keep full precision
                auto_adjust=False  # Use raw prices
            )

            if data.empty:
                logger.warning("No data returned from Yahoo Finance")
                return pd.DataFrame()

            # Clean column names (remove ticker prefix if present)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] for col in data.columns]

            # Standardize column names
            data.columns = [col.lower().replace(' ', '_')
                            for col in data.columns]
            if 'adj_close' in data.columns:
                data = data.drop('adj_close', axis=1)

            # Add volume column if missing (forex doesn't have volume)
            if 'volume' not in data.columns:
                data['volume'] = 0

            # Remove timezone info for consistency
            if data.index.tz is not None:
                data.index = data.index.tz_convert(None)

            logger.info(f"Yahoo Finance: {len(data)} candles retrieved")
            return data

        except Exception as e:
            logger.error(f"Yahoo Finance fetch failed: {e}")
            self.source_failures['yfinance'] += 1
            return pd.DataFrame()

    def fetch_alpha_vantage_data(self, interval: str = "1min", outputsize: str = "compact") -> pd.DataFrame:
        """
        Fetch data from Alpha Vantage API.

        Args:
            interval: 1min, 5min, 15min, 30min, 60min
            outputsize: compact (last 100 data points) or full
        """
        if not self.av_client:
            logger.warning("Alpha Vantage API key not configured")
            return pd.DataFrame()

        try:
            self._wait_for_rate_limit('alpha_vantage')
            logger.info(
                f"Fetching Alpha Vantage data: {interval}, {outputsize}")

            data, meta_data = self.av_client.get_currency_exchange_intraday(
                from_symbol=self.SYMBOL_ALPHA[0],
                to_symbol=self.SYMBOL_ALPHA[1],
                interval=interval,
                outputsize=outputsize
            )

            if data.empty:
                logger.warning("No data returned from Alpha Vantage")
                return pd.DataFrame()

            # Rename columns to match our standard
            column_mapping = {
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close'
            }

            data = data.rename(columns=column_mapping)
            data['volume'] = 0  # Forex doesn't have volume

            # Sort by index (datetime)
            data = data.sort_index()

            logger.info(f"Alpha Vantage: {len(data)} candles retrieved")
            return data

        except Exception as e:
            logger.error(f"Alpha Vantage fetch failed: {e}")
            self.source_failures['alpha_vantage'] += 1
            return pd.DataFrame()

    def fetch_twelve_data(self, interval: str = "1min", outputsize: int = 100) -> pd.DataFrame:
        """
        Fetch data from Twelve Data API.

        Args:
            interval: 1min, 5min, 15min, 30min, 1h, 4h, 1day
            outputsize: Number of data points to retrieve
        """
        if not self.twelve_data_key:
            logger.warning("Twelve Data API key not configured")
            return pd.DataFrame()

        try:
            self._wait_for_rate_limit('twelve_data')
            logger.info(
                f"Fetching Twelve Data: {interval}, {outputsize} points")

            url = "https://api.twelvedata.com/time_series"
            params = {
                'symbol': self.SYMBOL_TWELVE,
                'interval': interval,
                'outputsize': outputsize,
                'apikey': self.twelve_data_key
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            json_data = response.json()

            if 'values' not in json_data:
                logger.warning(
                    f"No values in Twelve Data response: {json_data}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(json_data['values'])

            # Convert datetime and set as index
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)

            # Convert price columns to float
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype(float)

            df['volume'] = 0  # Forex doesn't have volume
            df = df.sort_index()

            logger.info(f"Twelve Data: {len(df)} candles retrieved")
            return df

        except Exception as e:
            logger.error(f"Twelve Data fetch failed: {e}")
            self.source_failures['twelve_data'] += 1
            return pd.DataFrame()

    def fetch_latest_data(self) -> bool:
        """
        Fetch latest data using available sources with failover.

        Returns:
            bool: True if new data was obtained
        """
        sources = ['yfinance', 'alpha_vantage', 'twelve_data']

        for source in sources:
            # Skip sources that have failed too many times
            if self.source_failures[source] >= 3:
                continue

            try:
                if source == 'yfinance':
                    # Get last 2 days of 1-minute data
                    new_data = self.fetch_yfinance_data(
                        period="2d", interval="1m")

                elif source == 'alpha_vantage':
                    # Get intraday 1-minute data
                    new_data = self.fetch_alpha_vantage_data(
                        interval="1min", outputsize="compact")

                elif source == 'twelve_data':
                    # Get 1-minute data
                    new_data = self.fetch_twelve_data(
                        interval="1min", outputsize=100)

                else:
                    continue

                if new_data.empty:
                    logger.warning(f"No data from {source}")
                    continue

                # Check if we got new data
                new_count = self._merge_new_data(new_data, source)

                if new_count > 0:
                    logger.info(
                        f"Successfully fetched {new_count} new candles from {source}")
                    self.current_source = source
                    self.source_failures[source] = 0  # Reset failure counter

                    # Update all timeframes
                    self._update_all_timeframes()
                    self._save_state()
                    self._save_to_database()

                    return True

            except Exception as e:
                logger.error(f"Error fetching from {source}: {e}")
                self.source_failures[source] += 1

        logger.warning("All data sources failed or returned no new data")
        return False

    def _merge_new_data(self, new_data: pd.DataFrame, source: str) -> int:
        """
        Merge new data with existing data, avoiding duplicates.

        Returns:
            int: Number of new candles added
        """
        if new_data.empty:
            return 0

        if self.candles_1m.empty:
            self.candles_1m = new_data.copy()
            self.candles_1m = self.candles_1m.tail(self.BUFFER_SIZES['1M'])
            return len(self.candles_1m)

        # Find new candles (after last timestamp)
        last_timestamp = self.candles_1m.index[-1]
        new_candles = new_data[new_data.index > last_timestamp]

        if new_candles.empty:
            return 0

        # Append new candles
        self.candles_1m = pd.concat([self.candles_1m, new_candles])

        # Remove duplicates (keep last occurrence)
        self.candles_1m = self.candles_1m[~self.candles_1m.index.duplicated(
            keep='last')]

        # Maintain buffer size
        self.candles_1m = self.candles_1m.tail(self.BUFFER_SIZES['1M'])

        # Sort by index
        self.candles_1m = self.candles_1m.sort_index()

        return len(new_candles)

    def _aggregate_timeframe(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """Aggregate 1-minute data to specified timeframe."""
        if df.empty:
            return pd.DataFrame()

        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }

        if freq == '1W':
            df_resampled = df.resample('W-MON', label='left').agg(ohlc_dict)
        else:
            df_resampled = df.resample(freq, label='left').agg(ohlc_dict)

        # Remove incomplete candles and NaN values
        if not df_resampled.empty:
            df_resampled = df_resampled[:-1].dropna()

        return df_resampled

    def _update_all_timeframes(self) -> None:
        """Update all timeframe aggregations from 1-minute data."""
        if self.candles_1m.empty:
            return

        for tf_name, freq in self.TIMEFRAMES.items():
            try:
                aggregated = self._aggregate_timeframe(self.candles_1m, freq)

                if not aggregated.empty:
                    aggregated = aggregated.tail(
                        self.BUFFER_SIZES.get(tf_name, 100))

                self.timeframes[tf_name] = aggregated

            except Exception as e:
                logger.error(f"Failed to aggregate {tf_name}: {e}")

    def get_timeframe_data(self, timeframe: str) -> pd.DataFrame:
        """Get data for specified timeframe."""
        if timeframe == '1M':
            return self.candles_1m.copy()
        return self.timeframes.get(timeframe, pd.DataFrame()).copy()

    def _save_state(self) -> None:
        """Save current state for crash recovery."""
        try:
            state = {
                'candles_1m': self.candles_1m,
                'timeframes': self.timeframes,
                'current_source': self.current_source,
                'source_failures': self.source_failures,
                'timestamp': datetime.now()
            }

            with open(self.STATE_FILE, 'wb') as f:
                pickle.dump(state, f)

        except Exception as e:
            logger.error(f"State save failed: {e}")

    def load_state(self) -> bool:
        """Load state from file."""
        try:
            if not os.path.exists(self.STATE_FILE):
                return False

            with open(self.STATE_FILE, 'rb') as f:
                state = pickle.load(f)

            self.candles_1m = state.get('candles_1m', pd.DataFrame())
            self.timeframes = state.get('timeframes', {})
            self.current_source = state.get('current_source')
            self.source_failures = state.get(
                'source_failures', {'yfinance': 0, 'alpha_vantage': 0, 'twelve_data': 0})

            logger.info(f"State restored from {state.get('timestamp')}")

            if not self.candles_1m.empty:
                logger.info(
                    f"Restored {len(self.candles_1m)} 1-minute candles")

            return True

        except Exception as e:
            logger.error(f"State load failed: {e}")
            return False

    def _save_to_database(self) -> None:
        """Save data to SQLite database."""
        try:
            conn = sqlite3.connect(self.DB_FILE)

            # Save 1-minute data
            if not self.candles_1m.empty:
                df_save = self.candles_1m.reset_index()
                # Get the first column (datetime) regardless of its name
                datetime_col = df_save.columns[0]
                df_save = df_save.rename(columns={datetime_col: 'timestamp'})
                df_save['timestamp'] = pd.to_datetime(
                    df_save['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                df_save['source'] = self.current_source or 'unknown'
                df_save.to_sql('EURJPY_1M', conn,
                               if_exists='replace', index=False)

            # Save aggregated timeframes
            for tf_name, df in self.timeframes.items():
                if not df.empty:
                    df_save = df.reset_index()
                    # Get the first column (datetime) regardless of its name
                    datetime_col = df_save.columns[0]
                    df_save = df_save.rename(
                        columns={datetime_col: 'timestamp'})
                    df_save['timestamp'] = pd.to_datetime(
                        df_save['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    df_save['source'] = 'aggregated'
                    df_save.to_sql(
                        f'EURJPY_{tf_name}', conn, if_exists='replace', index=False)

            conn.close()

        except Exception as e:
            logger.error(f"Database save failed: {e}")
            logger.error(traceback.format_exc())  # Add this for full traceback

    def fetch_historical_bootstrap(self, days: int = 7) -> bool:
        """
        Bootstrap with historical data for initial setup.

        Args:
            days: Number of days of historical data to fetch
        """
        logger.info(f"Bootstrapping with {days} days of historical data")

        # Try yfinance first (best for historical data)
        try:
            period_map = {1: "1d", 2: "2d", 5: "5d",
                          7: "7d", 30: "1mo", 90: "3mo", 365: "1y"}
            period = period_map.get(days, f"{days}d")

            data = self.fetch_yfinance_data(period=period, interval="1m")

            if not data.empty:
                self.candles_1m = data.copy()
                self.candles_1m = self.candles_1m.tail(self.BUFFER_SIZES['1M'])
                self.current_source = 'yfinance'

                self._update_all_timeframes()
                self._save_state()
                self._save_to_database()

                logger.info(
                    f"Bootstrap successful: {len(self.candles_1m)} candles loaded")
                return True

        except Exception as e:
            logger.error(f"Bootstrap failed: {e}")

        return False

    def print_status(self) -> None:
        """Print current data status."""
        print(f"\n=== EUR/JPY Multi-Source Data Status ===")
        print(f"Timestamp: {datetime.now()}")
        print(f"Current Source: {self.current_source or 'None'}")
        print(f"Source Failures: {self.source_failures}")

        if not self.candles_1m.empty:
            latest_1m = self.candles_1m.iloc[-1]
            print(f"\n1M: {len(self.candles_1m)} candles")
            print(f"    Latest: {self.candles_1m.index[-1]} | O:{latest_1m['open']:.5f} "
                  f"H:{latest_1m['high']:.5f} L:{latest_1m['low']:.5f} C:{latest_1m['close']:.5f}")

        for tf_name in self.TIMEFRAMES.keys():
            df = self.timeframes.get(tf_name, pd.DataFrame())
            if not df.empty:
                latest = df.iloc[-1]
                print(f"{tf_name:>3}: {len(df)} candles")
                print(f"    Latest: {df.index[-1]} | O:{latest['open']:.5f} "
                      f"H:{latest['high']:.5f} L:{latest['low']:.5f} C:{latest['close']:.5f}")

        print("=" * 50)

    def validate_data(self) -> bool:
        """Validate data integrity."""
        if self.candles_1m.empty:
            logger.warning("No data to validate")
            return False

        try:
            # Check OHLC relationships
            invalid = (
                (self.candles_1m['high'] < self.candles_1m['low']) |
                (self.candles_1m['high'] < self.candles_1m['open']) |
                (self.candles_1m['high'] < self.candles_1m['close']) |
                (self.candles_1m['low'] > self.candles_1m['open']) |
                (self.candles_1m['low'] > self.candles_1m['close'])
            )

            if invalid.any():
                logger.error(
                    f"Found {invalid.sum()} invalid OHLC relationships")
                return False

            logger.info("Data validation passed")
            return True

        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            return False


def main():
    """Main execution function."""
    # Create .env reminder if it doesn't exist
    if not os.path.exists('.env'):
        logger.warning("No .env file found. Creating template...")
        with open('.env', 'w') as f:
            f.write(
                "# Alpha Vantage API Key (free from https://www.alphavantage.co/support/#api-key)\n")
            f.write("ALPHA_VANTAGE_API_KEY=your_api_key_here\n\n")
            f.write(
                "# Twelve Data API Key (optional, from https://twelvedata.com/)\n")
            f.write("TWELVE_DATA_API_KEY=your_api_key_here\n")
        logger.info("Please edit .env file with your API keys and restart")

    # Initialize aggregator
    aggregator = MultiSourceForexAggregator()

    # Load previous state or bootstrap
    if not aggregator.load_state():
        logger.info("No saved state found. Bootstrapping...")
        if not aggregator.fetch_historical_bootstrap(days=7):
            logger.error("Bootstrap failed. Will try to get live data...")

    # Validate data
    aggregator.validate_data()

    # Print initial status
    aggregator.print_status()

    # Main update loop
    logger.info("Starting real-time update loop...")
    update_interval = 60  # seconds
    consecutive_failures = 0
    max_failures = 5

    try:
        while True:
            try:
                if aggregator.fetch_latest_data():
                    aggregator.print_status()
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    logger.warning(
                        f"No new data ({consecutive_failures}/{max_failures})")

                if consecutive_failures >= max_failures:
                    logger.error(
                        "Too many consecutive failures. Attempting bootstrap...")
                    if aggregator.fetch_historical_bootstrap(days=1):
                        consecutive_failures = 0
                    else:
                        logger.error(
                            "Bootstrap also failed. Continuing anyway...")

                time.sleep(update_interval)

            except KeyboardInterrupt:
                logger.info("Shutdown requested")
                break

            except Exception as e:
                logger.error(f"Update loop error: {e}")
                logger.error(traceback.format_exc())
                time.sleep(update_interval * 2)

    finally:
        logger.info("Saving final state...")
        aggregator._save_state()
        aggregator._save_to_database()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
