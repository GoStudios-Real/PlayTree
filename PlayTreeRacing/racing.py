"""PlayTree Racing — Top-down arcade racer with GoStudios branding"""
import pygame
import sys
import random
import math
sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW")
from game_utils import controller, sfx, sfx_shoot, sfx_hit, sfx_collect, sfx_levelup, sfx_menu_click, sfx_menu_hover, sfx_damage, sfx_game_over, sfx_coin, sfx_engine, sfx_splash

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Racing — GoStudios")

BG = (30, 120, 30)
ROAD_COLOR = (60, 60, 65)
ROAD_LINE = (200, 200, 50)

try:
    font_big = pygame.font.SysFont("Segoe UI Semibold", 36)
    font_med = pygame.font.SysFont("Segoe UI", 22)
    font_sm = pygame.font.SysFont("Consolas", 14)
except Exception:
    font_big = pygame.font.Font(None, 36)
    font_med = pygame.font.Font(None, 22)
    font_sm = pygame.font.Font(None, 14)

ROAD_LEFT = 200
ROAD_RIGHT = 700
ROAD_W = ROAD_RIGHT - ROAD_LEFT
CAR_W, CAR_H = 30, 50

player_x = WIDTH // 2
player_y = HEIGHT - 120
player_speed = 0
player_max_speed = 7
player_accel = 0.12
player_decel = 0.06
player_turn = 4.0
player_laps = 0
player_dist = 0

