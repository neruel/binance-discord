import discord
from discord import app_commands
from discord.ui import View, Button, Select
import logging
import datetime
from typing import List, Dict
from services.binance import BinanceAPI

logger = logging.getLogger(__name__)

# Define market categories
MARKET_CRYPTO = "crypto"
MARKET_STOCK = "stock"

# Known crypto symbols for /market menu
KNOWN_CRYPTO = [
    ("BTCUSDT", "비트코인", "BTC"),
    ("ETHUSDT", "이더리움", "ETH"),
    ("BNBUSDT", "바이낸스코인", "BNB"),
    ("SOLUSDT", "솔라나", "SOL"),
    ("XRPUSDT", "리플", "XRP"),
    ("DOGEUSDT", "도지코인", "DOGE"),
]

# Known stock tokens for /market menu
KNOWN_STOCKS = [
    ("SKHYBUSDT", "SK하이닉스", "SKHY"),
    ("TSLABUSDT", "테슬라", "TSLA"),
    ("AAPLBUSDT", "애플", "AAPL"),
    ("MSFTBUSDT", "마이크로소프트", "MSFT"),
    ("NVDABUSDT", "엔비디아", "NVDA"),
]


class MarketView(View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="🪙 암호화폐", style=discord.ButtonStyle.primary, custom_id="market_crypto")
    async def crypto_button(self, interaction: discord.Interaction, button: Button):
        await show_market_selector(interaction, MARKET_CRYPTO)

    @discord.ui.button(label="📈 토큰화 주식", style=discord.ButtonStyle.secondary, custom_id="market_stock")
    async def stock_button(self, interaction: discord.Interaction, button: Button):
        await show_market_selector(interaction, MARKET_STOCK)


