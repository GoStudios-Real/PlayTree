import pygame
import math
import random
from config import *


class StormSystem:
    def __init__(self):
        self.active = False
        self.intensity = 0
        self.timer = 0
        self.duration = 0
        self.rain = []
        self.wind_x = 0
        self.wind_y = 0
        self.wind_gust = 0
        self.lightning_timer = 0
        self.flash_alpha = 0
        self.flash_rects = []
        self.thunder_shake = 0
        self.cloud_layers = []
        self.wind_angle = random.uniform(0, 6.28)
        self.ambient_dark = 0
        self.ambient_target = 0
        self._gen_clouds()

    def _gen_clouds(self):
        self.cloud_layers = []
        for i in range(12):
            self.cloud_layers.append({
                "x": random.randint(-200, WIDTH + 200),
                "y": random.randint(-50, HEIGHT // 3),
                "w": random.randint(150, 400),
                "h": random.randint(40, 100),
                "speed": random.uniform(0.5, 2.0),
                "alpha": random.randint(60, 140),
                "color_idx": random.randint(0, 2),
            })

    def start(self, duration=25, intensity=0.8):
        self.active = True
        self.duration = duration
        self.timer = duration
        self.intensity = min(1.0, intensity)
        self.ambient_target = self.intensity * 0.6
        self.lightning_timer = random.uniform(1, 3)
        self.wind_angle = random.uniform(0, 6.28)
        self._gen_clouds()

    def stop(self):
        self.active = False
        self.ambient_target = 0

    def update(self, dt):
        if not self.active:
            self.ambient_dark = max(0, self.ambient_dark - dt * 0.5)
            return

        self.timer -= dt
        if self.timer <= 0:
            self.stop()
            return

        fade = min(1.0, dt * 2)
        if self.timer > self.duration * 0.8:
            self.intensity = min(1.0, self.intensity + dt * 0.5)
        elif self.timer < self.duration * 0.2:
            self.intensity = max(0, self.intensity - dt * 0.3)

        self.ambient_dark += (self.ambient_target * self.intensity - self.ambient_dark) * fade

        self.wind_gust = math.sin(self.timer * 2.3) * 3 * self.intensity
        self.wind_x = math.cos(self.wind_angle) * (2 + self.wind_gust) * self.intensity
        self.wind_y = math.sin(self.wind_angle) * 0.3 * self.intensity

        if random.random() < 0.02 * self.intensity:
            self.wind_angle += random.uniform(-0.3, 0.3)

        rain_count = int(120 * self.intensity)
        while len(self.rain) < rain_count:
            self.rain.append(self._spawn_rain())

        self.rain = [r for r in self.rain if r["y"] < HEIGHT + 20 and r["x"] > -50 and r["x"] < WIDTH + 50]
        for r in self.rain:
            r["x"] += r["vx"] + self.wind_x
            r["y"] += r["vy"]
            r["life"] -= dt

        for cloud in self.cloud_layers:
            cloud["x"] += cloud["speed"] + self.wind_x * 0.3
            if cloud["x"] > WIDTH + 300:
                cloud["x"] = -cloud["w"] - 50
                cloud["y"] = random.randint(-50, HEIGHT // 3)

        self.lightning_timer -= dt
        if self.lightning_timer <= 0:
            self._strike_lightning()
            self.lightning_timer = random.uniform(0.8, 4.0) / max(self.intensity, 0.01)

        self.flash_alpha = max(0, self.flash_alpha - dt * 8)
        self.thunder_shake = max(0, self.thunder_shake - dt * 8)
        self.flash_rects = [f for f in self.flash_rects if f["life"] > 0]
        for f in self.flash_rects:
            f["life"] -= dt

    def _spawn_rain(self):
        return {
            "x": random.randint(-100, WIDTH + 100),
            "y": random.randint(-50, -10),
            "vx": self.wind_x + random.uniform(-0.5, 0.5),
            "vy": random.uniform(8, 14) * self.intensity,
            "len": random.randint(6, 16),
            "alpha": random.randint(40, 120),
            "life": random.uniform(1, 3),
        }

    def _strike_lightning(self):
        self.flash_alpha = 200
        self.thunder_shake = 4 * self.intensity

        lx = random.randint(100, WIDTH - 100)
        ly = 0
        segments = []
        cx, cy = lx, ly
        for i in range(random.randint(6, 12)):
            nx = cx + random.randint(-30, 30)
            ny = cy + random.randint(30, 70)
            segments.append(((cx, cy), (nx, ny)))
            cx, cy = nx, ny
            if random.random() < 0.3:
                bx = cx + random.randint(-50, 50)
                by = cy + random.randint(20, 50)
                segments.append(((cx, cy), (bx, by)))
        self.flash_rects.append({"segments": segments, "life": 0.15, "x": lx})

    def draw(self, screen, camera_x=0, camera_y=0):
        if not self.active and self.ambient_dark < 0.01:
            return

        if self.ambient_dark > 0.01:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 5, 25, int(self.ambient_dark * 180)))
            screen.blit(overlay, (0, 0))

        if self.active:
            self._draw_clouds(screen)
            self._draw_rain(screen)
            self._draw_lightning(screen)

    def _draw_clouds(self, screen):
        colors = [(30, 30, 45), (25, 25, 40), (20, 20, 35)]
        for cloud in self.cloud_layers:
            cx = int(cloud["x"])
            cy = int(cloud["y"])
            w = cloud["w"]
            h = cloud["h"]
            alpha = int(cloud["alpha"] * self.intensity)
            c = colors[cloud["color_idx"]]
            cloud_surf = pygame.Surface((w, h * 2), pygame.SRCALPHA)
            for i in range(5):
                offset_x = int(math.sin(i * 1.2 + self.timer * 0.5) * w * 0.15)
                offset_y = int(math.cos(i * 0.8) * h * 0.3)
                blob_alpha = max(0, alpha - i * 15)
                pygame.draw.ellipse(cloud_surf, (*c, blob_alpha),
                                    (offset_x, h // 2 + offset_y, w - i * 20, h - i * 8))
            screen.blit(cloud_surf, (cx, cy))

    def _draw_rain(self, screen):
        if not self.rain:
            return
        rain_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for r in self.rain:
            x = int(r["x"])
            y = int(r["y"])
            if 0 <= x <= WIDTH and -20 <= y <= HEIGHT:
                alpha = int(r["alpha"] * self.intensity)
                end_x = x + int(self.wind_x * 2)
                end_y = y + r["len"]
                pygame.draw.line(rain_surf, (150, 170, 200, alpha), (x, y), (end_x, end_y), 1)
        screen.blit(rain_surf, (0, 0))

    def _draw_lightning(self, screen):
        for flash in self.flash_rects:
            alpha = int(255 * (flash["life"] / 0.15))
            if alpha <= 0:
                continue
            bolt_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for (sx, sy), (ex, ey) in flash["segments"]:
                pygame.draw.line(bolt_surf, (200, 200, 255, alpha), (sx, sy), (ex, ey), 3)
                glow_alpha = max(0, alpha // 2)
                pygame.draw.line(bolt_surf, (150, 150, 255, glow_alpha), (sx, sy), (ex, ey), 6)
            screen.blit(bolt_surf, (0, 0))

        if self.flash_alpha > 0:
            flash_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_overlay.fill((200, 200, 255, int(self.flash_alpha * self.intensity)))
            screen.blit(flash_overlay, (0, 0))

    def draw_splash(self, screen, player_x, player_y, camera_x, camera_y):
        if not self.active:
            return
        sx = int(player_x - camera_x)
        sy = int(player_y - camera_y)
        splash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(int(8 * self.intensity)):
            angle = random.uniform(0, 6.28)
            dist = random.randint(15, 40)
            px = sx + math.cos(angle) * dist
            py = sy + math.sin(angle) * dist
            if 0 <= px <= WIDTH and 0 <= py <= HEIGHT:
                alpha = int(60 * self.intensity)
                pygame.draw.circle(splash_surf, (150, 170, 200, alpha), (int(px), int(py)), random.randint(1, 3))
        screen.blit(splash_surf, (0, 0))

    def get_wind_force(self):
        if not self.active:
            return 0, 0
        return self.wind_x * 0.5, self.wind_y * 0.5
