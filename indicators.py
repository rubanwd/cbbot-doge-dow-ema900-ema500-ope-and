class Indicators:
    @staticmethod
    def calculate_ema(df, span):
        return df['close'].ewm(span=span, adjust=False).mean()
    
    @staticmethod
    def calculate_sma(df, window):
        """
        Calculates the Simple Moving Average (SMA).
        """
        return df['close'].rolling(window=window).mean()

    @staticmethod
    def calculate_rsi(df, period=14):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(df):
        short_ema = df['close'].ewm(span=12, adjust=False).mean()
        long_ema = df['close'].ewm(span=26, adjust=False).mean()
        macd = short_ema - long_ema
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        return macd, macd_signal

    @staticmethod
    def calculate_trend_direction(df, long_ema_period=200):
        # Using long-term EMA to determine trend direction
        long_ema = df['close'].ewm(span=long_ema_period, adjust=False).mean()
        return 'uptrend' if df['close'].iloc[-1] > long_ema.iloc[-1] else 'downtrend'

    @staticmethod
    def calculate_bollinger_bands(df, window=20):
        middle_band = df['close'].rolling(window=window).mean()
        std_dev = df['close'].rolling(window=window).std()
        upper_band = middle_band + (std_dev * 2)
        lower_band = middle_band - (std_dev * 2)
        return upper_band, middle_band, lower_band
