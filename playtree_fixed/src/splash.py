import pygame
import math
import random
import time
from config import *


class SplashScreen:
    def __init__(self):
        self.timer = 0
        self.done = False
        self.phase = 0

        self.stars = []
        for _ in range(200):
            self.stars.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "speed": random.uniform(0.3, 2.5),
                "size": random.uniform(0.5, 2.5),
                "brightness": random.randint(80, 255),
                "twinkle": random.uniform(0, 6.28),
            })

        self.particles = []
        self.energy_rings = []
        self.shockwaves = []
        self.trail_particles = []

        self.tree_grow_progress = 0
        self.canopy_expand = 0
        self.root_spread = 0

        self.flash_alpha = 0
        self.fade_alpha = 255

        self.texts = [
            {"label": "GoConsole Game Studios", "font_size": 28, "color": (
                200, 180, 140), "start": 0.5, "end": 2.5, "y_offset": -10},
            {"label": "GoStudios", "font_size": 24, "color": (180, 200, 220), "start": 1.5, "end": 3.5, "y_offset": 20},
            {"label": "PLAYTREE", "font_size": 72, "color": GREEN_GLOW,
                "start": 2.8, "end": 7.0, "y_offset": -70, "glow": True},
            {"label": "GAMES", "font_size": 30, "color": GOLD, "start": 3.5, "end": 7.0, "y_offset": 20, "glow": True},
            {"label": f"v{VERSION}  \u2022  {CHAPTER} : {SEASON}", "font_size": 18,
                "color": (80, 100, 80), "start": 5.0, "end": 8.0, "y_offset": 70},
        ]

        self.logos = [
            {"text": "GoConsole", "start": 0.3, "end": 2.2, "size": 36, "color": (200, 180, 140), "icon": "studio"},
            {"text": "GoStudios", "start": 1.8, "end": 3.8, "size": 32, "color": (180, 200, 220), "icon": "tech"},
            {"text": "PLAYTREE", "start": 3.0, "end": 7.5, "size": 80, "color": GREEN_GLOW, "icon": "tree", "glow": True},
        ]

    def update(self, dt):
        self.timer += dt

        for star in self.stars:
            star["y"] += star["speed"]
            star["twinkle"] += dt * 3
            if star["y"] > HEIGHT + 10:
                star["y"] = -10
                star["x"] = random.randint(0, WIDTH)

        if 3.0 < self.timer < 3.3:
            if random.random() < 0.4:
                angle = random.uniform(0, 6.28)
                dist = random.randint(50, 200)
                self.particles.append({
                    "x": WIDTH // 2 + math.cos(angle) * dist,
                    "y": HEIGHT // 2 - 40 + math.sin(angle) * dist * 0.5,
                    "vx": math.cos(angle) * random.uniform(1, 4),
                    "vy": math.sin(angle) * random.uniform(1, 3) - 1,
                    "life": random.uniform(1, 3),
                    "max_life": 3,
                    "color": random.choice([GREEN_GLOW, GOLD, (100, 255, 180)]),
                    "size": random.uniform(2, 5),
                })

        if 2.8 < self.timer < 3.1:
            self.flash_alpha = min(255, int((self.timer - 2.8) * 800))
        else:
            self.flash_alpha = max(0, self.flash_alpha - dt * 400)

        if self.timer > 3.0 and len(self.shockwaves) < 2:
            self.shockwaves.append({
                "x": WIDTH // 2, "y": HEIGHT // 2 - 30,
                "radius": 0, "max_radius": 400,
                "speed": 300, "life": 1.0,
            })

        for ring in list(self.energy_rings):
            ring["radius"] += dt * 80
            ring["life"] -= dt * 0.5
            if ring["life"] <= 0:
                self.energy_rings.remove(ring)

        if 3.5 < self.timer < 6.0 and random.random() < 0.15:
            self.energy_rings.append({
                "x": WIDTH // 2 + random.randint(-100, 100),
                "y": HEIGHT // 2 - 40 + random.randint(-50, 50),
                "radius": random.randint(10, 30),
                "life": random.uniform(0.5, 1.5),
            })

        for p in list(self.particles):
            p["x"] += p["vx"] * dt * 60
            p["y"] += p["vy"] * dt * 60
            p["vy"] += 0.02
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

        for sw in list(self.shockwaves):
            sw["radius"] += sw["speed"] * dt
            sw["life"] -= dt * 1.5
            if sw["life"] <= 0:
                self.shockwaves.remove(sw)

        if self.timer < 3.0:
            self.fade_alpha = max(0, 255 - int(self.timer * 120))
        else:
            self.fade_alpha = 0

        if self.timer > 3.0:
            self.tree_grow_progress = min(1.0, self.timer - 3.0)
        if self.timer > 3.5:
            self.canopy_expand = min(1.0, (self.timer - 3.5) * 0.8)
        if self.timer > 3.2:
            self.root_spread = min(1.0, (self.timer - 3.2) * 0.7)

        if self.timer > 7.5:
            self.done = True

    def draw(self, screen):
        screen.fill((2, 2, 15))

        self._draw_stars(screen)
        self._draw_energy_rings(screen)
        self._draw_shockwaves(screen)
        self._draw_tree(screen)
        self._draw_particles(screen)
        self._draw_texts(screen)
        self._draw_flash(screen)
        self._draw_vignette(screen)
        self._draw_scanlines(screen)

        if self.fade_alpha > 0:
            fade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.fade_alpha))
            screen.blit(fade, (0, 0))

    def _draw_stars(self, screen):
        for star in self.stars:
            twinkle = (math.sin(star["twinkle"]) + 1) * 0.5
            b = int(star["brightness"] * twinkle)
            b = max(0, min(255, b))
            size = star["size"]
            if size > 1.5:
                glow = pygame.Surface((int(size * 6), int(size * 6)), pygame.SRCALPHA)
                pygame.draw.circle(glow, (b, b, b, b // 3), (int(size * 3), int(size * 3)), int(size * 3))
                screen.blit(glow, (int(star["x"] - size * 3), int(star["y"] - size * 3)))
            pygame.draw.circle(screen, (b, b, b), (int(star["x"]), int(star["y"])), max(1, int(size)))

    def _draw_energy_rings(self, screen):
        for ring in self.energy_rings:
            alpha = int(ring["life"] * 100)
            if alpha <= 0:
                continue
            r = int(ring["radius"])
            if r < 1:
                continue
            ring_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (*GREEN_GLOW[:3], alpha), (r + 2, r + 2), r, 1)
            screen.blit(ring_surf, (int(ring["x"]) - r - 2, int(ring["y"]) - r - 2))

    def _draw_shockwaves(self, screen):
        for sw in self.shockwaves:
            alpha = int(sw["life"] * 150)
            r = int(sw["radius"])
            if r < 1 or alpha <= 0:
                continue
            sw_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(sw_surf, (*GREEN_GLOW[:3], alpha), (r + 2, r + 2), r, 2)
            screen.blit(sw_surf, (sw["x"] - r - 2, sw["y"] - r - 2))

    def _draw_tree(self, screen):
        if self.tree_grow_progress <= 0:
            return

        cx, cy = WIDTH // 2, HEIGHT // 2 - 10
        progress = self.tree_grow_progress

        trunk_h = int(80 * progress)
        trunk_color = (60, 40, 30)
        trunk_w = int(16 * min(1, progress * 2))

        if trunk_h > 2:
            trunk_surf = pygame.Surface((trunk_w + 20, trunk_h + 10), pygame.SRCALPHA)
            pygame.draw.rect(trunk_surf, (*trunk_color, int(200 * progress)),
                             (10, 10, trunk_w, trunk_h), border_radius=3)
            glow_alpha = int(30 * progress)
            pygame.draw.rect(trunk_surf, (*GREEN_GLOW[:3], glow_alpha),
                             (5, 5, trunk_w + 10, trunk_h + 10), border_radius=5)
            screen.blit(trunk_surf, (cx - trunk_w // 2 - 10, cy - trunk_h))

        if self.canopy_expand > 0:
            canopy_data = [
                (65, (40, 120, 50)),
                (50, (50, 150, 60)),
                (35, (60, 180, 70)),
                (20, (80, 220, 90)),
            ]
            for radius, color in canopy_data:
                r = int(radius * self.canopy_expand)
                if r < 2:
                    continue
                canopy_y = cy - trunk_h - (65 - radius) * 0.5
                sway = math.sin(self.timer * 0.8) * 3 * self.canopy_expand

                glow_r = r + 12
                glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                g_alpha = int(50 * self.canopy_expand)
                pygame.draw.circle(glow_s, (*GREEN_GLOW[:3], g_alpha), (glow_r, glow_r), glow_r)
                screen.blit(glow_s, (int(cx + sway - glow_r), int(canopy_y - glow_r)))

                pygame.draw.circle(screen, color, (int(cx + sway), int(canopy_y)), r)

        if self.root_spread > 0:
            for i in range(4):
                angle = math.pi * (0.3 + i * 0.25)
                root_len = int(30 * self.root_spread)
                rx, ry = cx + int(math.cos(angle) * 8), cy
                for j in range(6):
                    nx = rx + int(math.cos(angle + math.sin(j * 0.8) * 0.4) * (root_len // 6))
                    ny = ry + 3 + j * 2
                    pygame.draw.line(screen, trunk_color, (rx, ry), (nx, ny), 2)
                    rx, ry = nx, ny

    def _draw_particles(self, screen):
        for p in self.particles:
            alpha = int((p["life"] / p["max_life"]) * 255)
            sz = p["size"] * (p["life"] / p["max_life"])
            if sz < 0.5 or alpha <= 0:
                continue

            glow_sz = int(sz * 4)
            if glow_sz > 0:
                glow = pygame.Surface((glow_sz * 2, glow_sz * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*p["color"][:3], alpha // 4), (glow_sz, glow_sz), glow_sz)
                screen.blit(glow, (int(p["x"] - glow_sz), int(p["y"] - glow_sz)))

            pygame.draw.circle(screen, (*p["color"][:3], alpha),
                               (int(p["x"]), int(p["y"])), max(1, int(sz)))

    def _draw_texts(self, screen):
        for entry in self.texts:
            t = self.timer
            start = entry["start"]
            end = entry["end"]
            mid = (start + end) / 2

            if t < start or t > end:
                continue

            if t < mid:
                alpha = min(255, int((t - start) / (mid - start) * 255))
                scale = 0.8 + 0.2 * min(1.0, (t - start) / (mid - start))
            else:
                fade_progress = (t - mid) / (end - mid)
                alpha = int(255 * (1.0 - fade_progress * 0.7))
                scale = 1.0 - fade_progress * 0.1

            if alpha <= 0:
                continue

            font_size = max(1, int(entry["font_size"] * scale))
            f = pygame.font.Font(None, font_size)
            text = f.render(entry["label"], True, entry["color"])

            text.set_alpha(alpha)

            tx = WIDTH // 2 - text.get_width() // 2
            ty = HEIGHT // 2 + entry["y_offset"]

            if entry.get("glow"):
                for gx, gy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
                    glow_surf = f.render(entry["label"], True, (*GREEN_GLOW[:3], alpha // 3))
                    glow_surf.set_alpha(alpha // 3)
                    screen.blit(glow_surf, (tx + gx, ty + gy))

                for r in range(3, 0, -1):
                    glow2 = f.render(entry["label"], True, (*GREEN_GLOW[:3], 20 // r))
                    glow2.set_alpha(20 // r)
                    screen.blit(glow2, (tx - r * 2, ty - r))
                    screen.blit(glow2, (tx + r * 2, ty + r))

            screen.blit(text, (tx, ty))

    def _draw_flash(self, screen):
        if self.flash_alpha > 0:
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((*GREEN_GLOW[:3], int(self.flash_alpha * 0.6)))
            screen.blit(flash, (0, 0))

    def _draw_vignette(self, screen):
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(60):
            alpha = int((60 - i) * 2.5)
            border = i * 4
            pygame.draw.rect(vignette, (0, 0, 0, alpha),
                             (border, border, WIDTH - border * 2, HEIGHT - border * 2),
                             border_radius=0)
        screen.blit(vignette, (0, 0))

    def _draw_scanlines(self, screen):
        scan = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 3):
            pygame.draw.line(scan, (0, 0, 0, 15), (0, y), (WIDTH, y))
        screen.blit(scan, (0, 0))
