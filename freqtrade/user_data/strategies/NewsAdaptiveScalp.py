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
class NewsAdaptiveScalp(IStrategy):
    """
    News Adaptive Scalp Strategy - Reacts to major market-moving events (like BTC hashrate drops)
    by increasing sensitivity to momentum and volatility. Uses 1-minute timeframe.
    """

    # Strategy interface version - allow new iterations of the strategy interface.
    INTERFACE_VERSION = 3

    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "0": 0.012,   # 1.2% immediately
        "1": 0.006,  # 0.6% after 1 minute
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.02  # Slightly wider stoploss to accommodate volatility

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.003  # Enable trailing stop earlier at 0.3%
    trailing_stop_positive_offset = 0.005  # Lock in profit at 0.5%
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = "1m"  # Ultra-short timeframe for scalping

    # Run "populate_indicators()"" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Hyperoptable parameters
    rsi_buy = IntParameter(25, 50, default=35, space='buy', optimize=True)
    rsi_sell = IntParameter(50, 75, default=65, space='sell', optimize=True)
    
    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 20

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
            "ema10": {"color": "blue"},
        },
        "subplots": {
            "RSI": {
                "rsi": {"color": "red"},
            }
        }
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # RSI for momentum
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=9)
        
        # EMAs for trend filtering
        dataframe['ema5'] = ta.EMA(dataframe, timeperiod=5)
        dataframe['ema10'] = ta.EMA(dataframe, timeperiod=10)
        
        # Price change percentage for volatility measurement
        dataframe['price_change'] = (dataframe['close'] - dataframe['open']) / dataframe['open']
        
        # Volume indicators
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=5).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        
        # Aggressive long entry conditions adapted for news impact
        dataframe.loc[
            (
                # RSI crosses above 35 (reactive threshold for news-driven volatility)
                (qtpylib.crossed_above(dataframe['rsi'], self.rsi_buy.value)) &
                # EMA crossover - faster EMA crosses above slower EMA
                (qtpylib.crossed_above(dataframe['ema5'], dataframe['ema10'])) &
                # Volatility filter - significant price change post-news
                (abs(dataframe['price_change']) > 0.001) # Increased sensitivity
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """
        
        # Quick exit for long positions
        dataframe.loc[
            (
                # RSI crosses below 65 (take profit)
                (qtpylib.crossed_below(dataframe['rsi'], self.rsi_sell.value)) |
                # EMA crossover in opposite direction
                (qtpylib.crossed_below(dataframe['ema5'], dataframe['ema10'])) |
                # Fixed time exit based on ROI
                (dataframe['close'] < dataframe['open'])  # Simple red candle exit
            ),
            "exit_long",
        ] = 1

        return dataframe