opponents = []
for i in range(8):
    ox = ROAD_LEFT + 30 + (i % 4) * (ROAD_W // 4)
    oy = 100 + i * 80 + random.randint(-20, 20)
    opponents.append({
        'x': ox, 'y': oy,
        'speed': random.uniform(2, 5),
        'color': random.choice([(220, 50, 50), (50, 50, 220), (220, 220, 50), (220, 120, 50), (50, 200, 200)]),
        'offset': 0,
    })

scroll = 0
trees = []
for _ in range(60):
    side = random.choice([-1, 1])
    tx = (ROAD_LEFT - 40) * (side == -1) + (ROAD_RIGHT + 40) * (side == 1) + random.randint(-80, 80)
    ty = random.randint(0, 2000)
    trees.append({'x': tx, 'y': ty, 'size': random.randint(15, 30), 'side': side})

speed_lines = []
score = 0
lap_time = 0
best_lap = 999
game_time = 0
fuel = 100
boost = 100
damage = 0
nitro_active = False
game_state = "menu"
race_started = False
countdown = 3
countdown_timer = 0


def draw_road():
    offset = int(scroll) % 100
    for x in range(int(ROAD_LEFT), int(ROAD_RIGHT), 3):
        stripe = ((x - ROAD_LEFT) // 30 + offset // 30) % 2
        c = (55, 55, 60) if stripe else (65, 65, 70)
        pygame.draw.line(screen, c, (x, 0), (x, HEIGHT))
    pygame.draw.line(screen, ROAD_LINE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
    pygame.draw.line(screen, ROAD_LINE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)

    center = (ROAD_LEFT + ROAD_RIGHT) // 2
    for y in range(-offset % 80, HEIGHT, 80):
        pygame.draw.rect(screen, ROAD_LINE, (center - 2, y, 4, 40))


def draw_car(x, y, color, w=CAR_W, h=CAR_H, is_player=False):
    car = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(car, color, (0, 0, w, h), border_radius=6)
    pygame.draw.rect(car, (255, 255, 255, 80), (3, 3, w - 6, h // 3), border_radius=4)
    if is_player:
        pygame.draw.rect(car, (255, 50, 50), (w // 2 - 3, h - 8, 6, 8), border_radius=2)
        pygame.draw.rect(car, (255, 50, 50), (4, h - 10, 5, 6), border_radius=2)
        pygame.draw.rect(car, (255, 50, 50), (w - 9, h - 10, 5, 6), border_radius=2)
        glow = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (126, 211, 33, 30), (0, 0, w + 8, h + 8), border_radius=8)
        screen.blit(glow, (x - 4, y - 4))
    else:
        pygame.draw.rect(car, (200, 200, 200, 60), (w // 2 - 2, 2, 4, 8), border_radius=2)
    screen.blit(car, (x - w // 2, y - h // 2))


def draw_tree(tx, ty, size):
    tx_screen = tx - player_x + WIDTH // 2
    ty_screen = (ty - scroll) % 2000 - 200
    if -50 < ty_screen < HEIGHT + 50:
        pygame.draw.circle(screen, (20, 80, 20), (int(tx_screen), int(ty_screen)), size)
        pygame.draw.circle(screen, (30, 100, 30), (int(tx_screen), int(ty_screen) - size // 2), size // 2)


def draw_hud():
    pygame.draw.rect(screen, (10, 10, 14, 200), (0, 0, WIDTH, 50))
    title = font_big.render("PLAYTREE RACING", True, (126, 211, 33))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 8))

    spd = abs(int(player_speed * 30))
    sp = font_med.render(f"{spd} km/h", True, (255, 255, 255))
    screen.blit(sp, (20, 12))

    sc = font_med.render(f"Score: {score}", True, (255, 220, 50))
    screen.blit(sc, (200, 12))

    lap = font_med.render(f"Lap: {player_laps}", True, (200, 200, 200))
    screen.blit(lap, (400, 12))

    fuel_bar_w = 100
    pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 240, 14, fuel_bar_w, 16), border_radius=4)
    fc = (50, 200, 50) if fuel > 50 else (200, 200, 50) if fuel > 20 else (200, 50, 50)
    pygame.draw.rect(screen, fc, (WIDTH - 240, 14, int(fuel_bar_w * fuel / 100), 16), border_radius=4)
    ft = font_sm.render("FUEL", True, (150, 150, 150))
    screen.blit(ft, (WIDTH - 130, 16))

    boost_bar_w = 80
    pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 120, 14, boost_bar_w, 16), border_radius=4)
    pygame.draw.rect(screen, (80, 180, 255), (WIDTH - 120, 14, int(boost_bar_w * boost / 100), 16), border_radius=4)
    bt = font_sm.render("NOS", True, (150, 150, 150))
    screen.blit(bt, (WIDTH - 35, 16))

    footer = font_sm.render("WASD/Arrows: Drive | Space: Nitro | ESC quit | Controller supported", True, (80, 80, 90))
    screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 28))


def draw_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    t = font_big.render("PLAYTREE RACING", True, (126, 211, 33))
    sub = font_med.render("Top-down arcade racing", True, (180, 180, 180))
    hint = font_med.render("Press ENTER to start", True, (255, 220, 50))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 10))
    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 40))


clock = pygame.time.Clock()
controller.init()
running = True

