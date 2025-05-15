import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import os # For API keys from environment variables (recommended)
import time

#--- Configuration

# IMPORTANT: It's best practice to use environment variables for API keys
# You can set them in your system or create a .env file (and use python-dotenv library)
# For this simple guide, we'll show direct input first, then environment variables.

#Testnet URL
TESTNET_BASE_URL = 'https://testnet.binancefuture.com'

#--- Logging Setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("trading_bot.log"), # Log to a file
                        logging.StreamHandler() # Log to console
                    ])

logger = logging.getLogger(__name__)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.api_key = api_key
        self.api_secret = api_secret

        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.FUTURES_URL = TESTNET_BASE_URL # Crucial for testnet futures

            # Test connectivity
            self.client.futures_ping()
            logger.info("Binance Futures Testnet connection successful.")
            account_info = self.client.futures_account_balance()
            logger.info(f"Account Balance: {account_info}")

        except BinanceAPIException as e:
            logger.error(f"Binance API Exception on connection: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during initialization: {e}")
            raise

    def _log_request(self, method_name, params):
        logger.info(f"Request: {method_name} with params: {params}")

    def _log_response(self, response):
        logger.info(f"Response: {response}")

    def _log_error(self, error_message):
        logger.error(f'Error: {error_message}')

    def place_market_order(self, symbol, side, quantity):
        """
        Places a market order.
        :param symbol: Trading symbol (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param quantity: Amount of the asset to buy/sell
        :return: Order response or None if error
        """
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity
        }
        self._log_request('futures_create_order (MARKET)', params)
        try:
            order = self.client.futures_create_order(**params)
            self._log_response(order)
            logger.info(f"Market {side} order for {quantity} {symbol} placed successfully. Order ID: {order.get('orderId')}")
            return order
        except BinanceAPIException as e:
            self._log_error(f"Binance API Exception placing market order: {e}")
            return None
        except BinanceOrderException as e:
            self._log_error(f"Binance Order Exception placing market order: {e}")
            return None
        except Exception as e:
            self._log_error(f"Unexpected error placing market order: {e}")
            return None

    def place_limit_order(self, symbol, side, quantity, price):
        """
        Places a limit order.
        :param symbol: Trading symbol (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param quantity: Amount of the asset to buy/sell
        :param price: Price at which to place the order
        :return: Order response or None if error
        """
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': 'LIMIT',
            'quantity': quantity,
            'price': price,
            'timeInForce': 'GTC' # Good Till Cancelled
        }
        self._log_request('futures_create_order (LIMIT)', params)
        try:
            order = self.client.futures_create_order(**params)
            self._log_response(order)
            logger.info(f"Limit {side} order for {quantity} {symbol} at {price} placed successfully. Order ID: {order.get('orderId')}")
            return order
        except BinanceAPIException as e:
            self._log_error(f"Binance API Exception placing limit order: {e}")
            return None
        except BinanceOrderException as e:
            self._log_error(f"Binance Order Exception placing limit order: {e}")
            return None
        except Exception as e:
            self._log_error(f"Unexpected error placing limit order: {e}")
            return None

    def place_stop_limit_order(self, symbol, side, quantity, price, stop_price):
        """
        Places a stop-limit order.
        :param symbol: Trading symbol (e.g., 'BTCUSDT')
        :param side: 'BUY' or 'SELL'
        :param quantity: Amount of the asset to buy/sell
        :param price: The price at which the limit order will be placed once the stopPrice is
                      triggered.
        :param stop_price: The price at which the order becomes active.
        :return: Order response or None if error
        """
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            # Changed type from 'STOP_MARKET' to 'STOP' for a true Stop-Limit order
            'type': 'STOP',
            'quantity': quantity,
            'price': price, # This is the limit price for the order once triggered
            'stopPrice': stop_price, # The price that triggers the order
            'timeInForce': 'GTC' # Or other if needed, GTC is common for stop orders
        }

        self._log_request('futures_create_order (STOP_LIMIT)', params) # Updated log message

        try:
            order = self.client.futures_create_order(**params)
            self._log_response(order)
            # Updated log message to reflect Stop-Limit order
            logger.info(f"Stop-Limit {side} order for {quantity} {symbol} at limit {price} with stop price {stop_price} placed. Order ID: {order.get('orderId')}")
            return order
        except BinanceAPIException as e:
            self._log_error(f"Binance API Exception placing stop-limit order: {e}")
            return None
        except BinanceOrderException as e:
            self._log_error(f"Binance Order Exception placing stop-limit order: {e}")
            return None
        except Exception as e:
            self._log_error(f"Unexpected error placing stop-limit order: {e}")
            return None


    def get_order_status(self, symbol, order_id):
        """
        Retrieves the status of a specific order.
        :param symbol: Trading symbol (e.g., 'BTCUSDT')
        :param order_id: The order ID
        :return: Order status or None if error
        """
        params = {'symbol': symbol.upper(), 'orderId': order_id}
        self._log_request('futures_get_order', params)
        try:
            order_status = self.client.futures_get_order(**params)
            self._log_response(order_status)
            logger.info(f"Status for order ID {order_id} ({symbol}): {order_status.get('status')}")
            return order_status
        except BinanceAPIException as e:
            self._log_error(f"Binance API Exception fetching order status: {e}")
            return None
        except Exception as e:
            self._log_error(f"Unexpected error fetching order status: {e}")
            return None

    def cancel_order(self, symbol, order_id):
        """
        Cancels an open order.
        :param symbol: Trading symbol (e.g., 'BTCUSDT')
        :param order_id: The order ID to cancel
        :return: Cancellation response or None if error
        """
        params = {'symbol': symbol.upper(), 'orderId': order_id}
        self._log_request('futures_cancel_order', params)
        try:
            response = self.client.futures_cancel_order(**params)
            self._log_response(response)
            logger.info(f"Order ID {order_id} ({symbol}) cancelled successfully.")
            return response
        except BinanceAPIException as e:
            self._log_error(f"Binance API Exception cancelling order: {e}")
            return None
        except Exception as e:
            self._log_error(f"Unexpected error cancelling order: {e}")
            return None

