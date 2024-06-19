import yfinance as yf
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime
from typing import Optional, List
import pytz


def get_yfinance_data(ticker_symbol: str, start: Optional[str] = "1990-01-01", end: Optional[str] = "2022-12-31",
                      timeframe: Optional[str] = '1d', drop_other_column=True) -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.

    Parameters: ticker_symbol (str): The ticker symbol of the stock.
    start (Optional[str]): The start date for the
    historical data in 'YYYY-MM-DD' format.
    Defaults to '1990-01-01'.
    end (Optional[str]): The end date for the
    historical data in 'YYYY-MM-DD' format.
    Defaults to '2022-12-31'.
    interval (Optional[str]): The interval for the
    historical data.
    Valid intervals are '1d', '1wk', '1mo', etc. Defaults to '1d'.

    Returns:
        pd.DataFrame: A DataFrame containing the historical stock data.
    """
    # Create a ticker object
    ticker = yf.Ticker(ticker_symbol)

    # Download historical data
    rates = ticker.history(start=start, end=end, interval=timeframe)
    if drop_other_column:
        drop_all_except(rates, 'Close')

    df = rates.rename(columns={'Close': 'Price'})

    return df


def get_csv_data(file_path: str, delim: Optional[str] = "\t", dailyBars: Optional[bool] = True, drop_other_column=True) \
        -> pd.DataFrame:
    """
      Reads data from a CSV file and processes it according to the specified settings.

      Parameters:
          file_path (str): The path to the CSV file.
          delim (Optional[str]): The delimiter used in the CSV file.
          Default to tab ('\t').
          dailyBars (Optional[bool]): If True, processes data as daily bars.
          If False, processes data as intraday bars.

      Returns:
          pd.DataFrame: A DataFrame containing the processed data.
      """
    df = pd.read_csv(file_path, delimiter=delim)

    if dailyBars:
        df.columns = ['Date', 'Open', 'High', 'Low', 'Price', 'TickVol', 'Vol', 'Spread']
        df['Datetime'] = pd.to_datetime(df['Date'])
    else:
        df.columns = ['Date', 'Time', 'Open', 'High', 'Low', 'Price', 'TickVol', 'Vol', 'Spread']
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])

    df.set_index('Datetime', inplace=True)

    if drop_other_column:
        df = drop_all_except(df, 'Price')

    return df


def get_mt5_data(authorized: [bool], symbol: str, timeframe: str,
                 start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                 start_pos: Optional[int] = None, end_pos: Optional[int] = None,
                 drop_other_column=True) -> Optional[pd.DataFrame]:
    """
    Fetches historical data from MetaTrader 5 for a given symbol within a specified date range and timeframe.

    Parameters:
        authorized (bool): authorized to access MT5 data.
        symbol (str): The symbols of the ticker to fetch data for.
        timeframe (str): The timeframe code (e.g., 'M1', 'H1', 'D1').
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        start_pos
        end_pos
        drop_other_column

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing the historical data with Datetime index.
                                Returns None if data fetching fails.
    """
    if not authorized:
        print("Not authorized to access MT5 data.")
        return

    # Get the timeframe
    timeframes = {
        "M1": mt5.TIMEFRAME_M1,
        "M2": mt5.TIMEFRAME_M2,
        "M3": mt5.TIMEFRAME_M3,
        "M4": mt5.TIMEFRAME_M4,
        "M5": mt5.TIMEFRAME_M5,
        "M6": mt5.TIMEFRAME_M6,
        "M10": mt5.TIMEFRAME_M10,
        "M12": mt5.TIMEFRAME_M12,
        "M15": mt5.TIMEFRAME_M15,
        "M20": mt5.TIMEFRAME_M20,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H2": mt5.TIMEFRAME_H2,
        "H3": mt5.TIMEFRAME_H3,
        "H4": mt5.TIMEFRAME_H4,
        "H6": mt5.TIMEFRAME_H6,
        "H8": mt5.TIMEFRAME_H8,
        "H12": mt5.TIMEFRAME_H12,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1,
    }

    bar_time = timeframes.get(timeframe)
    if bar_time is None:
        print(f"Invalid timeframe: {timeframe}")
        return None

    df = None

    rates = None
    if start_date is not None and end_date is not None:
        # Set time zone to UTC
        timezone = pytz.timezone("Etc/UTC")

        # Convert start and end dates to datetime objects in UTC
        #start_date = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone)
        #end_date = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone)

        # Fetch data from MetaTrader 5 between start and end dates
        rates = mt5.copy_rates_range(symbol, bar_time, start_date, end_date)

    if start_pos is not None and end_pos is not None:
        # Fetch data from MetaTrader 5 from start and end dates
        rates = mt5.copy_rates_from_pos(symbol, bar_time, start_pos, end_pos)

    if rates is None:
        print(f"Failed to fetch data for {symbol}")
        return None

        # Create DataFrame out of the obtained data
    df = pd.DataFrame(rates)
    df['Datetime'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('Datetime', inplace=True)
    if drop_other_column:
        drop_all_except(df, 'close')
    df = df.rename(columns={'close': 'Price'})

    return df


def drop_all_except(df: pd.DataFrame, keep_column: str) -> pd.DataFrame:
    """
    Drops all columns from the DataFrame except the specified column.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        keep_column (str): The name of the column to keep.

    Returns:
        pd.DataFrame: The DataFrame with only the specified column kept.
    """
    columns_to_drop = [col for col in df.columns if col != keep_column]
    df.drop(columns=columns_to_drop, inplace=True)

    # Backward Fill then Fill forward remaining NaNs
    df = df.ffill().bfill()

    # df.dropna(inplace=True)

    return df
