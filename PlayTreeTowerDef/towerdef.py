"""PlayTree Tower Defense — Strategic tower placement with GoStudios branding"""
import pygame
import sys; sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW"); from game_utils import controller, sfx, sfx_shoot, sfx_hit, sfx_collect, sfx_levelup, sfx_menu_click, sfx_menu_hover, sfx_damage, sfx_game_over, sfx_coin, sfx_explosion
import random
import math

pygame.init()

WIDTH, HEIGHT = 960, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Tower Defense — GoStudios")

TILE = 40
MAP_W, MAP_H = 20, 13

try:
    font_big = pygame.font.SysFont("Segoe UI Semibold", 30)
    font_med = pygame.font.SysFont("Segoe UI", 16)
    font_sm = pygame.font.SysFont("Consolas", 12)
    font_tile = pygame.font.SysFont("Consolas", 10)
except Exception:
    font_big = pygame.font.Font(None, 30)
    font_med = pygame.font.Font(None, 16)
    font_sm = pygame.font.Font(None, 12)
    font_tile = font_sm

TILE_GRASS = 0
TILE_PATH = 1
TILE_TOWER = 2
TILE_BASE = 3

path = []
path_set = set()
path_seq = []

def gen_path():
    global path, path_set, path_seq
    path = []
    path_set = set()
    px, py = 0, MAP_H // 2
    path.append((px, py))
    path_set.add((px, py))
    path_seq = [(px, py)]
    while px < MAP_W - 1:
        r = random.random()
        if r < 0.5 or px >= MAP_W - 3:
            px += 1
        elif r < 0.75:
            ny = max(1, min(MAP_H - 2, py + random.choice([-1, 1])))
            while py != ny:
                py += 1 if ny > py else -1
                path.append((px, py))
                path_set.add((px, py))
                path_seq.append((px, py))
            continue
        else:
            ny = max(1, min(MAP_H - 2, py + random.choice([-1, -1, 1, 1])))
            py = ny
        path.append((px, py))
        path_set.add((px, py))
        path_seq.append((px, py))
    return path

gen_path()

TOWER_TYPES = [
    {'name': 'Arrow', 'cost': 20, 'dmg': 3, 'range': 3.5, 'rate': 0.5, 'color': (126, 211, 33), 'proj_color': (126, 211, 33)},
    {'name': 'Cannon', 'cost': 40, 'dmg': 8, 'range': 2.5, 'rate': 1.5, 'color': (200, 80, 50), 'proj_color': (255, 150, 50)},
    {'name': 'Ice', 'cost': 30, 'dmg': 1, 'range': 3.0, 'rate': 0.3, 'color': (80, 180, 255), 'proj_color': (150, 220, 255), 'slow': True},
    {'name': 'Lightning', 'cost': 50, 'dmg': 5, 'range': 4.0, 'rate': 0.8, 'color': (255, 220, 50), 'proj_color': (255, 255, 150), 'chain': True},
    {'name': 'Poison', 'cost': 35, 'dmg': 2, 'range': 3.0, 'rate': 0.7, 'color': (150, 50, 200), 'proj_color': (200, 100, 255), 'dot': True},
]