def get_user_input(prompt, type_converter=str, validation_func=None, error_message="Invalid input."):
    """Generic function to get and validate user input."""
    while True:
        try:
            value = type_converter(input(prompt).strip())
            if validation_func:
                if validation_func(value):
                    return value
                else:
                    logger.warning(error_message)
            else:
                return value
        except ValueError:
            logger.warning(f"Invalid input type. Please enter a valid {type_converter.__name__}.")
        except Exception as e:
            logger.warning(f"An error occurred with input: {e}")

#--- CLI Enhancement ---

def display_menu():
    print("\n--- Binance Futures Trading Bot ---")
    print("1. Place Market Order")
    print("2. Place Limit Order")
    print("3. Place Stop-Limit Order") # Updated menu option
    print("4. Check Order Status")
    print("5. Cancel Order")
    print("6. View Account Balance (Testnet)")
    print("0. Exit")
    print("---------------------------------")

def main_cli(bot):
    while True:
        display_menu()
        choice = get_user_input("Enter your choice: ", int, lambda x: 0 <= x <= 6)

        if choice == 1: # Market Order
            symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str.upper)
            side = get_user_input("Enter side (BUY/SELL): ", str.upper, lambda x: x in ['BUY', 'SELL'])
            quantity = get_user_input("Enter quantity: ", float, lambda x: x > 0)
            order_details = bot.place_market_order(symbol, side, quantity)
            if order_details:
                print(f"Market order placed: {order_details}")

        elif choice == 2: # Limit Order
            symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str.upper)
            side = get_user_input("Enter side (BUY/SELL): ", str.upper, lambda x: x in ['BUY', 'SELL'])
            quantity = get_user_input("Enter quantity: ", float, lambda x: x > 0)
            price = get_user_input("Enter limit price: ", float, lambda x: x > 0)
            order_details = bot.place_limit_order(symbol, side, quantity, price)
            if order_details:
                print(f"Limit order placed: {order_details}")

        elif choice == 3: # Stop-Limit Order
            symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str.upper)
            side = get_user_input("Enter side (BUY/SELL): ", str.upper, lambda x: x in ['BUY', 'SELL'])
            quantity = get_user_input("Enter quantity: ", float, lambda x: x > 0)
            stop_price = get_user_input("Enter stop price (trigger price): ", float, lambda x: x > 0) # Clarified prompt
            limit_price = get_user_input("Enter limit price (for when stop is triggered): ", float, lambda x: x > 0) # Added prompt for limit price

            # Call place_stop_limit_order with both limit_price and stop_price
            order_details = bot.place_stop_limit_order(symbol, side, quantity, limit_price, stop_price)

            if order_details:
                print(f"Stop-Limit order placed: {order_details}") # Updated print message

        elif choice == 4: # Check Order Status
            symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str.upper)
            order_id = get_user_input("Enter Order ID: ", str)
            status = bot.get_order_status(symbol, order_id)
            if status:
                print(f"Order Status: {status}")

        elif choice == 5: # Cancel Order
            symbol = get_user_input("Enter symbol (e.g., BTCUSDT): ", str.upper)
            order_id = get_user_input("Enter Order ID to cancel: ", str)
            response = bot.cancel_order(symbol, order_id)
            if response:
                print(f"Order cancellation response: {response}")

        elif choice == 6: # View Account Balance
            try:
                balance = bot.client.futures_account_balance()
                print("\n--- Testnet Account Balance ---")
                for asset in balance:
                    if float(asset['balance']) > 0: # Show only assets with balance
                        print(f"Asset: {asset['asset']}, Balance: {asset['balance']}, Available: {asset['availableBalance']}")
                print("-----------------------------")
            except Exception as e:
                logger.error(f"Could not fetch account balance: {e}")
                print("Error: Could not fetch account balance.")

        elif choice == 0: # Exit
            logger.info("Exiting bot.")
            break

        else:
            print("Invalid choice. Please try again.")

        input("Press Enter to continue...") # Pause for user to read output

