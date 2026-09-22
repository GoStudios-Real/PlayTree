"""Generate Discord Developer Portal assets for PlayTree"""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"C:\Users\RhysC\Downloads\NEW\PlayTreeDiscord\assets"

def make_large_icon():
    sz = 512
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    draw.ellipse([10, 10, sz-10, sz-10], fill=(15, 18, 25, 255))
    draw.ellipse([20, 20, sz-20, sz-20], fill=(20, 24, 32, 255))

    cx, cy = sz // 2, sz // 2

    # Glow ring
    for i in range(4):
        r = 180 + i * 15
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(126, 211, 33, 80 - i*15), width=2)

    # Tree trunk
    draw.rounded_rectangle([cx-15, cy+20, cx+15, cy+100], radius=5, fill=(80, 55, 30, 255))

    # Canopy
    for ox, oy, r, g, b in [(0, -15, 55, 160, 65), (-25, 0, 40, 140, 55), (25, 0, 45, 150, 60), (0, -40, 48, 170, 70), (-15, -30, 35, 130, 50), (15, -30, 40, 145, 58)]:
        draw.ellipse([cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r], fill=(r, g, b, 255))

    # "P" letter
    try:
        font = ImageFont.truetype("arial.ttf", 100)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "P", font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2 + 2, cy - 30 + 2), "P", fill=(0, 0, 0, 100), font=font)
    draw.text((cx - tw//2, cy - 30), "P", fill=(126, 211, 33, 255), font=font)

    img.save(os.path.join(OUT, "playtree_large.png"), "PNG")
    print("playtree_large.png (512x512)")

def make_small_icon():
    sz = 96
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([0, 0, sz-1, sz-1], radius=16, fill=(20, 24, 32, 255))

    cx, cy = sz // 2, sz // 2
    draw.rounded_rectangle([cx-6, cy+8, cx+6, cy+35], radius=3, fill=(80, 55, 30, 255))

    for ox, oy, r in [(0, -5, 18), (-10, 2, 12), (10, 2, 12), (0, -15, 15)]:
        draw.ellipse([cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r], fill=(60+ox, 160+oy, 65, 255))

    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), "P", font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, cy - 12), "P", fill=(126, 211, 33, 255), font=font)

    img.save(os.path.join(OUT, "playtree_small.png"), "PNG")
    print("playtree_small.png (96x96)")

def make_banner():
    w, h = 960, 540
    img = Image.new("RGBA", (w, h), (10, 12, 16, 255))
    draw = ImageDraw.Draw(img)

    # Gradient
    for y in range(h):
        t = y / h
        r = int(10 + 15 * t)
        g = int(12 + 30 * (1 - abs(t - 0.5) * 2))
        b = int(16 + 15 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Grid
    for x in range(0, w, 40):
        draw.line([(x, 0), (x, h)], fill=(25, 40, 30, 60), width=1)
    for y in range(0, h, 40):
        draw.line([(0, y), (w, y)], fill=(25, 40, 30, 60), width=1)

    cx, cy = w // 2, h // 2

    # Tree
    draw.rounded_rectangle([cx-15, cy+20, cx+15, cy+80], radius=4, fill=(80, 55, 30, 255))
    for ox, oy, r in [(0, -10, 50), (-25, 5, 35), (25, 5, 35), (0, -30, 40), (-15, -20, 30), (15, -20, 30)]:
        draw.ellipse([cx+ox-r, cy+oy-r, cx+ox+r, cy+oy+r], fill=(50+ox//2, 150+oy, 60+ox//3, 255))

    # Glow
    for i in range(5):
        r = 90 + i * 18
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(126, 211, 33, max(10, 50-i*10)), width=2)

    # Title
    try:
        ft = ImageFont.truetype("arial.ttf", 60)
        fs = ImageFont.truetype("arial.ttf", 24)
        fv = ImageFont.truetype("arial.ttf", 14)
    except:
        ft = fs = fv = ImageFont.load_default()

    title = "PLAYTREE"
    bbox = draw.textbbox((0, 0), title, font=ft)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2 + 2, 42), title, fill=(0, 0, 0, 100), font=ft)
    draw.text((cx - tw//2, 40), title, fill=(126, 211, 33, 255), font=ft)

    sub = "GAME COLLECTION — 9 GAMES — GoStudios"
    bbox2 = draw.textbbox((0, 0), sub, font=fs)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((cx - tw2//2, 110), sub, fill=(140, 170, 140, 255), font=fs)

    # Game icons
    icons = ["P", "3D", "FB", "PZ", "RC", "DG", "SP", "TD", "UW"]
    colors = [(126,211,33), (80,180,255), (255,180,40), (200,80,255), (50,200,200), (200,120,60), (60,120,255), (200,200,50), (60,180,255)]
    positions = [(80,100), (200,380), (400,100), (600,380), (800,100), (150,280), (750,280), (400,380), (550,200)]
    for i, (icon, col, pos) in enumerate(zip(icons, colors, positions)):
        draw.rounded_rectangle([pos[0]-15, pos[1]-15, pos[0]+15, pos[1]+15], radius=5, fill=(25, 30, 38, 200), outline=(*col, 150), width=2)
        try:
            fi = ImageFont.truetype("arial.ttf", 14)
        except:
            fi = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), icon, font=fi)
        itw = bbox[2] - bbox[0]
        draw.text((pos[0] - itw//2, pos[1] - 7), icon, fill=(*col, 255), font=fi)

    draw.line([(0, 0), (w, 0)], fill=(126, 211, 33, 255), width=3)
    draw.line([(0, h-1), (w, h-1)], fill=(126, 211, 33, 255), width=3)

    vt = "gostudios-real.github.io"
    bbox3 = draw.textbbox((0, 0), vt, font=fv)
    tw3 = bbox3[2] - bbox3[0]
    draw.text((cx - tw3//2, h-25), vt, fill=(60, 80, 65, 255), font=fv)

    img.save(os.path.join(OUT, "playtree_banner.png"), "PNG")
    print("playtree_banner.png (960x540)")

make_large_icon()
make_small_icon()
make_banner()
print("All assets created!")