while running:
    dt = clock.tick(60) / 1000.0
    game_time += dt
    controller.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN and game_state == "menu":
                sfx.play("menu_click", sfx_menu_click)
                game_state = "race"
                race_started = False
                countdown = 3
                countdown_timer = 0
                player_x = WIDTH // 2
                player_speed = 0
                player_laps = 0
                player_dist = 0
                score = 0
                fuel = 100
                boost = 100
                damage = 0
                scroll = 0
                for i, op in enumerate(opponents):
                    op['y'] = 100 + i * 80
                    op['x'] = ROAD_LEFT + 30 + (i % 4) * (ROAD_W // 4)

    keys = pygame.key.get_pressed()

    if game_state == "menu" and controller.get_button(7):
        sfx.play("menu_click", sfx_menu_click)
        game_state = "race"
        race_started = False
        countdown = 3
        countdown_timer = 0
        player_x = WIDTH // 2
        player_speed = 0
        player_laps = 0
        player_dist = 0
        score = 0
        fuel = 100
        boost = 100
        damage = 0
        scroll = 0
        for i, op in enumerate(opponents):
            op['y'] = 100 + i * 80
            op['x'] = ROAD_LEFT + 30 + (i % 4) * (ROAD_W // 4)

    if game_state == "race":
        if not race_started:
            countdown_timer += dt
            if countdown_timer >= 1:
                countdown_timer = 0
                countdown -= 1
                if countdown <= 0:
                    race_started = True

        if race_started:
            turning = False
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                player_x -= player_turn
                turning = True
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                player_x += player_turn
                turning = True

            stick_x = controller.get_axis(0)
            if abs(stick_x) > 0.15:
                player_x += stick_x * player_turn
                turning = True

            player_x = max(ROAD_LEFT + CAR_W // 2, min(ROAD_RIGHT - CAR_W // 2, player_x))

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                player_speed = min(player_speed + player_accel, player_max_speed)
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                player_speed = max(player_speed - player_accel, -player_max_speed * 0.4)
            else:
                if player_speed > 0:
                    player_speed = max(0, player_speed - player_decel)
                elif player_speed < 0:
                    player_speed = min(0, player_speed + player_decel)

            rt = controller.get_axis(5)
            lt = controller.get_axis(4)
            if rt > 0.1:
                player_speed = min(player_speed + player_accel * rt, player_max_speed)
            elif lt > 0.1:
                player_speed = max(player_speed - player_accel * lt, -player_max_speed * 0.4)

            if (keys[pygame.K_SPACE] or controller.get_button(0)) and boost > 0:
                nitro_active = True
                player_speed = min(player_speed + 0.3, player_max_speed * 1.6)
                boost -= dt * 30
            else:
                nitro_active = False

            fuel -= dt * (2 + abs(player_speed) * 0.5)
            if fuel <= 0:
                fuel = 0
                player_speed *= 0.95

            scroll += player_speed
            player_dist += abs(player_speed)

            if player_dist > 3000:
                player_laps += 1
                player_dist = 0
                score += 500
                sfx.play("collect", sfx_collect)

            for op in opponents:
                op['y'] += op['speed'] - player_speed * 0.5
                op['offset'] = math.sin(game_time * 2 + op['x']) * 0.5
                op['x'] += op['offset']
                op['x'] = max(ROAD_LEFT + 25, min(ROAD_RIGHT - 25, op['x']))

                if op['y'] > HEIGHT + 50:
                    op['y'] = -80
                    op['x'] = ROAD_LEFT + 30 + random.randint(0, 3) * (ROAD_W // 4)
                    score += 50
                    sfx.play("collect", sfx_collect)

                dx = player_x - op['x']
                dy = (HEIGHT - 120) - op['y']
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 40:
                    player_speed *= 0.7
                    damage += 10
                    sfx.play("hit", sfx_hit)
                    op['y'] = -80
                    score = max(0, score - 20)

            speed_lines.clear()
            if abs(player_speed) > 3:
                for _ in range(int(abs(player_speed))):
                    speed_lines.append({
                        'x': random.randint(ROAD_LEFT + 5, ROAD_RIGHT - 5),
                        'y': random.randint(0, HEIGHT),
                        'l': random.randint(10, 30)
                    })

    screen.fill(BG)
    draw_road()

    for t in trees:
        draw_tree(t['x'], t['y'], t['size'])

    for op in opponents:
        draw_car(op['x'], (op['y'] - scroll) % 2000 - 200, op['color'])

    draw_car(player_x, HEIGHT - 120, (126, 211, 33), is_player=True)

    if nitro_active:
        for _ in range(3):
            pygame.draw.circle(screen, (255, 150, 30),
                               (int(player_x + random.randint(-8, 8)),
                                int(HEIGHT - 120 + 30 + random.randint(0, 15))),
                               random.randint(2, 5))

    for sl in speed_lines:
        pygame.draw.line(screen, (200, 200, 200), (sl['x'], sl['y']), (sl['x'], sl['y'] + sl['l']), 1)

    draw_hud()

    if game_state == "menu":
        draw_menu()
    elif game_state == "race" and not race_started:
        cd_text = font_big.render(str(max(countdown, 1)), True, (255, 220, 50))
        screen.blit(cd_text, (WIDTH // 2 - cd_text.get_width() // 2, HEIGHT // 2 - 40))

    pygame.display.flip()

pygame.quit()
