import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame

class NewsMomentumChaser(IStrategy):
    """Highly responsive strategy chasing momentum triggered by major news."""

    # Fastest timeframe for rapid response
    timeframe = '1m'
    whitelist = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']

    # Tight stoploss and quick profit-taking
    stoploss = -0.03  # 3% stop loss
    trailing_stop = True
    trailing_stop_positive = 0.005   # 0.5% profit trigger for trailing stop
    trailing_stop_positive_offset = 0.01  # start trailing at 1% profit
    trailing_only_offset_is_reached = True

    # Ultra-aggressive ROI for scalping
    minimal_roi = {
        "0": 0.015,   # 1.5% profit target immediately
        "2": 0.01,
        "5": 0.005,
        "10": 0
    }

    # Loosened thresholds for frequent entries
    rsi_buy_threshold = IntParameter(45, 55, default=50, space='buy')
    rsi_sell_threshold = IntParameter(55, 65, default=60, space='sell')
    ema_fast = IntParameter(3, 7, default=5, space='buy')
    ema_slow = IntParameter(10, 15, default=12, space='buy')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMA indicators
        dataframe['ema_fast'] = dataframe['close'].ewm(span=self.ema_fast.value, adjust=False).mean()
        dataframe['ema_slow'] = dataframe['close'].ewm(span=self.ema_slow.value, adjust=False).mean()
        # RSI
        dataframe['rsi'] = self.RSI(dataframe, period=10)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # EMA crossover bullish
        conditions.append(dataframe['ema_fast'] > dataframe['ema_slow'])
        # RSI trending upward or below threshold
        conditions.append(dataframe['rsi'] < self.rsi_buy_threshold.value)
        if conditions:
            dataframe.loc[np.all(np.array([cond.values for cond in conditions]), axis=0), 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # EMA crossover bearish or RSI overbought
        conditions.append((dataframe['ema_fast'] < dataframe['ema_slow']) | (dataframe['rsi'] > self.rsi_sell_threshold.value))
        if conditions:
            dataframe.loc[np.all(np.array([cond.values for cond in conditions]), axis=0), 'exit_long'] = 1
        return dataframe