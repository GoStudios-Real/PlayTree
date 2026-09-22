"""Generate Store screenshots — Part 3 (6 screenshots 1920x1080)"""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

random.seed(42)
SHOT_DIR = r"C:\Users\RhysC\Downloads\NEW\PlayTreeXboxStore\StoreAssets\Screenshots"
os.makedirs(SHOT_DIR, exist_ok=True)

def try_font(size):
    for name in ["arialbd.ttf", "arial.ttf", "consolab.ttf", "segoeuib.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def base_scene(title, subtitle):
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (8, 35, 60, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    return img, draw, w, h

def add_bars(draw, w, h, title, subtitle):
    draw.rectangle([0, 0, w, 70], fill=(0, 0, 0, 200))
    f = try_font(34)
    draw.text((30, 16), title, fill=(126, 211, 33, 255), font=f)
    f2 = try_font(22)
    bw = draw.textbbox((0, 0), subtitle, font=f2)[2]
    draw.text((w - 30 - bw, 24), subtitle, fill=(140, 170, 140, 255), font=f2)
    draw.rectangle([0, h - 50, w, h], fill=(0, 0, 0, 180))
    f3 = try_font(20)
    draw.text((30, h - 40), "PLAYTREE \u2014 GoConsole Game Studios", fill=(100, 140, 100, 255), font=f3)
    draw.rounded_rectangle([w - 160, h - 40, w - 30, h - 12], radius=6, fill=(107, 158, 10, 255))
    draw.text((w - 135, h - 38), "XBOX", fill=(255, 255, 255, 255), font=f3)

def save(img, name):
    img.convert("RGB").save(os.path.join(SHOT_DIR, name), quality=95)
    print(name)

# ---- 1: MAIN MENU ----
img, draw, w, h = base_scene("", "")
for y in range(70, h):
    k = (y - 70) / (h - 70)
    draw.line([(0, y), (w, y)], fill=(int(110 + k * 30), int(190 + k * 20), 255, 255))
draw.rectangle([0, h - 250, w, h], fill=(75, 150, 55, 255))
draw.rectangle([0, h - 250, w, h - 238], fill=(95, 180, 65, 255))
for i in range(9):
    tx = 60 + i * 210
    draw.rectangle([tx, h - 340, tx + 22, h - 250], fill=(95, 65, 22, 255))
    draw.rectangle([tx - 32, h - 385, tx + 54, h - 320], fill=(35, 110, 35, 255))
    draw.rectangle([tx - 22, h - 375, tx + 44, h - 355], fill=(45, 130, 45, 255))
f = try_font(46)
for i, b in enumerate(["Play", "Settings", "Marketplace"]):
    by = 370 + i * 85
    col = (126, 211, 33, 255) if i == 0 else (205, 205, 205, 255)
    draw.rounded_rectangle([w // 2 - 220, by, w // 2 + 220, by + 65], radius=10, fill=col)
    bbox = draw.textbbox((0, 0), b, font=f)
    draw.text((w // 2 - (bbox[2] - bbox[0]) // 2, by + 10), b, fill=(30, 30, 30, 255), font=f)
f2 = try_font(90)
bbox = draw.textbbox((0, 0), "PLAYTREE", font=f2)
tw = bbox[2] - bbox[0]
draw.text((w // 2 - tw // 2 + 4, 164), "PLAYTREE", fill=(0, 0, 0, 200), font=f2)
draw.text((w // 2 - tw // 2, 160), "PLAYTREE", fill=(210, 210, 210, 255), font=f2)
f3 = try_font(32)
draw.text((w // 2 + 300, 230), "Beta!!!", fill=(255, 255, 0, 255), font=f3)
add_bars(draw, w, h, "Main Menu", "Minecraft Beta Style")
save(img, "01_MainMenu.png")

# ---- 2: COMBAT ----
img, draw, w, h = base_scene("", "")
draw.rectangle([0, 70, w, h - 100], fill=(20, 45, 25, 255))
draw.rectangle([0, h - 200, w, h - 50], fill=(40, 85, 40, 255))
for i in range(12):
    tx = random.randint(0, w)
    draw.rectangle([tx, h - 280, tx + 14, h - 200], fill=(70, 50, 25, 255))
    draw.ellipse([tx - 20, h - 320, tx + 34, h - 270], fill=(30, 90, 30, 255))
px, py = 480, h // 2
draw.ellipse([px - 28, py - 28, px + 28, py + 28], fill=(100, 200, 255, 255))
draw.rectangle([px - 16, py + 28, px + 16, py + 75], fill=(60, 180, 180, 255))
for a in range(-40, 70, 4):
    r = 90
    x2 = px + int(r * math.cos(math.radians(a)))
    y2 = py + int(r * math.sin(math.radians(a)))
    draw.line([(px, py), (x2, y2)], fill=(255, 255, 200, 180), width=3)
for i in range(7):
    ex = px + 200 + i * 130
    ey = h // 2 + (i % 3) * 60 - 40
    draw.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], fill=(200, 60, 60, 255))
    draw.rectangle([ex - 28, ey - 40, ex + 28, ey - 32], fill=(60, 0, 0, 255))
    draw.rectangle([ex - 28, ey - 40, ex - 28 + int(56 * (1 - i * 0.12)), ey - 32], fill=(255, 50, 50, 255))
bx, by = w * 3 // 4, h // 3
draw.ellipse([bx - 65, by - 65, bx + 65, by + 65], fill=(180, 180, 200, 255))
draw.ellipse([bx - 42, by - 42, bx + 42, by + 12], fill=(220, 220, 240, 255))
draw.ellipse([bx - 28, by - 28, bx - 6, by - 6], fill=(255, 0, 0, 255))
draw.ellipse([bx + 6, by - 28, bx + 28, by - 6], fill=(255, 0, 0, 255))
f = try_font(40)
for i in range(5):
    draw.text((px + 160 + i * 90, py - 90 - i * 22), str(random.randint(50, 250)),
              fill=(255, 220, 50, 255), font=f)
f2 = try_font(54)
draw.text((50, 110), "COMBO x12!", fill=(255, 100, 50, 255), font=f2)
draw.rectangle([20, 90, 320, 155], fill=(0, 0, 0, 150))
draw.rectangle([30, 100, 300, 122], fill=(60, 0, 0, 255))
draw.rectangle([30, 100, 240, 122], fill=(255, 50, 50, 255))
draw.rectangle([30, 130, 300, 144], fill=(0, 0, 60, 255))
draw.rectangle([30, 130, 210, 144], fill=(50, 100, 255, 255))
add_bars(draw, w, h, "Combat \u2014 6 Classes, 12 Weapons", "Astro Toilet Boss Fight")
save(img, "02_Combat.png")

# ---- 3: OPEN WORLD ----
img, draw, w, h = base_scene("", "")
for y in range(70, h):
    k = (y - 70) / (h - 70)
    if k < 0.35:
        draw.line([(0, y), (w, y)], fill=(int(60 + k * 100), int(120 + k * 100), 255, 255))
    elif k < 0.55:
        draw.line([(0, y), (w, y)], fill=(140, 200, 220, 255))
    elif k < 0.65:
        draw.line([(0, y), (w, y)], fill=(60, 140, 60, 255))
    else:
        draw.line([(0, y), (w, y)], fill=(int(50 + (k - 0.65) * 40), int(120 - (k - 0.65) * 30), 50, 255))
# Mountains
for i in range(6):
    mx = i * 350 - 50
    mh = random.randint(150, 300)
    pts = [(mx, 650), (mx + 175, 650 - mh), (mx + 350, 650)]
    draw.polygon(pts, fill=(80, 100, 130, 255))
    draw.polygon([(mx + 100, 650), (mx + 175, 650 - mh + 40), (mx + 250, 650)], fill=(100, 120, 150, 255))
# Trees
for i in range(20):
    tx = random.randint(0, w)
    ty = random.randint(700, h - 100)
    draw.rectangle([tx - 6, ty - 40, tx + 6, ty], fill=(95, 65, 22, 255))
    draw.ellipse([tx - 25, ty - 75, tx + 25, ty - 30], fill=(35, 110, 35, 255))
# Water
draw.rectangle([0, h - 120, w, h - 60], fill=(45, 110, 185, 255))
for i in range(30):
    wx = i * 65 + random.randint(0, 20)
    draw.line([(wx, h - 95), (wx + 20, h - 95)], fill=(65, 150, 225, 255), width=2)
# Player
draw.ellipse([w // 2 - 14, h - 200, w // 2 + 14, h - 172], fill=(100, 200, 255, 255))
draw.rectangle([w // 2 - 10, h - 172, w // 2 + 10, h - 145], fill=(60, 180, 180, 255))
# Minimap
draw.rectangle([w - 220, 90, w - 30, 280], fill=(0, 0, 0, 160))
draw.rectangle([w - 218, 92, w - 32, 278], outline=(126, 211, 33, 255), width=2)
draw.ellipse([w - 130, 175, w - 118, 187], fill=(255, 50, 50, 255))
f = try_font(20)
draw.text((w - 210, 100), "9000x9000 WORLD", fill=(126, 211, 33, 255), font=f)
add_bars(draw, w, h, "Open World \u2014 16 Regions", "Day/Night Cycle & Weather")
save(img, "03_OpenWorld.png")

# ---- 4: BASE BUILDING ----
img, draw, w, h = base_scene("", "")
for y in range(70, h):
    k = (y - 70) / (h - 70)
    draw.line([(0, y), (w, y)], fill=(int(70 + k * 40), int(140 + k * 20), 60, 255))
# Houses
for i in range(4):
    hx = 150 + i * 400
    hy = h - 350
    draw.rectangle([hx, hy, hx + 250, hy + 200], fill=(150, 120, 80, 255))
    draw.polygon([(hx - 20, hy), (hx + 125, hy - 100), (hx + 270, hy)], fill=(160, 50, 50, 255))
    draw.rectangle([hx + 90, hy + 100, hx + 160, hy + 200], fill=(90, 60, 30, 255))
    draw.rectangle([hx + 30, hy + 40, hx + 80, hy + 90], fill=(100, 180, 255, 255))
    draw.rectangle([hx + 170, hy + 40, hx + 220, hy + 90], fill=(100, 180, 255, 255))
# Fence
for i in range(40):
    fx = i * 50
    draw.rectangle([fx, h - 140, fx + 8, h - 100], fill=(130, 100, 60, 255))
draw.rectangle([0, h - 125, w, h - 115], fill=(130, 100, 60, 255))
# Build UI
draw.rectangle([50, 100, 450, 380], fill=(0, 0, 0, 180))
draw.rectangle([52, 102, 448, 378], outline=(126, 211, 33, 255), width=2)
f = try_font(28)
draw.text((70, 115), "BUILD MENU", fill=(126, 211, 33, 255), font=f)
f2 = try_font(20)
items = ["Wooden Wall", "Stone Floor", "Roof", "Door", "Window", "Turret", "Workbench", "Chest"]
for j, item in enumerate(items):
    iy = 160 + j * 26
    col = (126, 211, 33, 255) if j == 0 else (180, 180, 180, 255)
    draw.text((80, iy), f"  {item}", fill=col, font=f2)
    if j == 0:
        draw.rectangle([70, iy - 3, 430, iy + 22], outline=(126, 211, 33, 255), width=1)
add_bars(draw, w, h, "Base Building", "Place Walls, Roofs, Turrets & More")
save(img, "04_BaseBuilding.png")

# ---- 5: MULTIPLAYER LOBBY ----
img, draw, w, h = base_scene("", "")
draw.rectangle([0, 70, w, h - 50], fill=(15, 20, 40, 255))
# Player cards
players = [
    ("Rhys", "Guardian", (100, 200, 255), "LVL 42"),
    ("Willow", "Mage", (200, 100, 255), "LVL 38"),
    ("Doggo", "Beast Tamer", (255, 215, 0), "LVL 99"),
    ("Bot_Astro", "Ranger", (100, 255, 100), "LVL 27"),
    ("GemCrusher", "Mechanic", (255, 150, 50), "LVL 31"),
    ("xX_NoScope", "Ranger", (50, 200, 200), "LVL 19"),
]
for i, (name, cls, col, lvl) in enumerate(players):
    row, c = divmod(i, 3)
    cx = 200 + c * 540
    cy = 180 + row * 340
    draw.rounded_rectangle([cx - 200, cy - 80, cx + 200, cy + 120], radius=16,
                           fill=(25, 30, 50, 255), outline=(*col, 255), width=3)
    # Avatar
    draw.ellipse([cx - 40, cy - 50, cx + 40, cy + 30], fill=(*col, 255))
    draw.rectangle([cx - 30, cy + 30, cx + 30, cy + 80], fill=(*col, 180))
    f = try_font(30)
    draw.text((cx - draw.textbbox((0, 0), name, font=f)[2] // 2, cy + 88), name,
              fill=(*col, 255), font=f)
    f2 = try_font(20)
    draw.text((cx - draw.textbbox((0, 0), cls, font=f2)[2] // 2, cy + 122), cls,
              fill=(160, 160, 160, 255), font=f2)
    # Level badge
    draw.rounded_rectangle([cx + 80, cy - 75, cx + 190, cy - 40], radius=8, fill=(*col, 255))
    f3 = try_font(22)
    draw.text((cx + 95, cy - 70), lvl, fill=(0, 0, 0, 255), font=f3)
# Ready check
f4 = try_font(36)
draw.text((w // 2 - 150, h - 120), "5/6 READY \u2014 Waiting...", fill=(126, 211, 33, 255), font=f4)
add_bars(draw, w, h, "Multiplayer Lobby", "GoConsoleOS Cross-Play")
save(img, "05_Multiplayer.png")

# ---- 6: BATTLE PASS / PROGRESSION ----
img, draw, w, h = base_scene("", "")
draw.rectangle([0, 70, w, h - 50], fill=(20, 15, 35, 255))
# Battle pass track
f = try_font(44)
draw.text((w // 2 - draw.textbbox((0, 0), "BATTLE PASS \u2014 SEASON 1", font=f)[2] // 2, 100),
          "BATTLE PASS \u2014 SEASON 1", fill=(255, 215, 0, 255), font=f)
for i in range(10):
    tx = 80 + i * 180
    ty = 250
    unlocked = i < 6
    col = (126, 211, 33, 255) if unlocked else (80, 80, 80, 255)
    draw.rounded_rectangle([tx, ty, tx + 150, ty + 150], radius=12,
                           fill=(30, 30, 50, 255), outline=col, width=3)
    # Tier number
    f2 = try_font(48)
    draw.text((tx + 50, ty + 40), str(i + 1), fill=col, font=f2)
    # Reward icon
    f3 = try_font(16)
    rewards = ["Skin", "Coins", "Emote", "Weapon", "Pet", "Crown", "Trail", "Banner", "Chest", "Mythic"]
    draw.text((tx + 35, ty + 110), rewards[i], fill=(200, 200, 200, 255) if unlocked else (100, 100, 100, 255), font=f3)
    if unlocked:
        draw.text((tx + 55, ty + 15), "OK", fill=(126, 211, 33, 255), font=try_font(18))
# XP bar
draw.rectangle([100, 480, w - 100, 520], fill=(40, 40, 60, 255))
draw.rectangle([100, 480, 100 + int((w - 200) * 0.62), 520], fill=(126, 211, 33, 255))
f4 = try_font(26)
draw.text((w // 2 - 80, 487), "6200 / 10000 XP", fill=(255, 255, 255, 255), font=f4)
# Stats
stats = [("Level", "42"), ("Wins", "128"), ("Kills", "3,417"), ("Playtime", "89h")]
f5 = try_font(24)
for i, (label, val) in enumerate(stats):
    sx = 180 + i * 400
    draw.rounded_rectangle([sx - 80, 570, sx + 80, 670], radius=12, fill=(30, 30, 50, 255),
                           outline=(126, 211, 33, 255), width=2)
    f6 = try_font(36)
    draw.text((sx - draw.textbbox((0, 0), val, font=f6)[2] // 2, 585), val,
              fill=(255, 215, 0, 255), font=f6)
    draw.text((sx - draw.textbbox((0, 0), label, font=f5)[2] // 2, 635), label,
              fill=(160, 160, 160, 255), font=f5)
# Achievements
f7 = try_font(28)
draw.text((100, 730), "RECENT ACHIEVEMENTS", fill=(126, 211, 33, 255), font=f7)
achs = ["First Steps", "Explorer", "Completionist", "Night Owl", "Marathon"]
f8 = try_font(20)
for i, a in enumerate(achs):
    ax = 100 + i * 340
    draw.rounded_rectangle([ax, 780, ax + 310, 830], radius=8, fill=(30, 30, 50, 255),
                           outline=(255, 215, 0, 255), width=1)
    draw.text((ax + 15, 793), a, fill=(255, 215, 0, 255), font=f8)
add_bars(draw, w, h, "Battle Pass & Progression", "Season 1 \u2014 100 Tiers")
save(img, "06_BattlePass.png")

print("Part 3 done — 6 screenshots")
