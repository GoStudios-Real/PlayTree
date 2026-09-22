"""Generate PLAYTREE Store trailer — 30s MP4"""
import subprocess, os, sys, math, random
from PIL import Image, ImageDraw, ImageFont

random.seed(42)
TRAILER_DIR = r"C:\Users\RhysC\Downloads\NEW\PlayTreeXboxStore\StoreAssets\Trailer"
FRAMES_DIR = os.path.join(TRAILER_DIR, "frames")
os.makedirs(FRAMES_DIR, exist_ok=True)

FPS = 30
DURATION = 30  # seconds
TOTAL = FPS * DURATION  # 900 frames
W, H = 1920, 1080

def try_font(size):
    for name in ["arialbd.ttf", "arial.ttf", "consolab.ttf", "segoeuib.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_logo(draw, cx, cy, s=1.0):
    tw, th = int(16 * s), int(50 * s)
    draw.rounded_rectangle([cx - tw // 2, cy + 10 * s, cx + tw // 2, cy + 10 * s + th],
                           radius=max(1, int(3 * s)), fill=(80, 55, 30, 255))
    for ox, oy, r, col in [
        (0, -15, 45, (55, 160, 65)), (-28, 5, 30, (40, 140, 55)),
        (28, 5, 30, (45, 150, 60)), (0, -38, 35, (48, 170, 70)),
    ]:
        draw.ellipse([cx + (ox - r) * s, cy + (oy - r) * s, cx + (ox + r) * s, cy + (oy + r) * s],
                     fill=(*col, 255))

def scene_splash(t):
    """0-5s: Studio splash + logo reveal"""
    img = Image.new("RGBA", (W, H), (6, 20, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    # Fade in
    alpha = min(255, int(t * 120))
    # Logo grows
    scale = min(4.0, t * 1.5)
    cx, cy = W // 2, H // 2 - 80
    draw_logo(draw, cx, cy, scale)
    # Title fades in after 2s
    if t > 2:
        ta = min(255, int((t - 2) * 150))
        f = try_font(int(min(120, (t - 2) * 60 + 40)))
        bbox = draw.textbbox((0, 0), "PLAYTREE", font=f)
        tw = bbox[2] - bbox[0]
        draw.text((W // 2 - tw // 2 + 4, H // 2 + 60), "PLAYTREE", fill=(0, 0, 0, ta), font=f)
        draw.text((W // 2 - tw // 2, H // 2 + 56), "PLAYTREE", fill=(126, 211, 33, ta), font=f)
    # Studio text
    if t > 3.5:
        f2 = try_font(28)
        s = "GoConsole Game Studios"
        bbox2 = draw.textbbox((0, 0), s, font=f2)
        a2 = min(255, int((t - 3.5) * 180))
        draw.text((W // 2 - (bbox2[2] - bbox2[0]) // 2, H // 2 + 170), s,
                  fill=(140, 170, 140, a2), font=f2)
    return img

def scene_world(t):
    """5-12s: World showcase with camera pan"""
    img = Image.new("RGBA", (W, H), (8, 35, 60, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    pan = int(t * 80)
    # Sky
    for y in range(H):
        k = y / H
        if k < 0.4:
            draw.line([(0, y), (W, y)], fill=(int(60 + k * 120), int(120 + k * 130), 255, 255))
        else:
            draw.line([(0, y), (W, y)], fill=(50, 130, 60, 255))
    # Mountains (scrolling)
    for i in range(8):
        mx = (i * 400 - pan % 400) - 100
        mh = 200 + (i * 37 % 150)
        draw.polygon([(mx, 550), (mx + 200, 550 - mh), (mx + 400, 550)],
                     fill=(70, 90, 120, 255))
    # Trees (scrolling)
    for i in range(30):
        tx = (i * 130 - pan % 130) - 50
        ty = 700 + (i * 53 % 120)
        draw.rectangle([tx - 8, ty - 50, tx + 8, ty], fill=(95, 65, 22, 255))
        draw.ellipse([tx - 30, ty - 90, tx + 30, ty - 35], fill=(35, 110, 35, 255))
    # Ground
    draw.rectangle([0, H - 180, W, H], fill=(75, 150, 55, 255))
    # Player walking
    px = W // 2
    bob = int(math.sin(t * 6) * 8)
    draw.ellipse([px - 18, H - 260 + bob, px + 18, H - 224 + bob], fill=(100, 200, 255, 255))
    draw.rectangle([px - 12, H - 224 + bob, px + 12, H - 185 + bob], fill=(60, 180, 180, 255))
    # HUD
    draw.rectangle([20, 90, 320, 155], fill=(0, 0, 0, 150))
    draw.rectangle([30, 100, 300, 122], fill=(60, 0, 0, 255))
    draw.rectangle([30, 100, 240, 122], fill=(255, 50, 50, 255))
    # Caption
    f = try_font(50)
    if t < 8:
        cap = "Explore a 9000\u00d79000 World"
    else:
        cap = "16 Regions \u2022 Day/Night \u2022 Weather"
    bbox = draw.textbbox((0, 0), cap, font=f)
    draw.rectangle([W // 2 - (bbox[2] - bbox[0]) // 2 - 30, H - 150,
                    W // 2 + (bbox[2] - bbox[0]) // 2 + 30, H - 80], fill=(0, 0, 0, 160))
    draw.text((W // 2 - (bbox[2] - bbox[0]) // 2, H - 140), cap,
              fill=(126, 211, 33, 255), font=f)
    return img

def scene_combat(t):
    """12-20s: Combat montage"""
    img = Image.new("RGBA", (W, H), (20, 45, 25, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, H - 200, W, H], fill=(40, 85, 40, 255))
    # Player
    px, py = W // 3, H // 2
    draw.ellipse([px - 28, py - 28, px + 28, py + 28], fill=(100, 200, 255, 255))
    draw.rectangle([px - 16, py + 28, px + 16, py + 75], fill=(60, 180, 180, 255))
    # Sword arc (animated)
    swing = (t * 180) % 90 - 45
    for a in range(int(swing) - 30, int(swing) + 30, 3):
        r = 95
        x2 = px + int(r * math.cos(math.radians(a)))
        y2 = py + int(r * math.sin(math.radians(a)))
        draw.line([(px, py), (x2, y2)], fill=(255, 255, 200, 200), width=4)
    # Enemies
    for i in range(5):
        ex = px + 250 + i * 140
        ey = H // 2 + (i % 3) * 50 - 30
        bob = int(math.sin(t * 4 + i) * 6)
        draw.ellipse([ex - 22, ey - 22 + bob, ex + 22, ey + 22 + bob], fill=(200, 60, 60, 255))
    # Astro Toilet boss
    bx, by = W * 3 // 4, H // 3
    bob2 = int(math.sin(t * 3) * 10)
    draw.ellipse([bx - 70, by - 70 + bob2, bx + 70, by + 70 + bob2], fill=(180, 180, 200, 255))
    draw.ellipse([bx - 45, by - 45 + bob2, bx + 45, by + 15 + bob2], fill=(220, 220, 240, 255))
    blink = int(abs(math.sin(t * 4)) * 255)
    draw.ellipse([bx - 30, by - 30 + bob2, bx - 8, by - 8 + bob2], fill=(blink, 0, 0, 255))
    draw.ellipse([bx + 8, by - 30 + bob2, bx + 30, by - 8 + bob2], fill=(blink, 0, 0, 255))
    # Damage numbers
    f = try_font(42)
    for i in range(4):
        nt = (t * 2 + i * 0.5) % 1.5
        na = int(255 * (1 - nt / 1.5))
        draw.text((px + 150 + i * 90, py - 80 - int(nt * 60)), str(random.randint(80, 300)),
                  fill=(255, 220, 50, na), font=f)
    # Combo
    f2 = try_font(56)
    draw.text((50, 110), f"COMBO x{int(t * 3) % 20 + 5}!", fill=(255, 100, 50, 255), font=f2)
    # Caption
    f3 = try_font(50)
    cap = "6 Classes \u2022 12 Weapons \u2022 Astro Toilets"
    bbox = draw.textbbox((0, 0), cap, font=f3)
    draw.rectangle([W // 2 - (bbox[2] - bbox[0]) // 2 - 30, H - 150,
                    W // 2 + (bbox[2] - bbox[0]) // 2 + 30, H - 80], fill=(0, 0, 0, 160))
    draw.text((W // 2 - (bbox[2] - bbox[0]) // 2, H - 140), cap,
              fill=(126, 211, 33, 255), font=f3)
    return img

def scene_features(t):
    """20-27s: Feature showcase"""
    img = Image.new("RGBA", (W, H), (15, 20, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    # Grid bg
    for x in range(0, W, 60):
        draw.line([(x, 0), (x, H)], fill=(126, 211, 33, 15))
    for y in range(0, H, 60):
        draw.line([(0, y), (W, y)], fill=(126, 211, 33, 15))
    # Feature tiles appearing one by one
    features = [
        ("Base Building", "Build your fortress"),
        ("Mounts & Pets", "5 mounts, pet evolution"),
        ("Multiplayer", "GoConsoleOS cross-play"),
        ("Battle Pass", "100 tiers Season 1"),
        ("Fishing", "Minigame rewards"),
        ("Enchanting", "Power up gear"),
    ]
    f = try_font(36)
    f2 = try_font(22)
    for i, (title, desc) in enumerate(features):
        appear_t = i * 1.0
        if t < 1.5 + appear_t:
            continue
        row, col = divmod(i, 3)
        cx = 340 + col * 640
        cy = 280 + row * 300
        alpha = min(255, int((t - 1.5 - appear_t) * 300))
        # Tile
        draw.rounded_rectangle([cx - 260, cy - 90, cx + 260, cy + 90], radius=20,
                               fill=(25, 30, 55, alpha), outline=(126, 211, 33, alpha), width=3)
        draw.text((cx - draw.textbbox((0, 0), title, font=f)[2] // 2, cy - 50), title,
                  fill=(126, 211, 33, alpha), font=f)
        draw.text((cx - draw.textbbox((0, 0), desc, font=f2)[2] // 2, cy + 10), desc,
                  fill=(160, 180, 160, alpha), font=f2)
    # Bottom banner
    f3 = try_font(44)
    draw.rectangle([0, H - 100, W, H], fill=(0, 0, 0, 200))
    draw.text((W // 2 - 280, H - 85), "28 SYSTEMS \u2014 ALL FREE TO PLAY",
              fill=(255, 215, 0, 255), font=f3)
    return img

def scene_outro(t):
    """27-30s: Outro CTA"""
    img = Image.new("RGBA", (W, H), (6, 20, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    # Glow
    for r in range(400, 0, -30):
        a = max(0, 30 - r // 13)
        draw.ellipse([W // 2 - r, H // 2 - 100 - r, W // 2 + r, H // 2 - 100 + r],
                     fill=(126, 211, 33, a))
    draw_logo(draw, W // 2, H // 2 - 140, 3.5)
    # Title
    f = try_font(100)
    bbox = draw.textbbox((0, 0), "PLAYTREE", font=f)
    tw = bbox[2] - bbox[0]
    draw.text((W // 2 - tw // 2 + 4, H // 2 + 10), "PLAYTREE", fill=(0, 0, 0, 220), font=f)
    draw.text((W // 2 - tw // 2, H // 2 + 6), "PLAYTREE", fill=(126, 211, 33, 255), font=f)
    # Chapter
    f2 = try_font(44)
    s = "Chapter 1 : Season 1 \u2014 Available Now"
    bbox2 = draw.textbbox((0, 0), s, font=f2)
    draw.text((W // 2 - (bbox2[2] - bbox2[0]) // 2, H // 2 + 130), s,
              fill=(255, 215, 0, 255), font=f2)
    # CTA button
    f3 = try_font(36)
    cta = "DOWNLOAD FREE ON XBOX & PC"
    bbox3 = draw.textbbox((0, 0), cta, font=f3)
    cta_w = bbox3[2] - bbox3[0]
    pulse = int(abs(math.sin(t * 3)) * 40 + 215)
    draw.rounded_rectangle([W // 2 - cta_w // 2 - 30, H // 2 + 210,
                            W // 2 + cta_w // 2 + 30, H // 2 + 270],
                           radius=12, fill=(126, 211, 33, pulse))
    draw.text((W // 2 - cta_w // 2, H // 2 + 224), cta, fill=(0, 0, 0, 255), font=f3)
    # Xbox badge
    f4 = try_font(24)
    draw.rounded_rectangle([W // 2 - 120, H // 2 + 300, W // 2 + 120, H // 2 + 340],
                           radius=8, fill=(107, 158, 10, 255))
    draw.text((W // 2 - 85, H // 2 + 308), "XBOX READY", fill=(255, 255, 255, 255), font=f4)
    return img

# Generate all frames
print(f"Generating {TOTAL} frames at {W}x{H}...")
scenes = [
    (0, 5 * FPS, scene_splash),
    (5 * FPS, 12 * FPS, scene_world),
    (12 * FPS, 20 * FPS, scene_combat),
    (20 * FPS, 27 * FPS, scene_features),
    (27 * FPS, 30 * FPS, scene_outro),
]

for i in range(TOTAL):
    t = i / FPS
    frame = None
    for start, end, fn in scenes:
        if start <= i < end:
            frame = fn(t)
            break
    if frame is None:
        frame = scene_outro(t)
    # Crossfade between scenes (0.5s)
    frame.save(os.path.join(FRAMES_DIR, f"frame_{i:04d}.png"))
    if i % 90 == 0:
        print(f"  {i}/{TOTAL} ({t:.0f}s)")

print("Frames done. Encoding video...")

# Encode with ffmpeg
output = os.path.join(TRAILER_DIR, "PLAYTREE_Trailer.mp4")
ffmpeg_cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1920:1080",
    "-movflags", "+faststart",
    output,
]
try:
    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=600)
    if result.returncode == 0:
        sz = os.path.getsize(output)
        print(f"Trailer created: {output} ({sz // (1024*1024)} MB)")
    else:
        print(f"ffmpeg error: {result.stderr[:500]}")
except FileNotFoundError:
    print("ffmpeg not found. Frames saved — encode manually with:")
    print(f"  ffmpeg -framerate {FPS} -i {FRAMES_DIR}\\frame_%04d.png -c:v libx264 -crf 20 -pix_fmt yuv420p {output}")
except Exception as e:
    print(f"Error: {e}")
    print(f"Frames saved in {FRAMES_DIR}")

print("Trailer generation done")
