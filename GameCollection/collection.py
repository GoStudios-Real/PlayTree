"""PlayTree Game Collection v4 — Achievements, Themes, Ratings, Music, Leaderboard, Animated BG"""
import pygame
import sys
import os
import subprocess
import math
import random
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from game_utils import controller, sfx, sfx_menu_click, sfx_menu_hover, sfx_collect, sfx_levelup, sfx_powerup
except ImportError:
    try:
        sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW")
        from game_utils import controller, sfx, sfx_menu_click, sfx_menu_hover, sfx_collect, sfx_levelup, sfx_powerup
    except ImportError:
        class _F:
            def __getattr__(self, n): return lambda *a, **k: None
        controller = _F(); sfx = _F()
        sfx_menu_click = sfx_menu_hover = sfx_collect = sfx_levelup = sfx_powerup = None

try:
    from bgmusic import music
except ImportError:
    class _M:
        def __getattr__(self, n): return lambda *a, **k: None
    music = _M()

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Game Collection v4 — GoStudios")

BASE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
PARENT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, "collection_data")
os.makedirs(DATA_DIR, exist_ok=True)

GAMES = [
    {"name": "PLAYTREE", "desc": "The original survival shooter. 28 systems, endless waves.", "exe": "PLAYTREE.exe", "color": (126, 211, 33), "dark": (30, 70, 20), "icon": "P", "tags": ["Shooter", "Survival"], "genre": "Shooter", "preview_color": (40, 100, 40)},
    {"name": "PLAYTREE 3D", "desc": "First-person OpenGL. Astro Toilets in 3D space.", "exe": "PlayTree 3D.exe", "color": (80, 180, 255), "dark": (15, 40, 70), "icon": "3D", "tags": ["FPS", "3D"], "genre": "FPS", "preview_color": (20, 50, 90)},
    {"name": "PLAYTREE FOOTBALL", "desc": "EA FC 27 style. FUT, Career, Transfer Market.", "exe": "PlayTree FootBall.exe", "color": (255, 180, 40), "dark": (60, 40, 10), "icon": "FB", "tags": ["Football", "Sports"], "genre": "Sports", "preview_color": (80, 60, 15)},
    {"name": "PLAYTREE PUZZLE", "desc": "Match-3 gem crusher. Chain combos, endless levels.", "exe": "PlayTree Puzzle.exe", "color": (200, 80, 255), "dark": (50, 20, 60), "icon": "PZ", "tags": ["Puzzle", "Match-3"], "genre": "Puzzle", "preview_color": (60, 25, 70)},
    {"name": "PLAYTREE RACING", "desc": "Top-down arcade racer. Drift, nitro boost, traffic.", "exe": "PlayTree Racing.exe", "color": (50, 200, 200), "dark": (15, 50, 50), "icon": "RC", "tags": ["Racing", "Arcade"], "genre": "Racing", "preview_color": (15, 60, 60)},
    {"name": "PLAYTREE DUNGEON", "desc": "Roguelike crawler. 10 floors, loot, level up.", "exe": "PlayTree Dungeon.exe", "color": (200, 120, 60), "dark": (50, 30, 15), "icon": "DG", "tags": ["Roguelike", "RPG"], "genre": "RPG", "preview_color": (55, 35, 18)},
    {"name": "PLAYTREE SPACE", "desc": "Twin-stick space shooter. 4 weapons, waves.", "exe": "PlayTree Space.exe", "color": (60, 120, 255), "dark": (15, 25, 60), "icon": "SP", "tags": ["Space", "Shooter"], "genre": "Shooter", "preview_color": (10, 18, 50)},
    {"name": "PLAYTREE TOWER DEF", "desc": "Strategic TD. 5 tower types, chain attacks.", "exe": "PlayTree Tower Defense.exe", "color": (200, 200, 50), "dark": (50, 50, 15), "icon": "TD", "tags": ["Strategy", "TD"], "genre": "Strategy", "preview_color": (55, 55, 15)},
    {"name": "PLAYTREE UNDERWATER", "desc": "Deep ocean exploration. Survive, collect treasure.", "exe": "PlayTree Underwater.exe", "color": (60, 180, 255), "dark": (10, 30, 60), "icon": "UW", "tags": ["Ocean", "Explore"], "genre": "Adventure", "preview_color": (8, 25, 55)},
]

