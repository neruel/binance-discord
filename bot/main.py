import discord
from discord import app_commands
from discord.ext import tasks
import logging
import asyncio
from config.settings import DISCORD_TOKEN
from bot.commands import setup_commands

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s:%(name)s:%(levelname)s:%(message)s'
)
logger = logging.getLogger('binance_bot')

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True  # If you want to read message content (not needed for slash commands but good to have)

class BinanceBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This is called when the bot starts up
        setup_commands(self.tree)
        # Sync commands to Discord (global sync can take up to an hour)
        # For development, we can sync to a specific guild for instant updates
        # Uncomment and set GUILD_ID if you want to test in a specific server
        # GUILD_ID = discord.Object(id=YOUR_GUILD_ID)
        # self.tree.copy_global_to(guild=GUILD_ID)
        # await self.tree.sync(guild=GUILD_ID)
        await self.tree.sync()
        logger.info("Slash commands synced.")

    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot ID: {self.user.id}')
        # Set activity
        activity = discord.Activity(type=discord.ActivityType.watching, name="/market")
        await self.change_presence(activity=activity)

    async def on_interaction(self, interaction: discord.Interaction):
        # Log interactions for debugging
        logger.info(f'Interaction: {interaction.type} {interaction.data.get("name", "no name") if interaction.data else ""}')

async def main():
    async with BinanceBot() as bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutting down...")