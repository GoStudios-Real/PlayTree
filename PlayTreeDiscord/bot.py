"""PlayTree Discord Bot — Main Entry Point"""
import discord
from discord.ext import commands, tasks
import json
import os
import sys
import subprocess
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TOKEN, GUILD_ID, STATS_FILE, GAMES, DISCORD_APP_ID

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

rich_presence_process = None


def start_rich_presence():
    global rich_presence_process
    try:
        rp_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rich_presence.py")
        if os.path.exists(rp_script):
            rich_presence_process = subprocess.Popen(
                [sys.executable, rp_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            print("Rich Presence started")
    except Exception as e:
        print(f"Rich Presence failed: {e}")


def load_stats():
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_stats(data):
    try:
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        with open(STATS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def get_user_data(stats, user_id):
    uid = str(user_id)
    if "discord_users" not in stats:
        stats["discord_users"] = {}
    if uid not in stats["discord_users"]:
        stats["discord_users"][uid] = {
            "favorites": [],
            "ratings": {},
            "launches": {},
            "playtime": {},
            "achievements": [],
        }
    return stats["discord_users"][uid]


@bot.event
async def on_ready():
    await bot.load_extension("cogs.games")
    await bot.load_extension("cogs.stats")
    await bot.load_extension("cogs.profile")

    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"Synced commands to guild {GUILD_ID}")
    else:
        await bot.tree.sync()
        print("Synced commands globally")

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="PlayTree Game Collection"
        )
    )
    print(f"PlayTree Bot ready — {bot.user}")
    print(f"App ID: {DISCORD_APP_ID}")
    print(f"Commands: /games /play /random /stats /achievements /leaderboard /profile /favorite /rate /nowplaying /links /serverstats /help")

    start_rich_presence()
    update_presence.start()


@tasks.loop(minutes=5)
async def update_presence():
    try:
        stats = load_stats()
        total = sum(stats.get("launches", {}).values())
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name=f"PlayTree | {total} launches"
            )
        )
    except Exception:
        pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"Error: {error}", delete_after=10)


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: No DISCORD_TOKEN found in .env")
        sys.exit(1)
    bot.run(TOKEN)
