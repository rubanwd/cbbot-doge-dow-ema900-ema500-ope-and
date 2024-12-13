#  helpers.py

import time

class Helpers:
    @staticmethod
    def calculate_and_print_indicators(df, indicators):
        # Calculate indicators
        df['EMA_9'] = indicators.calculate_ema(df, 9)
        df['RSI'] = indicators.calculate_rsi(df, 14)
        df['Bollinger_upper'], df['Bollinger_middle'], df['Bollinger_lower'] = indicators.calculate_bollinger_bands(df)

        # Get the latest indicator values
        rsi = df['RSI'].iloc[-1]
        bollinger_upper = df['Bollinger_upper'].iloc[-1]
        bollinger_middle = df['Bollinger_middle'].iloc[-1]
        bollinger_lower = df['Bollinger_lower'].iloc[-1]
        current_price = df['close'].iloc[-1]

        # Return the calculated indicators and price
        return rsi, bollinger_upper, bollinger_middle, bollinger_lower, current_price

    # @staticmethod
    # def check_last_closed_position(data_fetcher, symbol):
    #     last_closed_position = data_fetcher.get_last_closed_position(symbol)
    #     if last_closed_position:
    #         last_closed_time = int(last_closed_position['updatedTime']) / 1000
    #         current_time = time.time()
    #         time_since_last_close = current_time - last_closed_time
    #         print(f"Time since last closed position: {int(time_since_last_close)} seconds")
    #         if time_since_last_close < 120:
    #             print("The last closed position was less than 3 minutes ago. A new order will not be placed.")
    #             return False
    #     return True
