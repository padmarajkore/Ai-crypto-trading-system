# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these imports ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Optional, Union

from freqtrade.strategy import (
    IStrategy,
    Trade,
    Order,
    PairLocks,
    informative,
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    RealParameter,
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)

import talib.abstract as ta
from technical import qtpylib


class TrendVolatilityScalp(IStrategy):
    """
    Trend + Volatility Scalping Strategy
    Logic:
    1. Filter by 200 EMA to determine overall market direction.
    2. Use ADX to ensure a strong trend is present (ADX > 25).
    3. Use EMA 20 for entry timing (crossovers).
    4. Use Bollinger Bands to ensure we are not buying at the absolute top of a move.
    5. RSI for momentum confirmation.
    """

    INTERFACE_VERSION = 3

    can_short: bool = True

    # ROI table: Tight for scalping but allowing some room to breathe
    minimal_roi = {
        "0": 0.05,      # 5% at 0 min
        "30": 0.02,     # 2% after 30 min
        "60": 0.01,     # 1% after 1 hour
        "120": 0.005    # 0.5% after 2 hours
    }

    # Stoploss: 3% to avoid getting stopped out by noise, but protected
    stoploss = -0.03

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.008
    trailing_stop_positive_offset = 0.015
    trailing_only_offset_is_reached = True

    timeframe = "5m"

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    startup_candle_count: int = 200

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Trend Indicators
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        dataframe['ema200'] = ta.EMA(dataframe, timeperiod=200)
        
        # Momentum
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Volatility & Trend Strength
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        
        # Bollinger Bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        dataframe['bb_percent'] = (
            (dataframe['close'] - dataframe['bb_lowerband']) / 
            (dataframe['bb_upperband'] - dataframe['bb_lowerband'])
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # LONG Entry
        dataframe.loc[
            (
                # Strong trend confirmation
                (dataframe['adx'] > 25) &
                # Overall Bullish trend
                (dataframe['close'] > dataframe['ema200']) &
                # Price crossing above EMA 20 (Mean reversion/Trend continuation)
                (qtpylib.crossed_above(dataframe['close'], dataframe['ema20'])) &
                # RSI not overbought
                (dataframe['rsi'] < 65) &
                # Avoid buying if price is already touching the upper BB
                (dataframe['bb_percent'] < 0.8)
            ),
            "enter_long",
        ] = 1

        # SHORT Entry
        dataframe.loc[
            (
                # Strong trend confirmation
                (dataframe['adx'] > 25) &
                # Overall Bearish trend
                (dataframe['close'] < dataframe['ema200']) &
                # Price crossing below EMA 20
                (qtpylib.crossed_below(dataframe['close'], dataframe['ema20'])) &
                # RSI not oversold
                (dataframe['rsi'] > 35) &
                # Avoid selling if price is already touching the lower BB
                (dataframe['bb_percent'] > 0.2)
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Exit Long
        dataframe.loc[
            (
                # Exit when momentum fades
                (dataframe['rsi'] > 75) |
                # Price crosses below EMA 50 (Trend reversal)
                (qtpylib.crossed_below(dataframe['close'], dataframe['ema50'])) |
                # Price hits upper BB band (Overextended)
                (dataframe['close'] > dataframe['bb_upperband'])
            ),
            "exit_long",
        ] = 1

        # Exit Short
        dataframe.loc[
            (
                # Exit when momentum fades
                (dataframe['rsi'] < 25) |
                # Price crosses above EMA 50 (Trend reversal)
                (qtpylib.crossed_above(dataframe['close'], dataframe['ema50'])) |
                # Price hits lower BB band (Overextended)
                (dataframe['close'] < dataframe['bb_lowerband'])
            ),
            "exit_short",
        ] = 1

        return dataframe
