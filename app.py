# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from trading_bot import BasicBot # Import your BasicBot class

app = Flask(__name__)
# Configure a secret key for Flask sessions (needed for flashing messages)
# It's best practice to set this environment variable securely
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_if_env_not_set')

# Initialize the bot instance (outside of routes, so it's persistent)
# It's best practice to get API keys from environment variables in production
api_key = os.environ.get('BINANCE_TEST_API_KEY')
api_secret = os.environ.get('BINANCE_TEST_API_SECRET')

# Basic check for API keys at startup
if not api_key or not api_secret:
    print("WARNING: BINANCE_TEST_API_KEY or BINANCE_TEST_API_SECRET not found in environment variables.")
    print("Please set them for secure operation.")
    # In a real app, you might render a configuration page or handle this more gracefully
    # For this example, we'll proceed but bot operations will likely fail without keys
    bot = None # Initialize bot as None if keys are missing
    print("Bot initialization skipped due to missing API keys.")
else:
    try:
        bot = BasicBot(api_key=api_key, api_secret=api_secret, testnet=True)
        print("Bot initialized successfully.")
    except Exception as e:
        print(f"Error initializing bot: {e}")
        bot = None # Set bot to None if initialization fails
        print("Bot initialization failed.")


@app.route('/')
def index():
    """Renders the main dashboard page and displays flashed messages."""
    account_balance = None
    if bot: # Only attempt API calls if bot was initialized successfully
        try:
            # Fetch balance to display on the dashboard
            balance_info = bot.client.futures_account_balance()
            # Filter for assets with positive balance
            account_balance = [asset for asset in balance_info if float(asset.get('balance', 0)) > 0]
        except Exception as e:
            print(f"Error fetching balance: {e}")
            flash(f"Error fetching account balance: {e}", 'error') # Flash error message

    # get_flashed_messages() retrieves and clears the messages from the session
    messages = get_flashed_messages(with_categories=True)

    return render_template('index.html', account_balance=account_balance, messages=messages)

@app.route('/place_order', methods=['POST'])
def place_order():
    """Handles order placement requests from the form."""
    if not bot:
        flash("Bot not initialized. API keys may be missing or invalid.", 'error')
        return redirect(url_for('index'))

    order_type = request.form.get('order_type')
    symbol = request.form.get('symbol').upper()
    side = request.form.get('side').upper()
    quantity_str = request.form.get('quantity')

    try:
        quantity = float(quantity_str)
        if quantity <= 0:
             flash("Quantity must be greater than zero.", 'error')
             return redirect(url_for('index'))

        order_details = None
        message = None
        category = 'success' # Default category for success messages

        if order_type == 'market':
            order_details = bot.place_market_order(symbol, side, quantity)
            if order_details:
                message = f"Market {side} order placed successfully. Order ID: {order_details.get('orderId')}"
            else:
                 message = "Failed to place market order (check terminal logs for API error)."
                 category = 'error'

        elif order_type == 'limit':
            price_str = request.form.get('price')
            try:
                price = float(price_str)
                if price <= 0:
                    flash("Limit price must be greater than zero.", 'error')
                    return redirect(url_for('index'))

                # Add notional value check
                notional_value = quantity * price
                if notional_value < 100: # Assuming minimum notional is 100 USDT
                    flash(f"Order notional value ({notional_value:.2f} USDT) is too small. Must be at least 100 USDT.", 'error')
                    return redirect(url_for('index'))

                order_details = bot.place_limit_order(symbol, side, quantity, price)
                if order_details:
                    message = f"Limit {side} order placed successfully for {quantity} {symbol} at {price}. Order ID: {order_details.get('orderId')}"
                else:
                    message = "Failed to place limit order (check terminal logs for API error)."
                    category = 'error'
            except ValueError:
                flash("Invalid number input for limit price.", 'error')
                return redirect(url_for('index'))


        elif order_type == 'stop_limit':
            stop_price_str = request.form.get('stop_price')
            limit_price_str = request.form.get('limit_price') # Get limit price for stop-limit
            try:
                stop_price = float(stop_price_str)
                limit_price = float(limit_price_str)

                if stop_price <= 0 or limit_price <= 0:
                    flash("Stop price and Limit price must be greater than zero.", 'error')
                    return redirect(url_for('index'))

                 # Add notional value check for stop-limit (using limit price)
                notional_value = quantity * limit_price
                if notional_value < 100: # Assuming minimum notional is 100 USDT
                    flash(f"Order notional value ({notional_value:.2f} USDT) is too small. Must be at least 100 USDT.", 'error')
                    return redirect(url_for('index'))

                order_details = bot.place_stop_limit_order(symbol, side, quantity, limit_price, stop_price) # Pass both prices
                if order_details:
                    message = f"Stop-Limit {side} order placed successfully for {quantity} {symbol} with stop price {stop_price} and limit price {limit_price}. Order ID: {order_details.get('orderId')}"
                else:
                    message = "Failed to place stop-limit order (check terminal logs for API error)."
                    category = 'error'
            except ValueError:
                flash("Invalid number input for stop price or limit price.", 'error')
                return redirect(url_for('index'))

        else:
            message = "Invalid order type selected."
            category = 'error'

        if message:
            flash(message, category)

    except ValueError:
        flash("Invalid number input for quantity.", 'error')
    except Exception as e:
        flash(f"An unexpected error occurred while placing the order: {e}", 'error')
        print(f"Error placing order: {e}") # Still log to terminal for detailed debugging


    return redirect(url_for('index')) # Always redirect after POST


