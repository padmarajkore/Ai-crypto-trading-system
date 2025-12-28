import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter, CategoricalParameter
from pandas import DataFrame

class AggressiveScalp(IStrategy):
    """Aggressive short-term scalping strategy for major USDT pairs.
    Entry: EMA9 crosses above EMA21 AND RSI(14) below 40 (oversold).
    Exit: EMA9 crosses below EMA21 OR ROI reached.
    """

    # Minimal timeframe for fast signals
    timeframe = '5m'
    # Limit to whitelisted pairs only
    whitelist = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT']

    # Parameters (can be tuned later)
    stoploss = -0.05  # 5% stop loss
    trailing_stop = True
    trailing_stop_positive = 0.01   # 1% profit trigger for trailing stop
    trailing_stop_positive_offset = 0.02  # start trailing at 2% profit
    trailing_only_offset_is_reached = True

    # ROI table – minimal targets for scalping
    minimal_roi = {
        "0": 0.02,   # 2% profit quickly
        "10": 0.015,
        "30": 0.01,
        "60": 0.005
    }

    # Hyperparameters for future optimization (optional)
    rsi_buy_threshold = IntParameter(30, 50, default=40, space='buy')
    rsi_sell_threshold = IntParameter(60, 80, default=70, space='sell')
    ema_fast = IntParameter(5, 12, default=9, space='buy')
    ema_slow = IntParameter(18, 30, default=21, space='buy')

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # EMA indicators
        dataframe['ema_fast'] = dataframe['close'].ewm(span=self.ema_fast.value, adjust=False).mean()
        dataframe['ema_slow'] = dataframe['close'].ewm(span=self.ema_slow.value, adjust=False).mean()
        # RSI
        dataframe['rsi'] = self.RSI(dataframe, period=14)
        # ATR for volatility filter (optional)
        dataframe['atr'] = self.ATR(dataframe, period=14)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # EMA crossover bullish
        conditions.append(dataframe['ema_fast'] > dataframe['ema_slow'])
        # Ensure previous candle EMA fast was below slow (crossover)
        conditions.append(dataframe['ema_fast'].shift(1) <= dataframe['ema_slow'].shift(1))
        # RSI below threshold (oversold)
        conditions.append(dataframe['rsi'] < self.rsi_buy_threshold.value)
        # Volatility filter – avoid extremely high ATR (top 5% of recent period)
        recent_atr = dataframe['atr'].rolling(window=20).mean()
        conditions.append(dataframe['atr'] < recent_atr * 1.5)
        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        # EMA crossover bearish
        conditions.append(dataframe['ema_fast'] < dataframe['ema_slow'])
        # Ensure previous candle EMA fast was above slow (crossover)
        conditions.append(dataframe['ema_fast'].shift(1) >= dataframe['ema_slow'].shift(1))
        # RSI above sell threshold (overbought)
        conditions.append(dataframe['rsi'] > self.rsi_sell_threshold.value)
        if conditions:
            dataframe.loc[reduce(lambda x, y: x & y, conditions), 'exit_long'] = 1
        return dataframe
