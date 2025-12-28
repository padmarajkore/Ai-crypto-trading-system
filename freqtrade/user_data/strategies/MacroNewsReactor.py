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
    informative,  # @informative decorator
    # Hyperopt Parameters
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,

    IntParameter,
    RealParameter,
    # timeframe helpers
    timeframe_to_minutes,
    timeframe_to_next_date,
    timeframe_to_prev_date,
    # Strategy helper functions
    merge_informative_pair,
    stoploss_from_absolute,
    stoploss_from_open,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
from technical import qtpylib


# This class is a sample. Feel free to customize it.
class MacroNewsReactor(IStrategy):
    """
    Macro News Reactor Strategy - Designed for reacting to high-impact macroeconomic news events.
    Utilizes adaptive indicators and widened stoploss for volatility resilience.
    """

    # Strategy interface version - allow new iterations of the strategy interface.
    INTERFACE_VERSION = 3

    can_short: bool = False

    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "0": 0.012,   # 1.2% profit target
        "2": 0.006,   # 0.6% after 2 mins
    }

    # Optimal stoploss designed for the strategy.
    stoploss = -0.025  # Wider stoploss for macro volatility

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.003
    trailing_stop_positive_offset = 0.006
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = "5m"

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    rsi_buy = IntParameter(25, 40, default=35, space='buy', optimize=True)
    rsi_sell = IntParameter(60, 75, default=70, space='sell', optimize=True)
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }

    # Optional order time in force.
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    plot_config = {
        "main_plot": {
            "ema5": {"color": "orange"},
            "ema20": {"color": "purple"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"},
            }
        }
    }

    def informative_pairs(self):
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # EMAs
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema20'] = ta.EMA(dataframe, timeperiod=20)
        
        # Volatility (ATR)
        dataframe['atr'] = ta.ATR(dataframe, timeperiod=14)
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] < self.rsi_buy.value) &
                (qtpylib.crossed_above(dataframe['ema5'], dataframe['ema20'])) &
                (dataframe['atr'] > dataframe['atr'].shift(1))  # Rising volatility
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe['rsi'] > self.rsi_sell.value) |
                (qtpylib.crossed_below(dataframe['ema5'], dataframe['ema20']))
            ),
            "exit_long",
        ] = 1

        return dataframe