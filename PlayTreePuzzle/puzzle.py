"""PlayTree Puzzle — Match-3 gem crusher with GoStudios branding"""
import pygame
import sys; sys.path.insert(0, r"C:\Users\RhysC\Downloads\NEW"); from game_utils import controller, sfx, sfx_shoot, sfx_hit, sfx_collect, sfx_levelup, sfx_menu_click, sfx_menu_hover, sfx_damage, sfx_game_over, sfx_coin
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PlayTree Puzzle — GoStudios")

BG = (12, 14, 18)
GRID_X, GRID_Y = 100, 110
CELL = 60
COLS, ROWS = 8, 8
GEM_COLORS = {
    0: (126, 211, 33),   # green
    1: (80, 180, 255),   # blue
    2: (255, 80, 80),    # red
    3: (255, 200, 40),   # yellow
    4: (200, 80, 255),   # purple
    5: (255, 140, 40),   # orange
}
GEM_NAMES = ["Leaf", "Crystal", "Fire", "Star", "Amber", "Sun"]

try:
    font_big = pygame.font.SysFont("Segoe UI Semibold", 36)
    font_med = pygame.font.SysFont("Segoe UI", 22)
    font_sm = pygame.font.SysFont("Consolas", 14)
    font_title = pygame.font.SysFont("Segoe UI Semibold", 48)
except Exception:
    font_big = pygame.font.Font(None, 36)
    font_med = pygame.font.Font(None, 22)
    font_sm = pygame.font.Font(None, 14)
    font_title = pygame.font.Font(None, 48)

grid = [[0] * COLS for _ in range(ROWS)]
for r in range(ROWS):
    for c in range(COLS):
        grid[r][c] = random.randint(0, len(GEM_COLORS) - 1)

selected = None
score = 0
moves = 30
level = 1
combo = 0
animating = False
anim_queue = []
falling = False
fall_data = []
sparkles = []
game_over = False
swap_anim = None
swap_t = 0


def remove_matches():
    global score, combo
    matched = set()
    for r in range(ROWS):
        for c in range(COLS - 2):
            v = grid[r][c]
            if v >= 0 and v == grid[r][c+1] == grid[r][c+2]:
                length = 3
                while c + length < COLS and grid[r][c+length] == v:
                    length += 1
                for i in range(length):
                    matched.add((r, c + i))
    for c in range(COLS):
        for r in range(ROWS - 2):
            v = grid[r][c]
            if v >= 0 and v == grid[r+1][c] == grid[r+2][c]:
                length = 3
                while r + length < ROWS and grid[r+length][c] == v:
                    length += 1
                for i in range(length):
                    matched.add((r + i, c))
    if matched:
        combo += 1
        pts = len(matched) * 10 * combo
        score += pts
        for r, c in matched:
            cx = GRID_X + c * CELL + CELL // 2
            cy = GRID_Y + r * CELL + CELL // 2
            col = GEM_COLORS[grid[r][c]]
            for _ in range(6):
                sparkles.append({
                    'x': cx, 'y': cy,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-4, 1),
                    'life': 1.0,
                    'color': col
                })
            grid[r][c] = -1
    return len(matched) > 0


def drop_gems():
    global falling
    fell = False
    for c in range(COLS):
        empty = 0
        for r in range(ROWS - 1, -1, -1):
            if grid[r][c] == -1:
                empty += 1
            elif empty > 0:
                grid[r + empty][c] = grid[r][c]
                grid[r][c] = -1
                fell = True
        for r in range(empty):
            grid[r][c] = random.randint(0, len(GEM_COLORS) - 1)
            fell = True
    falling = fell
    return fell


def swap_gems(r1, c1, r2, c2):
    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]


def has_valid_moves():
    for r in range(ROWS):
        for c in range(COLS):
            if c + 1 < COLS:
                swap_gems(r, c, r, c + 1)
                if remove_matches():
                    swap_gems(r, c, r, c + 1)
                    grid[r][c] = grid[r][c+1] if grid[r][c] != grid[r][c+1] else grid[r][c]
                    return True
                swap_gems(r, c, r, c + 1)
            if r + 1 < ROWS:
                swap_gems(r, c, r + 1, c)
                if remove_matches():
                    swap_gems(r, c, r + 1, c)
                    return True
                swap_gems(r, c, r + 1, c)
    return False


