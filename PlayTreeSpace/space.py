"""PlayTree Space — Twin-stick space shooter with GoStudios branding"""
import pygame
import sys
sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW")
from game_utils import controller, sfx, sfx_shoot, sfx_hit, sfx_collect, sfx_levelup, sfx_menu_click, sfx_menu_hover, sfx_damage, sfx_game_over, sfx_coin, sfx_laser, sfx_explosion, sfx_powerup
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Space — GoStudios")

try:
    font_big = pygame.font.SysFont("Segoe UI Semibold", 32)
    font_med = pygame.font.SysFont("Segoe UI", 18)
    font_sm = pygame.font.SysFont("Consolas", 13)
except Exception:
    font_big = pygame.font.Font(None, 32)
    font_med = pygame.font.Font(None, 18)
    font_sm = pygame.font.Font(None, 13)

stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.5, 2.0), random.randint(40, 120)) for _ in range(150)]

player = {'x': WIDTH // 2, 'y': HEIGHT // 2, 'hp': 10, 'max_hp': 10, 'speed': 4, 'angle': 0, 'fire_rate': 0.15, 'fire_cd': 0, 'weapon': 0, 'shield': 0}
bullets = []
enemy_bullets = []
enemies = []
particles = []
powerups = []
score = 0
wave = 1
wave_timer = 0
game_state = "menu"
weapons = ["Laser", "Spread", "Missile", "Beam"]
WEAPON_COLORS = [(126, 211, 33), (80, 180, 255), (255, 120, 40), (200, 80, 255)]
shake = 0


def spawn_wave():
    global wave, wave_timer
    wave_timer = 0
    types = [
        ('scout', 20, 30, (60, 200, 60), 2),
        ('fighter', 40, 60, (60, 120, 200), 3),
        ('tank', 80, 120, (200, 60, 60), 5),
        ('bomber', 30, 50, (200, 200, 50), 4),
        ('elite', 100, 150, (150, 50, 200), 6),
    ]
    available = types[:min(wave, len(types))]
    count = 3 + wave * 2
    for _ in range(count):
        t = random.choice(available)
        side = random.randint(0, 3)
        if side == 0:
            ex, ey = random.randint(0, WIDTH), -30
        elif side == 1:
            ex, ey = WIDTH + 30, random.randint(0, HEIGHT)
        elif side == 2:
            ex, ey = random.randint(0, WIDTH), HEIGHT + 30
        else:
            ex, ey = -30, random.randint(0, HEIGHT)
        enemies.append({
            'x': ex, 'y': ey, 'type': t[0], 'hp': t[1], 'max_hp': t[1],
            'speed': t[3] * 0.5, 'color': t[4], 'dmg': t[2], 'score': t[3] * 10,
            'angle': 0, 'shoot_cd': random.uniform(1, 3),
        })


def spawn_powerup(x, y):
    if random.random() < 0.15:
        kind = random.choice(['hp', 'weapon', 'shield'])
        powerups.append({'x': x, 'y': y, 'kind': kind, 'life': 10})


def fire_weapon():
    global shake
    player['fire_cd'] = player['fire_rate']
    wx, wy = player['x'], player['y']
    px, py = pygame.mouse.get_pos()
    angle = math.atan2(py - wy, px - wx)

    shake = 2
    sfx.play('shoot', sfx_shoot)
    w = player['weapon']

    if w == 0:
        bullets.append({
            'x': wx, 'y': wy,
            'vx': math.cos(angle) * 10, 'vy': math.sin(angle) * 10,
            'dmg': 2, 'life': 60, 'color': WEAPON_COLORS[0], 'size': 3
        })
    elif w == 1:
        for off in [-0.2, -0.1, 0, 0.1, 0.2]:
            bullets.append({
                'x': wx, 'y': wy,
                'vx': math.cos(angle + off) * 9, 'vy': math.sin(angle + off) * 9,
                'dmg': 1.5, 'life': 45, 'color': WEAPON_COLORS[1], 'size': 2
            })
    elif w == 2:
        bullets.append({
            'x': wx, 'y': wy,
            'vx': math.cos(angle) * 7, 'vy': math.sin(angle) * 7,
            'dmg': 8, 'life': 80, 'color': WEAPON_COLORS[2], 'size': 5
        })
    elif w == 3:
        bullets.append({
            'x': wx, 'y': wy,
            'vx': math.cos(angle) * 15, 'vy': math.sin(angle) * 15,
            'dmg': 1, 'life': 30, 'color': WEAPON_COLORS[3], 'size': 2, 'beam': True
        })


def spawn_particles(x, y, color, count=5):
    for _ in range(count):
        a = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, 4)
        particles.append({
            'x': x, 'y': y,
            'vx': math.cos(a) * spd, 'vy': math.sin(a) * spd,
            'life': 1.0, 'color': color
        })


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
                    sfx.play('menu_click', sfx_menu_click)
                else:
                    running = False
            elif event.key == pygame.K_RETURN and game_state == "menu":
                game_state = "play"
                sfx.play('menu_click', sfx_menu_click)
                player['x'] = WIDTH // 2
                player['y'] = HEIGHT // 2
                player['hp'] = 10
                player['max_hp'] = 10
                player['weapon'] = 0
                player['shield'] = 0
                score = 0
                wave = 1
                bullets.clear()
                enemy_bullets.clear()
                enemies.clear()
                particles.clear()
                powerups.clear()
                spawn_wave()

    if controller.connected:
        if controller.just_pressed("btn_start"):
            if game_state == "play":
                game_state = "menu"
            else:
                running = False
        if controller.just_pressed("btn_a") and game_state == "menu":
            game_state = "play"
            player['x'] = WIDTH // 2
            player['y'] = HEIGHT // 2
            player['hp'] = 10
            player['max_hp'] = 10
            player['weapon'] = 0
            player['shield'] = 0
            score = 0
            wave = 1
            bullets.clear()
            enemy_bullets.clear()
            enemies.clear()
            particles.clear()
            powerups.clear()
            spawn_wave()
            sfx.play('menu_click', sfx_menu_click)
        if controller.just_pressed("btn_x") and game_state == "play":
            player['weapon'] = (player['weapon'] + 1) % len(weapons)

    if game_state == "play":
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        if controller.connected:
            cx = controller.move_x()
            cy = controller.move_y()
            if abs(cx) > 0.1 or abs(cy) > 0.1:
                dx = cx
                dy = cy
        if dx != 0 or dy != 0:
            ln = math.sqrt(dx * dx + dy * dy)
            player['x'] += dx / ln * player['speed']
            player['y'] += dy / ln * player['speed']
        player['x'] = max(20, min(WIDTH - 20, player['x']))
        player['y'] = max(20, min(HEIGHT - 20, player['y']))

        mx, my = pygame.mouse.get_pos()
        player['angle'] = math.atan2(my - player['y'], mx - player['x'])
        if controller.connected:
            ctrl_angle = controller.aim_angle(player['x'], player['y'])
            if ctrl_angle is not None:
                player['angle'] = ctrl_angle

        player['fire_cd'] = max(0, player['fire_cd'] - dt)
        if pygame.mouse.get_pressed()[0] and player['fire_cd'] <= 0:
            fire_weapon()
        if controller.connected and player['fire_cd'] <= 0:
            if controller.trigger("btn_rt") > 0.5 or controller.get_button("btn_a"):
                fire_weapon()

        for b in bullets[:]:
            b['x'] += b['vx']
            b['y'] += b['vy']
            b['life'] -= 1
            if b['life'] <= 0 or b['x'] < -50 or b['x'] > WIDTH + 50 or b['y'] < -50 or b['y'] > HEIGHT + 50:
                bullets.remove(b)
                continue
            for e in enemies[:]:
                d = math.hypot(b['x'] - e['x'], b['y'] - e['y'])
                if d < 18:
                    e['hp'] -= b['dmg']
                    sfx.play('hit', sfx_hit)
                    spawn_particles(b['x'], b['y'], e['color'], 3)
                    if not b.get('beam'):
                        if b in bullets:
                            bullets.remove(b)
                    if e['hp'] <= 0:
                        score += e['score']
                        sfx.play('explosion', sfx_explosion)
                        spawn_particles(e['x'], e['y'], e['color'], 12)
                        spawn_powerup(e['x'], e['y'])
                        enemies.remove(e)
                    break

        for e in enemies[:]:
            angle = math.atan2(player['y'] - e['y'], player['x'] - e['x'])
            e['x'] += math.cos(angle) * e['speed']
            e['y'] += math.sin(angle) * e['speed']
            e['shoot_cd'] -= dt
            if e['shoot_cd'] <= 0:
                e['shoot_cd'] = random.uniform(1.5, 3)
                ea = math.atan2(player['y'] - e['y'], player['x'] - e['x'])
                enemy_bullets.append({
                    'x': e['x'], 'y': e['y'],
                    'vx': math.cos(ea) * 4, 'vy': math.sin(ea) * 4,
                    'dmg': 1, 'life': 120, 'color': (255, 100, 100)
                })
            d = math.hypot(player['x'] - e['x'], player['y'] - e['y'])
            if d < 22:
                dmg = e['dmg'] * dt
                if player['shield'] > 0:
                    player['shield'] -= dmg
                else:
                    player['hp'] -= dmg
                    sfx.play('damage', sfx_damage)
                if player['hp'] <= 0:
                    sfx.play('game_over', sfx_game_over)
                    game_state = "menu"
                    spawn_particles(player['x'], player['y'], (126, 211, 33), 20)

        for b in enemy_bullets[:]:
            b['x'] += b['vx']
            b['y'] += b['vy']
            b['life'] -= 1
            if b['life'] <= 0 or b['x'] < -50 or b['x'] > WIDTH + 50 or b['y'] < -50 or b['y'] > HEIGHT + 50:
                enemy_bullets.remove(b)
                continue
            d = math.hypot(b['x'] - player['x'], b['y'] - player['y'])
            if d < 15:
                if player['shield'] > 0:
                    player['shield'] -= b['dmg']
                else:
                    player['hp'] -= b['dmg']
                    sfx.play('damage', sfx_damage)
                spawn_particles(b['x'], b['y'], (255, 100, 100), 3)
                if b in enemy_bullets:
                    enemy_bullets.remove(b)
                if player['hp'] <= 0:
                    sfx.play('game_over', sfx_game_over)
                    game_state = "menu"
                    spawn_particles(player['x'], player['y'], (126, 211, 33), 20)

        for p in powerups[:]:
            d = math.hypot(p['x'] - player['x'], p['y'] - player['y'])
            if d < 20:
                if p['kind'] == 'hp':
                    player['hp'] = min(player['max_hp'], player['hp'] + 3)
                elif p['kind'] == 'weapon':
                    player['weapon'] = (player['weapon'] + 1) % len(weapons)
                elif p['kind'] == 'shield':
                    player['shield'] += 5
                powerups.remove(p)
                sfx.play('powerup', sfx_powerup)
                spawn_particles(p['x'], p['y'], (255, 220, 50), 8)

        for pa in particles[:]:
            pa['x'] += pa['vx']
            pa['y'] += pa['vy']
            pa['vx'] *= 0.95
            pa['vy'] *= 0.95
            pa['life'] -= 0.03
            if pa['life'] <= 0:
                particles.remove(pa)

        if len(enemies) == 0:
            wave_timer += dt
            if wave_timer > 2:
                wave += 1
                sfx.play('levelup', sfx_levelup)
                spawn_wave()

        for s in stars:
            s[1] += s[2]
            if s[1] > HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, WIDTH)

    screen.fill((5, 5, 12))

    for sx, sy, spd, br in stars:
        c = int(br)
        pygame.draw.circle(screen, (c, c, c), (int(sx), int(sy)), 1)

    if game_state == "play":
        shake_x = random.randint(-int(shake), int(shake)) if shake > 0 else 0
        shake_y = random.randint(-int(shake), int(shake)) if shake > 0 else 0
        shake *= 0.85

        for b in enemy_bullets:
            pygame.draw.circle(screen, b['color'], (int(b['x']), int(b['y'])), 4)

        for b in bullets:
            col = b['color']
            pygame.draw.circle(screen, col, (int(b['x']), int(b['y'])), b['size'])
            if b.get('beam'):
                pygame.draw.line(screen, col, (int(b['x']), int(b['y'])),
                                 (int(b['x'] - b['vx'] * 3), int(b['y'] - b['vy'] * 3)), 2)

        for e in enemies:
            pygame.draw.circle(screen, e['color'], (int(e['x']), int(e['y'])), 14)
            pygame.draw.circle(screen, (30, 30, 30), (int(e['x']), int(e['y'])), 14, 2)
            hw = 20
            hr = e['hp'] / e['max_hp']
            pygame.draw.rect(screen, (40, 40, 40), (e['x'] - hw // 2, e['y'] - 24, hw, 4))
            pygame.draw.rect(screen, (200, 50, 50), (e['x'] - hw // 2, e['y'] - 24, int(hw * hr), 4))

        for pa in particles:
            c = pa['color']
            alpha = int(pa['life'] * 255)
            pygame.draw.circle(screen, c, (int(pa['x']), int(pa['y'])), max(1, int(pa['life'] * 4)))

        for p in powerups:
            col = (50, 200, 50) if p['kind'] == 'hp' else (80, 180, 255) if p['kind'] == 'weapon' else (200, 200, 255)
            pygame.draw.rect(screen, col, (p['x'] - 8, p['y'] - 8, 16, 16), border_radius=4)
            if p['kind'] == 'hp':
                pt = font_sm.render("+", True, (255, 255, 255))
            elif p['kind'] == 'weapon':
                pt = font_sm.render("W", True, (255, 255, 255))
            else:
                pt = font_sm.render("S", True, (255, 255, 255))
            screen.blit(pt, (p['x'] - pt.get_width() // 2, p['y'] - pt.get_height() // 2))

        angle = player['angle']
        pts = []
        for i in range(3):
            a = angle + (i - 1) * 0.3
            px2 = player['x'] + math.cos(angle) * 18
            py2 = player['y'] + math.sin(angle) * 18
            pts.append((px2 + math.cos(angle + 2.4 - i * 0.8) * 12,
                        py2 + math.sin(angle + 2.4 - i * 0.8) * 12))
        pygame.draw.polygon(screen, WEAPON_COLORS[player['weapon']], pts)
        pygame.draw.polygon(screen, (30, 30, 30), pts, 2)

        if player['shield'] > 0:
            shield_alpha = int(min(player['shield'] / 5, 1) * 80)
            sh = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(sh, (100, 150, 255, shield_alpha), (25, 25), 25)
            screen.blit(sh, (player['x'] - 25, player['y'] - 25))

        pygame.draw.rect(screen, (10, 10, 14, 200), (0, 0, WIDTH, 45))
        t = font_big.render("PLAYTREE SPACE", True, (126, 211, 33))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 6))

        sc = font_med.render(f"Score: {score}", True, (255, 220, 50))
        screen.blit(sc, (20, 10))

        wv = font_med.render(f"Wave: {wave}", True, (200, 200, 200))
        screen.blit(wv, (200, 10))

        wn = font_med.render(f"Weapon: {weapons[player['weapon']]}", True, WEAPON_COLORS[player['weapon']])
        screen.blit(wn, (380, 10))

        hp_bar_w = 100
        pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 160, 12, hp_bar_w, 16), border_radius=4)
        pygame.draw.rect(screen, (50, 200, 50), (WIDTH - 160, 12, int(hp_bar_w * player['hp'] / player['max_hp']), 16), border_radius=4)
        ht = font_sm.render(f"HP", True, (255, 255, 255))
        screen.blit(ht, (WIDTH - 50, 14))

        en = font_med.render(f"Enemies: {len(enemies)}", True, (255, 80, 80))
        screen.blit(en, (WIDTH - 200, 28))

        footer = font_sm.render("WASD: Move | Mouse: Aim & Shoot | Collect powerups | ESC quit", True, (60, 60, 70))
        screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 22))

    if game_state == "menu":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        t = font_big.render("PLAYTREE SPACE", True, (126, 211, 33))
        sub = font_med.render("Twin-stick space shooter — defeat all waves", True, (180, 180, 180))
        hint = font_med.render("Press ENTER to launch", True, (255, 220, 50))
        if score > 0:
            sc = font_med.render(f"Last Score: {score} | Wave: {wave}", True, (200, 200, 200))
            screen.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2 + 20))
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 10))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 50))

    pygame.display.flip()

pygame.quit()
