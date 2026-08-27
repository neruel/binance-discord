import os
import discord
from discord import app_commands
import logging
import asyncio
from aiohttp import web
from config.settings import DISCORD_TOKEN, validate_config
from bot.commands import setup_commands

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
)
logger = logging.getLogger('binance_bot')

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True


async def handle_health_check(request):
    return web.Response(text="Binance Discord Bot is ONLINE!")


async def start_health_check_server():
    """Starts a lightweight web server so Render / Koyeb free Web Service tier works for $0/mo."""
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    app.router.add_get("/health", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check web server running on port {port}")


class BinanceBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Start HTTP server for Render / Koyeb Free Web Service tier compatibility
        asyncio.create_task(start_health_check_server())
        # Setup slash commands
        setup_commands(self.tree)
        # Sync slash commands globally
        synced = await self.tree.sync()
        logger.info(f"Synced {len(synced)} slash commands globally.")

    async def on_ready(self):
        logger.info(f'Bot {self.user} is now ONLINE!')
        logger.info(f'Bot User ID: {self.user.id}')
        activity = discord.Activity(type=discord.ActivityType.watching, name="/시세검색 [검색어]")
        await self.change_presence(activity=activity)

    async def on_interaction(self, interaction: discord.Interaction):
        logger.info(f'Interaction received: {interaction.type} - {interaction.data.get("name", "component") if interaction.data else ""}')


async def main():
    validate_config()
    async with BinanceBot() as bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")