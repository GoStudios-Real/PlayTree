"""PlayTree Discord Bot — Games Cog"""
import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import psutil
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAMES, WEBSITE_URL, GITHUB_URL, ITCH_URL


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="games", description="Show all PlayTree games")
    async def games(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="PlayTree Game Collection",
            description="9 games by GoStudios — all free to play",
            color=0x7ED321,
        )

        for game in GAMES:
            embed.add_field(
                name=f"[{game['icon']}] {game['name']}",
                value=f"{game['desc']}\n*{game['genre']}*",
                inline=True,
            )

        embed.set_footer(text="Use /play <game> for details | /random to pick one")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Show game info and launch details")
    @app_commands.describe(game="The game to play")
    @app_commands.choices(
        game=[
            app_commands.Choice(name=g["name"], value=g["name"]) for g in GAMES
        ]
    )
    async def play(self, interaction: discord.Interaction, game: str):
        game_data = next((g for g in GAMES if g["name"] == game), None)
        if not game_data:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        stats = self.bot.get_cog("Stats")
        all_stats = {}
        if stats:
            all_stats = stats.load_stats()

        game_launches = sum(
            all_stats.get("launches", {}).get(g["name"], 0)
            for g in GAMES
            if g["name"] == game
        )
        game_ratings = []
        for uid, ud in all_stats.get("discord_users", {}).items():
            r = ud.get("ratings", {}).get(game)
            if r:
                game_ratings.append(r)
        avg_rating = sum(game_ratings) / len(game_ratings) if game_ratings else 0

        embed = discord.Embed(
            title=game_data["name"],
            description=game_data["desc"],
            color=game_data["color"],
        )
        embed.add_field(name="Genre", value=game_data["genre"], inline=True)
        embed.add_field(name="Total Launches", value=str(game_launches), inline=True)
        embed.add_field(
            name="Avg Rating",
            value=f"{'*' * int(avg_rating)}{' ' * (5 - int(avg_rating))} {avg_rating:.1f}/5"
            if avg_rating > 0
            else "Not rated yet",
            inline=True,
        )
        embed.add_field(
            name="How to Play",
            value=f"Run `{game_data['exe']}` from your PlayTree folder",
            inline=False,
        )
        embed.set_footer(text="Use /rate to rate this game | /favorite to set as favorite")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="random", description="Pick a random PlayTree game to play")
    async def random_game(self, interaction: discord.Interaction):
        game = random.choice(GAMES)
        embed = discord.Embed(
            title="Random Game Pick!",
            description=f"**{game['name']}**\n{game['desc']}",
            color=game["color"],
        )
        embed.set_footer(text=f"Genre: {game['genre']} | Use /play {game['name']} for more info")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Show what PlayTree games are running")
    async def nowplaying(self, interaction: discord.Interaction):
        game_names = set()
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"].lower().replace(".exe", "")
                for g in GAMES:
                    if g["exe"].lower().replace(".exe", "") == name:
                        game_names.add(g["name"])
            except Exception:
                pass

        embed = discord.Embed(title="Now Playing", color=0x7ED321)
        if game_names:
            for gname in game_names:
                g = next((x for x in GAMES if x["name"] == gname), None)
                if g:
                    embed.add_field(name=f"{g['icon']} {g['name']}", value=g["desc"], inline=True)
            embed.set_footer(text="Detected via process scan")
        else:
            embed.description = "No PlayTree games currently running."
            embed.set_footer(text="Launch a game to see it here!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="links", description="Get PlayTree download and social links")
    async def links(self, interaction: discord.Interaction):
        embed = discord.Embed(title="PlayTree Links", description="All official PlayTree links", color=0x7ED321)
        embed.add_field(name="itch.io", value=f"[Download Games]({ITCH_URL})", inline=True)
        embed.add_field(name="Website", value=f"[gostudios-real.github.io]({WEBSITE_URL})", inline=True)
        embed.add_field(name="GitHub", value=f"[Source Code]({GITHUB_URL})", inline=True)
        embed.set_footer(text="GoStudios | GoConsole Game Studios")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverstats", description="Show server PlayTree stats")
    async def serverstats(self, interaction: discord.Interaction):
        stats_cog = self.bot.get_cog("Stats")
        if not stats_cog:
            await interaction.response.send_message("Stats not available.", ephemeral=True)
            return
        all_stats = stats_cog.load_stats()
        all_users = all_stats.get("discord_users", {})
        total_playtime = sum(sum(ud.get("playtime", {}).values()) for ud in all_users.values())
        total_launches = sum(sum(ud.get("launches", {}).values()) for ud in all_users.values())
        games_played = set()
        for ud in all_users.values():
            for gname, launches in ud.get("launches", {}).items():
                if launches > 0:
                    games_played.add(gname)

        embed = discord.Embed(title="Server PlayTree Stats", color=0x7ED321)
        embed.add_field(name="Total Players", value=str(len(all_users)), inline=True)
        embed.add_field(name="Total Launches", value=str(total_launches), inline=True)
        embed.add_field(name="Unique Games Played", value=f"{len(games_played)}/9", inline=True)
        h = int(total_playtime // 3600)
        m = int((total_playtime % 3600) // 60)
        embed.add_field(name="Total Playtime", value=f"{h}h {m}m", inline=True)
        embed.set_footer(text="Powered by GoStudios")
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="countdown", description="Countdown to PlayTree Chapter 1 Season 1")
    async def countdown(self, interaction: discord.Interaction):
        import datetime
        target = datetime.datetime(2026, 9, 25, 17, 34, 0)
        now = datetime.datetime.now()
        diff = target - now
        if diff.total_seconds() <= 0:
            embed = discord.Embed(
                title="Chapter 1 : Season 1",
                description="**LIVE NOW!**",
                color=0xFFD700,
            )
        else:
            days = diff.days
            hours, rem = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            embed = discord.Embed(
                title="PlayTree Chapter 1 : Season 1",
                description="Countdown to launch",
                color=0x7ED321,
            )
            embed.add_field(name="Days", value=f"**{days}**", inline=True)
            embed.add_field(name="Hours", value=f"**{hours}**", inline=True)
            embed.add_field(name="Minutes", value=f"**{minutes}**", inline=True)
            embed.add_field(name="Seconds", value=f"**{seconds}**", inline=True)
            embed.add_field(
                name="Launch Date",
                value="September 25, 2026 at 5:34 PM",
                inline=False,
            )
        embed.set_footer(text=f"Live at gostudios-real.github.io/GoStudios-Real-playtree.github.io/")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Games(bot))
