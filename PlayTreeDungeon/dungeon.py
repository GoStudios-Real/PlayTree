"""PlayTree Dungeon — Roguelike dungeon crawler with GoStudios branding"""
import pygame
import sys
sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW")
from game_utils import controller, sfx, sfx_shoot, sfx_hit, sfx_collect, sfx_levelup, sfx_menu_click, sfx_menu_hover, sfx_damage, sfx_game_over, sfx_coin, sfx_footstep
import random
import math

pygame.init()

WIDTH, HEIGHT = 960, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Dungeon — GoStudios")

TILE = 48
MAP_W, MAP_H = 20, 15

try:
    font_big = pygame.font.SysFont("Segoe UI Semibold", 32)
    font_med = pygame.font.SysFont("Segoe UI", 18)
    font_sm = pygame.font.SysFont("Consolas", 13)
    font_tile = pygame.font.SysFont("Consolas", 20, bold=True)
except Exception:
    font_big = pygame.font.Font(None, 32)
    font_med = pygame.font.Font(None, 18)
    font_sm = pygame.font.Font(None, 13)
    font_tile = pygame.font.Font(None, 20)

TILE_FLOOR = 0
TILE_WALL = 1
TILE_DOOR = 2
TILE_STAIRS = 3

PLAYER_COLOR = (126, 211, 33)
ENEMY_COLORS = {
    'slime': (60, 200, 60),
    'skeleton': (220, 220, 200),
    'demon': (200, 50, 50),
    'shadow': (80, 40, 120),
    'golem': (140, 120, 100),
}