ACHIEVEMENTS = [
    {"id": "first_launch", "name": "First Steps", "desc": "Launch any game for the first time", "icon": "*", "color": (126, 211, 33), "check": lambda s: sum(s.get("launches", {}).values()) >= 1},
    {"id": "five_games", "name": "Explorer", "desc": "Launch 5 different games", "icon": "E", "color": (80, 180, 255), "check": lambda s: len([k for k, v in s.get("launches", {}).items() if v > 0]) >= 5},
    {"id": "all_games", "name": "Completionist", "desc": "Launch all 9 games", "icon": "C", "color": (255, 220, 50), "check": lambda s: len([k for k, v in s.get("launches", {}).items() if v > 0]) >= 9},
    {"id": "ten_launches", "name": "Regular", "desc": "Launch games 10 times total", "icon": "R", "color": (200, 80, 255), "check": lambda s: sum(s.get("launches", {}).values()) >= 10},
    {"id": "fifty_launches", "name": "Dedicated", "desc": "Launch games 50 times total", "icon": "D", "color": (255, 120, 60), "check": lambda s: sum(s.get("launches", {}).values()) >= 50},
    {"id": "hour_played", "name": "Time Investment", "desc": "Play for 1 hour total", "icon": "T", "color": (60, 200, 120), "check": lambda s: sum(s.get("playtime", {}).values()) >= 3600},
    {"id": "rate_all", "name": "Critic", "desc": "Rate all 9 games", "icon": "CR", "color": (200, 200, 80), "check": lambda s: len(s.get("ratings", {})) >= 9},
    {"id": "fav_three", "name": "Fan Favorite", "desc": "Favorite 3 games", "icon": "F", "color": (255, 100, 100), "check": lambda s: len(s.get("favorites", [])) >= 3},
    {"id": "night_owl", "name": "Night Owl", "desc": "Launch a game after midnight", "icon": "N", "color": (100, 100, 200), "check": lambda s: any(time.localtime(s.get("last_played", {}).get(g, 0)).tm_hour in range(0, 5) for g in s.get("last_played", {}))},
    {"id": "speedrunner", "name": "Speedrunner", "desc": "Launch 3 games within 60 seconds", "icon": "S", "color": (255, 200, 50), "check": lambda s: False},
    {"id": "variety", "name": "Genre Hopper", "desc": "Play games from 5 different genres", "icon": "V", "color": (180, 120, 255), "check": lambda s: len(set(GAMES[i]["genre"] for i, g in enumerate(GAMES) if s.get("launches", {}).get(g["name"], 0) > 0)) >= 5},
    {"id": "marathon", "name": "Marathon", "desc": "Play for 5 hours total", "icon": "M", "color": (255, 150, 50), "check": lambda s: sum(s.get("playtime", {}).values()) >= 18000},
]

THEMES = {
    "dark": {"bg": (10, 10, 14), "card": (25, 25, 32), "header": (10, 10, 14), "text": (200, 200, 200), "accent": (126, 211, 33), "muted": (50, 50, 60)},
    "midnight": {"bg": (8, 8, 25), "card": (18, 18, 40), "header": (8, 8, 25), "text": (180, 190, 220), "accent": (100, 140, 255), "muted": (40, 45, 70)},
    "forest": {"bg": (12, 18, 12), "card": (20, 32, 20), "header": (12, 18, 12), "text": (180, 210, 180), "accent": (80, 180, 80), "muted": (35, 55, 35)},
    "ember": {"bg": (18, 10, 10), "card": (35, 18, 18), "header": (18, 10, 10), "text": (220, 190, 190), "accent": (255, 100, 60), "muted": (55, 30, 30)},
    "cyberpunk": {"bg": (10, 5, 20), "card": (20, 10, 35), "header": (10, 5, 20), "text": (200, 180, 255), "accent": (255, 0, 150), "muted": (60, 30, 80)},
    "retro": {"bg": (20, 18, 12), "card": (35, 30, 20), "header": (20, 18, 12), "text": (220, 200, 140), "accent": (255, 200, 50), "muted": (60, 55, 35)},
    "pastel": {"bg": (25, 22, 28), "card": (40, 35, 45), "header": (25, 22, 28), "text": (220, 200, 230), "accent": (255, 150, 200), "muted": (70, 60, 75)},
    "ice": {"bg": (10, 15, 22), "card": (18, 25, 38), "header": (10, 15, 22), "text": (180, 210, 240), "accent": (100, 220, 255), "muted": (35, 50, 70)},
}

STATS_FILE = os.path.join(DATA_DIR, "stats.json")

def load_stats():
    try:
        with open(STATS_FILE) as f: return json.load(f)
    except: return {"playtime": {}, "launches": {}, "favorites": [], "theme": "dark", "last_played": {}, "ratings": {}, "achievements": [], "notifications": [], "music_enabled": True}

def save_stats(s):
    try:
        with open(STATS_FILE, "w") as f: json.dump(s, f, indent=2)
    except: pass

stats = load_stats()
for key in ["favorites", "theme", "last_played", "playtime", "launches", "ratings", "achievements", "notifications", "music_enabled"]:
    if key not in stats: stats[key] = [] if key in ["favorites", "achievements", "notifications"] else {} if key in ["playtime", "launches", "last_played", "ratings"] else True

current_theme = stats.get("theme", "dark")
if current_theme not in THEMES: current_theme = "dark"
TH = THEMES[current_theme]

COLS = 4
CARD_W, CARD_H = 280, 310
CARD_GAP_X, CARD_GAP_Y = 28, 28
total_grid_w = COLS * CARD_W + (COLS - 1) * CARD_GAP_X
start_x = (WIDTH - total_grid_w) // 2
HEADER_H = 130
CARD_AREA_Y = HEADER_H + 35

