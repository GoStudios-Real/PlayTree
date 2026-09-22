"""PlayTree Underwater — Explore the deep ocean, survive, collect treasure"""
import pygame
import sys
import random
import math

sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW")
from game_utils import controller, sfx, sfx_shoot, sfx_hit, sfx_collect, sfx_levelup, sfx_menu_click, sfx_menu_hover, sfx_damage, sfx_game_over, sfx_coin, sfx_bubble, sfx_splash, sfx_powerup

pygame.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Underwater — GoStudios")

try:
    ft = pygame.font.SysFont("Segoe UI Semibold", 34)
    fn = pygame.font.SysFont("Segoe UI", 20)
    fs = pygame.font.SysFont("Consolas", 14)
    fi = pygame.font.SysFont("Consolas", 22, bold=True)
except Exception:
    ft = fn = fs = fi = pygame.font.Font(None, 22)

# Colors
DEEP_BG = (5, 15, 35)
SAND = (160, 140, 90)
SAND_DARK = (130, 115, 70)
CORAL_COLORS = [(220, 80, 80), (220, 120, 60), (200, 60, 120), (180, 50, 180), (60, 180, 180)]
FISH_COLORS = [(255, 180, 50), (80, 200, 255), (255, 100, 100), (100, 255, 100), (255, 150, 255), (200, 200, 80)]
ENEMY_COLORS = {"shark": (100, 110, 130), "jellyfish": (180, 100, 255), "eel": (40, 180, 80), "puffer": (200, 180, 60), "kraken": (120, 40, 140)}

# World
WORLD_W, WORLD_H = 4000, 3000
player = {"x": 200, "y": WORLD_H // 2, "vx": 0, "vy": 0, "hp": 100, "max_hp": 100, "oxygen": 100, "max_oxygen": 100, "speed": 3.5, "gold": 0, "gems": 0, "depth": 0, "treasures": 0}
cam_x, cam_y = 0, 0

# Terrain
coral = []
for _ in range(80):
    cx = random.randint(50, WORLD_W - 50)
    cy = random.randint(WORLD_H - 200, WORLD_H - 30)
    coral.append({"x": cx, "y": cy, "color": random.choice(CORAL_COLORS), "size": random.randint(10, 35), "type": random.randint(0, 2)})

seaweed = []
for _ in range(120):
    sx = random.randint(20, WORLD_W - 20)
    sy = random.randint(WORLD_H - 180, WORLD_H - 10)
    seaweed.append({"x": sx, "y": sy, "h": random.randint(30, 90), "phase": random.uniform(0, 6.28), "color": (20 + random.randint(0, 30), 80 + random.randint(0, 60), 40 + random.randint(0, 30))})

rocks = []
for _ in range(50):
    rx = random.randint(0, WORLD_W)
    ry = random.randint(WORLD_H - 120, WORLD_H)
    rocks.append({"x": rx, "y": ry, "w": random.randint(20, 60), "h": random.randint(15, 40), "color": (60 + random.randint(0, 40), 55 + random.randint(0, 35), 50 + random.randint(0, 30))})

# Fish (ambient)
fish = []
for _ in range(40):
    fx = random.randint(0, WORLD_W)
    fy = random.randint(50, WORLD_H - 200)
    fish.append({"x": fx, "y": fy, "speed": random.uniform(0.5, 2.5), "dir": random.choice([-1, 1]), "color": random.choice(FISH_COLORS), "size": random.randint(4, 10), "wobble": random.uniform(0, 6.28)})

# Enemies
enemies = []
def spawn_enemy():
    types = [
        {"name": "shark", "hp": 20, "dmg": 15, "speed": 2.0, "size": 25, "color": ENEMY_COLORS["shark"], "xp": 30},
        {"name": "jellyfish", "hp": 8, "dmg": 8, "speed": 0.8, "size": 15, "color": ENEMY_COLORS["jellyfish"], "xp": 15, "stun": True},
        {"name": "eel", "hp": 12, "dmg": 10, "speed": 2.5, "size": 12, "color": ENEMY_COLORS["eel"], "xp": 20},
        {"name": "puffer", "hp": 15, "dmg": 12, "speed": 0.5, "size": 20, "color": ENEMY_COLORS["puffer"], "xp": 25, "explode": True},
        {"name": "kraken", "hp": 50, "dmg": 25, "speed": 1.0, "size": 35, "color": ENEMY_COLORS["kraken"], "xp": 80, "boss": True},
    ]
    t = random.choice(types)
    side = random.randint(0, 3)
    if side == 0: ex, ey = cam_x - 100, random.randint(0, WORLD_H)
    elif side == 1: ex, ey = cam_x + WIDTH + 100, random.randint(0, WORLD_H)
    elif side == 2: ex, ey = random.randint(0, WORLD_W), cam_y - 100
    else: ex, ey = random.randint(0, WORLD_W), cam_y + HEIGHT + 100
    enemies.append({"x": ex, "y": ey, **t, "max_hp": t["hp"], "phase": random.uniform(0, 6.28), "attack_cd": 0})

for _ in range(15):
    spawn_enemy()

# Collectibles
collectibles = []
def spawn_collectible():
    types = [
        {"kind": "gold", "color": (255, 220, 50), "value": 10},
        {"kind": "gem", "color": (100, 200, 255), "value": 25},
        {"kind": "heart", "color": (255, 80, 80), "value": 0},
        {"kind": "oxygen", "color": (80, 180, 255), "value": 0},
        {"kind": "treasure", "color": (255, 180, 40), "value": 100},
    ]
    t = random.choice(types)
    cx = random.randint(50, WORLD_W - 50)
    cy = random.randint(50, WORLD_H - 50)
    collectibles.append({"x": cx, "y": cy, **t, "bob": random.uniform(0, 6.28)})

for _ in range(60):
    spawn_collectible()

# Bubbles
bubbles = []
def spawn_bubble(x, y):
    bubbles.append({"x": x + random.uniform(-5, 5), "y": y, "vy": random.uniform(-1.5, -0.5), "size": random.uniform(2, 6), "life": 1.0})

# Particles
particles = []
def spawn_particles(x, y, color, count=8):
    for _ in range(count):
        a = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, 4)
        particles.append({"x": x, "y": y, "vx": math.cos(a) * spd, "vy": math.sin(a) * spd, "life": 1.0, "color": color})

