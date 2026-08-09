import discord
from discord import app_commands
from discord.ui import View, Button, Select
import logging
from services.binance import BinanceAPI
import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

# Define market categories
MARKET_CRYPTO = "crypto"
MARKET_STOCK = "stock"

# Known crypto symbols (USDT pairs)
KNOWN_CRYPTO = [
    ("BTCUSDT", "Bitcoin", "BTC"),
    ("ETHUSDT", "Ethereum", "ETH"),
    ("BNBUSDT", "BNB", "BNB"),
    ("SOLUSDT", "Solana", "SOL"),
    ("XRPUSDT", "XRP", "XRP"),
    ("DOGEUSDT", "Dogecoin", "DOGE"),
]
# Known stock tokens (as of verification via Binance API)
# Format: (symbol, name, display ticker)
KNOWN_STOCKS = [
    ("TSLABUSDT", "Tesla", "TSLA"),
    ("AAPLBUSDT", "Apple", "AAPL"),
    ("MSFTBUSDT", "Microsoft", "MSFT"),
    ("NVDABUSDT", "NVIDIA", "NVDA"),
    ("SKHYBUSDT", "SK Hynix", "SKHY"),
    # Note: Samsung Electronics (005930) not found as USDT pair on Binance Spot
]

class MarketView(View):
    def __init__(self):
        super().__init__(timeout=180)  # 3 minutes timeout

    @discord.ui.button(label="���🪙 Crypto", style=discord.ButtonStyle.primary, custom_id="market_crypto")
    async def crypto_button(self, interaction: discord.Interaction, button: Button):
        await show_market_selector(interaction, MARKET_CRYPTO)

    @discord.ui.button(label="���📈 Stocks", style=discord.ButtonStyle.secondary, custom_id="market_stock")
    async def stock_button(self, interaction: discord.Interaction, button: Button):
        await show_market_selector(interaction, MARKET_STOCK)


class AssetSelect(Select):
    def __init__(self, market_type: str, assets: List[Dict]):
        self.market_type = market_type
        self.assets = assets
        options = [
            discord.SelectOption(
                label=asset["display"],
                value=asset["symbol"],
                description=asset.get("description", "")
            )
            for asset in assets
        ]
        super().__init__(
            placeholder=f"Select a {market_type}",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"asset_select_{market_type}"
        )

    async def callback(self, interaction: discord.Interaction):
        symbol = self.values[0]
        await show_price_embed(interaction, symbol, self.market_type)


class AssetSelectView(View):
    def __init__(self, market_type: str, assets: List[Dict]):
        super().__init__(timeout=180)
        self.add_item(AssetSelect(market_type, assets))
        # Add a back button
        self.add_item(Button(label="�◀ Back", style=discord.ButtonStyle.danger, custom_id="back_button"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data["custom_id"] == "back_button":
            await show_market_terminal(interaction)
            return False  # Prevent further handling
        return True


async def show_market_terminal(interaction: discord.Interaction):
    embed = discord.Embed(
        title="���📊 MARKET TERMINAL",
        description="Binance Market Data\n\nSelect a market to begin.",
        color=0x00ff00
    )
    # You can add image or thumbnail if desired
    view = MarketView()
    await interaction.response.send_message(embed=embed, view=view)


async def show_market_selector(interaction: discord.Interaction, market_type: str):
    api = BinanceAPI()
    assets = []
    if market_type == MARKET_CRYPTO:
        # Get active USDT pairs and filter to known crypto
        active_symbols = set(api.get_active_symbols("USDT"))
        for symbol, name, display in KNOWN_CRYPTO:
            if symbol in active_symbols:
                assets.append({
                    "symbol": symbol,
                    "display": f"{display} ({name})",
                    "description": f"{name} USDT"
                })
        title = "���🪙 Crypto Selection"
    else:  # stock
        active_symbols = set(api.get_active_symbols("USDT"))
        for symbol, name, display in KNOWN_STOCKS:
            if symbol in active_symbols:
                assets.append({
                    "symbol": symbol,
                    "display": f"{display} ({name})",
                    "description": f"{name} USDT (Tokenized Stock)"
                })
        title = "���📈 Stock Selection"

    if not assets:
        await interaction.response.send_message(
            "No assets available for this market. Please check the Binance API.",
            ephemeral=True
        )
        return

    view = AssetSelectView(market_type, assets)
    embed = discord.Embed(
        title=title,
        description="Select an asset to view its price.",
        color=0x00aaaa
    )
    await interaction.response.edit_message(embed=embed, view=view)


async def show_price_embed(interaction: discord.Interaction, symbol: str, market_type: str):
    api = BinanceAPI()
    price_data = api.get_symbol_price(symbol)
    ticker_data = api.get_24hr_ticker(symbol)

    if not price_data:
        await interaction.response.send_message(
            f"Failed to fetch price for {symbol}. Please try again later.",
            ephemeral=True
        )
        return

    price = float(price_data["price"])
    change_percent = 0
    change_amount = 0
    if ticker_data:
        change_percent = float(ticker_data.get("priceChangePercent", 0))
        change_amount = float(ticker_data.get("priceChange", 0))

    # Determine arrow and color
    if change_percent > 0:
        arrow = "�▲"
        color = 0x00ff00  # green
    elif change_percent < 0:
        arrow = "�▼"
        color = 0xff0000  # red
    else:
        arrow = "−"
        color = 0xffff00  # yellow

    # Determine display name from symbol
    display_name = symbol
    name = ""
    if market_type == MARKET_CRYPTO:
        for sym, n, disp in KNOWN_CRYPTO:
            if sym == symbol:
                display_name = f"{disp} ({n})"
                name = n
                break
    else:
        for sym, n, disp in KNOWN_STOCKS:
            if sym == symbol:
                display_name = f"{disp} ({n})"
                name = n
                break

    market_name = "Binance Spot"

    embed = discord.Embed(
        title=f"���📈 {display_name}",
        color=color,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Price", value=f"{price:,.8f} USDT", inline=False)
    embed.add_field(name="Change", value=f"{arrow} {change_percent:+.2f}%", inline=False)
    embed.add_field(name="Market", value=market_name, inline=False)
    # Approximate KST: UTC+9
    utc_time = discord.utils.utcnow()
    embed.set_footer(text=f"Updated {utc_time.strftime('%H:%M:%S UTC')} (KST: +9h)")

    # Back button
    view = View()
    view.add_item(Button(label="�◀ Back", style=discord.ButtonStyle.danger, custom_id="price_back"))

    await interaction.response.edit_message(embed=embed, view=view)


def setup_commands(tree: app_commands.CommandTree):
    @tree.command(name="market", description="Open the Market Terminal")
    async def market(interaction: discord.Interaction):
        logger.info("MARKET COMMAND CALLBACK STARTED")
        await show_market_terminal(interaction)
        logger.info("SENDING MARKET RESPONSE")

    # Note: We handle button/select interactions via the views' callbacks.
    # No need to register separate command handlers for buttons if we use View.