try:
    ft = pygame.font.SysFont("Segoe UI Semibold", 38)
    fn = pygame.font.SysFont("Segoe UI Semibold", 20)
    fd = pygame.font.SysFont("Segoe UI", 14)
    ftg = pygame.font.SysFont("Consolas", 11, bold=True)
    fb = pygame.font.SysFont("Segoe UI Semibold", 17)
    fs = pygame.font.SysFont("Segoe UI", 13)
    fv = pygame.font.SysFont("Consolas", 11)
    fi = pygame.font.SysFont("Consolas", 16, bold=True)
    fstar = pygame.font.SysFont("Segoe UI", 16)
except Exception:
    ft = fn = fd = ftg = fb = fs = fv = fi = fstar = pygame.font.Font(None, 20)

hovered_idx = -1
launched = False
launch_name = ""
clock = pygame.time.Clock()
anim_t = 0
scroll_y = 0
scroll_target = 0

search_text = ""
search_active = False
filter_genre = "All"
genres = ["All"] + sorted(set(g["genre"] for g in GAMES))
show_favorites_only = False
show_achievements = False
show_leaderboard = False
show_settings = False
ctrl_cursor = 0
sfx_enabled = stats.get("sfx_enabled", True)
music_enabled = stats.get("music_enabled", True)

new_achievements = []
for ach in ACHIEVEMENTS:
    if ach["id"] not in stats.get("achievements", []) and ach["check"](stats):
        stats.setdefault("achievements", []).append(ach["id"])
        new_achievements.append(ach)
        stats.setdefault("notifications", []).append({"text": f"Achievement: {ach['name']}!", "time": time.time(), "color": ach["color"]})
if new_achievements:
    save_stats(stats)
    if sfx_enabled and sfx_levelup:
        sfx.play("levelup", sfx_levelup)

notifications = stats.get("notifications", [])
active_notifications = [n for n in notifications if time.time() - n["time"] < 5]

# Animated BG particles
bg_particles = []
for _ in range(40):
    bg_particles.append({"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "vx": random.uniform(-0.3, 0.3), "vy": random.uniform(-0.5, 0.1), "size": random.randint(1, 3), "color": random.choice([(40, 80, 40), (30, 60, 80), (60, 40, 80), (80, 60, 40)])})

def find_exe(name):
    for d in [PARENT_DIR, BASE_DIR, os.path.join(PARENT_DIR, "dist")]:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return None

def get_filtered_games():
    filtered = GAMES
    if show_favorites_only:
        filtered = [g for g in filtered if g["name"] in stats.get("favorites", [])]
    if filter_genre != "All":
        filtered = [g for g in filtered if g["genre"] == filter_genre]
    if search_text:
        q = search_text.lower()
        filtered = [g for g in filtered if q in g["name"].lower() or q in g["desc"].lower() or q in " ".join(g["tags"]).lower()]
    return filtered

def card_rect(idx, filtered):
    col = idx % COLS
    row = idx // COLS
    x = start_x + col * (CARD_W + CARD_GAP_X)
    y = CARD_AREA_Y + row * (CARD_H + CARD_GAP_Y) - scroll_y
    return x, y

def draw_stars():
    for sx, sy, brightness in bg_stars:
        c = int(25 + 35 * brightness)
        pygame.draw.circle(screen, (c, c, c), (int(sx), int((sy + anim_t * 6 * brightness) % HEIGHT)), 1)

bg_stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0)) for _ in range(60)]

def draw_bg_particles():
    for p in bg_particles:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        if p["y"] < -5: p["y"] = HEIGHT + 5; p["x"] = random.randint(0, WIDTH)
        if p["x"] < -5: p["x"] = WIDTH + 5
        if p["x"] > WIDTH + 5: p["x"] = -5
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])

