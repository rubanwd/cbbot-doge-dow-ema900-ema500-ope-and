# data_fetcher

from pybit.unified_trading import HTTP
import json
import time

class DataFetcher:
    def __init__(self, api_key, api_secret, testnet=True):
        # Инициализация сессии
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )

    def get_historical_data(self, symbol, interval, limit):
        try:
            response = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            return response['result']['list']
        except Exception as e:
            print(f"Ошибка при получении исторических данных: {e}")
            return None
        
    def get_real_time_price(self, symbol):
        try:
            response = self.session.get_tickers(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            return float(response['result']['list'][0]['lastPrice'])
        except Exception as e:
            print(f"Ошибка при получении текущей цены: {e}")
            return None
        
    def get_current_leverage(self, symbol):
        try:
            response = self.session.get_positions(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            positions = response['result']['list']
            if positions:
                return float(positions[0]['leverage'])  # Assuming we only care about the first position
            else:
                return None
        except Exception as e:
            print(f"Ошибка при получении текущего плеча: {e}")
            return None
        
    def set_leverage(self, symbol, leverage):
        try:
            current_leverage = self.get_current_leverage(symbol)
            if current_leverage is not None and current_leverage == leverage:
                print(f"Leverage is already set to {leverage}x for {symbol}. No modification needed.")
                return

            response = self.session.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            print(f"Leverage set to {leverage}x for {symbol}.")
        except Exception as e:
            print(f"Ошибка при установке плеча: {e}")



    def place_order(self, symbol, side, qty, current_price, leverage, stop_loss=None, take_profit=None):
        try:
            # Set leverage before placing an order
            self.set_leverage(symbol, leverage)

            position_idx = 1 if side.lower() == 'buy' else 2

            # Adjust price based on the side of the order
            if side.lower() == 'buy':
                price = current_price * 0.9997  # 0.1% below the current market price
                if stop_loss and stop_loss >= price:
                    print("Stop-loss is higher than or equal to the limit price for a Buy order. Adjusting stop-loss...")
                    stop_loss = price * 0.995  # Ensure stop-loss is slightly below the limit price
            else:
                price = current_price * 1.0003  # 0.1% above the current market price
                if stop_loss and stop_loss <= price:
                    print("Stop-loss is lower than or equal to the limit price for a Sell order. Adjusting stop-loss...")
                    stop_loss = price * 1.005  # Ensure stop-loss is slightly above the limit price

            order_params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": "Limit",  # Set order type to "Limit"
                "qty": qty,
                "price": str(price),  # Use the adjusted price
                "positionIdx": position_idx,
            }

            if stop_loss:
                order_params["stopLoss"] = str(stop_loss)
            if take_profit:
                order_params["takeProfit"] = str(take_profit)

            # Attempt to place the order
            response = self.session.place_order(**order_params)
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            return response['result']
        except Exception as e:
            print(f"Ошибка при размещении ордера: {e}")
            return None


    def get_open_positions(self, symbol):
        try:
            response = self.session.get_positions(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            positions = response['result']['list']

            # Filter out positions where size is 0
            active_positions = [pos for pos in positions if float(pos['size']) > 0]

            # Use json.dumps to print the active positions in a structured format
            if active_positions:
                print("Active Open Positions:")
                print(json.dumps(active_positions, indent=4))
            else:
                print("No opened positions.")

            return active_positions
        except Exception as e:
            print(f"Ошибка при получении позиций: {e}")
            return None

    import time

    def get_open_orders(self, symbol):
        try:
            response = self.session.get_open_orders(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            open_orders = response['result']['list']

            current_time = time.time()
            orders_to_cancel = []

            for order in open_orders:
                created_time = int(order['createdTime']) / 1000  # Convert from milliseconds to seconds
                if current_time - created_time > 180:  # 180 seconds = 3 minutes
                    orders_to_cancel.append(order)

            if orders_to_cancel:
                for order in orders_to_cancel:
                    self.cancel_order(order['orderId'], symbol)
                    print(f"Order {order['orderId']} cancelled as it was older than 3 minutes.")
            else:
                print("No orders older than 3 minutes.")

            return open_orders
        except Exception as e:
            print(f"Ошибка при получении лимитных ордеров: {e}")
            return None


    def cancel_order(self, order_id, symbol):
        try:
            response = self.session.cancel_order(
                category="linear",
                symbol=symbol,  # Ensure the symbol is included in the request
                orderId=order_id
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")
            print(f"Order {order_id} successfully cancelled.")
        except Exception as e:
            print(f"Ошибка при отмене ордера {order_id}: {e}")
        
    def get_last_closed_position(self, symbol):
        try:
            response = self.session.get_positions(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] != 0:
                raise Exception(f"API Error: {response['retMsg']}")

            positions = response['result']['list']

            # Filter for closed positions by checking if 'size' is 0 and the position has been closed
            closed_positions = [pos for pos in positions if float(pos['size']) == 0]

            if closed_positions:
                # print("Closed Positions:")
                # print(json.dumps(closed_positions, indent=4))
                # Sort closed positions by 'updatedTime' to get the most recent one
                last_closed_position = max(closed_positions, key=lambda x: int(x['updatedTime']))
                return last_closed_position
            else:
                print("No closed positions found.")
                return None
        except Exception as e:
            print(f"Error fetching last closed position: {e}")
            return None

