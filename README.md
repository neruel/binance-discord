# Binance Discord Market Bot

A Discord bot that provides real-time market data from Binance for cryptocurrencies and stocks via an interactive terminal interface.

## Features

- `/market` command to open the Market Terminal
- Interactive buttons and select menus for market selection
- Real-time price data from Binance REST API (with plans for WebSocket integration)
- Support for major cryptocurrencies and stocks
- Clean Embed displays with price, change, and timestamp
- Back navigation buttons

## Project Structure

```
binance-discord/
├── bot/                 # Core bot code
├── config/              # Configuration files
├── services/            # Service classes (Binance API, etc.)
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
���└── README.md            # This file
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd binance-discord
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your Discord Bot Token, Binance API Key, and Binance API Secret
   - **Never commit your `.env` file**

5. **Create a Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Enable the Privileged Gateway Intents (if needed)
   - Copy the bot token to `.env`

6. **Get Binance API Keys**
   - Sign up at [Binance](https://www.binance.com/)
   - Create API keys in the API Management section
   - Add them to `.env`

7. **Run the bot**
   ```bash
   python -m bot.main  # or however your entry point is structured
   ```

## Usage

In Discord, use the slash command:

```
/market
```

Then select either "Crypto" or "Stocks" to choose an asset, and view its current price.

## Current Supported Assets

*Verified via live Binance API data:*
- **Cryptocurrencies**: BTC, ETH, BNB, SOL, XRP, DOGE
- **Stocks (Tokenized)**: Tesla (TSLA), Apple (AAPL), Microsoft (MSFT), NVIDIA (NVDA), SK Hynix (SKHY)

*Note: Samsung Electronics (005930) is not currently available as a USDT pair on Binance Spot.*

## Known Limitations

- Currently uses REST polling; real-time WebSocket updates planned for future version
- Stock symbols depend on Binance Spot offering for tokenized equities
- Error handling is basic; improve for production use

## License

MIT