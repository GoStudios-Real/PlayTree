import pygame
import math
import random
from config import *


class Tile:
    def __init__(self, tx, ty, biome):
        self.tx = tx
        self.ty = ty
        self.biome = biome
        self.walkable = True
        self.height = random.uniform(0, 1)
        self.decorations = []
        self.resource = None
        self._generate()

    def _generate(self):
        if random.random() < 0.03:
            self.resource = random.choice(list(RESOURCES.keys()))
        if random.random() < 0.12:
            tree_type = random.choice(["tree", "rock", "flower", "crystal", "bush", "tall_tree", "bush_cluster"])
            self.decorations.append(tree_type)
        if random.random() < 0.015:
            building_type = random.choice(["ruins", "tower", "shrine", "cabin", "camp"])
            self.decorations.append(f"building_{building_type}")


class Chunk:
    def __init__(self, cx, cy, biome_idx):
        self.cx = cx
        self.cy = cy
        self.biome_idx = biome_idx
        self.biome = REGIONS[biome_idx % len(REGIONS)]
        self.tiles = {}
        self.generated = False

    def generate(self):
        if self.generated:
            return
        for tx in range(CHUNK_SIZE):
            for ty in range(CHUNK_SIZE):
                self.tiles[(tx, ty)] = Tile(
                    self.cx * CHUNK_SIZE + tx,
                    self.cy * CHUNK_SIZE + ty,
                    self.biome_idx
                )
        self.generated = True


