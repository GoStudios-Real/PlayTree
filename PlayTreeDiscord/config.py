"""PlayTree Discord Bot — Configuration"""
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN", "")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
COLLECTION_DATA = r"C:\Users\RhysC\Downloads\NEW\GameCollection\collection_data"
STATS_FILE = os.path.join(COLLECTION_DATA, "stats.json")

# Rich Presence / Activity
DISCORD_APP_ID = "1548510077055537184"
WEBSITE_URL = "https://gostudios-real.github.io/GoStudios-Real-playtree.github.io/"
GITHUB_URL = "https://github.com/GoStudios-Real/PlayTree"
ITCH_URL = "https://playtree-corporation.itch.io/playtree"

GAMES = [
    {"name": "PLAYTREE", "exe": "PLAYTREE.exe", "color": 0x7ED321, "icon": "P", "genre": "Shooter", "desc": "Original survival shooter. 28 systems, endless waves."},
    {"name": "PLAYTREE 3D", "exe": "PlayTree 3D.exe", "color": 0x50B4FF, "icon": "3D", "genre": "FPS", "desc": "First-person OpenGL. Astro Toilets in 3D space."},
    {"name": "PLAYTREE FOOTBALL", "exe": "PlayTree FootBall.exe", "color": 0xFFB428, "icon": "FB", "genre": "Sports", "desc": "EA FC 27 style. FUT, Career, Transfer Market."},
    {"name": "PLAYTREE PUZZLE", "exe": "PlayTree Puzzle.exe", "color": 0xC850FF, "icon": "PZ", "genre": "Puzzle", "desc": "Match-3 gem crusher. Chain combos, endless levels."},
    {"name": "PLAYTREE RACING", "exe": "PlayTree Racing.exe", "color": 0x32C8C8, "icon": "RC", "genre": "Racing", "desc": "Top-down arcade racer. Drift, nitro boost, traffic."},
    {"name": "PLAYTREE DUNGEON", "exe": "PlayTree Dungeon.exe", "color": 0xC8783C, "icon": "DG", "genre": "RPG", "desc": "Roguelike crawler. 10 floors, loot, level up."},
    {"name": "PLAYTREE SPACE", "exe": "PlayTree Space.exe", "color": 0x3C78FF, "icon": "SP", "genre": "Shooter", "desc": "Twin-stick space shooter. 4 weapons, waves."},
    {"name": "PLAYTREE TOWER DEF", "exe": "PlayTree Tower Defense.exe", "color": 0xC8C832, "icon": "TD", "genre": "Strategy", "desc": "Strategic TD. 5 tower types, chain attacks."},
    {"name": "PLAYTREE UNDERWATER", "exe": "PlayTree Underwater.exe", "color": 0x3CB4FF, "icon": "UW", "genre": "Adventure", "desc": "Deep ocean exploration. Survive, collect treasure."},
]

ACHIEVEMENTS = [
    {"id": "first_launch", "name": "First Steps", "desc": "Launch any game", "icon": "*"},
    {"id": "five_games", "name": "Explorer", "desc": "Launch 5 different games", "icon": "E"},
    {"id": "all_games", "name": "Completionist", "desc": "Launch all 9 games", "icon": "C"},
    {"id": "ten_launches", "name": "Regular", "desc": "10 total launches", "icon": "R"},
    {"id": "fifty_launches", "name": "Dedicated", "desc": "50 total launches", "icon": "D"},
    {"id": "hour_played", "name": "Time Investment", "desc": "Play 1 hour total", "icon": "T"},
    {"id": "rate_all", "name": "Critic", "desc": "Rate all 9 games", "icon": "CR"},
    {"id": "fav_three", "name": "Fan Favorite", "desc": "Favorite 3 games", "icon": "F"},
    {"id": "night_owl", "name": "Night Owl", "desc": "Launch after midnight", "icon": "N"},
    {"id": "speedrunner", "name": "Speedrunner", "desc": "3 games in 60s", "icon": "S"},
    {"id": "variety", "name": "Genre Hopper", "desc": "5 different genres", "icon": "V"},
    {"id": "marathon", "name": "Marathon", "desc": "Play 5 hours total", "icon": "M"},
]
