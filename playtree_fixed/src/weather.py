import pygame
import math
import random
from config import WIDTH, HEIGHT


class WeatherSystem:
    def __init__(self):
        self.current = "clear"
        self.timer = 0
        self.duration = 0
        self.particles = []
        self.intensity = 0
        self.fog_alpha = 0
        self.fog_timer = 0

    def update(self, dt):
        if self.current == "clear":
            self.timer -= dt
            if self.timer <= 0:
                self.start_random()

        else:
            self.duration -= dt
            if self.duration <= 0:
                self.current = "clear"
                self.timer = random.uniform(30, 90)
                self.particles = []
                return

            if self.current == "rain":
                if random.random() < 0.8:
                    self.particles.append({
                        "x": random.uniform(0, WIDTH),
                        "y": -10,
                        "speed": random.uniform(400, 700),
                        "length": random.uniform(8, 20),
                        "alpha": random.randint(60, 120),
                    })
                self.intensity = min(1.0, self.intensity + dt * 0.3)
            elif self.current == "snow":
                if random.random() < 0.5:
                    self.particles.append({
                        "x": random.uniform(0, WIDTH),
                        "y": -5,
                        "speed": random.uniform(30, 80),
                        "size": random.uniform(2, 5),
                        "drift": random.uniform(-20, 20),
                        "alpha": random.randint(100, 200),
                    })
                self.intensity = min(1.0, self.intensity + dt * 0.2)
            elif self.current == "fog":
                self.fog_alpha = min(80, self.fog_alpha + dt * 15)
                self.fog_timer += dt

            for p in self.particles[:]:
                if self.current == "rain":
                    p["y"] += p["speed"] * dt
                    p["x"] += 30 * dt
                    if p["y"] > HEIGHT + 20:
                        self.particles.remove(p)
                elif self.current == "snow":
                    p["y"] += p["speed"] * dt
                    p["x"] += p["drift"] * dt
                    if p["y"] > HEIGHT + 10:
                        self.particles.remove(p)

            if len(self.particles) > 500:
                self.particles = self.particles[-500:]

    def start_random(self):
        roll = random.random()
        if roll < 0.4:
            self.current = "rain"
            self.duration = random.uniform(15, 30)
            self.intensity = 0
        elif roll < 0.7:
            self.current = "snow"
            self.duration = random.uniform(20, 40)
            self.intensity = 0
        elif roll < 0.85:
            self.current = "fog"
            self.duration = random.uniform(10, 25)
            self.fog_alpha = 0
            self.fog_timer = 0
        else:
            self.timer = random.uniform(15, 40)

    def draw(self, surface):
        if self.current == "rain":
            for p in self.particles:
                pygame.draw.line(surface, (150, 180, 220, p["alpha"]),
                                 (int(p["x"]), int(p["y"])),
                                 (int(p["x"] + 3), int(p["y"] + p["length"])), 1)

        elif self.current == "snow":
            for p in self.particles:
                alpha = int(p["alpha"])
                snow_surf = pygame.Surface((int(p["size"] * 2), int(p["size"] * 2)), pygame.SRCALPHA)
                pygame.draw.circle(snow_surf, (220, 230, 255, alpha),
                                   (int(p["size"]), int(p["size"])), int(p["size"]))
                surface.blit(snow_surf, (int(p["x"]), int(p["y"])))

        elif self.current == "fog":
            fog_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i in range(5):
                offset = math.sin(self.fog_timer * 0.3 + i) * 100
                fog_surf.fill((100, 110, 120, int(self.fog_alpha * (0.3 + 0.1 * i))), (0, 0, WIDTH, HEIGHT))
            surface.blit(fog_surf, (0, 0))

    def get_enemy_multiplier(self):
        if self.current == "rain":
            return 1.2
        elif self.current == "fog":
            return 1.3
        elif self.current == "snow":
            return 0.9
        return 1.0

    def get_player_speed_mult(self):
        if self.current == "rain":
            return 0.9
        elif self.current == "snow":
            return 0.85
        return 1.0
