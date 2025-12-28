# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
import talib.abstract as ta
from technical import qtpylib

class BearishMarketScalp(IStrategy):
    """
    BearishMarketScalp - Optimized for high-quality entries in uncertain/bearish markets.
    Targets 3-5% daily profit by reducing noise and increasing win rate.
    Uses 5m timeframe to filter out 1m volatility.
    """
    INTERFACE_VERSION = 3
    can_short: bool = False

    # ROI table: 1% profit in 10 mins, or 2% in 30 mins
    minimal_roi = {
        "0": 0.02,
        "10": 0.015,
        "30": 0.01,
        "60": 0.005
    }

    # Tight stoploss to protect capital
    stoploss = -0.02

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.005
    trailing_stop_positive_offset = 0.01
    trailing_only_offset_is_reached = True

    timeframe = '5m'
    process_only_new_candles = True
    startup_candle_count: int = 30

    # Hyperopt parameters
    buy_rsi = IntParameter(30, 50, default=45, space='buy')
    sell_rsi = IntParameter(60, 80, default=70, space='sell')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Trend Filter (EMA 50)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        
        # Volume
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=20).mean()
        
        # Bollinger Bands for volatility
        bollinger = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2.0, nbdevdn=2.0)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        In a bearish/uncertain market, we only enter if:
        1. Price is above EMA 50 (local uptrend)
        2. RSI is recovering from mid-range (momentum)
        3. Volume is above average (confirmation)
        4. Price just touched or is near the lower Bollinger Band (oversold bounce)
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > self.buy_rsi.value) &
                (dataframe['rsi'] < 60) &
                (dataframe['close'] > dataframe['ema50']) &
                (dataframe['volume'] > dataframe['volume_mean'] * 1.2) &
                (dataframe['close'] < dataframe['bb_middleband']) # Entering on the bottom half of BB
            ),
            'enter_long'] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit when:
        1. RSI reaches overbought
        2. Price crosses below EMA 20
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > self.sell_rsi.value) |
                (qtpylib.crossed_below(dataframe['close'], dataframe['ema20']))
            ),
            'exit_long'] = 1

        return dataframe