@app.route('/check_status', methods=['POST'])
def check_status():
    """Handles checking order status."""
    if not bot:
        flash("Bot not initialized. API keys may be missing or invalid.", 'error')
        return redirect(url_for('index'))

    symbol = request.form.get('status_symbol').upper()
    order_id = request.form.get('order_id')

    if not symbol or not order_id:
        flash("Symbol and Order ID are required to check status.", 'error')
        return redirect(url_for('index'))

    try:
        status_result = bot.get_order_status(symbol, order_id)
        if status_result:
            # Format the status for display
            status_message = f"Status for Order ID {order_id} ({symbol}): {status_result.get('status')}"
            # You could include more details from status_result here
            flash(status_message, 'success')
        else:
            flash(f"Order ID {order_id} ({symbol}) not found or error fetching status (check terminal logs).", 'error')

    except Exception as e:
        flash(f"An error occurred while fetching status for Order ID {order_id}: {e}", 'error')
        print(f"Error fetching status: {e}") # Still log to terminal


    return redirect(url_for('index')) # Redirect back after POST

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    """Handles canceling an order."""
    if not bot:
        flash("Bot not initialized. API keys may be missing or invalid.", 'error')
        return redirect(url_for('index'))

    symbol = request.form.get('cancel_symbol').upper()
    order_id = request.form.get('cancel_order_id')

    if not symbol or not order_id:
        flash("Symbol and Order ID are required to cancel order.", 'error')
        return redirect(url_for('index'))

    try:
        cancel_response = bot.cancel_order(symbol, order_id)
        if cancel_response:
            # Binance API cancel response might vary, check documentation for details
            # A simple success message based on the response structure
            flash(f"Order ID {order_id} ({symbol}) cancelled successfully.", 'success')
        else:
             flash(f"Order ID {order_id} ({symbol}) not found or error cancelling (check terminal logs).", 'error')

    except Exception as e:
        flash(f"An error occurred while cancelling Order ID {order_id}: {e}", 'error')
        print(f"Error cancelling order: {e}") # Still log to terminal


    return redirect(url_for('index')) # Redirect back after POST


if __name__ == '__main__':
    # Use a development server for testing
    # In production, use a production-ready WSGI server like Gunicorn or uWSGI
    # debug=True allows for automatic code reloading and detailed error pages
    app.run(debug=True)