# Light rays
light_rays = []
for _ in range(12):
    light_rays.append({"x": random.randint(0, WORLD_W), "w": random.randint(30, 80), "alpha": random.randint(10, 30)})

# Treasure chests
chests = []
for _ in range(15):
    chests.append({"x": random.randint(100, WORLD_W - 100), "y": random.randint(WORLD_H - 150, WORLD_H - 20), "opened": False, "content": random.choice(["gold", "gem", "treasure"])})

game_state = "menu"
score = 0
wave = 1
wave_timer = 0
damage_flash = 0
invincible = 0
boost = 0
boost_max = 100
game_over = False
restart_pressed = False
prev_at_surface = False

clock = pygame.time.Clock()
controller.init()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    controller.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "play":
                    game_state = "menu"
                else:
                    running = False
            elif event.key == pygame.K_RETURN and game_state == "menu":
                game_state = "play"
                game_over = False
                player["x"] = 200
                player["y"] = WORLD_H // 2
                player["hp"] = 100
                player["oxygen"] = 100
                player["gold"] = 0
                player["gems"] = 0
                player["treasures"] = 0
                score = 0
                wave = 1
                enemies.clear()
                collectibles.clear()
                chests.clear()
                for _ in range(15): spawn_enemy()
                for _ in range(60): spawn_collectible()
                for _ in range(15):
                    chests.append({"x": random.randint(100, WORLD_W - 100), "y": random.randint(WORLD_H - 150, WORLD_H - 20), "opened": False, "content": random.choice(["gold", "gem", "treasure"])})
            elif event.key == pygame.K_r and game_over:
                game_over = False
                game_state = "play"
                player["x"] = 200
                player["y"] = WORLD_H // 2
                player["hp"] = 100
                player["oxygen"] = 100
                player["gold"] = 0
                player["gems"] = 0
                player["treasures"] = 0
                score = 0
                wave = 1
                enemies.clear()
                collectibles.clear()
                chests.clear()
                for _ in range(15): spawn_enemy()
                for _ in range(60): spawn_collectible()
                for _ in range(15):
                    chests.append({"x": random.randint(100, WORLD_W - 100), "y": random.randint(WORLD_H - 150, WORLD_H - 20), "opened": False, "content": random.choice(["gold", "gem", "treasure"])})

    # Controller button handling
    if controller.just_pressed("btn_start"):
        if game_state == "play":
            game_state = "menu"
            sfx.play("menu_click", sfx_menu_click)
        else:
            running = False
    if controller.just_pressed("btn_a") and game_state == "menu":
        game_state = "play"
        game_over = False
        player["x"] = 200
        player["y"] = WORLD_H // 2
        player["hp"] = 100
        player["oxygen"] = 100
        player["gold"] = 0
        player["gems"] = 0
        player["treasures"] = 0
        score = 0
        wave = 1
        enemies.clear()
        collectibles.clear()
        chests.clear()
        for _ in range(15): spawn_enemy()
        for _ in range(60): spawn_collectible()
        for _ in range(15):
            chests.append({"x": random.randint(100, WORLD_W - 100), "y": random.randint(WORLD_H - 150, WORLD_H - 20), "opened": False, "content": random.choice(["gold", "gem", "treasure"])})
        sfx.play("menu_click", sfx_menu_click)
    if controller.just_pressed("btn_y") and game_over:
        game_over = False
        game_state = "play"
        player["x"] = 200
        player["y"] = WORLD_H // 2
        player["hp"] = 100
        player["oxygen"] = 100
        player["gold"] = 0
        player["gems"] = 0
        player["treasures"] = 0
        score = 0
        wave = 1
        enemies.clear()
        collectibles.clear()
        chests.clear()
        for _ in range(15): spawn_enemy()
        for _ in range(60): spawn_collectible()
        for _ in range(15):
            chests.append({"x": random.randint(100, WORLD_W - 100), "y": random.randint(WORLD_H - 150, WORLD_H - 20), "opened": False, "content": random.choice(["gold", "gem", "treasure"])})
        sfx.play("menu_click", sfx_menu_click)

    if game_state == "play" and not game_over:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        # Controller left stick movement
        stick_x = controller.move_x()
        stick_y = controller.move_y()
        if abs(stick_x) > 0.15:
            dx += stick_x
        if abs(stick_y) > 0.15:
            dy += stick_y

        spd = player["speed"]
        if (keys[pygame.K_LSHIFT] or controller.get_button("btn_a")) and boost > 0:
            spd *= 1.6
            boost -= dt * 40
        else:
            boost = min(boost_max, boost + dt * 8)

        if dx != 0 or dy != 0:
            ln = math.sqrt(dx * dx + dy * dy)
            player["vx"] = dx / ln * spd
            player["vy"] = dy / ln * spd
            if random.random() < 0.3:
                spawn_bubble(player["x"], player["y"] + 10)
        else:
            player["vx"] *= 0.9
            player["vy"] *= 0.9

        player["x"] += player["vx"]
        player["y"] += player["vy"]
        player["x"] = max(20, min(WORLD_W - 20, player["x"]))
        player["y"] = max(20, min(WORLD_H - 20, player["y"]))

        player["depth"] = max(0, int((player["y"] / WORLD_H) * 100))

        # Oxygen drain — faster deeper
        drain = dt * (3 + player["depth"] * 0.1)
        if player["y"] < WORLD_H * 0.3:
            drain *= 0.5
        player["oxygen"] -= drain
        if player["oxygen"] <= 0:
            player["oxygen"] = 0
            player["hp"] -= dt * 20
        if player["y"] < WORLD_H * 0.15:
            player["oxygen"] = min(player["max_oxygen"], player["oxygen"] + dt * 5)
            if not prev_at_surface:
                sfx.play("splash", sfx_splash)
            prev_at_surface = True
        else:
            prev_at_surface = False

        invincible = max(0, invincible - dt)
        damage_flash = max(0, damage_flash - dt * 3)

        # Update fish
        for f in fish:
            f["x"] += f["speed"] * f["dir"]
            f["wobble"] += dt * 3
            f["y"] += math.sin(f["wobble"]) * 0.3
            if f["x"] > WORLD_W + 20: f["dir"] = -1; f["x"] = WORLD_W + 20
            if f["x"] < -20: f["dir"] = 1; f["x"] = -20

        # Update enemies
        for e in enemies[:]:
            ex = player["x"] - e["x"]
            ey = player["y"] - e["y"]
            d = math.hypot(ex, ey)

            if e["name"] == "jellyfish":
                e["phase"] += dt * 2
                e["y"] += math.sin(e["phase"]) * 0.5
                e["x"] += math.cos(e["phase"] * 0.7) * 0.3
                if d < 150:
                    e["x"] += ex / d * e["speed"] * 0.3
                    e["y"] += ey / d * e["speed"] * 0.3
            elif e["name"] == "eel":
                e["phase"] += dt * 5
                if d < 200:
                    e["x"] += math.cos(e["phase"]) * e["speed"]
                    e["y"] += ey / d * e["speed"]
            elif e["name"] == "shark":
                if d < 300:
                    e["x"] += ex / d * e["speed"]
                    e["y"] += ey / d * e["speed"]
            elif e["name"] == "kraken":
                e["phase"] += dt
                if d < 400:
                    e["x"] += ex / d * e["speed"]
                    e["y"] += ey / d * e["speed"]
                # Spawn mini tentacles
                if random.random() < 0.02:
                    spawn_particles(e["x"], e["y"], (180, 80, 220), 3)
            else:
                if d < 200:
                    e["x"] += ex / d * e["speed"]
                    e["y"] += ey / d * e["speed"]

            e["attack_cd"] = max(0, e["attack_cd"] - dt)
            if d < e["size"] + 15 and e["attack_cd"] <= 0:
                if invincible <= 0:
                    player["hp"] -= e["dmg"]
                    damage_flash = 1
                    invincible = 0.5
                    spawn_particles(player["x"], player["y"], (255, 80, 80), 6)
                    sfx.play("hit", sfx_hit)
                    sfx.play("damage", sfx_damage)
                e["attack_cd"] = 1.5

            if e["hp"] <= 0:
                score += e["xp"]
                spawn_particles(e["x"], e["y"], e["color"], 12)
                if e.get("explode"):
                    for e2 in enemies:
                        if e2 is not e and math.hypot(e2["x"] - e["x"], e2["y"] - e["y"]) < 100:
                            e2["hp"] -= 15
                enemies.remove(e)

        # Collectibles
        for c in collectibles[:]:
            c["bob"] += dt * 2
            by = math.sin(c["bob"]) * 4
            d = math.hypot(player["x"] - c["x"], player["y"] - (c["y"] + by))
            if d < 25:
                if c["kind"] == "gold":
                    player["gold"] += c["value"]
                    score += c["value"]
                    sfx.play("coin", sfx_coin)
                elif c["kind"] == "gem":
                    player["gems"] += 1
                    score += c["value"]
                    sfx.play("collect", sfx_collect)
                elif c["kind"] == "heart":
                    player["hp"] = min(player["max_hp"], player["hp"] + 25)
                    sfx.play("collect", sfx_collect)
                elif c["kind"] == "oxygen":
                    player["oxygen"] = min(player["max_oxygen"], player["oxygen"] + 40)
                    sfx.play("collect", sfx_collect)
                elif c["kind"] == "treasure":
                    player["treasures"] += 1
                    score += c["value"]
                    sfx.play("collect", sfx_collect)
                spawn_particles(c["x"], c["y"], c["color"], 8)
                collectibles.remove(c)

        # Chests
        for ch in chests:
            if not ch["opened"]:
                d = math.hypot(player["x"] - ch["x"], player["y"] - ch["y"])
                if d < 30:
                    ch["opened"] = True
                    if ch["content"] == "gold":
                        player["gold"] += 50
                        score += 50
                    elif ch["content"] == "gem":
                        player["gems"] += 3
                        score += 75
                    elif ch["content"] == "treasure":
                        player["treasures"] += 1
                        score += 100
                    spawn_particles(ch["x"], ch["y"], (255, 220, 50), 15)
                    sfx.play("powerup", sfx_powerup)

        # Bubbles
        for b in bubbles[:]:
            b["y"] += b["vy"]
            b["x"] += math.sin(b["y"] * 0.05) * 0.3
            b["life"] -= 0.01
            if b["life"] <= 0 or b["y"] < 0:
                bubbles.remove(b)

        # Ambient bubbles
        if random.random() < 0.1:
            spawn_bubble(random.randint(0, WORLD_W), WORLD_H)
            sfx.play("bubble", sfx_bubble)

        # Particles
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vx"] *= 0.95
            p["vy"] *= 0.95
            p["life"] -= 0.03
            if p["life"] <= 0:
                particles.remove(p)

        # Wave spawning
        wave_timer += dt
        if wave_timer > 15 and len(enemies) < 20:
            wave += 1
            wave_timer = 0
            for _ in range(3 + wave):
                spawn_enemy()

        # Respawn collectibles
        if len(collectibles) < 20:
            for _ in range(5):
                spawn_collectible()

        # Death
        if player["hp"] <= 0:
            game_over = True
            sfx.play("game_over", sfx_game_over)

    # Camera
    cam_x = player["x"] - WIDTH // 2
    cam_y = player["y"] - HEIGHT // 2

    # ===== DRAW =====
    # Background gradient (darker at bottom = deeper)
    screen.fill(DEEP_BG)
    for y in range(HEIGHT):
        wy = (cam_y + y) / WORLD_H
        r = int(5 + 8 * wy)
        g = int(15 + 20 * (1 - wy))
        b = int(35 + 40 * (1 - wy))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Light rays from surface
    for ray in light_rays:
        rx = ray["x"] - cam_x
        if -ray["w"] < rx < WIDTH + ray["w"]:
            ray_surf = pygame.Surface((ray["w"], HEIGHT), pygame.SRCALPHA)
            for i in range(0, ray["w"], 2):
                a = int(ray["alpha"] * (1 - abs(i - ray["w"] // 2) / (ray["w"] // 2)))
                pygame.draw.line(ray_surf, (100, 200, 255, a), (i, 0), (i + 5, HEIGHT))
            screen.blit(ray_surf, (rx - ray["w"] // 2, 0))

    # Seaweed
    for sw in seaweed:
        sx = sw["x"] - cam_x
        sy = sw["y"] - cam_y
        if -50 < sx < WIDTH + 50:
            phase = math.sin(time.time() * 1.5 + sw["phase"]) * 8
            points = []
            for i in range(0, sw["h"], 5):
                px = sx + phase * (i / sw["h"])
                py = sy - i
                points.append((px, py))
            if len(points) > 1:
                for i in range(len(points) - 1):
                    w = max(1, int(4 * (1 - i / len(points))))
                    pygame.draw.line(screen, sw["color"], points[i], points[i + 1], w)

    # Rocks
    for rock in rocks:
        rx = rock["x"] - cam_x
        ry = rock["y"] - cam_y
        if -60 < rx < WIDTH + 60:
            pygame.draw.ellipse(screen, rock["color"], (rx, ry, rock["w"], rock["h"]))

    # Sand floor
    sand_y = WORLD_H - cam_y - 30
    if sand_y < HEIGHT + 100:
        pygame.draw.rect(screen, SAND, (0, max(0, sand_y), WIDTH, HEIGHT))
        for i in range(0, WIDTH, 6):
            dy2 = random.randint(-3, 3) if i % 12 == 0 else 0
            pygame.draw.circle(screen, SAND_DARK, (i, int(sand_y + dy2)), 2)

    # Coral
    for c in coral:
        cx = c["x"] - cam_x
        cy = c["y"] - cam_y
        if -40 < cx < WIDTH + 40:
            s = c["size"]
            if c["type"] == 0:
                pygame.draw.circle(screen, c["color"], (int(cx), int(cy)), s)
                pygame.draw.circle(screen, c["color"], (int(cx - s * 0.6), int(cy + s * 0.3)), int(s * 0.6))
                pygame.draw.circle(screen, c["color"], (int(cx + s * 0.6), int(cy + s * 0.3)), int(s * 0.6))
            elif c["type"] == 1:
                for branch in range(3):
                    bx = cx + (branch - 1) * s * 0.4
                    bh = s * (0.8 + branch * 0.2)
                    pygame.draw.line(screen, c["color"], (int(bx), int(cy)), (int(bx + (branch - 1) * 5), int(cy - bh)), max(3, s // 4))
                    pygame.draw.circle(screen, c["color"], (int(bx + (branch - 1) * 5), int(cy - bh)), max(3, s // 5))
            else:
                pygame.draw.polygon(screen, c["color"], [
                    (cx, cy - s), (cx - s * 0.3, cy), (cx + s * 0.3, cy)
                ])
                pygame.draw.polygon(screen, c["color"], [
                    (cx - s * 0.4, cy - s * 0.5), (cx - s * 0.7, cy), (cx - s * 0.1, cy)
                ])

    # Fish
    for f in fish:
        fx = f["x"] - cam_x
        fy = f["y"] - cam_y
        if -20 < fx < WIDTH + 20 and -20 < fy < HEIGHT + 20:
            sz = f["size"]
            if f["dir"] > 0:
                pts = [(fx + sz, fy), (fx - sz, fy - sz * 0.5), (fx - sz, fy + sz * 0.5)]
            else:
                pts = [(fx - sz, fy), (fx + sz, fy - sz * 0.5), (fx + sz, fy + sz * 0.5)]
            pygame.draw.polygon(screen, f["color"], pts)
            pygame.draw.circle(screen, (20, 20, 20), (int(fx + f["dir"] * sz * 0.4), int(fy - 1)), 1)
            tail_x = fx - f["dir"] * sz * 1.3
            pygame.draw.polygon(screen, f["color"], [(tail_x, fy), (tail_x - f["dir"] * 5, fy - 4), (tail_x - f["dir"] * 5, fy + 4)])

    # Treasure chests
    for ch in chests:
        chx = ch["x"] - cam_x
        chy = ch["y"] - cam_y
        if -30 < chx < WIDTH + 30:
            if not ch["opened"]:
                pygame.draw.rect(screen, (120, 80, 30), (chx - 12, chy - 8, 24, 16), border_radius=3)
                pygame.draw.rect(screen, (180, 140, 50), (chx - 12, chy - 10, 24, 6), border_radius=2)
                pygame.draw.rect(screen, (255, 220, 50), (chx - 2, chy - 6, 4, 4))
            else:
                pygame.draw.rect(screen, (80, 60, 25), (chx - 12, chy - 4, 24, 10), border_radius=2)

    # Collectibles
    for c in collectibles:
        cx = c["x"] - cam_x
        cy = c["y"] - cam_y + math.sin(c["bob"]) * 4
        if -15 < cx < WIDTH + 15 and -15 < cy < HEIGHT + 15:
            if c["kind"] == "gold":
                pygame.draw.circle(screen, c["color"], (int(cx), int(cy)), 6)
                pygame.draw.circle(screen, (200, 180, 30), (int(cx), int(cy)), 6, 1)
            elif c["kind"] == "gem":
                pygame.draw.polygon(screen, c["color"], [(cx, cy - 7), (cx + 6, cy), (cx, cy + 7), (cx - 6, cy)])
            elif c["kind"] == "heart":
                pygame.draw.circle(screen, c["color"], (int(cx - 4), int(cy - 2)), 5)
                pygame.draw.circle(screen, c["color"], (int(cx + 4), int(cy - 2)), 5)
                pygame.draw.polygon(screen, c["color"], [(cx - 9, cy), (cx, cy + 9), (cx + 9, cy)])
            elif c["kind"] == "oxygen":
                pygame.draw.circle(screen, c["color"], (int(cx), int(cy)), 8, 2)
                pygame.draw.line(screen, c["color"], (int(cx), int(cy - 4)), (int(cx), int(cy + 4)), 2)
                pygame.draw.line(screen, c["color"], (int(cx - 4), int(cy)), (int(cx + 4), int(cy)), 2)
            elif c["kind"] == "treasure":
                pygame.draw.rect(screen, c["color"], (cx - 8, cy - 6, 16, 12), border_radius=2)
                pygame.draw.rect(screen, (255, 255, 200), (cx - 2, cy - 2, 4, 4))

    # Enemies
    for e in enemies:
        ex = e["x"] - cam_x
        ey = e["y"] - cam_y
        if -50 < ex < WIDTH + 50 and -50 < ey < HEIGHT + 50:
            sz = e["size"]
            if e["name"] == "shark":
                pts = [(ex + sz, ey), (ex - sz * 0.8, ey - sz * 0.5), (ex - sz * 0.3, ey), (ex - sz * 0.8, ey + sz * 0.5)]
                pygame.draw.polygon(screen, e["color"], pts)
                pygame.draw.polygon(screen, (70, 80, 100), [(ex, ey - sz * 0.5), (ex - sz * 0.2, ey), (ex + sz * 0.3, ey - sz * 0.2)])
                pygame.draw.circle(screen, (255, 255, 255), (int(ex + sz * 0.5), int(ey - 2)), 2)
                pygame.draw.circle(screen, (0, 0, 0), (int(ex + sz * 0.5), int(ey - 2)), 1)
            elif e["name"] == "jellyfish":
                pygame.draw.ellipse(screen, e["color"], (ex - sz, ey - sz * 0.6, sz * 2, sz))
                for t in range(4):
                    tx = ex - sz * 0.6 + t * sz * 0.4
                    tl = sz * (0.8 + math.sin(e["phase"] + t) * 0.3)
                    pygame.draw.line(screen, (*e["color"][:2], max(0, e["color"][2] - 30)), (int(tx), int(ey + sz * 0.3)), (int(tx + math.sin(e["phase"] + t) * 5), int(ey + sz * 0.3 + tl)), 2)
            elif e["name"] == "eel":
                pts = []
                for i in range(10):
                    t = i / 9
                    exx = ex - sz * 2 * t + sz
                    eyy = ey + math.sin(e["phase"] + t * 6) * sz * 0.5
                    pts.append((exx, eyy))
                if len(pts) > 2:
                    pygame.draw.lines(screen, e["color"], False, [(int(p[0]), int(p[1])) for p in pts], 4)
                pygame.draw.circle(screen, (255, 255, 100), (int(ex + sz), int(ey - 2)), 2)
            elif e["name"] == "puffer":
                puff = 1 + math.sin(e["phase"]) * 0.3
                pygame.draw.circle(screen, e["color"], (int(ex), int(ey)), int(sz * puff))
                for i in range(8):
                    a = i * math.pi / 4 + e["phase"]
                    sx2 = ex + math.cos(a) * sz * puff * 1.2
                    sy2 = ey + math.sin(a) * sz * puff * 1.2
                    pygame.draw.line(screen, e["color"], (int(ex), int(ey)), (int(sx2), int(sy2)), 2)
                pygame.draw.circle(screen, (20, 20, 20), (int(ex + 4), int(ey - 3)), 2)
            elif e["name"] == "kraken":
                pygame.draw.circle(screen, e["color"], (int(ex), int(ey)), sz)
                pygame.draw.circle(screen, (80, 30, 100), (int(ex), int(ey)), sz, 2)
                for i in range(8):
                    a = i * math.pi / 4 + e["phase"] * 0.3
                    tl = sz * 1.5
                    tx = ex + math.cos(a) * tl
                    ty = ey + math.sin(a) * tl + math.sin(e["phase"] + i) * 10
                    pygame.draw.line(screen, e["color"], (int(ex + math.cos(a) * sz * 0.8), int(ey + math.sin(a) * sz * 0.8)), (int(tx), int(ty)), 4)
                    pygame.draw.circle(screen, (200, 100, 255), (int(tx), int(ty)), 3)
                pygame.draw.circle(screen, (255, 50, 50), (int(ex - 8), int(ey - 5)), 4)
                pygame.draw.circle(screen, (255, 50, 50), (int(ex + 8), int(ey - 5)), 4)
                pygame.draw.circle(screen, (0, 0, 0), (int(ex - 8), int(ey - 5)), 2)
                pygame.draw.circle(screen, (0, 0, 0), (int(ex + 8), int(ey - 5)), 2)

            # HP bar
            if e["hp"] < e["max_hp"]:
                hw = sz * 1.5
                pygame.draw.rect(screen, (40, 40, 40), (ex - hw // 2, ey - sz - 12, hw, 4))
                pygame.draw.rect(screen, (200, 50, 50), (ex - hw // 2, ey - sz - 12, int(hw * e["hp"] / e["max_hp"]), 4))

    # Player (submarine/diver)
    px = player["x"] - cam_x
    py = player["y"] - cam_y
    if invincible > 0 and int(invincible * 10) % 2 == 0:
        pass
    else:
        # Body
        pygame.draw.ellipse(screen, (50, 150, 200), (px - 18, py - 10, 36, 20))
        pygame.draw.ellipse(screen, (40, 120, 170), (px - 18, py - 10, 36, 20), 2)
        # Cockpit
        pygame.draw.ellipse(screen, (150, 220, 255), (px + 2, py - 6, 14, 12))
        pygame.draw.ellipse(screen, (200, 240, 255), (px + 4, py - 4, 8, 6))
        # Propeller
        prop_phase = pygame.time.get_ticks() * 0.02
        for i in range(3):
            a = prop_phase + i * math.pi * 2 / 3
            pygame.draw.line(screen, (180, 180, 180), (int(px - 18), int(py)), (int(px - 18 + math.cos(a) * 6), int(py + math.sin(a) * 6)), 2)
        # Light
        if player["y"] < WORLD_H * 0.5:
            light_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
            pygame.draw.polygon(light_surf, (255, 255, 200, 20), [(30, 20), (60, 0), (60, 40)])
            screen.blit(light_surf, (px + 15, py - 20))

    # Bubbles
    for b in bubbles:
        bx = b["x"] - cam_x
        by = b["y"] - cam_y
        if 0 < bx < WIDTH and 0 < by < HEIGHT:
            alpha = int(b["life"] * 150)
            sz = int(b["size"])
            pygame.draw.circle(screen, (150, 220, 255), (int(bx), int(by)), sz)
            pygame.draw.circle(screen, (200, 240, 255), (int(bx - sz * 0.3), int(by - sz * 0.3)), max(1, sz // 3))

    # Particles
    for p in particles:
        px2 = p["x"] - cam_x
        py2 = p["y"] - cam_y
        r = max(1, int(p["life"] * 4))
        pygame.draw.circle(screen, p["color"], (int(px2), int(py2)), r)

    # Depth indicator — vertical bar
    bar_x = WIDTH - 30
    bar_h = HEIGHT - 200
    bar_y = 100
    pygame.draw.rect(screen, (20, 20, 30), (bar_x, bar_y, 16, bar_h), border_radius=8)
    depth_frac = player["y"] / WORLD_H
    pygame.draw.rect(screen, (60, 150, 220), (bar_x, bar_y, 16, int(bar_h * depth_frac)), border_radius=8)
    marker_y = bar_y + int(bar_h * depth_frac)
    pygame.draw.polygon(screen, (255, 255, 255), [(bar_x - 6, marker_y), (bar_x, marker_y - 4), (bar_x, marker_y + 4)])
    dt_label = fs.render(f"{player['depth']}m", True, (200, 200, 200))
    screen.blit(dt_label, (bar_x - 35, marker_y - 8))

    # ===== HUD =====
    pygame.draw.rect(screen, (5, 10, 20, 200), (0, 0, WIDTH, 55))
    title = ft.render("PLAYTREE UNDERWATER", True, (80, 200, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 8))

    # HP bar
    hp_w = 150
    pygame.draw.rect(screen, (40, 40, 40), (20, 12, hp_w, 16), border_radius=4)
    hp_r = player["hp"] / player["max_hp"]
    hp_c = (50, 200, 50) if hp_r > 0.5 else (200, 200, 50) if hp_r > 0.25 else (200, 50, 50)
    pygame.draw.rect(screen, hp_c, (20, 12, int(hp_w * hp_r), 16), border_radius=4)
    ht = fs.render(f"HP {int(player['hp'])}/{player['max_hp']}", True, (255, 255, 255))
    screen.blit(ht, (24, 13))

    # Oxygen bar
    o2_w = 150
    pygame.draw.rect(screen, (40, 40, 40), (20, 32, o2_w, 14), border_radius=3)
    o2_c = (80, 180, 255) if player["oxygen"] > 50 else (200, 200, 50) if player["oxygen"] > 20 else (200, 80, 80)
    pygame.draw.rect(screen, o2_c, (20, 32, int(o2_w * player["oxygen"] / player["max_oxygen"]), 14), border_radius=3)
    ot = fs.render(f"O2 {int(player['oxygen'])}", True, (200, 220, 255))
    screen.blit(ot, (24, 33))

    # Boost
    boost_w = 100
    pygame.draw.rect(screen, (40, 40, 40), (200, 32, boost_w, 14), border_radius=3)
    pygame.draw.rect(screen, (50, 200, 150), (200, 32, int(boost_w * boost / boost_max), 14), border_radius=3)
    bt = fs.render("BOOST", True, (100, 200, 150))
    screen.blit(bt, (210, 33))

    # Score & collectibles
    sc = fn.render(f"Score: {score}", True, (255, 220, 50))
    screen.blit(sc, (350, 14))
    gd = fs.render(f"Gold:{player['gold']} Gems:{player['gems']} Chests:{player['treasures']}", True, (200, 200, 200))
    screen.blit(gd, (350, 34))
    wv = fs.render(f"Wave: {wave}  Enemies: {len(enemies)}", True, (255, 100, 100))
    screen.blit(wv, (600, 14))

    # Controls
    footer = fs.render("WASD/Left Stick: Move | Shift/A: Boost | Collect gold/gems | Avoid enemies | ESC/Start: quit", True, (50, 70, 90))
    screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 22))

    # Menu
    if game_state == "menu":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        t = ft.render("PLAYTREE UNDERWATER", True, (80, 200, 255))
        sub = fn.render("Explore the deep ocean — survive — collect treasure", True, (180, 180, 180))
        hint = fn.render("Press ENTER to dive", True, (255, 220, 50))
        controls = fs.render("WASD/Left Stick: Move | Shift/A: Boost | Collect gold | Avoid enemies", True, (120, 120, 130))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 80))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 20))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))
        screen.blit(controls, (WIDTH // 2 - controls.get_width() // 2, HEIGHT // 2 + 80))

    # Game over
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        t = ft.render("YOU DROWNED", True, (80, 180, 255))
        d = fn.render(f"Score: {score} | Gold: {player['gold']} | Gems: {player['gems']} | Chests: {player['treasures']}", True, (200, 200, 200))
        h = fn.render("Press R to dive again or ESC to quit", True, (255, 220, 50))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(d, (WIDTH // 2 - d.get_width() // 2, HEIGHT // 2 + 10))
        screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

pygame.quit()
