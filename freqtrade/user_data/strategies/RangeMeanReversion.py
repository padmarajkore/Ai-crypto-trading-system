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


class RangeMeanReversion(IStrategy):
    """
    Range Mean Reversion Scalping Strategy
    Designed for consolidating markets like the current BTC/ETH environment.
    
    Logic:
    1. Only trade when ADX < 25 (indicates consolidation/lack of trend).
    2. Entry Long: Price hits Lower Bollinger Band and RSI < 35.
    3. Entry Short: Price hits Upper Bollinger Band and RSI > 65.
    4. Exit: Middle Bollinger Band or 1.5% profit.
    """

    INTERFACE_VERSION = 3

    can_short: bool = True

    # ROI table: Scalping targets
    minimal_roi = {
        "0": 0.02,      # 2% at 0 min
        "15": 0.01,     # 1% after 15 min
        "45": 0.005,    # 0.5% after 45 min
        "0": 0.03       # Absolute cap
    }

    # Stoploss: 1.5% - Tight for range trading to avoid breakout losses
    stoploss = -0.015

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.005
    trailing_stop_positive_offset = 0.01
    trailing_only_offset_is_reached = True

    timeframe = "5m"

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    startup_candle_count: int = 100

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Volatility / Range Indicators
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2.5)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']
        
        # Momentum
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Trend Strength - used to AVOID trends
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14)
        
        # Stochastics for better range timing
        stoch = ta.STOCH(dataframe)
        dataframe['slowk'] = stoch['slowk']
        dataframe['slowd'] = stoch['slowd']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # LONG Entry
        dataframe.loc[
            (
                # Low ADX = Market is sideways/consolidating
                (dataframe['adx'] < 25) &
                # Price is at or below the lower Bollinger Band
                (dataframe['close'] <= dataframe['bb_lowerband']) &
                # RSI is oversold
                (dataframe['rsi'] < 35) &
                # Stochastic K crossing D upwards in oversold zone
                (qtpylib.crossed_above(dataframe['slowk'], dataframe['slowd'])) &
                (dataframe['slowk'] < 30)
            ),
            "enter_long",
        ] = 1

        # SHORT Entry
        dataframe.loc[
            (
                # Low ADX = Market is sideways/consolidating
                (dataframe['adx'] < 25) &
                # Price is at or above the upper Bollinger Band
                (dataframe['close'] >= dataframe['bb_upperband']) &
                # RSI is overbought
                (dataframe['rsi'] > 65) &
                # Stochastic K crossing D downwards in overbought zone
                (qtpylib.crossed_below(dataframe['slowk'], dataframe['slowd'])) &
                (dataframe['slowk'] > 70)
            ),
            "enter_short",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Exit Long
        dataframe.loc[
            (
                # Exit at the middle band (mean reversion target)
                (dataframe['close'] >= dataframe['bb_middleband']) |
                # Or if RSI becomes overbought
                (dataframe['rsi'] > 70)
            ),
            "exit_long",
        ] = 1

        # Exit Short
        dataframe.loc[
            (
                # Exit at the middle band (mean reversion target)
                (dataframe['close'] <= dataframe['bb_middleband']) |
                # Or if RSI becomes oversold
                (dataframe['rsi'] < 30)
            ),
            "exit_short",
        ] = 1

        return dataframe