gold = 100
lives = 20
wave = 0
wave_active = False
enemies = []
towers = []
projectiles = []
particles = []
selected_tower = 0
hover_tile = None
ctrl_cursor = [MAP_W // 2, MAP_H // 2]
game_state = "menu"
spawn_queue = []
spawn_timer = 0
score = 0
game_over = False

ENEMY_TYPES = [
    {'name': 'Grunt', 'hp': 10, 'speed': 1.0, 'reward': 5, 'color': (200, 80, 80)},
    {'name': 'Runner', 'hp': 6, 'speed': 2.0, 'reward': 7, 'color': (80, 200, 80)},
    {'name': 'Tank', 'hp': 30, 'speed': 0.5, 'reward': 15, 'color': (100, 100, 200)},
    {'name': 'Healer', 'hp': 15, 'speed': 0.8, 'reward': 12, 'color': (200, 200, 100)},
    {'name': 'Boss', 'hp': 100, 'speed': 0.3, 'reward': 50, 'color': (200, 50, 50)},
]

def spawn_wave():
    global wave, wave_active, spawn_queue, spawn_timer
    wave += 1
    wave_active = True
    spawn_queue = []
    available = ENEMY_TYPES[:min(wave, len(ENEMY_TYPES))]
    count = 5 + wave * 3
    for i in range(count):
        t = random.choice(available)
        spawn_queue.append({'type': t, 'delay': i * 0.5})
    spawn_timer = 0

def spawn_enemy(et):
    if path_seq:
        sx, sy = path_seq[0]
        enemies.append({
            'x': sx, 'y': sy,
            'type': et,
            'hp': et['hp'] * (1 + wave * 0.1),
            'max_hp': et['hp'] * (1 + wave * 0.1),
            'speed': et['speed'],
            'reward': et['reward'],
            'color': et['color'],
            'path_idx': 0,
            'slow_timer': 0,
            'dot_timer': 0,
            'dot_dmg': 0,
        })

def update_enemies(dt):
    global lives, score, wave_active, game_over
    for e in enemies[:]:
        if e['slow_timer'] > 0:
            spd = e['speed'] * 0.4
            e['slow_timer'] -= dt
        else:
            spd = e['speed']

        if e['dot_timer'] > 0:
            e['hp'] -= e['dot_dmg'] * dt
            e['dot_timer'] -= dt

        if e['hp'] <= 0:
            score += e['reward'] * 10
            spawn_particles(e['x'], e['y'], e['color'], 8)
            if e['type']['name'] == 'Boss':
                sfx_explosion()
            else:
                sfx_hit()
            enemies.remove(e)
            continue

        if e['path_idx'] < len(path_seq) - 1:
            tx, ty = path_seq[e['path_idx'] + 1]
            dx = tx - e['x']
            dy = ty - e['y']
            dist = math.hypot(dx, dy)
            if dist < 0.1:
                e['path_idx'] += 1
            else:
                e['x'] += dx / dist * spd * dt * 3
                e['y'] += dy / dist * spd * dt * 3
        else:
            lives -= 1
            sfx_damage()
            enemies.remove(e)
            if lives <= 0:
                game_over = True
                sfx_game_over()

    if len(enemies) == 0 and len(spawn_queue) == 0 and wave_active:
        wave_active = False

def update_towers(dt):
    for t in towers:
        t['cd'] = max(0, t['cd'] - dt)
        if t['cd'] <= 0:
            tx, ty = t['x'], t['y']
            best = None
            best_dist = t['range']
            for e in enemies:
                d = math.hypot(e['x'] - tx, e['y'] - ty)
                if d <= t['range'] and (best is None or e['path_idx'] > best['path_idx']):
                    best = e
                    best_dist = d
            if best:
                t['cd'] = t['rate']
                tw = t['type']
                sfx_shoot()
                projectiles.append({
                    'x': tx, 'y': ty,
                    'tx': best['x'], 'ty': best['y'],
                    'target': best,
                    'dmg': tw['dmg'],
                    'speed': 6,
                    'color': tw['proj_color'],
                    'slow': tw.get('slow', False),
                    'chain': tw.get('chain', False),
                    'dot': tw.get('dot', False),
                })

def update_projectiles(dt):
    for p in projectiles[:]:
        dx = p['tx'] - p['x']
        dy = p['ty'] - p['y']
        dist = math.hypot(dx, dy)
        if dist < 0.3 or p['target'] not in enemies:
            if p['target'] in enemies:
                p['target']['hp'] -= p['dmg']
                if p['slow']:
                    p['target']['slow_timer'] = 2
                if p['dot']:
                    p['target']['dot_timer'] = 3
                    p['target']['dot_dmg'] = p['dmg'] * 0.5
                if p['chain']:
                    for e2 in enemies:
                        if e2 is not p['target'] and math.hypot(e2['x'] - p['target']['x'], e2['y'] - p['target']['y']) < 2:
                            e2['hp'] -= p['dmg'] * 0.5
                spawn_particles(p['tx'], p['ty'], p['color'], 3)
            projectiles.remove(p)
        else:
            p['x'] += dx / dist * p['speed']
            p['y'] += dy / dist * p['speed']

def spawn_particles(x, y, color, count=5):
    for _ in range(count):
        a = random.uniform(0, math.pi * 2)
        spd = random.uniform(0.5, 2)
        particles.append({
            'x': x, 'y': y,
            'vx': math.cos(a) * spd, 'vy': math.sin(a) * spd,
            'life': 1.0, 'color': color
        })

def draw_map():
    for y in range(MAP_H):
        for x in range(MAP_W):
            sx, sy = x * TILE, y * TILE + 45
            if (x, y) in path_set:
                pygame.draw.rect(screen, (80, 70, 55), (sx, sy, TILE, TILE))
                pygame.draw.rect(screen, (70, 60, 45), (sx + 1, sy + 1, TILE - 2, TILE - 2))
            else:
                c = (35, 75, 35) if (x + y) % 2 == 0 else (30, 68, 30)
                pygame.draw.rect(screen, c, (sx, sy, TILE, TILE))

    if path_seq:
        pygame.draw.rect(screen, (50, 200, 50), (path_seq[0][0] * TILE + 8, path_seq[0][1] * TILE + 53, TILE - 16, TILE - 16), border_radius=4)
        st = font_sm.render("IN", True, (255, 255, 255))
        screen.blit(st, (path_seq[0][0] * TILE + TILE // 2 - st.get_width() // 2, path_seq[0][1] * TILE + 53 + TILE // 2 - st.get_height() // 2))
        ex, ey = path_seq[-1]
        pygame.draw.rect(screen, (200, 50, 50), (ex * TILE + 8, ey * TILE + 53, TILE - 16, TILE - 16), border_radius=4)
        et = font_sm.render("END", True, (255, 255, 255))
        screen.blit(et, (ex * TILE + TILE // 2 - et.get_width() // 2, ey * TILE + 53 + TILE // 2 - et.get_height() // 2))

def draw_towers():
    for t in towers:
        sx = t['x'] * TILE + TILE // 2
        sy = t['y'] * TILE + 53 + TILE // 2
        tw = t['type']
        pygame.draw.circle(screen, tw['color'], (sx, sy), 14)
        pygame.draw.circle(screen, (20, 20, 20), (sx, sy), 14, 2)
        if t['cd'] < t['rate'] * 0.3:
            pygame.draw.circle(screen, (255, 255, 255, 100), (sx, sy), 16, 1)
        nm = font_tile.render(tw['name'][:3], True, (255, 255, 255))
        screen.blit(nm, (sx - nm.get_width() // 2, sy - nm.get_height() // 2))

def draw_enemies():
    for e in enemies:
        sx = int(e['x'] * TILE + TILE // 2)
        sy = int(e['y'] * TILE + 53 + TILE // 2)
        pygame.draw.circle(screen, e['color'], (sx, sy), 10)
        pygame.draw.circle(screen, (20, 20, 20), (sx, sy), 10, 2)
        hw = 18
        hr = e['hp'] / e['max_hp']
        pygame.draw.rect(screen, (40, 40, 40), (sx - hw // 2, sy - 16, hw, 4))
        pygame.draw.rect(screen, (50, 200, 50) if hr > 0.5 else (200, 200, 50) if hr > 0.25 else (200, 50, 50),
                          (sx - hw // 2, sy - 16, int(hw * hr), 4))
        if e['slow_timer'] > 0:
            pygame.draw.circle(screen, (150, 220, 255), (sx, sy), 12, 2)
        if e['dot_timer'] > 0:
            pygame.draw.circle(screen, (200, 100, 255), (sx, sy), 13, 1)

def draw_projectiles():
    for p in projectiles:
        sx = int(p['x'] * TILE + TILE // 2)
        sy = int(p['y'] * TILE + 53 + TILE // 2)
        pygame.draw.circle(screen, p['color'], (sx, sy), 4)

def draw_particles():
    for p in particles[:]:
        sx = int(p['x'] * TILE + TILE // 2)
        sy = int(p['y'] * TILE + 53 + TILE // 2)
        r = max(1, int(p['life'] * 3))
        pygame.draw.circle(screen, p['color'], (sx, sy), r)
        p['x'] += p['vx'] * 0.02
        p['y'] += p['vy'] * 0.02
        p['life'] -= 0.04
        if p['life'] <= 0:
            particles.remove(p)

def draw_hud():
    pygame.draw.rect(screen, (10, 10, 14, 220), (0, 0, WIDTH, 45))
    t = font_big.render("PLAYTREE TOWER DEFENSE", True, (126, 211, 33))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 6))

    gd = font_med.render(f"Gold: {gold}", True, (255, 220, 50))
    screen.blit(gd, (20, 12))

    lv = font_med.render(f"Lives: {lives}", True, (200, 80, 80) if lives <= 5 else (200, 200, 200))
    screen.blit(lv, (150, 12))

    wv = font_med.render(f"Wave: {wave}", True, (200, 200, 200))
    screen.blit(wv, (300, 12))

    sc = font_med.render(f"Score: {score}", True, (200, 200, 200))
    screen.blit(sc, (450, 12))

    en = font_med.render(f"Enemies: {len(enemies)}", True, (255, 80, 80))
    screen.blit(en, (600, 12))

    pygame.draw.rect(screen, (20, 20, 26), (0, HEIGHT - 55, WIDTH, 55))
    for i, tw in enumerate(TOWER_TYPES):
        bx = 20 + i * 140
        by = HEIGHT - 50
        selected = i == selected_tower
        if selected:
            pygame.draw.rect(screen, tw['color'], (bx, by, 130, 45), border_radius=6)
            tc = (10, 10, 10)
        else:
            pygame.draw.rect(screen, (30, 30, 40), (bx, by, 130, 45), border_radius=6)
            pygame.draw.rect(screen, tw['color'], (bx, by, 130, 45), 1, border_radius=6)
            tc = tw['color']
        nm = font_med.render(tw['name'], True, tc)
        screen.blit(nm, (bx + 8, by + 4))
        cs = font_sm.render(f"{tw['cost']}g", True, (255, 220, 50) if gold >= tw['cost'] else (100, 100, 100))
        screen.blit(cs, (bx + 8, by + 24))
        ds = font_sm.render(f"D:{tw['dmg']} R:{tw['range']}", True, (150, 150, 160))
        screen.blit(ds, (bx + 50, by + 24))

    if not wave_active and not game_over:
        hint = font_med.render("Press SPACE to start next wave", True, (255, 220, 50))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 22))
    else:
        hint = font_sm.render("1-5: Select tower | Click: Place | Right-click: Sell | Ctrl: A=Place B=Sell X/Bumpers=Select Start=ESC", True, (60, 60, 70))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 18))

def draw_hover():
    if hover_tile:
        mx, my = pygame.mouse.get_pos()
        x, y = hover_tile
        sx, sy = x * TILE, y * TILE + 45
        if (x, y) not in path_set and not any(t['x'] == x and t['y'] == y for t in towers):
            tw = TOWER_TYPES[selected_tower]
            if gold >= tw['cost']:
                pygame.draw.rect(screen, (*tw['color'], 40), (sx, sy, TILE, TILE))
                cs = int(tw['range'] * TILE)
                hover_surf = pygame.Surface((cs * 2, cs * 2), pygame.SRCALPHA)
                pygame.draw.circle(hover_surf, (*tw['color'], 30), (cs, cs), cs)
                screen.blit(hover_surf, (sx + TILE // 2 - cs, sy + TILE // 2 - cs))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    t = font_big.render("BASE DESTROYED!", True, (200, 50, 50))
    d = font_med.render(f"Wave: {wave} | Score: {score}", True, (200, 200, 200))
    h = font_med.render("Press R to restart or ESC to quit", True, (255, 220, 50))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(d, (WIDTH // 2 - d.get_width() // 2, HEIGHT // 2))
    screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 40))

def restart():
    global gold, lives, wave, wave_active, enemies, towers, projectiles, particles, score, game_over, spawn_queue, spawn_timer, path, path_set, path_seq
    gen_path()
    gold = 100
    lives = 20
    wave = 0
    wave_active = False
    enemies.clear()
    towers.clear()
    projectiles.clear()
    particles.clear()
    score = 0
    game_over = False
    spawn_queue.clear()
    spawn_timer = 0

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
                restart()
            elif event.key == pygame.K_r and game_over:
                restart()
            elif event.key == pygame.K_SPACE and game_state == "play" and not wave_active and not game_over:
                spawn_wave()
                sfx_menu_click()
            elif game_state == "play":
                if pygame.K_1 <= event.key <= pygame.K_5:
                    selected_tower = event.key - pygame.K_1
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "play" and not game_over:
            mx, my = event.pos
            gx = mx // TILE
            gy = (my - 45) // TILE
            if 0 <= gx < MAP_W and 0 <= gy < MAP_H:
                if event.button == 1:
                    tw = TOWER_TYPES[selected_tower]
                    if (gx, gy) not in path_set and not any(t['x'] == gx and t['y'] == gy for t in towers) and gold >= tw['cost']:
                        gold -= tw['cost']
                        towers.append({
                            'x': gx, 'y': gy,
                            'type': tw, 'cd': 0
                        })
                        sfx_coin()
                elif event.button == 3:
                    for t in towers:
                        if t['x'] == gx and t['y'] == gy:
                            gold += t['type']['cost'] // 2
                            towers.remove(t)
                            break

    # --- Controller input ---
    if game_state == "menu":
        if controller.btn_start_pressed():
            game_state = "play"
            restart()
        if controller.btn_a_pressed():
            game_state = "play"
            restart()
    elif game_over:
        if controller.btn_start_pressed() or controller.btn_a_pressed():
            restart()
    else:
        stick_x, stick_y = controller.left_stick()
        dead = 0.3
        if abs(stick_x) > dead:
            ctrl_cursor[0] = max(0, min(MAP_W - 1, ctrl_cursor[0] + (1 if stick_x > 0 else -1)))
        if abs(stick_y) > dead:
            ctrl_cursor[1] = max(0, min(MAP_H - 1, ctrl_cursor[1] + (1 if stick_y > 0 else -1)))
        if controller.dpad_up_pressed():
            ctrl_cursor[1] = max(0, ctrl_cursor[1] - 1)
        if controller.dpad_down_pressed():
            ctrl_cursor[1] = min(MAP_H - 1, ctrl_cursor[1] + 1)
        if controller.dpad_left_pressed():
            ctrl_cursor[0] = max(0, ctrl_cursor[0] - 1)
        if controller.dpad_right_pressed():
            ctrl_cursor[0] = min(MAP_W - 1, ctrl_cursor[0] + 1)
        cx, cy = ctrl_cursor
        hover_tile = (cx, cy)
        if controller.btn_start_pressed():
            game_state = "menu"
        elif controller.btn_a_pressed():
            if not wave_active and not game_over:
                spawn_wave()
                sfx_menu_click()
            elif not game_over:
                tw = TOWER_TYPES[selected_tower]
                if (cx, cy) not in path_set and not any(t['x'] == cx and t['y'] == cy for t in towers) and gold >= tw['cost']:
                    gold -= tw['cost']
                    towers.append({'x': cx, 'y': cy, 'type': tw, 'cd': 0})
                    sfx_coin()
        if controller.btn_b_pressed():
            for t in towers:
                if t['x'] == cx and t['y'] == cy:
                    gold += t['type']['cost'] // 2
                    towers.remove(t)
                    break
        if controller.btn_x_pressed():
            selected_tower = (selected_tower + 1) % len(TOWER_TYPES)
        if controller.right_bumper_pressed():
            selected_tower = (selected_tower + 1) % len(TOWER_TYPES)
        if controller.left_bumper_pressed():
            selected_tower = (selected_tower - 1) % len(TOWER_TYPES)

    if game_state == "play" and not game_over:
        mx, my = pygame.mouse.get_pos()
        gx = mx // TILE
        gy = (my - 45) // TILE
        if 0 <= gx < MAP_W and 0 <= gy < MAP_H:
            hover_tile = (gx, gy)
        else:
            hover_tile = None

        if spawn_queue:
            spawn_timer += dt
            while spawn_queue and spawn_timer >= spawn_queue[0]['delay']:
                se = spawn_queue.pop(0)
                spawn_enemy(se['type'])

        update_enemies(dt)
        update_towers(dt)
        update_projectiles(dt)

    screen.fill((15, 15, 20))
    draw_map()
    draw_towers()
    draw_enemies()
    draw_projectiles()
    draw_particles()
    draw_hover()
    draw_hud()

    if game_over:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
