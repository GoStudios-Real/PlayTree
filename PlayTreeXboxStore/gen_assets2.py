"""Generate Store hero, banners, and screenshots — Part 2"""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

random.seed(42)
STORE = r"C:\Users\RhysC\Downloads\NEW\PlayTreeXboxStore\StoreAssets"
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
    step = max(40, w // 40)
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=(126, 211, 33, 16), width=1)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=(126, 211, 33, 16), width=1)
    return img, draw

# ===== HERO 1920x1080 =====
w, h = 1920, 1080
img, draw = make_bg(w, h, (6, 30, 55))
# Radial glow
for r in range(500, 0, -25):
    a = max(0, 35 - r // 14)
    glow = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    gd.ellipse([0, 0, r * 2, r * 2], fill=(126, 211, 33, a))
    img.paste(glow, (w // 2 - r, 400 - r), glow)
draw = ImageDraw.Draw(img, "RGBA")
draw_logo(img, w // 2, 370, 5.0)
f = try_font(140)
bbox = draw.textbbox((0, 0), "PLAYTREE", font=f)
tw = bbox[2] - bbox[0]
draw.text((w // 2 - tw // 2 + 5, 535), "PLAYTREE", fill=(0, 0, 0, 220), font=f)
draw.text((w // 2 - tw // 2, 530), "PLAYTREE", fill=(126, 211, 33, 255), font=f)
f2 = try_font(40)
s = "Chapter 1 : Season 1"
bbox2 = draw.textbbox((0, 0), s, font=f2)
draw.text((w // 2 - (bbox2[2] - bbox2[0]) // 2, 700), s, fill=(255, 215, 0, 255), font=f2)
f3 = try_font(26)
s2 = "GoConsole Game Studios  \u2022  9000\u00d79000 World  \u2022  28 Systems  \u2022  Free to Play"
bbox3 = draw.textbbox((0, 0), s2, font=f3)
draw.text((w // 2 - (bbox3[2] - bbox3[0]) // 2, 765), s2, fill=(160, 200, 160, 255), font=f3)
# Feature pills
features = ["Astro Toilets", "Base Building", "Mounts & Pets", "Multiplayer", "Battle Pass"]
f4 = try_font(22)
widths = [draw.textbbox((0, 0), ft, font=f4)[2] - draw.textbbox((0, 0), ft, font=f4)[0] + 50 for ft in features]
px = (w - sum(widths)) // 2
for ft, ftw in zip(features, widths):
    draw.rounded_rectangle([px - 15, 840, px + ftw - 15, 882], radius=22,
                           fill=(126, 211, 33, 40), outline=(126, 211, 33, 180))
    draw.text((px + 10, 849), ft, fill=(126, 211, 33, 255), font=f4)
    px += ftw
# Bottom bar
draw.rectangle([0, h - 60, w, h], fill=(0, 0, 0, 180))
f5 = try_font(24)
draw.text((40, h - 46), "\u00a92026 PlayTree Corporation  \u2022  Valid signed  \u2022  Windows & Xbox",
          fill=(100, 140, 100, 255), font=f5)
draw.rounded_rectangle([w - 240, h - 52, w - 40, h - 14], radius=8, fill=(107, 158, 10, 255))
draw.text((w - 200, h - 47), "XBOX READY", fill=(255, 255, 255, 255), font=f5)
img.convert("RGB").save(os.path.join(STORE, "Hero_1920x1080.png"))
print("Hero_1920x1080.png")

# ===== STORE FEATURE BANNER 3840x1200 =====
bw, bh = 3840, 1200
banner, bd = make_bg(bw, bh, (6, 30, 55))
draw_logo(banner, bw // 4, bh // 2, 7.0)
bd = ImageDraw.Draw(banner, "RGBA")
fb = try_font(180)
bd.text((bw // 2 + 40, bh // 2 - 120), "PLAYTREE", fill=(0, 0, 0, 200), font=fb)
bd.text((bw // 2 + 35, bh // 2 - 125), "PLAYTREE", fill=(126, 211, 33, 255), font=fb)
fb2 = try_font(52)
bd.text((bw // 2 + 40, bh // 2 + 90), "Chapter 1 : Season 1 \u2014 Now on Xbox & PC",
        fill=(255, 215, 0, 255), font=fb2)
banner.convert("RGB").save(os.path.join(STORE, "StoreFeatureBanner_3840x1200.png"))
print("StoreFeatureBanner_3840x1200.png")

# ===== LOGO KEY ART 1200x600 =====
lw, lh = 1200, 600
img2, d2 = make_bg(lw, lh, (6, 30, 55))
draw_logo(img2, lw // 2, 240, 4.0)
d2 = ImageDraw.Draw(img2, "RGBA")
fl = try_font(90)
bbox = d2.textbbox((0, 0), "PLAYTREE", font=fl)
d2.text((lw // 2 - (bbox[2] - bbox[0]) // 2 + 3, 373), "PLAYTREE", fill=(0, 0, 0, 200), font=fl)
d2.text((lw // 2 - (bbox[2] - bbox[0]) // 2, 370), "PLAYTREE", fill=(126, 211, 33, 255), font=fl)
fl2 = try_font(28)
d2.text((lw // 2 - 130, 480), "GoConsole Game Studios", fill=(140, 170, 140, 255), font=fl2)
img2.convert("RGB").save(os.path.join(STORE, "LogoKeyArt_1200x600.png"))
print("LogoKeyArt_1200x600.png")

print("Part 2 done")
