"""PlayTree Creator Studio — standalone runtime.

Plays a project file (.ptproj / game.json) with no editor needed.
Used for Playtest inside the studio and inside exported games.

Movement: WASD / Arrow keys. ESC = quit. R = restart.
Top-down rules: solids block, coins score, lava/water hurt,
enemies hurt on touch, reach the GOAL flag to win.
"""
import json
import os
import sys

EMPTY, GROUND, STONE, WATER, LAVA, TREE, COIN, ENEMY, GOAL, SPAWN = range(10)
SOLID = {GROUND, STONE, TREE}
HAZARD = {WATER: 1, LAVA: 2}
TILE_COLORS = {
    EMPTY: (24, 32, 48),
    GROUND: (74, 140, 82),
    STONE: (110, 116, 128),
    WATER: (54, 110, 190),
    LAVA: (214, 92, 40),
    TREE: (44, 96, 56),
    COIN: (255, 215, 80),
    ENEMY: (214, 66, 66),
    GOAL: (120, 235, 150),
    SPAWN: (80, 200, 255),
}
TILE_NAMES = ["Empty", "Ground", "Stone", "Water", "Lava", "Tree", "Coin", "Enemy", "Goal", "Spawn"]


def new_project(name="My PlayTree Game", cols=32, rows=16, border=True):
    cells = [[EMPTY] * cols for _ in range(rows)]
    if border:
        for x in range(cols):
            cells[0][x] = GROUND
            cells[rows - 1][x] = GROUND
        for y in range(rows):
            cells[y][0] = GROUND
            cells[y][cols - 1] = GROUND
        cells[rows // 2][2] = SPAWN
        cells[rows // 2][cols - 3] = GOAL
    return {"name": name, "version": 1, "cols": cols, "rows": rows, "tile": 32,
            "cells": cells, "player": {"x": 2, "y": rows // 2}}


def save_project(project, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=1)
    return path


def load_project(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class PlayGame:
    def __init__(self, project):
        self.p = project
        self.cols = project["cols"]
        self.rows = project["rows"]
        self.cells = [row[:] for row in project["cells"]]
        self.spawn = self._find(SPAWN) or tuple(project.get("player", {}).values()) or (1, 1)
        self.coins_total = 0
        self.enemies = []
        for y in range(self.rows):
            for x in range(self.cols):
                c = self.cells[y][x]
                if c == COIN:
                    self.coins_total += 1
                elif c == ENEMY:
                    self.enemies.append({"x": x + 0.5, "y": y + 0.5, "dx": 1.0})
        self.reset()

    def _find(self, t):
        for y in range(self.rows):
            for x in range(self.cols):
                if self.cells[y][x] == t:
                    return (x, y)
        return None

    def reset(self):
        self.x, self.y = float(self.spawn[0]), float(self.spawn[1])
        self.hearts = 3
        self.score = 0
        self.won = False
        self.lost = False
        self.invuln = 0.0
        self.coins = 0
        for e in self.enemies:
            e["dx"] = 1.0

    def solid(self, cx, cy):
        if cx < 0 or cy < 0 or cx >= self.cols or cy >= self.rows:
            return True
        return self.cells[cy][cx] in SOLID

    def _hurt(self):
        if self.invuln > 0 or self.won or self.lost:
            return
        self.hearts -= 1
        self.invuln = 1.5
        if self.hearts <= 0:
            self.lost = True
        else:
            self.x, self.y = float(self.spawn[0]), float(self.spawn[1])

    def update(self, dt, move=(0, 0)):
        if self.won or self.lost:
            return
        self.invuln = max(0.0, self.invuln - dt)
        dx, dy = move
        speed = 4.5
        nx = self.x + dx * speed * dt
        ny = self.y + dy * speed * dt
        r = 0.32
        for tx in (int(nx - r), int(nx + r)):
            if self.solid(tx, int(self.y - r)) or self.solid(tx, int(self.y + r)):
                nx = self.x
                break
        for ty in (int(ny - r), int(ny + r)):
            if self.solid(int(nx - r), ty) or self.solid(int(nx + r), ty):
                ny = self.y
                break
        self.x, self.y = nx, ny
        cx, cy = int(self.x), int(self.y)
        if 0 <= cx < self.cols and 0 <= cy < self.rows:
            tile = self.cells[cy][cx]
            if tile in HAZARD:
                self._hurt()
            elif tile == COIN:
                self.cells[cy][cx] = EMPTY
                self.coins += 1
                self.score += 10
            elif tile == GOAL:
                self.won = True
                self.score += 100
        for e in self.enemies:
            ex = e["x"] + e["dx"] * 1.2 * dt
            if self.solid(int(ex + 0.4 * e["dx"]), int(e["y"])):
                e["dx"] *= -1
            else:
                e["x"] = ex
            if abs(e["x"] - self.x) < 0.7 and abs(e["y"] - self.y) < 0.7:
                self._hurt()


def draw(surface, game):
    import pygame
    tile = int(game.p.get("tile", 32))
    w, h = surface.get_size()
    scale = min(w / float(game.cols * tile), h / float(game.rows * tile))
    t = max(8, int(tile * scale))
    ox = (w - t * game.cols) // 2
    oy = (h - t * game.rows) // 2
    surface.fill((14, 19, 32))
    for y in range(game.rows):
        for x in range(game.cols):
            c = game.cells[y][x]
            if c == EMPTY:
                continue
            col = TILE_COLORS[c]
            pygame.draw.rect(surface, col, (ox + x * t, oy + y * t, t, t))
            if c in (COIN,):
                pygame.draw.circle(surface, (255, 245, 180),
                                   (ox + x * t + t // 2, oy + y * t + t // 2), max(3, t // 4))
            if c == GOAL:
                pygame.draw.rect(surface, (255, 255, 255),
                                 (ox + x * t + t // 4, oy + y * t + t // 4, t // 2, t // 2), 2)
    px = ox + int(game.x * t)
    py = oy + int(game.y * t)
    if game.invuln <= 0 or int(game.invuln * 10) % 2 == 0:
        pygame.draw.circle(surface, (90, 235, 255), (px, py), max(5, t // 3))
    for e in game.enemies:
        pygame.draw.circle(surface, (235, 80, 80),
                           (ox + int(e["x"] * t), oy + int(e["y"] * t)), max(4, t // 3))
    font = pygame.font.Font(None, 26)
    hud = font.render("Hearts: {}   Coins: {}/{}   Score: {}".format(
        max(0, game.hearts), game.coins, game.coins_total, game.score), True, (230, 255, 235))
    surface.blit(hud, (12, 8))
    if game.won or game.lost:
        msg = "YOU WIN!  Press R to replay, ESC to exit" if game.won else \
              "GAME OVER  Press R to restart, ESC to exit"
        big = pygame.font.Font(None, 52).render(msg, True, (255, 215, 90) if game.won else (255, 110, 110))
        surface.blit(big, big.get_rect(center=(w // 2, h // 2)))


def run(project, headless_frames=0, surface=None):
    """Interactive loop. headless_frames>0 runs without input (for tests)."""
    import pygame
    pygame.init()
    own = surface is None
    if own:
        surface = pygame.display.set_mode((960, 600))
    pygame.display.set_caption("PlayTree — " + project.get("name", "Game"))
    clock = pygame.time.Clock()
    game = PlayGame(project)
    frames = 0
    while True:
        dt = clock.tick(60) / 1000.0
        move = [0, 0]
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return game
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return game
                if ev.key == pygame.K_r:
                    game.reset()
        if headless_frames <= 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                move[1] = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                move[1] = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                move[0] = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                move[0] = 1
        game.update(dt, tuple(move))
        draw(surface, game)
        if own:
            pygame.display.flip()
        else:
            pygame.display.flip()
        frames += 1
        if headless_frames and frames >= headless_frames:
            return game


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    path = argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.json")
    if not os.path.exists(path):
        print("Project not found:", path)
        return 1
    run(load_project(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
