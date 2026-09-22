"""PlayTree Discord Bot — Profile Cog"""
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAMES, ACHIEVEMENTS, STATS_FILE


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_stats(self):
        try:
            with open(STATS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}

    def save_stats(self, data):
        try:
            os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
            with open(STATS_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def get_user_data(self, stats, user_id):
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

    def format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    @app_commands.command(name="profile", description="Show your PlayTree profile card")
    @app_commands.describe(member="User to view profile for")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        all_stats = self.load_stats()
        user_data = self.get_user_data(all_stats, target.id)

        total_launches = sum(user_data.get("launches", {}).values())
        total_playtime = sum(user_data.get("playtime", {}).values())
        achievements = user_data.get("achievements", [])
        fav = user_data.get("favorites", [])
        ratings = user_data.get("ratings", {})

        # Rank
        all_users = all_stats.get("discord_users", {})
        ranked = sorted(
            all_users.items(),
            key=lambda x: sum(x[1].get("playtime", {}).values()),
            reverse=True,
        )
        rank = next(
            (i + 1 for i, (uid, _) in enumerate(ranked) if uid == str(target.id)),
            len(ranked) + 1,
        )

        # Favorite game
        fav_game = None
        if fav:
            fav_game = next((g for g in GAMES if g["name"] == fav[0]), None)

        # Avg rating given
        user_ratings = [v for v in ratings.values() if v > 0]
        avg_rating = sum(user_ratings) / len(user_ratings) if user_ratings else 0

        # Color from favorite
        color = fav_game["color"] if fav_game else 0x7ED321

        embed = discord.Embed(
            title=f"PlayTree Profile: {target.display_name}",
            color=color,
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        # Stats section
        embed.add_field(
            name="Stats",
            value=(
                f"**Playtime:** {self.format_time(total_playtime)}\n"
                f"**Launches:** {total_launches}\n"
                f"**Rank:** #{rank} server"
            ),
            inline=True,
        )

        embed.add_field(
            name="Collection",
            value=(
                f"**Achievements:** {len(achievements)}/{len(ACHIEVEMENTS)}\n"
                f"**Games Rated:** {len(user_ratings)}/9\n"
                f"**Avg Rating:** {'*' * int(avg_rating)}{' ' * (5 - int(avg_rating))} {avg_rating:.1f}"
                if user_ratings
                else f"**Games Rated:** 0/9\n**Avg Rating:** Not rated"
            ),
            inline=True,
        )

        embed.add_field(
            name="Favorite",
            value=fav_game["name"] if fav_game else "None set\nUse `/favorite` to set",
            inline=True,
        )

        # Recent achievements
        if achievements:
            ach_names = []
            for aid in achievements[:5]:
                ach = next((a for a in ACHIEVEMENTS if a["id"] == aid), None)
                if ach:
                    ach_names.append(f"{ach['icon']} {ach['name']}")
            if ach_names:
                embed.add_field(
                    name="Recent Achievements",
                    value="\n".join(ach_names),
                    inline=False,
                )

        embed.set_footer(text="Use /favorite to set | /rate to rate games")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="favorite", description="Set your favorite PlayTree game")
    @app_commands.describe(game="Your favorite game")
    @app_commands.choices(
        game=[
            app_commands.Choice(name=g["name"], value=g["name"]) for g in GAMES
        ]
    )
    async def favorite(self, interaction: discord.Interaction, game: str):
        game_data = next((g for g in GAMES if g["name"] == game), None)
        if not game_data:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        all_stats = self.load_stats()
        user_data = self.get_user_data(all_stats, interaction.user.id)

        favs = user_data.get("favorites", [])
        if game in favs:
            favs.remove(game)
            await interaction.response.send_message(
                f"Removed **{game}** from favorites."
            )
        else:
            favs.clear()
            favs.append(game)
            user_data["favorites"] = favs
            await interaction.response.send_message(
                f"Set **{game}** as your favorite! :star:"
            )

        self.save_stats(all_stats)

    @app_commands.command(name="rate", description="Rate a PlayTree game 1-5 stars")
    @app_commands.describe(game="Game to rate", rating="Rating 1-5")
    @app_commands.choices(
        game=[
            app_commands.Choice(name=g["name"], value=g["name"]) for g in GAMES
        ]
    )
    async def rate(
        self,
        interaction: discord.Interaction,
        game: str,
        rating: app_commands.Range[int, 1, 5],
    ):
        game_data = next((g for g in GAMES if g["name"] == game), None)
        if not game_data:
            await interaction.response.send_message("Game not found.", ephemeral=True)
            return

        all_stats = self.load_stats()
        user_data = self.get_user_data(all_stats, interaction.user.id)

        if "ratings" not in user_data:
            user_data["ratings"] = {}
        user_data["ratings"][game] = rating
        self.save_stats(all_stats)

        stars = "*" * rating + " " * (5 - rating)
        await interaction.response.send_message(
            f"Rated **{game}**: {stars} {rating}/5"
        )

    @app_commands.command(name="help", description="List all PlayTree bot commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="PlayTree Bot Commands",
            description="All commands for the PlayTree Discord Bot",
            color=0x7ED321,
        )

        commands_list = [
            ("/games", "Show all 9 PlayTree games"),
            ("/play <game>", "Show game info and launch details"),
            ("/random", "Pick a random game to play"),
            ("/stats [user]", "Show playtime, launches, rank"),
            ("/achievements [user]", "Show unlocked achievements"),
            ("/leaderboard", "Server playtime ranking"),
            ("/profile [user]", "Show your PlayTree profile card"),
            ("/favorite <game>", "Set your favorite game"),
            ("/rate <game> <1-5>", "Rate a game"),
            ("/help", "Show this help message"),
        ]

        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.set_footer(text="PlayTree Game Collection — GoStudios")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