class AssetSelect(Select):
    def __init__(self, market_type: str, assets: List[Dict]):
        self.market_type = market_type
        self.assets = assets
        placeholder_text = "조회할 암호화폐 선택" if market_type == MARKET_CRYPTO else "조회할 토큰화 주식 선택"
        options = [
            discord.SelectOption(
                label=asset["display"],
                value=asset["symbol"],
                description=asset.get("description", "")
            )
            for asset in assets
        ]
        super().__init__(
            placeholder=placeholder_text,
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
        self.add_item(Button(label="◀ 이전으로", style=discord.ButtonStyle.danger, custom_id="back_button"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.data.get("custom_id") == "back_button":
            await show_market_terminal(interaction)
            return False
        return True


async def show_market_terminal(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📊 바이낸스 마켓 터미널",
        description="바이낸스 실시간 시세 데이터 터미널입니다.\n\n아래 마켓 버튼을 누르거나, `/시세검색 (검색어)` 명령어로 바로 검색하세요.",
        color=0x00ff00
    )
    view = MarketView()
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, view=view)
    else:
        await interaction.response.send_message(embed=embed, view=view)


async def show_market_selector(interaction: discord.Interaction, market_type: str):
    api = BinanceAPI()
    assets = []
    if market_type == MARKET_CRYPTO:
        for symbol, name, display in KNOWN_CRYPTO:
            assets.append({
                "symbol": symbol,
                "display": f"{name} ({display})",
                "description": f"{name} USDT 실시간 시세"
            })
        title = "🪙 암호화폐 종목 선택"
    else:
        for symbol, name, display in KNOWN_STOCKS:
            assets.append({
                "symbol": symbol,
                "display": f"{name} ({display})",
                "description": f"{name} USDT (토큰화 주식)"
            })
        title = "📈 토큰화 주식 종목 선택"

    view = AssetSelectView(market_type, assets)
    embed = discord.Embed(
        title=title,
        description="상세 시세를 확인할 종목을 선택하세요.",
        color=0x00aaaa
    )
    await interaction.response.edit_message(embed=embed, view=view)


async def show_price_embed(interaction: discord.Interaction, symbol: str, market_type: str):
    api = BinanceAPI()
    ticker = api.get_24hr_ticker(symbol)

    if not ticker:
        await interaction.response.send_message(
            f"❌ {symbol} 시세 정보를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.",
            ephemeral=True
        )
        return

    price = float(ticker.get("lastPrice", 0))
    change_percent = float(ticker.get("priceChangePercent", 0))

    color = 0x00ff00 if change_percent > 0 else (0xff0000 if change_percent < 0 else 0xffff00)
    arrow = "🔺" if change_percent > 0 else ("🔻" if change_percent < 0 else "➖")

    embed = discord.Embed(
        title=f"📈 {symbol} 실시간 시세",
        color=color
    )
    embed.add_field(name="💰 현재가", value=f"**{format_price_str(price)} USDT**", inline=False)
    embed.add_field(name="📊 24시간 변동률", value=f"**{arrow} {change_percent:+.2f}%**", inline=False)
    
    kst_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S KST')
    embed.set_footer(text=f"Binance Spot • 갱신시각: {kst_time}")

    view = View()
    view.add_item(Button(label="◀ 이전으로", style=discord.ButtonStyle.danger, custom_id="price_back"))

    await interaction.response.edit_message(embed=embed, view=view)


def format_price_str(price: float) -> str:
    """Format float price smoothly according to magnitude."""
    if price >= 100:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:,.4f}"
    else:
        return f"${price:,.6f}"


async def handle_price_search(interaction: discord.Interaction, query: str):
    """Handle /시세검색 search logic for single and multi-results in Korean."""
    await interaction.response.defer()

    api = BinanceAPI()
    results = api.search_symbols(query)

    kst_now = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S KST')

    if not results:
        embed = discord.Embed(
            title="❌ 검색 결과 없음",
            description=f"**'{query}'** 에 해당하는 시세 정보를 찾을 수 없습니다.",
            color=0xff0000
        )
        embed.add_field(
            name="💡 검색 팁",
            value="• 종목명 (예: `SK하이닉스`, `테슬라`, `엔비디아`, `애플`, `마이크로소프트`)\n"
                  "• 암호화폐 (예: `비트코인`, `이더리움`, `리플`, `도지`)\n"
                  "• 티커/심볼 (예: `SKHY`, `TSLA`, `BTC`, `SKHYBUSDT`)",
            inline=False
        )
        embed.set_footer(text=f"Binance Spot • 갱신시각: {kst_now}")
        await interaction.followup.send(embed=embed)
        return

    # Case 1: Exactly 1 result found
    if len(results) == 1:
        asset = results[0]
        symbol = asset["symbol"]
        ticker = api.get_24hr_ticker(symbol)

        if not ticker:
            await interaction.followup.send(f"❌ {symbol} 시세를 가져오는 데 실패했습니다.")
            return

        price = float(ticker.get("lastPrice", 0))
        change_pct = float(ticker.get("priceChangePercent", 0))
        high_price = float(ticker.get("highPrice", 0))
        low_price = float(ticker.get("lowPrice", 0))
        volume = float(ticker.get("volume", 0))

        color = 0x00ff00 if change_pct > 0 else (0xff0000 if change_pct < 0 else 0xffff00)
        arrow = "🔺" if change_pct > 0 else ("🔻" if change_pct < 0 else "➖")

        market_type_kr = "토큰화 주식" if asset.get('market_type') == "Stock (Tokenized)" else "암호화폐"
        display_title = f"📈 {asset.get('korean_name', asset['display'])} ({symbol})"

        embed = discord.Embed(
            title=display_title,
            color=color,
            description=f"**종목 구분**: {market_type_kr}"
        )
        embed.add_field(name="💰 현재가", value=f"**{format_price_str(price)} USDT**", inline=True)
        embed.add_field(name="📊 24시간 변동률", value=f"**{arrow} {change_pct:+.2f}%**", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer for 3-col grid

        embed.add_field(name="🔺 24시간 최고가", value=f"{format_price_str(high_price)} USDT", inline=True)
        embed.add_field(name="🔻 24시간 최저가", value=f"{format_price_str(low_price)} USDT", inline=True)
        embed.add_field(name="📈 24시간 거래량", value=f"{volume:,.2f}", inline=True)

        embed.set_footer(text=f"Binance Spot • 갱신시각: {kst_now}")
        await interaction.followup.send(embed=embed)
        return

    # Case 2: 2 or more results found (Multi-result response)
    embed = discord.Embed(
        title=f"🔍 '{query}' 시세 검색 결과 (총 {len(results)}건)",
        description="검색된 종목의 실시간 시세 목록입니다:",
        color=0x00aaff
    )

    for i, asset in enumerate(results, 1):
        symbol = asset["symbol"]
        ticker = api.get_24hr_ticker(symbol)
        if ticker:
            price = float(ticker.get("lastPrice", 0))
            change_pct = float(ticker.get("priceChangePercent", 0))
            arrow = "🔺" if change_pct > 0 else ("🔻" if change_pct < 0 else "➖")
            price_text = f"{format_price_str(price)} USDT"
            change_text = f"{arrow} {change_pct:+.2f}%"
        else:
            price_text = "조회불가"
            change_text = "조회불가"

        name_display = asset.get("korean_name") or asset.get("name") or symbol
        field_name = f"{i}. {name_display} ({symbol})"
        field_value = f"현재가: **{price_text}** | 24시간 변동률: **{change_text}**"

        embed.add_field(name=field_name, value=field_value, inline=False)

    embed.set_footer(text=f"Binance Spot • 갱신시각: {kst_now}")
    await interaction.followup.send(embed=embed)


def setup_commands(tree: app_commands.CommandTree):
    @tree.command(name="시세검색", description="토큰화 주식 및 암호화폐 실시간 시세를 검색합니다 (예: SK하이닉스, 테슬라, BTC)")
    @app_commands.describe(검색어="검색할 종목명, 별칭 또는 티커 (예: SK하이닉스, 테슬라, BTC, SK)")
    async def price_search_kr(interaction: discord.Interaction, 검색어: str):
        logger.info(f"Command /시세검색 invoked with query: {검색어}")
        await handle_price_search(interaction, 검색어)

    @tree.command(name="search", description="토큰화 주식 및 암호화폐 실시간 시세를 검색합니다 (영문 명령어)")
    @app_commands.describe(query="검색할 종목명 또는 티커 (예: SKHY, TSLA, BTC)")
    async def price_search_en(interaction: discord.Interaction, query: str):
        logger.info(f"Command /search invoked with query: {query}")
        await handle_price_search(interaction, query)

    @tree.command(name="market", description="바이낸스 마켓 터미널을 열어 종목을 선택합니다")
    async def market(interaction: discord.Interaction):
        logger.info("MARKET COMMAND CALLBACK STARTED")
        await show_market_terminal(interaction)