def gen_dungeon():
    m = [[TILE_WALL] * MAP_W for _ in range(MAP_H)]
    rooms = []
    for _ in range(50):
        rw = random.randint(3, 6)
        rh = random.randint(3, 5)
        rx = random.randint(1, MAP_W - rw - 1)
        ry = random.randint(1, MAP_H - rh - 1)
        overlap = False
        for ox, oy, ow, oh in rooms:
            if rx < ox + ow + 1 and rx + rw + 1 > ox and ry < oy + oh + 1 and ry + rh + 1 > oy:
                overlap = True
                break
        if not overlap:
            rooms.append((rx, ry, rw, rh))
            for yy in range(ry, ry + rh):
                for xx in range(rx, rx + rw):
                    m[yy][xx] = TILE_FLOOR
    for i in range(len(rooms) - 1):
        x1, y1, _, _ = rooms[i]
        x2, y2, _, _ = rooms[i + 1]
        cx1 = x1 + rooms[i][2] // 2
        cy1 = y1 + rooms[i][3] // 2
        cx2 = x2 + rooms[i + 1][2] // 2
        cy2 = y2 + rooms[i + 1][3] // 2
        for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
            m[cy1][x] = TILE_FLOOR
        for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
            m[y][cx2] = TILE_FLOOR

    if rooms:
        lx, ly = rooms[-1]
        m[ly + rooms[-1][3] // 2][lx + rooms[-1][2] // 2] = TILE_STAIRS

    return m, rooms

def spawn_enemies(rooms, floor):
    enemies = []
    types = ['slime', 'skeleton', 'demon', 'shadow', 'golem']
    available = types[:min(floor + 1, len(types))]
    for rx, ry, rw, rh in rooms[1:]:
        count = random.randint(1, min(3, floor + 1))
        for _ in range(count):
            ex = random.randint(rx, rx + rw - 1)
            ey = random.randint(ry, ry + rh - 1)
            t = random.choice(available)
            enemies.append({
                'x': ex, 'y': ey, 'type': t,
                'hp': 2 + floor, 'max_hp': 2 + floor,
                'dmg': 1 + floor // 2,
                'color': ENEMY_COLORS[t],
                'move_timer': 0,
            })
    return enemies

def spawn_items(rooms, floor):
    items = []
    for rx, ry, rw, rh in rooms[2:]:
        if random.random() < 0.4:
            ix = random.randint(rx, rx + rw - 1)
            iy = random.randint(ry, ry + rh - 1)
            kind = random.choice(['hp', 'atk', 'coin'])
            items.append({'x': ix, 'y': iy, 'kind': kind})
    return items

dungeon, rooms = gen_dungeon()
floor = 1
player = {
    'x': rooms[0][0] + rooms[0][2] // 2,
    'y': rooms[0][1] + rooms[0][3] // 2,
    'hp': 20, 'max_hp': 20,
    'atk': 3,
    'xp': 0,
    'level': 1,
    'gold': 0,
}
enemies = spawn_enemies(rooms, floor)
items = spawn_items(rooms, floor)
messages = []
turn = 0
animating = False
anim_queue = []
game_over = False
victory = False
player_dir = (0, -1)
camera_x = 0
camera_y = 0


def add_msg(text, color=(200, 200, 200)):
    messages.append((text, color))
    if len(messages) > 6:
        messages.pop(0)


def move_enemies():
    global game_over
    for e in enemies:
        e['move_timer'] += 1
        if e['move_timer'] < 2:
            continue
        e['move_timer'] = 0
        dx = player['x'] - e['x']
        dy = player['y'] - e['y']
        dist = abs(dx) + abs(dy)
        if dist <= 1:
            player['hp'] -= e['dmg']
            add_msg(f"{e['type'].title()} hits you for {e['dmg']}!", (255, 80, 80))
            sfx_damage()
            if player['hp'] <= 0:
                player['hp'] = 0
                game_over = True
                sfx_game_over()
        elif dist < 8:
            mx = 0 if dx == 0 else (1 if dx > 0 else -1)
            my = 0 if dy == 0 else (1 if dy > 0 else -1)
            nx, ny = e['x'] + mx, e['y'] + my
            if 0 <= nx < MAP_W and 0 <= ny < MAP_H and dungeon[ny][nx] == TILE_FLOOR:
                blocked = any(oo['x'] == nx and oo['y'] == ny for oo in enemies if oo is not e)
                if not blocked and not (nx == player['x'] and ny == player['y']):
                    e['x'], e['y'] = nx, ny


def player_attack(dx, dy):
    global turn
    nx, ny = player['x'] + dx, player['y'] + dy
    for e in enemies:
        if e['x'] == nx and e['y'] == ny:
            dmg = player['atk'] + random.randint(0, 2)
            e['hp'] -= dmg
            add_msg(f"You hit {e['type']} for {dmg}!", (126, 211, 33))
            sfx_hit()
            if e['hp'] <= 0:
                xp_gain = 5 + floor * 2
                gold_gain = random.randint(1, 5 + floor)
                player['xp'] += xp_gain
                player['gold'] += gold_gain
                add_msg(f"{e['type'].title()} defeated! +{xp_gain}xp +{gold_gain}g", (255, 220, 50))
                if player['xp'] >= player['level'] * 15:
                    player['level'] += 1
                    player['max_hp'] += 5
                    player['hp'] = player['max_hp']
                    player['atk'] += 1
                    add_msg(f"LEVEL UP! Now level {player['level']}!", (200, 120, 255))
                    sfx_levelup()
                enemies.remove(e)
            turn += 1
            move_enemies()
            check_items()
            return True
    return False


def try_move(dx, dy):
    global turn
    nx, ny = player['x'] + dx, player['y'] + dy
    if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
        tile = dungeon[ny][nx]
        if tile == TILE_FLOOR or tile == TILE_STAIRS:
            blocked = any(e['x'] == nx and e['y'] == ny for e in enemies)
            if not blocked:
                player['x'], player['y'] = nx, ny
                player_dir = (dx, dy)
                sfx_footstep()
                turn += 1
                move_enemies()
                check_items()
                if tile == TILE_STAIRS:
                    next_floor()
                return True
            else:
                return player_attack(dx, dy)
    return False


def check_items():
    for it in items[:]:
        if it['x'] == player['x'] and it['y'] == player['y']:
            if it['kind'] == 'hp':
                heal = 5 + floor
                player['hp'] = min(player['max_hp'], player['hp'] + heal)
                add_msg(f"Found health potion! +{heal} HP", (50, 200, 50))
                sfx_collect()
            elif it['kind'] == 'atk':
                player['atk'] += 1
                add_msg("Found attack scroll! +1 ATK", (255, 120, 50))
                sfx_collect()
            elif it['kind'] == 'coin':
                g = random.randint(5, 15)
                player['gold'] += g
                add_msg(f"Found {g} gold!", (255, 220, 50))
                sfx_coin()
            items.remove(it)


def next_floor():
    global dungeon, rooms, enemies, items, floor, game_over, victory
    floor += 1
    if floor > 10:
        victory = True
        return
    dungeon, rooms = gen_dungeon()
    player['x'] = rooms[0][0] + rooms[0][2] // 2
    player['y'] = rooms[0][1] + rooms[0][3] // 2
    enemies = spawn_enemies(rooms, floor)
    items = spawn_items(rooms, floor)
    add_msg(f"Floor {floor} — Deeper into the dungeon...", (200, 120, 255))


def draw_map():
    cam_x = player['x'] * TILE - WIDTH // 2 + TILE // 2
    cam_y = player['y'] * TILE - HEIGHT // 2 + TILE // 2

    for y in range(MAP_H):
        for x in range(MAP_W):
            sx = x * TILE - cam_x
            sy = y * TILE - cam_y
            if sx < -TILE or sx > WIDTH or sy < -TILE or sy > HEIGHT:
                continue
            tile = dungeon[y][x]
            if tile == TILE_WALL:
                pygame.draw.rect(screen, (30, 28, 35), (sx, sy, TILE, TILE))
                pygame.draw.rect(screen, (20, 18, 25), (sx + 1, sy + 1, TILE - 2, TILE - 2))
            elif tile == TILE_FLOOR:
                c = (50, 48, 55) if (x + y) % 2 == 0 else (45, 43, 50)
                pygame.draw.rect(screen, c, (sx, sy, TILE, TILE))
            elif tile == TILE_STAIRS:
                pygame.draw.rect(screen, (50, 48, 55), (sx, sy, TILE, TILE))
                st = font_tile.render(">", True, (255, 220, 50))
                screen.blit(st, (sx + TILE // 2 - st.get_width() // 2, sy + TILE // 2 - st.get_height() // 2))

    for it in items:
        sx = it['x'] * TILE - cam_x + TILE // 2
        sy = it['y'] * TILE - cam_y + TILE // 2
        if it['kind'] == 'hp':
            pygame.draw.circle(screen, (50, 200, 50), (sx, sy), 8)
        elif it['kind'] == 'atk':
            pygame.draw.circle(screen, (255, 120, 50), (sx, sy), 8)
        elif it['kind'] == 'coin':
            pygame.draw.circle(screen, (255, 220, 50), (sx, sy), 8)

    for e in enemies:
        sx = e['x'] * TILE - cam_x + TILE // 2
        sy = e['y'] * TILE - cam_y + TILE // 2
        pygame.draw.circle(screen, e['color'], (sx, sy), 14)
        pygame.draw.circle(screen, (20, 20, 20), (sx, sy), 14, 2)
        hp_w = 20
        hp_r = e['hp'] / e['max_hp']
        pygame.draw.rect(screen, (40, 40, 40), (sx - hp_w // 2, sy - 22, hp_w, 4))
        pygame.draw.rect(screen, (200, 50, 50), (sx - hp_w // 2, sy - 22, int(hp_w * hp_r), 4))
        nm = font_sm.render(e['type'][:4], True, (255, 255, 255))
        screen.blit(nm, (sx - nm.get_width() // 2, sy - 34))

    psx = player['x'] * TILE - cam_x + TILE // 2
    psy = player['y'] * TILE - cam_y + TILE // 2
    glow = pygame.Surface((TILE + 10, TILE + 10), pygame.SRCALPHA)
    pygame.draw.circle(glow, (126, 211, 33, 40), (TILE // 2 + 5, TILE // 2 + 5), TILE // 2 + 5)
    screen.blit(glow, (psx - TILE // 2 - 5, psy - TILE // 2 - 5))
    pygame.draw.circle(screen, PLAYER_COLOR, (psx, psy), 12)
    pygame.draw.circle(screen, (80, 160, 30), (psx, psy), 12, 2)
    ex = int(psx + player_dir[0] * 8)
    ey = int(psy + player_dir[1] * 8)
    pygame.draw.circle(screen, (200, 255, 200), (ex, ey), 3)


def draw_hud():
    pygame.draw.rect(screen, (10, 10, 14, 220), (0, 0, WIDTH, 50))
    t = font_big.render("PLAYTREE DUNGEON", True, (126, 211, 33))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 8))

    fl = font_med.render(f"Floor {floor}", True, (200, 120, 255))
    screen.blit(fl, (20, 14))

    hp_bar_w = 120
    pygame.draw.rect(screen, (40, 40, 40), (120, 16, hp_bar_w, 18), border_radius=4)
    hp_r = player['hp'] / player['max_hp']
    hp_c = (50, 200, 50) if hp_r > 0.5 else (200, 200, 50) if hp_r > 0.25 else (200, 50, 50)
    pygame.draw.rect(screen, hp_c, (120, 16, int(hp_bar_w * hp_r), 18), border_radius=4)
    ht = font_sm.render(f"HP {player['hp']}/{player['max_hp']}", True, (255, 255, 255))
    screen.blit(ht, (124, 17))

    at = font_med.render(f"ATK:{player['atk']}  LV:{player['level']}  XP:{player['xp']}", True, (255, 200, 50))
    screen.blit(at, (320, 14))

    gd = font_med.render(f"Gold:{player['gold']}", True, (255, 220, 50))
    screen.blit(gd, (600, 14))

    en = font_med.render(f"Enemies:{len(enemies)}", True, (255, 80, 80))
    screen.blit(en, (730, 14))

    pygame.draw.rect(screen, (10, 10, 14, 180), (0, HEIGHT - 120, WIDTH, 120))
    for i, (msg, col) in enumerate(messages[-6:]):
        mt = font_sm.render(msg, True, col)
        screen.blit(mt, (20, HEIGHT - 115 + i * 18))

    footer = font_sm.render("Arrow keys: Move/Attack | Collect items | > = stairs | ESC quit", True, (60, 60, 70))
    screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 16))


def draw_death():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    t = font_big.render("YOU DIED", True, (200, 50, 50))
    d = font_med.render(f"Floor {floor} | Gold: {player['gold']} | Level: {player['level']}", True, (200, 200, 200))
    h = font_med.render("Press R to restart or ESC to quit", True, (255, 220, 50))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(d, (WIDTH // 2 - d.get_width() // 2, HEIGHT // 2))
    screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 40))


def draw_victory():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    t = font_big.render("DUNGEON CLEARED!", True, (126, 211, 33))
    d = font_med.render(f"Gold: {player['gold']} | Level: {player['level']}", True, (200, 200, 200))
    h = font_med.render("Press R to play again or ESC to quit", True, (255, 220, 50))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(d, (WIDTH // 2 - d.get_width() // 2, HEIGHT // 2))
    screen.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT // 2 + 40))


def restart():
    global dungeon, rooms, enemies, items, floor, turn, messages, game_over, victory, player_dir
    dungeon, rooms = gen_dungeon()
    floor = 1
    player['x'] = rooms[0][0] + rooms[0][2] // 2
    player['y'] = rooms[0][1] + rooms[0][3] // 2
    player['hp'] = 20
    player['max_hp'] = 20
    player['atk'] = 3
    player['xp'] = 0
    player['level'] = 1
    player['gold'] = 0
    enemies = spawn_enemies(rooms, floor)
    items = spawn_items(rooms, floor)
    messages = []
    turn = 0
    game_over = False
    victory = False
    player_dir = (0, -1)
    add_msg("You enter the dungeon...", (200, 120, 255))


clock = pygame.time.Clock()
controller.init()
running = True
move_delay = 0

while running:
    dt = clock.tick(60) / 1000.0
    move_delay = max(0, move_delay - dt)
    controller.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and (game_over or victory):
                restart()
            elif not game_over and not victory:
                dx, dy = 0, 0
                if event.key in (pygame.K_UP, pygame.K_w):
                    dx, dy = 0, -1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    dx, dy = 0, 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    dx, dy = -1, 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    dx, dy = 1, 0
                if dx != 0 or dy != 0:
                    try_move(dx, dy)

    # Controller input
    if not game_over and not victory:
        lx = controller.get_axis('left_x')
        ly = controller.get_axis('left_y')
        deadzone = 0.5
        if move_delay <= 0:
            if abs(lx) > deadzone or abs(ly) > deadzone:
                if abs(lx) > abs(ly):
                    try_move(1 if lx > 0 else -1, 0)
                else:
                    try_move(0, 1 if ly > 0 else -1)
                move_delay = 0.15
        if controller.get_button_pressed('a'):
            dx, dy = player_dir
            player_attack(dx, dy)
        if controller.get_button_pressed('x'):
            if dungeon[player['y']][player['x']] == TILE_STAIRS:
                next_floor()
    if controller.get_button_pressed('start'):
        running = False
    if controller.get_button_pressed('y') and (game_over or victory):
        restart()

    screen.fill((15, 15, 20))
    draw_map()
    draw_hud()

    if game_over:
        draw_death()
    elif victory:
        draw_victory()

    pygame.display.flip()

pygame.quit()
