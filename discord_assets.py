"""Create Discord profile picture and banner for PlayTree / GoStudios"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, math

OUT = r"C:\Users\RhysC\Downloads\NEW"

# ============================================================
# DISCORD PROFILE PICTURE  — 512x512
# ============================================================
def make_profile_pic():
    sz = 512
    img = Image.new("RGB", (sz, sz), (10, 12, 16))
    draw = ImageDraw.Draw(img)

    # Radial gradient background
    cx, cy = sz // 2, sz // 2
    for r in range(sz // 2, 0, -1):
        t = r / (sz // 2)
        cr = int(10 + (20 - 10) * (1 - t))
        cg = int(12 + (60 - 12) * (1 - t))
        cb = int(16 + (30 - 16) * (1 - t))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb))

    # Grid pattern
    for x in range(0, sz, 32):
        draw.line([(x, 0), (x, sz)], fill=(30, 50, 35), width=1)
    for y in range(0, sz, 32):
        draw.line([(0, y), (sz, y)], fill=(30, 50, 35), width=1)

    # Central tree icon
    # Trunk
    trunk_w, trunk_h = 40, 100
    tx = cx - trunk_w // 2
    ty = cy + 40
    draw.rounded_rectangle([tx, ty, tx + trunk_w, ty + trunk_h], radius=6, fill=(80, 55, 30))

    # Canopy circles
    for i, (ox, oy, r, g, b) in enumerate([
        (0, -30, 50, 160, 65),
        (-25, -15, 40, 180, 75),
        (25, -15, 45, 170, 70),
        (0, -50, 35, 140, 55),
        (-15, -45, 38, 155, 60),
        (15, -45, 42, 165, 68),
    ]):
        draw.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r], fill=(r, g, b))

    # Outer glow ring
    for i in range(8):
        alpha = 40 - i * 5
        ring_r = 160 + i * 8
        draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
                      outline=(126, 211, 33, alpha), width=2)

    # "P" letter overlay
    try:
        font = ImageFont.truetype("arial.ttf", 120)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "P", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Shadow
    draw.text((cx - tw // 2 + 3, cy - th // 2 - 10 + 3), "P", fill=(0, 0, 0), font=font)
    draw.text((cx - tw // 2, cy - th // 2 - 10), "P", fill=(126, 211, 33), font=font)

    # "GoStudios" text at bottom
    try:
        font_sm = ImageFont.truetype("arial.ttf", 28)
    except:
        font_sm = ImageFont.load_default()
    bbox2 = draw.textbbox((0, 0), "GoStudios", font=font_sm)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((cx - tw2 // 2, sz - 55), "GoStudios", fill=(180, 210, 180), font=font_sm)

    # Border
    draw.rounded_rectangle([0, 0, sz - 1, sz - 1], radius=0, outline=(126, 211, 33), width=4)

    img.save(os.path.join(OUT, "discord_profile_512.png"), "PNG")
    print(f"discord_profile_512.png saved ({img.size})")


# ============================================================
# DISCORD BANNER  — 600x240 (or 960x540 for nitro)
# ============================================================
def make_banner():
    w, h = 960, 540
    img = Image.new("RGB", (w, h), (10, 12, 16))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(h):
        t = y / h
        r = int(10 + 15 * t)
        g = int(12 + 45 * (1 - abs(t - 0.5) * 2))
        b = int(16 + 20 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Grid pattern
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill=(25, 45, 30), width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill=(25, 45, 30), width=1)

    # Scattered small game icons
    icons_data = [
        (80, 100, "P", (126, 211, 33)),   # PlayTree
        (250, 380, "3D", (80, 180, 255)),  # 3D
        (450, 120, "FB", (255, 180, 40)),  # Football
        (620, 350, "PZ", (200, 80, 255)),  # Puzzle
        (780, 150, "RC", (50, 200, 200)),  # Racing
        (850, 400, "DG", (200, 120, 60)),  # Dungeon
        (150, 420, "SP", (60, 120, 255)),  # Space
        (700, 80, "TD", (200, 200, 50)),   # Tower Def
    ]
    try:
        font_icon = ImageFont.truetype("arial.ttf", 22)
    except:
        font_icon = ImageFont.load_default()

    for ix, iy, label, color in icons_data:
        # Square icon bg
        draw.rounded_rectangle([ix - 18, iy - 18, ix + 18, iy + 18], radius=6, fill=(25, 30, 38), outline=color, width=2)
        bbox = draw.textbbox((0, 0), label, font=font_icon)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        draw.text((ix - tw // 2, iy - th // 2), label, fill=color, font=font_icon)

    # Central tree — larger
    tree_cx, tree_cy = w // 2, h // 2 + 30
    # Trunk
    draw.rounded_rectangle([tree_cx - 18, tree_cy + 20, tree_cx + 18, tree_cy + 80], radius=4, fill=(80, 55, 30))
    # Canopy
    for ox, oy, r in [(0, -10, 55), (-25, 5, 40), (25, 5, 40), (0, -35, 45), (-15, -25, 38), (15, -25, 38)]:
        draw.ellipse([tree_cx + ox - r, tree_cy + oy - r, tree_cx + ox + r, tree_cy + oy + r],
                      fill=(50 + ox // 2, 150 + oy, 60 + ox // 3))

    # Glow rings around tree
    for i in range(6):
        ring_r = 100 + i * 15
        draw.ellipse([tree_cx - ring_r, tree_cy - ring_r, tree_cx + ring_r, tree_cy + ring_r],
                      outline=(126, 211, 33, max(10, 40 - i * 8)), width=1)

    # "PLAYTREE" title
    try:
        font_title = ImageFont.truetype("arial.ttf", 64)
        font_sub = ImageFont.truetype("arial.ttf", 26)
    except:
        font_title = font_sub = ImageFont.load_default()

    title = "PLAYTREE"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    # Shadow
    draw.text((w // 2 - tw // 2 + 3, 53), title, fill=(0, 0, 0), font=font_title)
    draw.text((w // 2 - tw // 2, 50), title, fill=(126, 211, 33), font=font_title)

    # Subtitle
    sub = "GAME COLLECTION — 8 GAMES — GoStudios"
    bbox2 = draw.textbbox((0, 0), sub, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((w // 2 - tw2 // 2, 125), sub, fill=(140, 170, 140), font=font_sub)

    # Separator line
    draw.line([(w // 2 - 200, 160), (w // 2 + 200, 160)], fill=(50, 80, 55), width=2)

    # Bottom text
    try:
        font_vs = ImageFont.truetype("arial.ttf", 16)
    except:
        font_vs = ImageFont.load_default()
    vt = "gostudios-real.github.io"
    bbox3 = draw.textbbox((0, 0), vt, font=font_vs)
    tw3 = bbox3[2] - bbox3[0]
    draw.text((w // 2 - tw3 // 2, h - 30), vt, fill=(60, 80, 65), font=font_vs)

    # Top/bottom border lines
    draw.line([(0, 0), (w, 0)], fill=(126, 211, 33), width=3)
    draw.line([(0, h - 1), (w, h - 1)], fill=(126, 211, 33), width=3)

    img.save(os.path.join(OUT, "discord_banner_960x540.png"), "PNG")
    print(f"discord_banner_960x540.png saved ({img.size})")

    # Also make a 600x240 version for standard Discord
    img2 = img.resize((600, 240), Image.LANCZOS)
    img2.save(os.path.join(OUT, "discord_banner_600x240.png"), "PNG")
    print(f"discord_banner_600x240.png saved ({img2.size})")


make_profile_pic()
make_banner()
print("Done!")