if __name__ == "__main__":
    logger.info("Starting Trading Bot Application...")

    #--- Method 1: Get API Keys from Environment Variables (Recommended & Secure) ---
    # Set these environment variables in your system before running the script:
    # export BINANCE_TEST_API_KEY="your_testnet_api_key"
    # export BINANCE_TEST_API_SECRET="your_testnet_api_secret"
    # On Windows:
    # set BINANCE_TEST_API_KEY="your_testnet_api_key"
    # set BINANCE_TEST_API_SECRET="your_testnet_api_secret"

    api_key = os.environ.get('56cc474c3c74204fbdac7625299f3393153c719b559cc5c0afe4ea2ffd4bc9c4')
    api_secret = os.environ.get('ed50634319d32a2aa24727a6f294db926b2772bde6f02fa60ae3f5e5b6d4979c')

    #--- Method 2: Input API Keys directly (Less Secure - for quick testing only)
    if not api_key or not api_secret:
        print("API keys not found in environment variables.")
        print("Please enter your Binance Futures Testnet API credentials.")
        api_key = get_user_input("Enter your Testnet API Key: ").strip()
        api_secret = get_user_input("Enter your Testnet Secret Key: ").strip()

    if not api_key or not api_secret:
        logger.error("API Key and Secret Key are required to run the bot. Exiting.")
        print("API Key and Secret Key are required. Exiting.")
    else:
        try:
            bot_instance = BasicBot(api_key=api_key, api_secret=api_secret, testnet=True)
            main_cli(bot_instance)
        except Exception as e:
            logger.critical(f"Failed to initialize or run the bot: {e}")
            print(f"Critical error: Failed to initialize or run the bot. Check logs. Error: {e}")
