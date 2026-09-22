PlayTree Discord Bot
====================

A Discord bot for the PlayTree Game Collection community.

Setup
-----
1. Install Python 3.12+
2. Install dependencies:
   pip install discord.py python-dotenv psutil
3. Edit .env and set your DISCORD_TOKEN
4. Run: python bot.py (or double-click start_bot.bat)

Commands
--------
/games          - Show all 9 PlayTree games
/play <game>    - Show game info and launch details
/random         - Pick a random game to play
/stats [user]   - Show playtime, launches, rank
/achievements   - Show unlocked achievements
/leaderboard    - Server playtime ranking
/profile [user] - Show your PlayTree profile card
/favorite       - Set your favorite game
/rate <1-5>     - Rate a game
/help           - List all commands

Bot Info
--------
- Name: PLAYTREE#3995
- 9 games tracked
- 12 achievements
- Reads stats from GameCollection/collection_data/stats.json
- Slash commands only (no prefix needed)

Files
-----
bot.py              - Main entry point
config.py           - Token, game data, achievements
.env                - Bot token (keep secret!)
cogs/games.py       - /games, /play, /random
cogs/stats.py       - /stats, /achievements, /leaderboard
cogs/profile.py     - /profile, /favorite, /rate
start_bot.bat       - Double-click to start
