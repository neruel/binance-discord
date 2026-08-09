# Next Steps to Run the Binance Discord Market Bot

## 1. Get Required API Credentials

### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application", give it a name, and create
3. Go to "Bot" tab → "Add Bot" → "Yes, do it!"
4. Under "TOKEN", click "Copy" (you'll need to reset if you lose it)
5. Under "Privileged Gateway Intents", enable:
   - PRESENCE INTENT
   - SERVER MEMBERS INTENT
   - MESSAGE CONTENT INTENT (if you plan to read message content)

### Binance API Keys
1. Log in to [Binance](https://www.binance.com/)
2. Go to [API Management](https://www.binance.com/en/my/settings/api-management)
3. Create API key (you may need to complete security verification)
4. Label it (e.g., "Discord Bot")
5. DO NOT enable any trading or withdrawal permissions (read-only is fine)
6. Copy both API Key and Secret Key

## 2. Configure Environment

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` with your actual credentials:
   ```
   DISCORD_TOKEN=your_discord_bot_token_here
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_API_SECRET=your_binance_api_secret_here
   ```

3. **IMPORTANT**: Never share or commit your `.env` file!

## 3. Install Dependencies

```bash
# Make sure you're in the project directory
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Run the Bot

```bash
python -m bot.main
```

You should see log output indicating the bot has connected to Discord and synced commands.

## 5. Test in Discord

1. Invite your bot to a server using the OAuth2 URL Generator in Discord Developer Portal
   - Select "bot" scope
   - Select "applications.commands" permission
   - Copy the generated URL and open it in a browser to invite the bot

2. In Discord, use the slash command:
   ```
   /market
   ```

3. You should see the Market Terminal interface with Crypto and Stocks buttons
4. Navigate through the menus to view prices

## 6. Troubleshooting

### Common Issues

**LoginFailure: Improper token has been passed**
- Double-check your DISCORD_TOKEN in .env
- Make sure there are no extra spaces or characters

**401 Unauthorized from Binance**
- Check your BINANCE_API_KEY and BINANCE_API_SECRET
- Verify the API key has permission to read market data

**Command not showing up in Discord**
- It can take up to an hour for global command sync
- For testing, uncomment the GUILD_ID lines in bot/main.py to sync to a specific server
- Make sure the bot has "applications.commands" permission in the server

**No assets showing up**
- Run `python test_binance.py` to verify API connectivity
- Check that the symbols in KNOWN_CRYPTO and KNOWN_STOCKS are still valid

## 7. File Overview

- `bot/main.py` - Entry point, Discord client setup
- `bot/commands.py` - All slash commands and UI interactions
- `services/binance.py` - Binance API wrapper
- `config/settings.py` - Environment variable loading
- `requirements.txt` - Python dependencies
- `.env.example` - Template for environment variables
- `README.md` - General project information
- `IMPLEMENTATION_SUMMARY.md` - This file
- `test_binance.py` - Verification script for Binance API
- `test_commands.py` - Verification for command setup

## 8. Need Help?

If you encounter issues:
1. Check the console output for error messages
2. Verify your API credentials are correct
3. Ensure you have internet connectivity to reach Discord and Binance APIs
4. Look at the log files if you enable file logging