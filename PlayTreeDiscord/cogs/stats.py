"""PlayTree Discord Bot — Stats Cog"""
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GAMES, ACHIEVEMENTS, STATS_FILE


class Stats(commands.Cog):
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
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        else:
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            return f"{h}h {m}m"

    @app_commands.command(name="stats", description="Show your PlayTree stats")
    @app_commands.describe(member="User to check stats for")
    async def stats(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        all_stats = self.load_stats()
        user_data = self.get_user_data(all_stats, target.id)

        total_launches = sum(user_data.get("launches", {}).values())
        total_playtime = sum(user_data.get("playtime", {}).values())
        games_played = len([k for k, v in user_data.get("launches", {}).items() if v > 0])
        fav = user_data.get("favorites", [])
        achievements = user_data.get("achievements", [])

        # Calculate rank
        all_users = all_stats.get("discord_users", {})
        ranked = sorted(all_users.items(), key=lambda x: sum(x[1].get("playtime", {}).values()), reverse=True)
        rank = next((i + 1 for i, (uid, _) in enumerate(ranked) if uid == str(target.id)), len(ranked) + 1)

        # Favorite game
        fav_game = None
        if fav:
            fav_game = next((g for g in GAMES if g["name"] == fav[0]), None)

        embed = discord.Embed(
            title=f"PlayTree Stats: {target.display_name}",
            color=target.color if target.color != discord.Color.default() else 0x7ED321,
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(name="Total Launches", value=str(total_launches), inline=True)
        embed.add_field(name="Playtime", value=self.format_time(total_playtime), inline=True)
        embed.add_field(name="Games Played", value=f"{games_played}/9", inline=True)

        embed.add_field(name="Rank", value=f"#{rank} server", inline=True)
        embed.add_field(
            name="Favorite",
            value=fav_game["name"] if fav_game else "None set",
            inline=True,
        )
        embed.add_field(
            name="Achievements",
            value=f"{len(achievements)}/{len(ACHIEVEMENTS)}",
            inline=True,
        )

        # Per-game breakdown
        game_lines = []
        for g in GAMES:
            launches = user_data.get("launches", {}).get(g["name"], 0)
            if launches > 0:
                game_lines.append(f"**{g['name']}**: {launches}x")
        if game_lines:
            embed.add_field(
                name="Game Breakdown",
                value="\n".join(game_lines[:9]),
                inline=False,
            )

        embed.set_footer(text="Use /achievements to see badges | /profile for profile card")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="achievements", description="Show achievement progress")
    @app_commands.describe(member="User to check achievements for")
    async def achievements(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        all_stats = self.load_stats()
        user_data = self.get_user_data(all_stats, target.id)
        unlocked = user_data.get("achievements", [])

        embed = discord.Embed(
            title=f"Achievements: {target.display_name}",
            description=f"{len(unlocked)}/{len(ACHIEVEMENTS)} unlocked",
            color=0x7ED321,
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        for ach in ACHIEVEMENTS:
            is_unlocked = ach["id"] in unlocked
            status = "DONE" if is_unlocked else "LOCKED"
            emoji = ":white_check_mark:" if is_unlocked else ":lock:"
            embed.add_field(
                name=f"{emoji} {ach['name']}",
                value=f"{ach['desc']}\n*{status}*",
                inline=True,
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="Server playtime leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        all_stats = self.load_stats()
        all_users = all_stats.get("discord_users", {})

        ranked = []
        for uid, ud in all_users.items():
            total_pt = sum(ud.get("playtime", {}).values())
            total_l = sum(ud.get("launches", {}).values())
            if total_pt > 0 or total_l > 0:
                ranked.append((uid, total_pt, total_l))
        ranked.sort(key=lambda x: x[1], reverse=True)

        embed = discord.Embed(
            title="PlayTree Leaderboard",
            description="Top players by playtime",
            color=0xFFD700,
        )

        if not ranked:
            embed.add_field(name="No data yet", value="Be the first to play!", inline=False)
        else:
            lines = []
            medals = [":first:", ":second:", ":third:"]
            for i, (uid, pt, launches) in enumerate(ranked[:10]):
                try:
                    user = await self.bot.fetch_user(int(uid))
                    name = user.display_name
                except Exception:
                    name = f"User {uid[:8]}..."
                medal = medals[i] if i < 3 else f"**#{i+1}**"
                h = int(pt // 3600)
                m = int((pt % 3600) // 60)
                time_str = f"{h}h {m}m" if h > 0 else f"{m}m"
                lines.append(f"{medal} **{name}** — {time_str} | {launches} launches")

            embed.description = "\n".join(lines)

        embed.set_footer(text="Playtime updates when you use /stats")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Stats(bot))
