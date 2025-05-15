# Simplified Crypto Trading Bot (Binance Futures Testnet)

This project is a simplified trading bot built in Python, designed to connect to the Binance Futures Testnet and execute basic trading operations via a web-based user interface.

## Features

* Connects securely to the Binance Futures Testnet using API keys (managed via environment variables).
* Supports placing the following order types:
    * Market Orders (BUY/SELL)
    * Limit Orders (BUY/SELL)
    * **True Stop-Limit Orders** (BUY/SELL) - _Implemented as per advanced task requirement._
* Provides a basic web-based user interface (GUI) using Flask.
* Allows viewing of account balance on the Testnet.
* Enables checking the status of placed orders.
* Allows cancellation of open orders.
* Logs all bot actions and API interactions to a file (`trading_bot.log`) and the console.

## Technologies Used

* Python
* Flask (for the web UI)
* python-binance library (for interacting with the Binance API)
* Git (for version control)

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone [Your GitHub Repository HTTPS URL Here]
    cd SimplifiedTradingBot # Or whatever your project folder is named
    ```
2.  **Set up a Python Virtual Environment (Recommended):**
    ```bash
    # Create venv
    python -m venv venv
    # Activate venv (on Windows Command Prompt)
    venv\Scripts\activate
    # Activate venv (on Git Bash/MinGW or Linux/macOS)
    source venv/bin/activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    # If you don't have a requirements.txt, install manually:
    # pip install python-binance Flask python-dotenv # python-dotenv if you use a .env file
    ```
    *(Note: You might want to create a `requirements.txt` file by running `pip freeze > requirements.txt` after installing libraries)*.
4.  **Binance Futures Testnet Account and API Keys:**
    * Ensure you have a Binance Futures Testnet account (`https://testnet.binancefuture.com/`).
    * Obtain API keys from the Testnet account's API Management section.
    * **Crucially:** Set your API Key and Secret Key as environment variables in your terminal **before** running the application for security. Also set a `FLASK_SECRET_KEY`.
        * On Linux/macOS:
            ```bash
            export BINANCE_TEST_API_KEY="YOUR_KEY"
            export BINANCE_TEST_API_SECRET="YOUR_SECRET"
            export FLASK_SECRET_KEY="your_random_flask_key"
            ```
        * On Windows (Command Prompt):
            ```cmd
            set BINANCE_TEST_API_KEY="YOUR_KEY"
            set BINANCE_TEST_API_SECRET="YOUR_SECRET"
            set FLASK_SECRET_KEY="your_random_flask_key"
            ```
        * On Windows (PowerShell):
            ```powershell
            $env:BINANCE_TEST_API_KEY="YOUR_KEY"
            $env:BINANCE_TEST_API_SECRET="YOUR_SECRET"
            $env:FLASK_SECRET_KEY="your_random_flask_key"
            ```
    * **(Alternative - Less Secure for Production):** You could use a `.env` file and the `python-dotenv` library for local development, but ensure `.env` is in your `.gitignore`.

5.  **Fund Your Testnet Account:** Get test USDT from the Testnet Faucet (`https://testnet.binancefuture.com/`).

## How to Run the Flask Web UI

1.  Make sure you have followed the [Setup and Installation](#setup-and-installation) steps.
2.  Navigate to your project directory in the terminal.
3.  Ensure your environment variables (API keys and Flask Secret Key) are set in your current terminal session.
4.  Run the Flask application:
    ```bash
    python app.py
    ```
5.  Open your web browser and go to the address shown in your terminal (usually `http://127.0.0.1:5000/`).

## Project Structure