def draw_preview(game, x, y):
    pw, ph = 100, 60
    px = x + CARD_W // 2 - pw // 2
    py = y + 18
    ps = pygame.Surface((pw, ph), pygame.SRCALPHA)
    base = game.get("preview_color", (30, 30, 40))
    pygame.draw.rect(ps, base, (0, 0, pw, ph), border_radius=6)
    for i in range(5):
        rx = random.randint(5, pw - 15)
        ry = random.randint(5, ph - 15)
        rw = random.randint(8, 20)
        rh = random.randint(5, 12)
        rc = tuple(min(255, c + random.randint(-20, 40)) for c in game["color"])
        pygame.draw.rect(ps, rc, (rx, ry, rw, rh), border_radius=3)
    for i in range(3):
        sx2 = random.randint(10, pw - 10)
        sy2 = random.randint(10, ph - 10)
        pygame.draw.circle(ps, (*game["color"], 100), (sx2, sy2), random.randint(2, 5))
    pygame.draw.rect(ps, (255, 255, 255, 30), (2, 2, pw - 4, ph // 3), border_radius=4)
    screen.blit(ps, (px, py))

def draw_star_rating(game, x, y, interactive=False):
    rating = stats.get("ratings", {}).get(game["name"], 0)
    star_x = x + 15
    star_y = y
    mx, my = pygame.mouse.get_pos()
    for i in range(5):
        col = (255, 220, 50) if i < rating else (60, 60, 70)
        if interactive and star_x + i * 18 <= mx <= star_x + i * 18 + 16 and star_y <= my <= star_y + 16:
            col = (255, 240, 100)
        st = fstar.render("*", True, col)
        screen.blit(st, (star_x + i * 18, star_y))

def draw_card(game, idx, hover, filtered):
    x, y = card_rect(idx, filtered)
    if y + CARD_H < 0 or y > HEIGHT + 20:
        return
    bob = math.sin(anim_t * 1.5 + idx * 1.2) * 3
    y += bob
    if hovered_idx == idx:
        glow = pygame.Surface((CARD_W + 12, CARD_H + 12), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*game["color"], 35), (0, 0, CARD_W + 12, CARD_H + 12), border_radius=14)
        screen.blit(glow, (x - 6, y - 6))
        y -= 3

    r = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
    pygame.draw.rect(r, (*TH["card"], 240), (0, 0, CARD_W, CARD_H), border_radius=12)
    screen.blit(r, (x, y))

    is_fav = game["name"] in stats.get("favorites", [])
    if is_fav:
        star = fn.render("*", True, (255, 220, 50))
        screen.blit(star, (x + CARD_W - 22, y + 8))

    launches = stats.get("launches", {}).get(game["name"], 0)
    if launches > 0:
        badge = ftg.render(f"{launches}x", True, TH["muted"])
        screen.blit(badge, (x + 8, y + 8))

    draw_preview(game, x, y)

    nm = fn.render(game["name"], True, (230, 230, 230))
    screen.blit(nm, (x + CARD_W // 2 - nm.get_width() // 2, y + 82))

    tag_x = x + 10
    tag_y = y + 108
    for tg in game["tags"][:2]:
        ts = ftg.render(tg, True, game["color"])
        tw = ts.get_width() + 12
        tb = pygame.Surface((tw, 18), pygame.SRCALPHA)
        pygame.draw.rect(tb, (*game["color"], 25), (0, 0, tw, 18), border_radius=5)
        screen.blit(tb, (tag_x, tag_y))
        screen.blit(ts, (tag_x + 6, tag_y + 2))
        tag_x += tw + 5

    words = game["desc"].split()
    lines = []
    line = ""
    for w in words:
        test = line + " " + w if line else w
        if fd.size(test)[0] > CARD_W - 30:
            lines.append(line); line = w
        else: line = test
    if line: lines.append(line)
    dy = y + 135
    for dl in lines[:2]:
        dt = fd.render(dl, True, TH["text"])
        screen.blit(dt, (x + 15, dy)); dy += 17

    draw_star_rating(game, x, y + CARD_H - 78)

    btn_y = y + CARD_H - 50
    btn_w = CARD_W - 30
    btn_h = 38
    btn_x = x + 15
    if hovered_idx == idx:
        pygame.draw.rect(screen, game["color"], (btn_x, btn_y, btn_w, btn_h), border_radius=8)
        bt = fb.render("LAUNCH", True, (10, 10, 10))
    else:
        pygame.draw.rect(screen, game["color"], (btn_x, btn_y, btn_w, btn_h), 2, border_radius=8)
        bt = fb.render("LAUNCH", True, game["color"])
    screen.blit(bt, (btn_x + btn_w // 2 - bt.get_width() // 2, btn_y + btn_h // 2 - bt.get_height() // 2))

def draw_header(filtered):
    pygame.draw.rect(screen, (*TH["header"], 230), (0, 0, WIDTH, HEADER_H))
    title = ft.render("PLAYTREE", True, TH["accent"])
    sub_text = f"{len(filtered)} GAMES"
    if show_favorites_only: sub_text += " | FAVORITES"
    if filter_genre != "All": sub_text += f" | {filter_genre.upper()}"
    if search_text: sub_text += f' | "{search_text}"'
    sub = fs.render(f"GAME COLLECTION v4 — {sub_text}", True, TH["muted"])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 18))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 62))
    pygame.draw.line(screen, TH["muted"], (WIDTH // 2 - 180, 95), (WIDTH // 2 + 180, 95), 1)

    ctrl_txt = fs.render("Controller: " + ("Connected" if controller.connected else "None"), True, (80, 200, 80) if controller.connected else (150, 80, 80))
    screen.blit(ctrl_txt, (20, 12))
    total_launches = sum(stats.get("launches", {}).values())
    total_playtime = sum(stats.get("playtime", {}).values())
    stats_txt = fs.render(f"{total_launches} launches | {int(total_playtime // 60)}m played | {len(stats.get('achievements', []))}/{len(ACHIEVEMENTS)} achievements", True, TH["muted"])
    screen.blit(stats_txt, (20, 30))

    music_label = "MUSIC: ON" if music_enabled else "MUSIC: OFF"
    music_col = (80, 200, 80) if music_enabled else (150, 80, 80)
    screen.blit(fs.render(music_label, True, music_col), (20, 48))

    ver = fv.render("v4.0 | GoStudios | gostudios-real.github.io", True, TH["muted"])
    screen.blit(ver, (WIDTH // 2 - ver.get_width() // 2, HEIGHT - 22))

def draw_toolbar():
    toolbar_y = HEADER_H
    pygame.draw.rect(screen, (*TH["header"], 200), (0, toolbar_y, WIDTH, 30))
    tb_items = []
    sx = 20
    fav_color = TH["accent"] if show_favorites_only else TH["muted"]
    tb_items.append(("fav", "FAVORITES" if show_favorites_only else "FAVORITES", sx, fav_color)); sx += 90

    for i, g in enumerate(genres):
        sel = g == filter_genre
        col = TH["accent"] if sel else TH["muted"]
        tb_items.append((f"genre_{i}", g, sx, col))
        sx += fs.size(g)[0] + 18

    sx = WIDTH - 300
    tb_items.append(("achievements", "ACHIEVEMENTS", sx, TH["accent"] if show_achievements else TH["muted"])); sx += 110
    tb_items.append(("leaderboard", "LEADERBOARD", sx, TH["accent"] if show_leaderboard else TH["muted"])); sx += 120
    tb_items.append(("theme", current_theme.upper(), sx, TH["accent"])); sx += 80
    tb_items.append(("settings", "SETTINGS", sx, TH["muted"]))

    for item_id, label, ix, col in tb_items:
        ts = fs.render(label, True, col)
        screen.blit(ts, (ix, toolbar_y + 8))
    return tb_items

def draw_search_bar():
    search_y = HEADER_H + 32
    search_w = 300
    search_x = WIDTH // 2 - search_w // 2
    sb = pygame.Surface((search_w, 26), pygame.SRCALPHA)
    border_c = TH["accent"] if search_active else TH["muted"]
    pygame.draw.rect(sb, (*TH["card"], 200), (0, 0, search_w, 26), border_radius=6)
    pygame.draw.rect(sb, border_c, (0, 0, search_w, 26), 1, border_radius=6)
    screen.blit(sb, (search_x, search_y))
    placeholder = "Search games... (Tab)" if not search_text else search_text
    st = fs.render(placeholder, True, TH["text"] if search_text else TH["muted"])
    screen.blit(st, (search_x + 10, search_y + 6))
    if search_active and int(anim_t * 2) % 2 == 0:
        cx = search_x + 10 + fs.size(search_text)[0] + 2
        pygame.draw.line(screen, TH["accent"], (cx, search_y + 5), (cx, search_y + 21), 1)

def draw_achievements_panel():
    pw, ph = 700, 500
    px = (WIDTH - pw) // 2
    py = (HEIGHT - ph) // 2
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*TH["card"], 245), (0, 0, pw, ph), border_radius=14)
    pygame.draw.rect(panel, TH["accent"], (0, 0, pw, ph), 2, border_radius=14)
    screen.blit(panel, (px, py))

    st = fn.render("ACHIEVEMENTS", True, TH["accent"])
    screen.blit(st, (px + pw // 2 - st.get_width() // 2, py + 15))

    unlocked = stats.get("achievements", [])
    ut = fs.render(f"{len(unlocked)}/{len(ACHIEVEMENTS)} Unlocked", True, TH["text"])
    screen.blit(ut, (px + pw // 2 - ut.get_width() // 2, py + 45))

    y = py + 75
    for ach in ACHIEVEMENTS:
        is_unlocked = ach["id"] in unlocked
        col = ach["color"] if is_unlocked else TH["muted"]
        icon_bg = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(icon_bg, (*col, 60 if is_unlocked else 20), (0, 0, 32, 32), border_radius=8)
        screen.blit(icon_bg, (px + 20, y))
        ic = fi.render(ach["icon"], True, col)
        screen.blit(ic, (px + 28, y + 6))
        nm = fs.render(ach["name"], True, col)
        screen.blit(nm, (px + 65, y + 2))
        ds = fv.render(ach["desc"], True, TH["muted"] if is_unlocked else (60, 60, 60))
        screen.blit(ds, (px + 65, y + 18))
        if is_unlocked:
            check = fs.render("DONE", True, (80, 200, 80))
            screen.blit(check, (px + pw - 60, y + 8))
        y += 38

    close = fs.render("[ESC to close]", True, TH["muted"])
    screen.blit(close, (px + pw // 2 - close.get_width() // 2, py + ph - 25))

def draw_leaderboard():
    pw, ph = 500, 450
    px = (WIDTH - pw) // 2
    py = (HEIGHT - ph) // 2
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*TH["card"], 245), (0, 0, pw, ph), border_radius=14)
    pygame.draw.rect(panel, TH["accent"], (0, 0, pw, ph), 2, border_radius=14)
    screen.blit(panel, (px, py))

    st = fn.render("PLAYTIME LEADERBOARD", True, TH["accent"])
    screen.blit(st, (px + pw // 2 - st.get_width() // 2, py + 15))

    sorted_games = sorted(GAMES, key=lambda g: stats.get("playtime", {}).get(g["name"], 0), reverse=True)
    y = py + 55
    for i, game in enumerate(sorted_games[:9]):
        pt = stats.get("playtime", {}).get(game["name"], 0)
        launches = stats.get("launches", {}).get(game["name"], 0)
        mins = int(pt // 60)
        rank = f"#{i + 1}"
        rt = fi.render(rank, True, game["color"])
        screen.blit(rt, (px + 20, y))
        nm = fs.render(game["name"], True, TH["text"])
        screen.blit(nm, (px + 60, y))
        pt_txt = fs.render(f"{mins}m | {launches}x", True, TH["muted"])
        screen.blit(pt_txt, (px + pw - 120, y))

        bar_w = 200
        bar_max = max(1, max(stats.get("playtime", {}).get(g["name"], 0) for g in GAMES))
        fill = int(bar_w * pt / bar_max) if bar_max > 0 else 0
        pygame.draw.rect(screen, TH["muted"], (px + 60, y + 18, bar_w, 6), border_radius=3)
        pygame.draw.rect(screen, game["color"], (px + 60, y + 18, fill, 6), border_radius=3)
        y += 42

    close = fs.render("[ESC to close]", True, TH["muted"])
    screen.blit(close, (px + pw // 2 - close.get_width() // 2, py + ph - 25))

def draw_settings():
    pw, ph = 500, 350
    px = (WIDTH - pw) // 2
    py = (HEIGHT - ph) // 2
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*TH["card"], 245), (0, 0, pw, ph), border_radius=14)
    pygame.draw.rect(panel, TH["accent"], (0, 0, pw, ph), 2, border_radius=14)
    screen.blit(panel, (px, py))

    st = fn.render("SETTINGS", True, TH["accent"])
    screen.blit(st, (px + pw // 2 - st.get_width() // 2, py + 15))
    y = py + 60
    items = []

    theme_names = list(THEMES.keys())
    for tn in theme_names:
        sel = tn == current_theme
        col = TH["accent"] if sel else TH["text"]
        ts = fs.render(f"Theme: {tn.upper()}", True, col)
        screen.blit(ts, (px + 30, y))
        items.append(("theme", tn, px + 30, y, ts.get_width(), 20))
        y += 25

    sfx_label = f"SFX: {'ON' if sfx_enabled else 'OFF'}"
    sfx_col = (80, 200, 80) if sfx_enabled else (200, 80, 80)
    sfx_ts = fs.render(sfx_label, True, sfx_col)
    screen.blit(sfx_ts, (px + 30, y))
    items.append(("sfx", "toggle", px + 30, y, sfx_ts.get_width(), 20))
    y += 28

    mus_label = f"MUSIC: {'ON' if music_enabled else 'OFF'}"
    mus_col = (80, 200, 80) if music_enabled else (200, 80, 80)
    mus_ts = fs.render(mus_label, True, mus_col)
    screen.blit(mus_ts, (px + 30, y))
    items.append(("music", "toggle", px + 30, y, mus_ts.get_width(), 20))

    close = fs.render("[ESC to close]", True, TH["muted"])
    screen.blit(close, (px + pw // 2 - close.get_width() // 2, py + ph - 25))
    return items

def draw_notifications():
    ny = HEIGHT - 60
    for i, notif in enumerate(active_notifications[:3]):
        age = time.time() - notif["time"]
        alpha = max(0, 255 - int(age * 60))
        ns = pygame.Surface((400, 30), pygame.SRCALPHA)
        pygame.draw.rect(ns, (*TH["card"], min(220, alpha)), (0, 0, 400, 30), border_radius=8)
        pygame.draw.rect(ns, (*notif.get("color", TH["accent"]), min(200, alpha)), (0, 0, 400, 30), 1, border_radius=8)
        nt = fs.render(notif["text"], True, (*notif.get("color", TH["accent"]),))
        ns.blit(nt, (10, 7))
        screen.blit(ns, (WIDTH - 420, ny - i * 38))

def draw_launch_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    box_w, box_h = 380, 140
    bx = (WIDTH - box_w) // 2
    by = (HEIGHT - box_h) // 2
    r = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    pygame.draw.rect(r, (*TH["card"], 250), (0, 0, box_w, box_h), border_radius=14)
    screen.blit(r, (bx, by))
    st = fn.render(f"Launching {launch_name}...", True, TH["accent"])
    screen.blit(st, (WIDTH // 2 - st.get_width() // 2, by + 30))
    ht = fs.render("Close game window to return", True, TH["muted"])
    screen.blit(ht, (WIDTH // 2 - ht.get_width() // 2, by + 65))
    bw = 180
    bx2 = (WIDTH - bw) // 2
    by2 = by + 100
    pygame.draw.rect(screen, TH["muted"], (bx2, by2, bw, 5), border_radius=2)
    prog = (math.sin(anim_t * 4) + 1) / 2
    pygame.draw.rect(screen, TH["accent"], (bx2, by2, int(bw * prog), 5), border_radius=2)

controller.init()
if music_enabled:
    try: music.play("calm")
    except: pass

running = True
while running:
    dt = clock.tick(60) / 1000.0
    anim_t += dt
    hovered_idx = -1
    mx, my = pygame.mouse.get_pos()
    controller.update()
    scroll_y += (scroll_target - scroll_y) * 0.15
    filtered = get_filtered_games()

    active_notifications = [n for n in stats.get("notifications", []) if time.time() - n["time"] < 5]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_settings: show_settings = False
                elif show_achievements: show_achievements = False
                elif show_leaderboard: show_leaderboard = False
                elif search_active: search_active = False; search_text = ""
                elif launched: launched = False
                else: running = False
            elif event.key == pygame.K_TAB and not show_settings and not show_achievements and not show_leaderboard:
                search_active = not search_active
            elif event.key == pygame.K_f and not show_settings and not show_achievements and not show_leaderboard and not search_active:
                show_favorites_only = not show_favorites_only; scroll_target = 0
            elif event.key == pygame.K_a and not show_settings and not search_active:
                show_achievements = not show_achievements
            elif event.key == pygame.K_l and not show_settings and not search_active:
                show_leaderboard = not show_leaderboard
            elif event.key == pygame.K_m and not show_settings and not search_active:
                music_enabled = not music_enabled
                stats["music_enabled"] = music_enabled
                save_stats(stats)
                if music_enabled: music.play("calm")
                else: music.stop()
            elif search_active:
                if event.key == pygame.K_BACKSPACE: search_text = search_text[:-1]
                elif event.key == pygame.K_RETURN: search_active = False
                elif len(search_text) < 30 and event.unicode.isprintable():
                    search_text += event.unicode
                    if sfx_enabled and sfx_menu_hover: sfx.play("hover", sfx_menu_hover)
        elif event.type == pygame.MOUSEWHEEL:
            if not show_settings and not show_achievements and not show_leaderboard:
                scroll_target -= event.y * 40
                total_h = math.ceil(len(filtered) / COLS) * (CARD_H + CARD_GAP_Y)
                max_scroll = max(0, total_h - (HEIGHT - CARD_AREA_Y - 30))
                scroll_target = max(0, min(max_scroll, scroll_target))
        elif event.type == pygame.MOUSEBUTTONDOWN and not launched:
            if show_settings:
                settings_items = draw_settings()
                clicked = False
                for item_id, val, ix, iy, iw, ih in settings_items:
                    if ix <= mx <= ix + iw and iy <= my <= iy + ih:
                        if item_id == "theme":
                            current_theme = val; TH = THEMES[current_theme]
                            stats["theme"] = current_theme; save_stats(stats)
                            if sfx_enabled and sfx_collect: sfx.play("collect", sfx_collect)
                        elif item_id == "sfx":
                            sfx_enabled = not sfx_enabled; stats["sfx_enabled"] = sfx_enabled; save_stats(stats)
                        elif item_id == "music":
                            music_enabled = not music_enabled; stats["music_enabled"] = music_enabled; save_stats(stats)
                            if music_enabled: music.play("calm")
                            else: music.stop()
                        clicked = True
                if not clicked and not (WIDTH // 2 - 250 <= mx <= WIDTH // 2 + 250 and HEIGHT // 2 - 175 <= my <= HEIGHT // 2 + 175):
                    show_settings = False
            elif not show_achievements and not show_leaderboard:
                toolbar_items = draw_toolbar()
                for item_id, label, ix, iy_pos in toolbar_items:
                    ts = fs.render(label, True, (0, 0, 0))
                    tw = ts.get_width()
                    if ix <= mx <= ix + tw and HEADER_H <= my <= HEADER_H + 28:
                        if item_id == "fav":
                            show_favorites_only = not show_favorites_only; scroll_target = 0
                            if sfx_enabled and sfx_menu_click: sfx.play("click", sfx_menu_click)
                        elif item_id.startswith("genre_"):
                            gi = int(item_id.split("_")[1]); filter_genre = genres[gi]; scroll_target = 0
                            if sfx_enabled and sfx_menu_click: sfx.play("click", sfx_menu_click)
                        elif item_id == "theme":
                            theme_names = list(THEMES.keys()); ci = theme_names.index(current_theme)
                            current_theme = theme_names[(ci + 1) % len(theme_names)]; TH = THEMES[current_theme]
                            stats["theme"] = current_theme; save_stats(stats)
                            if sfx_enabled and sfx_menu_click: sfx.play("click", sfx_menu_click)
                        elif item_id == "settings": show_settings = not show_settings
                        elif item_id == "achievements": show_achievements = not show_achievements
                        elif item_id == "leaderboard": show_leaderboard = not show_leaderboard
                        break
                else:
                    if not search_active or not (WIDTH // 2 - 150 <= mx <= WIDTH // 2 + 150 and HEADER_H + 32 <= my <= HEADER_H + 58):
                        for i, game in enumerate(filtered):
                            cx, cy = card_rect(i, filtered)
                            bob = math.sin(anim_t * 1.5 + i * 1.2) * 3
                            if cx <= mx <= cx + CARD_W and (cy + bob) <= my <= (cy + bob) + CARD_H:
                                star_area_y = (cy + bob) + CARD_H - 82
                                btn_area_y = (cy + bob) + CARD_H - 55
                                if star_area_y <= my <= star_area_y + 18:
                                    star_idx = (mx - cx - 15) // 18
                                    if 0 <= star_idx < 5:
                                        current = stats.get("ratings", {}).get(game["name"], 0)
                                        new_val = int(star_idx) + 1
                                        if current == new_val: new_val = 0
                                        stats.setdefault("ratings", {})[game["name"]] = new_val
                                        save_stats(stats)
                                        if sfx_enabled and sfx_collect: sfx.play("collect", sfx_collect)
                                elif btn_area_y <= my <= btn_area_y + 38:
                                    exe_path = find_exe(game["exe"])
                                    if exe_path:
                                        launched = True; launch_name = game["name"]
                                        stats.setdefault("launches", {})[game["name"]] = stats.get("launches", {}).get(game["name"], 0) + 1
                                        stats.setdefault("last_played", {})[game["name"]] = time.time()
                                        start_t = stats.setdefault("_launch_times", [])
                                        start_t.append(time.time())
                                        stats["_launch_times"] = [t for t in start_t if time.time() - t < 60]
                                        if len(stats["_launch_times"]) >= 3:
                                            if "speedrunner" not in stats.get("achievements", []):
                                                stats.setdefault("achievements", []).append("speedrunner")
                                                stats.setdefault("notifications", []).append({"text": "Achievement: Speedrunner!", "time": time.time(), "color": (255, 200, 50)})
                                        save_stats(stats)
                                        for ach in ACHIEVEMENTS:
                                            if ach["id"] not in stats.get("achievements", []) and ach["check"](stats):
                                                stats.setdefault("achievements", []).append(ach["id"])
                                                stats.setdefault("notifications", []).append({"text": f"Achievement: {ach['name']}!", "time": time.time(), "color": ach["color"]})
                                                if sfx_enabled and sfx_levelup: sfx.play("levelup", sfx_levelup)
                                        save_stats(stats)
                                        try: subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
                                        except: launched = False
                                        if sfx_enabled and sfx_collect: sfx.play("collect", sfx_collect)
                                else:
                                    name = game["name"]
                                    favs = stats.setdefault("favorites", [])
                                    if name in favs: favs.remove(name)
                                    else: favs.append(name)
                                    save_stats(stats)
                                    if sfx_enabled and sfx_menu_click: sfx.play("click", sfx_menu_click)
                                break

    for i in range(len(filtered)):
        cx, cy = card_rect(i, filtered)
        bob = math.sin(anim_t * 1.5 + i * 1.2) * 3
        if cx <= mx <= cx + CARD_W and (cy + bob) <= my <= (cy + bob) + CARD_H:
            if cy + bob >= CARD_AREA_Y: hovered_idx = i

    if controller.connected and not launched and not show_settings and not show_achievements and not show_leaderboard:
        if controller.just_pressed("btn_start"): running = False
        if controller.just_pressed("btn_x"): search_active = not search_active
        if controller.just_pressed("btn_y"): show_favorites_only = not show_favorites_only; scroll_target = 0
        if controller.just_pressed("btn_lb"): show_achievements = not show_achievements
        if controller.just_pressed("btn_rb"): show_leaderboard = not show_leaderboard
        stick_y = controller.get_axis("move_y")
        if abs(stick_y) > 0.3:
            scroll_target += stick_y * 5
            total_h = math.ceil(len(filtered) / COLS) * (CARD_H + CARD_GAP_Y)
            max_scroll = max(0, total_h - (HEIGHT - CARD_AREA_Y - 30))
            scroll_target = max(0, min(max_scroll, scroll_target))
        if controller.just_pressed("btn_a") and filtered:
            game = filtered[min(ctrl_cursor, len(filtered) - 1)]
            exe_path = find_exe(game["exe"])
            if exe_path:
                launched = True; launch_name = game["name"]
                stats.setdefault("launches", {})[game["name"]] = stats.get("launches", {}).get(game["name"], 0) + 1
                stats.setdefault("last_played", {})[game["name"]] = time.time()
                save_stats(stats)
                try: subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
                except: launched = False
                if sfx_enabled and sfx_collect: sfx.play("collect", sfx_collect)
        if controller.just_pressed("btn_b") and filtered:
            game = filtered[min(ctrl_cursor, len(filtered) - 1)]
            favs = stats.setdefault("favorites", [])
            if game["name"] in favs: favs.remove(game["name"])
            else: favs.append(game["name"])
            save_stats(stats)
            if sfx_enabled and sfx_menu_click: sfx.play("click", sfx_menu_click)

    screen.fill(TH["bg"])
    draw_stars()
    draw_bg_particles()
    draw_search_bar()

    for i, game in enumerate(filtered):
        draw_card(game, i, i == hovered_idx, filtered)

    draw_header(filtered)
    draw_toolbar()
    draw_notifications()

    if not filtered and not show_settings and not show_achievements and not show_leaderboard:
        no_games = fn.render("No games found", True, TH["muted"])
        screen.blit(no_games, (WIDTH // 2 - no_games.get_width() // 2, HEIGHT // 2))

    if show_achievements: draw_achievements_panel()
    if show_leaderboard: draw_leaderboard()
    if show_settings: draw_settings()
    if launched: draw_launch_overlay()

    pygame.display.flip()

save_stats(stats)
music.stop()
pygame.quit()
