import pygame
import math
import random
from config import *


class Particle:
    def __init__(self, x, y, color, speed=2, life=60, size=4, glow=True):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        self.life = life
        self.max_life = life
        self.size = size
        self.glow = glow
        self.gravity = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size *= 0.98
        return self.life > 0 and self.size > 0.5

    def draw(self, screen, camera_x=0, camera_y=0):
        alpha = int(255 * (self.life / self.max_life))
        sx, sy = int(self.x - camera_x), int(self.y - camera_y)
        if not (0 <= sx <= WIDTH + 50 and 0 <= sy <= HEIGHT + 50):
            return
        if self.glow:
            for r in range(3, 0, -1):
                glow_alpha = alpha // (r * 2)
                glow_color = (*self.color[:3], glow_alpha)
                glow_surf = pygame.Surface((self.size * r * 4, self.size * r * 4), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    glow_color,
                    (glow_surf.get_width() // 2,
                     glow_surf.get_height() // 2),
                    self.size * r * 2)
                screen.blit(glow_surf, (sx - glow_surf.get_width() // 2, sy - glow_surf.get_height() // 2))
        color_alpha = (*self.color[:3], alpha)
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, color_alpha, (int(self.size), int(self.size)), int(self.size))
        screen.blit(s, (sx - self.size, sy - self.size))


class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.emitters = []

    def emit(self, x, y, color, count=10, speed=3, life=40, size=4, glow=True, gravity=0):
        for _ in range(count):
            p = Particle(
                x,
                y,
                color,
                speed *
                random.uniform(
                    0.5,
                    1.5),
                random.randint(
                    life //
                    2,
                    life),
                random.uniform(
                    size *
                    0.5,
                    size *
                    1.5),
                glow)
            p.gravity = gravity
            self.particles.append(p)

    def burst(self, x, y, color, count=20, speed=5, life=30, size=6):
        self.emit(x, y, color, count, speed, life, size, True)

    def trail(self, x, y, color, rate=1, speed=1, life=20, size=3):
        if random.random() < rate:
            self.emit(x + random.uniform(-5, 5), y + random.uniform(-5, 5), color, 1, speed, life, size)

    def fountain(self, x, y, color, rate=1, speed=3, life=50, size=4):
        if random.random() < rate:
            for _ in range(2):
                p = Particle(
                    x,
                    y,
                    color,
                    speed *
                    random.uniform(
                        0.3,
                        1.0),
                    random.randint(
                        life //
                        2,
                        life),
                    random.uniform(
                        size *
                        0.5,
                        size *
                        1.5),
                    True)
                p.vy = -abs(p.vy) - 1
                p.gravity = 0.1
                self.particles.append(p)

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, screen, camera_x=0, camera_y=0):
        for p in self.particles:
            p.draw(screen, camera_x, camera_y)

    def clear(self):
        self.particles.clear()
        self.emitters.clear()


class GlowEffect:
    @staticmethod
    def draw_glow(screen, x, y, color, radius, alpha=128):
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -1):
            a = alpha * (r // radius)
            pygame.draw.circle(surf, (*color[:3], a), (radius, radius), r)
        screen.blit(surf, (x - radius, y - radius), special_flags=pygame.BLEND_ALPHA_SDL2)

    @staticmethod
    def draw_glow_text(screen, text, font, color, x, y, glow_color=None, glow_radius=3):
        if glow_color is None:
            glow_color = color
        for dx, dy in [(-glow_radius, 0), (glow_radius, 0), (0, -glow_radius), (0, glow_radius),
                       (-glow_radius, -glow_radius), (glow_radius, glow_radius),
                       (-glow_radius, glow_radius), (glow_radius, -glow_radius)]:
            glow = font.render(text, True, (*glow_color[:3], 60))
            screen.blit(glow, (x + dx, y + dy))
        main = font.render(text, True, color)
        screen.blit(main, (x, y))

    @staticmethod
    def gradient_rect(screen, color1, color2, rect, vertical=True):
        x, y, w, h = rect
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(h if vertical else w):
            t = i / max(h, w)
            c = tuple(int(a + (b - a) * t) for a, b in zip(color1[:3], color2[:3]))
            if vertical:
                pygame.draw.line(surf, c, (0, i), (w, i))
            else:
                pygame.draw.line(surf, c, (i, 0), (i, h))
        screen.blit(surf, (x, y))


class StarField:
    def __init__(self, count=200):
        self.stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT),
                       random.uniform(0.5, 2.5), random.uniform(0, 1)) for _ in range(count)]

    def draw(self, screen, time=0):
        for x, y, sz, phase in self.stars:
            brightness = int(180 + 75 * math.sin(time * 0.02 + phase * 6.28))
            pygame.draw.circle(screen, (brightness, brightness, brightness), (int(x), int(y)), sz)
