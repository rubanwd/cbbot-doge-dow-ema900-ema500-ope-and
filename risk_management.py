# risk_management.py

import pandas as pd
import os
from helpers import Helpers  # Ensure this import is present
from indicators import Indicators

class RiskManagement:
    def __init__(self, atr_period=14, atr_multiplier=1.5, risk_ratio=1.5):
        self.atr_period = atr_period
        self.atr_multiplier = atr_multiplier
        self.risk_ratio = risk_ratio
        self.stop_loss_percentage = float(os.getenv("STOP_LOSS_PERCENTAGE", 5.0))
        self.indicators = Indicators()

    def calculate_atr(self, df):
        high = df['high'].astype(float)
        low = df['low'].astype(float)
        close = df['close'].astype(float)
        df['previous_close'] = close.shift(1)
        df['tr'] = pd.concat([
            high - low,
            (high - df['previous_close']).abs(),
            (low - df['previous_close']).abs()
        ], axis=1).max(axis=1)
        atr = df['tr'].rolling(window=self.atr_period).mean().iloc[-1]
        return atr

    def calculate_risk_management(self, df, trend):
        atr = self.calculate_atr(df)
        stop_loss_distance = self.stop_loss_percentage / 100 * df['close'].iloc[-1]
        take_profit_distance = atr * self.atr_multiplier

        if trend == 'long':
            stop_loss = df['close'].iloc[-1] - stop_loss_distance
            take_profit = df['close'].iloc[-1] + take_profit_distance
        elif trend == 'short':
            stop_loss = df['close'].iloc[-1] + stop_loss_distance
            take_profit = df['close'].iloc[-1] - take_profit_distance
        else:
            raise ValueError("Trend must be either 'long' or 'short'")

        return stop_loss, take_profit