class World:
    def __init__(self):
        self.chunks = {}
        self.world_surf = None
        self.region_centers = []
        self._generate_region_centers()

    def _generate_region_centers(self):
        cols = 4
        rows = 4
        # Local region grid around the spawn (0..~2000) — the 10^25 world is
        # infinite for practical play, so regions must NOT scale with WORLD_W.
        spacing_x = 800
        spacing_y = 800
        for i, region in enumerate(REGIONS):
            col = i % cols
            row = i // cols
            rx = 300 + (col - 1) * spacing_x + random.randint(-200, 200)
            ry = 300 + (row - 1) * spacing_y + random.randint(-200, 200)
            self.region_centers.append({"name": region["name"], "color": region["color"],
                                        "x": rx, "y": ry, "radius": 400 + random.randint(-80, 80)})

    def get_chunk(self, cx, cy):
        key = (cx, cy)
        if key not in self.chunks:
            biome_idx = abs(cx * 7 + cy * 13) % len(REGIONS)
            self.chunks[key] = Chunk(cx, cy, biome_idx)
        chunk = self.chunks[key]
        if not chunk.generated:
            chunk.generate()
        return chunk

    def get_tile(self, wx, wy):
        cx = wx // CHUNK_SIZE
        cy = wy // CHUNK_SIZE
        chunk = self.get_chunk(cx, cy)
        tx = wx % CHUNK_SIZE
        ty = wy % CHUNK_SIZE
        return chunk.tiles.get((tx, ty))

    def get_region_at(self, x, y):
        for rc in self.region_centers:
            dx = x - rc["x"]
            dy = y - rc["y"]
            if dx * dx + dy * dy < rc["radius"] * rc["radius"]:
                return rc
        return None

    def get_region_color(self, x, y):
        region = self.get_region_at(x, y)
        return region["color"] if region else (40, 60, 30)

    def draw(self, screen, camera_x, camera_y, time=0):
        start_cx = int(camera_x // (CHUNK_SIZE * TILE_SIZE)) - 1
        start_cy = int(camera_y // (CHUNK_SIZE * TILE_SIZE)) - 1
        end_cx = int((camera_x + WIDTH) // (CHUNK_SIZE * TILE_SIZE)) + 1
        end_cy = int((camera_y + HEIGHT) // (CHUNK_SIZE * TILE_SIZE)) + 1

        for cx in range(start_cx, end_cx + 1):
            for cy in range(start_cy, end_cy + 1):
                chunk = self.get_chunk(cx, cy)
                self._draw_chunk(screen, chunk, camera_x, camera_y, time)

        # Region labels
        for rc in self.region_centers:
            sx = rc["x"] - camera_x
            sy = rc["y"] - camera_y
            if 0 <= sx <= WIDTH and -200 <= sy <= HEIGHT + 200:
                pulse = math.sin(time * 0.5 + rc["x"] * 0.01) * 0.3 + 0.7
                alpha = int(30 * pulse)
                glow_surf = pygame.Surface((400, 200), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*rc["color"][:3], alpha), (200, 100), 150)
                screen.blit(glow_surf, (sx - 200, sy - 100))

    def _draw_chunk(self, screen, chunk, camera_x, camera_y, time):
        base_c = chunk.biome["color"]
        ambient = chunk.biome["ambient"]

        for (tx, ty), tile in chunk.tiles.items():
            wx = (chunk.cx * CHUNK_SIZE + tx) * TILE_SIZE
            wy = (chunk.cy * CHUNK_SIZE + ty) * TILE_SIZE
            sx = int(wx - camera_x)
            sy = int(wy - camera_y)

            if sx < -TILE_SIZE or sx > WIDTH + TILE_SIZE or sy < -TILE_SIZE or sy > HEIGHT + TILE_SIZE:
                continue

            # Terrain with height variation
            h_var = tile.height * 20
            c = tuple(min(255, max(0, int(v * (0.85 + tile.height * 0.3)))) for v in base_c)
            pygame.draw.rect(screen, c, (sx, sy, TILE_SIZE, TILE_SIZE))

            # Grid lines
            pygame.draw.rect(screen, (*c[:3], 10), (sx, sy, TILE_SIZE, TILE_SIZE), 1)

            # Decorations
            for dec in tile.decorations:
                dx = sx + TILE_SIZE // 2
                dy = sy + TILE_SIZE // 2
                if dec == "tree":
                    pygame.draw.circle(screen, (30, 80 + int(tile.height * 40), 30), (dx, dy - 4), 6)
                    pygame.draw.rect(screen, (80, 50, 30), (dx - 1, dy, 3, 6))
                elif dec == "tall_tree":
                    pygame.draw.rect(screen, (70, 45, 25), (dx - 2, dy - 2, 4, 10))
                    pygame.draw.circle(screen, (25, 70 + int(tile.height * 30), 25), (dx, dy - 8), 9)
                    pygame.draw.circle(screen, (35, 90 + int(tile.height * 20), 35), (dx - 3, dy - 6), 6)
                elif dec == "bush":
                    pygame.draw.ellipse(screen, (35, 90 + int(tile.height * 30), 35), (dx - 5, dy - 2, 10, 7))
                    pygame.draw.ellipse(screen, (45, 110 + int(tile.height * 20), 45), (dx - 3, dy - 4, 6, 5))
                elif dec == "bush_cluster":
                    for bi in range(3):
                        bx = dx - 6 + bi * 6
                        by = dy - 1 + (bi % 2) * 2
                        pygame.draw.ellipse(screen, (30 + bi * 5, 80 + bi * 10 +
                                            int(tile.height * 20), 30), (bx - 4, by - 2, 8, 6))
                elif dec == "rock":
                    pygame.draw.circle(screen, (100, 95, 90), (dx, dy), 4)
                elif dec == "flower":
                    fc = (random.randint(200, 255), random.randint(100, 200), random.randint(100, 200))
                    pygame.draw.circle(screen, fc, (dx, dy), 2)
                elif dec == "crystal":
                    for i in range(3):
                        c_pos = (dx + random.randint(-4, 4), dy + random.randint(-4, 4))
                        pygame.draw.circle(screen, CRYSTAL, c_pos, 2)
                        glow = pygame.Surface((10, 10), pygame.SRCALPHA)
                        pygame.draw.circle(glow, (*CRYSTAL[:3], 40), (5, 5), 5)
                        screen.blit(glow, (c_pos[0] - 5, c_pos[1] - 5))
                elif dec.startswith("building_"):
                    btype = dec.replace("building_", "")
                    bw, bh = 20, 16
                    if btype == "ruins":
                        bw, bh = 24, 18
                        pygame.draw.rect(screen, (80, 75, 70), (dx - bw // 2, dy - bh, bw, bh))
                        pygame.draw.rect(screen, (70, 65, 60), (dx - bw // 2, dy - bh, bw, bh), 1)
                        pygame.draw.rect(screen, (90, 85, 80), (dx - bw // 2 + 3, dy - bh + 3, 5, 8))
                        pygame.draw.rect(screen, (90, 85, 80), (dx + bw // 2 - 8, dy - bh + 3, 5, 8))
                    elif btype == "tower":
                        bw, bh = 14, 24
                        pygame.draw.rect(screen, (90, 85, 80), (dx - bw // 2, dy - bh, bw, bh))
                        pygame.draw.polygon(
                            screen, (100, 60, 40), [
                                (dx - bw // 2 - 2, dy - bh), (dx, dy - bh - 8), (dx + bw // 2 + 2, dy - bh)])
                        pygame.draw.rect(screen, (60, 50, 40), (dx - 2, dy - bh + 5, 4, 6))
                    elif btype == "shrine":
                        bw, bh = 18, 12
                        pygame.draw.rect(screen, (120, 110, 100), (dx - bw // 2, dy - bh, bw, bh))
                        glow_s = pygame.Surface((16, 16), pygame.SRCALPHA)
                        pygame.draw.circle(glow_s, (*GOLD[:3], 40), (8, 8), 8)
                        screen.blit(glow_s, (dx - 8, dy - bh - 4))
                        pygame.draw.circle(screen, GOLD, (dx, dy - bh - 2), 3)
                    elif btype == "cabin":
                        bw, bh = 22, 16
                        pygame.draw.rect(screen, (100, 70, 40), (dx - bw // 2, dy - bh, bw, bh))
                        pygame.draw.polygon(
                            screen, (80, 50, 30), [
                                (dx - bw // 2 - 2, dy - bh), (dx, dy - bh - 10), (dx + bw // 2 + 2, dy - bh)])
                        pygame.draw.rect(screen, (60, 40, 20), (dx - 3, dy - 8, 6, 8))
                        pygame.draw.rect(screen, (180, 200, 160), (dx + 4, dy - bh + 4, 4, 4))
                    elif btype == "camp":
                        for ci in range(3):
                            cx2 = dx - 8 + ci * 8
                            cy2 = dy - 2
                            pygame.draw.line(screen, (80, 50, 30), (cx2, cy2), (cx2 + 3, cy2 - 8), 1)
                        fire_s = pygame.Surface((10, 10), pygame.SRCALPHA)
                        pygame.draw.circle(fire_s, (*ORANGE[:3], 60), (5, 5), 5)
                        screen.blit(fire_s, (dx - 5, dy - 4))
                        pygame.draw.circle(screen, (255, 150, 30), (dx, dy - 2), 3)

            # Resource node
            if tile.resource:
                r_color = RESOURCES[tile.resource]["color"]
                rx = sx + TILE_SIZE // 2
                ry = sy + TILE_SIZE // 2
                pulse = math.sin(time * 2 + rx * 0.1) * 0.3 + 0.7
                r_c = tuple(int(v * pulse) for v in r_color[:3])
                pygame.draw.circle(screen, r_c, (rx, ry), 5)
                glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*r_color[:3], 60), (10, 10), 8)
                screen.blit(glow_surf, (rx - 10, ry - 10))

        # Chunk border
        chx = int(chunk.cx * CHUNK_SIZE * TILE_SIZE - camera_x)
        chy = int(chunk.cy * CHUNK_SIZE * TILE_SIZE - camera_y)
        ch_w = CHUNK_SIZE * TILE_SIZE
        ch_h = CHUNK_SIZE * TILE_SIZE
        pygame.draw.rect(screen, (*ambient[:3], 8), (chx, chy, ch_w, ch_h), 1)
