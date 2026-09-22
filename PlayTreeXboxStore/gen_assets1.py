"""Generate Microsoft Store / Xbox assets for PLAYTREE — Part 1: core assets"""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

OUT = r"C:\Users\RhysC\Downloads\NEW\PlayTreeXboxStore\Assets"
STORE = r"C:\Users\RhysC\Downloads\NEW\PlayTreeXboxStore\StoreAssets"
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(STORE, "Screenshots"), exist_ok=True)

def try_font(size):
    for name in ["arialbd.ttf", "arial.ttf", "consolab.ttf", "segoeuib.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_logo(img, cx, cy, scale=1.0):
    draw = ImageDraw.Draw(img, "RGBA")
    s = scale
    tw, th = int(16 * s), int(50 * s)
    draw.rounded_rectangle([cx - tw // 2, cy + 10 * s, cx + tw // 2, cy + 10 * s + th],
                           radius=max(1, int(3 * s)), fill=(80, 55, 30, 255))
    for ox, oy, r, col in [
        (0, -15, 45, (55, 160, 65)), (-28, 5, 30, (40, 140, 55)),
        (28, 5, 30, (45, 150, 60)), (0, -38, 35, (48, 170, 70)),
        (-16, -25, 25, (35, 130, 50)), (16, -25, 28, (40, 145, 58)),
    ]:
        draw.ellipse([cx + (ox - r) * s, cy + (oy - r) * s, cx + (ox + r) * s, cy + (oy + r) * s],
                     fill=(*col, 255))
    for i in range(3):
        r = (60 + i * 8) * s
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(126, 211, 33, max(15, 60 - i * 18)),
                     width=max(1, int(2 * s)))

def make_bg(w, h, base=(10, 47, 86)):
    img = Image.new("RGBA", (w, h), (*base, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(h):
        t = y / h
        r = int(base[0] * (1 - t) + 8 * t)
        g = int(base[1] * (1 - t) + 30 * t)
        b = int(base[2] * (1 - t) + 20 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    step = max(30, w // 30)
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=(126, 211, 33, 18), width=1)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=(126, 211, 33, 18), width=1)
    return img, draw

# --- StoreLogo 300x300 ---
img = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
draw = ImageDraw.Draw(img, "RGBA")
draw.rounded_rectangle([0, 0, 299, 299], radius=40, fill=(10, 47, 86, 255))
draw_logo(img, 150, 155, 1.6)
f = try_font(90)
bbox = draw.textbbox((0, 0), "P", font=f)
draw.text((150 - (bbox[2] - bbox[0]) // 2, 175), "P", fill=(126, 211, 33, 255), font=f)
img.save(os.path.join(OUT, "StoreLogo.png"))
print("StoreLogo.png")

# --- Tiles ---
tiles = [
    ("SmallTile.png", 71, 71), ("MediumTile.png", 150, 150),
    ("WideTile.png", 310, 150), ("LargeTile.png", 310, 310),
    ("Square44x44Logo.png", 44, 44), ("Square150x150Logo.png", 150, 150),
    ("Wide310x150Logo.png", 310, 150), ("Square310x310Logo.png", 310, 310),
    ("Square71x71Logo.png", 71, 71),
]
for name, w, h in tiles:
    img, draw = make_bg(w, h, (10, 47, 86))
    draw.rounded_rectangle([2, 2, w - 3, h - 3], radius=max(4, w // 12),
                           outline=(126, 211, 33), width=2)
    s = min(w, h) / 80
    draw_logo(img, w // 2, int(h * 0.42), s)
    f = try_font(max(10, int(min(w, h) * 0.16)))
    bbox = draw.textbbox((0, 0), "PLAYTREE", font=f)
    tw = bbox[2] - bbox[0]
    if tw < w - 8:
        draw.text((w // 2 - tw // 2, int(h * 0.68)), "PLAYTREE", fill=(126, 211, 33), font=f)
    img.save(os.path.join(OUT, name))
    print(name)

# --- Splash 620x300 ---
w, h = 620, 300
img, draw = make_bg(w, h, (10, 47, 86))
draw_logo(img, w // 2, 120, 2.2)
f = try_font(48)
bbox = draw.textbbox((0, 0), "PLAYTREE", font=f)
tw = bbox[2] - bbox[0]
draw.text((w // 2 - tw // 2 + 2, 195), "PLAYTREE", fill=(0, 0, 0, 200), font=f)
draw.text((w // 2 - tw // 2, 193), "PLAYTREE", fill=(126, 211, 33, 255), font=f)
f2 = try_font(16)
s = "GoConsole Game Studios"
bbox2 = draw.textbbox((0, 0), s, font=f2)
draw.text((w // 2 - (bbox2[2] - bbox2[0]) // 2, 255), s, fill=(140, 170, 140, 255), font=f2)
img.save(os.path.join(OUT, "SplashScreen.png"))
print("SplashScreen.png")

# Alt splash sizes
for nm, aw, ah in [("SplashScreen620x300.png", 620, 300), ("SplashScreen1240x600.png", 1240, 600)]:
    img.resize((aw, ah), Image.LANCZOS).save(os.path.join(OUT, nm))
    print(nm)

print("Part 1 done")