def draw_gem(r, c, alpha=255):
    v = grid[r][c]
    if v < 0:
        return
    x = GRID_X + c * CELL
    y = GRID_Y + r * CELL
    col = GEM_COLORS[v]

    if selected and selected == (r, c):
        glow = pygame.Surface((CELL + 8, CELL + 8), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*col, 60), (0, 0, CELL + 8, CELL + 8), border_radius=12)
        screen.blit(glow, (x - 4, y - 4))

    gem = pygame.Surface((CELL - 6, CELL - 6), pygame.SRCALPHA)
    pygame.draw.rect(gem, col, (0, 0, CELL - 6, CELL - 6), border_radius=10)
    pygame.draw.rect(gem, (255, 255, 255, 40), (4, 4, CELL - 16, CELL // 2 - 6), border_radius=6)
    screen.blit(gem, (x + 3, y + 3))


def draw_grid():
    for r in range(ROWS):
        for c in range(COLS):
            x = GRID_X + c * CELL
            y = GRID_Y + r * CELL
            clr = (20, 22, 28) if (r + c) % 2 == 0 else (24, 26, 32)
            pygame.draw.rect(screen, clr, (x, y, CELL, CELL), border_radius=4)
            draw_gem(r, c)
    pygame.draw.rect(screen, (40, 42, 50), (GRID_X - 2, GRID_Y - 2, COLS * CELL + 4, ROWS * CELL + 4), 2, border_radius=6)


def draw_hud():
    title = font_big.render("PLAYTREE PUZZLE", True, (126, 211, 33))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 12))

    sc = font_med.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(sc, (GRID_X, 68))

    mv = font_med.render(f"Moves: {moves}", True, (255, 200, 50) if moves > 10 else (255, 80, 80))
    screen.blit(mv, (WIDTH - 200, 68))

    lv = font_med.render(f"Level {level}", True, (180, 180, 190))
    screen.blit(lv, (WIDTH // 2 - lv.get_width() // 2, 68))

    combo_txt = font_sm.render(f"Combo x{combo}" if combo > 1 else "", True, (255, 180, 40))
    screen.blit(combo_txt, (GRID_X + COLS * CELL + 20, GRID_Y + 20))

    footer = font_sm.render("Click gems to swap | Match 3+ to score | ESC quit", True, (80, 80, 90))
    screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, HEIGHT - 28))


def draw_sparkles():
    for s in sparkles[:]:
        pygame.draw.circle(screen, s['color'], (int(s['x']), int(s['y'])), int(3 * s['life']))
        s['x'] += s['vx']
        s['y'] += s['vy']
        s['life'] -= 0.04
        if s['life'] <= 0:
            sparkles.remove(s)


def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    t1 = font_big.render("LEVEL COMPLETE!" if score >= level * 500 else "OUT OF MOVES!", True, (126, 211, 33) if score >= level * 500 else (255, 80, 80))
    t2 = font_med.render(f"Score: {score} | Press R to continue", True, (200, 200, 200))
    screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 + 20))


clock = pygame.time.Clock()
controller.init()
controller_cursor = [COLS // 2, ROWS // 2]
running = True

while running:
    dt = clock.tick(60) / 1000.0

    controller.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r and game_over:
                if score >= level * 500:
                    level += 1
                    moves = 30 + level * 2
                    sfx.play("levelup", sfx_levelup)
                else:
                    moves = 30
                score = 0
                combo = 0
                game_over = False
                for r in range(ROWS):
                    for c in range(COLS):
                        grid[r][c] = random.randint(0, len(GEM_COLORS) - 1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over and not animating:
            mx, my = event.pos
            gc = (mx - GRID_X) // CELL
            gr = (my - GRID_Y) // CELL
            if 0 <= gc < COLS and 0 <= gr < ROWS:
                if selected is None:
                    selected = (gr, gc)
                    sfx.play("menu_hover", sfx_menu_hover)
                else:
                    sr, sc = selected
                    if abs(sr - gr) + abs(sc - gc) == 1:
                        swap_gems(sr, sc, gr, gc)
                        if not remove_matches():
                            swap_gems(sr, sc, gr, gc)
                            sfx.play("hit", sfx_hit)
                        else:
                            moves -= 1
                            combo = 0
                            sfx.play("coin", sfx_coin)
                            while remove_matches():
                                drop_gems()
                    sfx.play("menu_click", sfx_menu_click)
                    selected = None

    if not game_over and not animating:
        if controller.just_pressed("dpad_up") and controller_cursor[1] > 0:
            controller_cursor[1] -= 1
        if controller.just_pressed("dpad_down") and controller_cursor[1] < ROWS - 1:
            controller_cursor[1] += 1
        if controller.just_pressed("dpad_left") and controller_cursor[0] > 0:
            controller_cursor[0] -= 1
        if controller.just_pressed("dpad_right") and controller_cursor[0] < COLS - 1:
            controller_cursor[0] += 1

    if controller.just_pressed("btn_start"):
        running = False
    if controller.just_pressed("btn_y") and game_over:
        if score >= level * 500:
            level += 1
            moves = 30 + level * 2
            sfx.play("levelup", sfx_levelup)
        else:
            moves = 30
        score = 0
        combo = 0
        game_over = False
        for r in range(ROWS):
            for c in range(COLS):
                grid[r][c] = random.randint(0, len(GEM_COLORS) - 1)
    if controller.just_pressed("btn_a") and not game_over and not animating:
        gr, gc = controller_cursor[1], controller_cursor[0]
        if selected is None:
            selected = (gr, gc)
            sfx.play("menu_hover", sfx_menu_hover)
        else:
            sr, sc = selected
            if abs(sr - gr) + abs(sc - gc) == 1:
                swap_gems(sr, sc, gr, gc)
                if not remove_matches():
                    swap_gems(sr, sc, gr, gc)
                    sfx.play("hit", sfx_hit)
                else:
                    moves -= 1
                    combo = 0
                    sfx.play("coin", sfx_coin)
                    while remove_matches():
                        drop_gems()
            sfx.play("menu_click", sfx_menu_click)
            selected = None

    drop_gems()

    if not game_over and moves <= 0:
        game_over = True

    screen.fill(BG)
    draw_grid()
    draw_hud()
    draw_sparkles()

    if game_over:
        draw_game_over()

    pygame.display.flip()

pygame.quit()
