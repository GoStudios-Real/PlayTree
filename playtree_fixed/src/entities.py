import pygame
import math
import random
from config import *
from src.particles import GlowEffect


class Enemy:
    def __init__(self, x, y, enemy_type=0):
        data = ENEMIES[enemy_type % len(ENEMIES)]
        self.x = x
        self.y = y
        self.name = data["name"]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.attack = data["attack"]
        self.speed = data["speed"]
        self.color = data["color"]
        self.size = 12 + enemy_type * 2
        self.enemy_type = enemy_type
        self.anim_time = random.uniform(0, 6.28)
        self.aggro_range = 200
        self.attack_range = 25
        self.attack_cooldown = 0
        self.state = "idle"
        self.state_timer = 0
        self.vx = 0
        self.vy = 0
        self.glow_t = random.uniform(0, 6.28)

    def update(self, dt, player_x, player_y):
        self.anim_time += dt
        self.glow_t += dt
        self.state_timer = max(0, self.state_timer - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.aggro_range:
            # attack_cooldown is set by CombatSystem.deal_damage_to_player
            # when the hit lands — resetting it here would swallow every swing
            if dist < self.attack_range and self.attack_cooldown <= 0:
                self.state = "attacking"
            else:
                self.state = "chasing"
        else:
            if self.state_timer <= 0:
                self.state = random.choice(["idle", "wander"])
                self.state_timer = random.uniform(1, 3)
                if self.state == "wander":
                    angle = random.uniform(0, 6.28)
                    self.vx = math.cos(angle) * self.speed * 0.5
                    self.vy = math.sin(angle) * self.speed * 0.5

        if self.state == "chasing":
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed
            self.vx = math.cos(angle) * self.speed
            self.vy = math.sin(angle) * self.speed
        elif self.state == "wander":
            self.x += self.vx
            self.y += self.vy
        elif self.state == "attacking":
            pass

        self.x = max(10, min(WORLD_W - 10, self.x))
        self.y = max(10, min(WORLD_H - 10, self.y))

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 50), (sx - self.size, sy +
                            self.size * 0.5, self.size * 2, self.size * 0.5))

        # Glow
        glow_r = self.size + 8 + int(math.sin(self.glow_t * 2) * 3)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        glow_color = (*self.color[:3], int(30 + math.sin(self.glow_t) * 15))
        pygame.draw.circle(glow_surf, glow_color, (glow_r, glow_r), glow_r)
        screen.blit(glow_surf, (sx - glow_r, sy - glow_r))

        # Body
        body_offset = int(math.sin(self.anim_time * 3) * 2) if self.state == "chasing" else 0
        pygame.draw.circle(screen, self.color, (sx, sy + body_offset), self.size)

        # Corruption effect (dark veins)
        for i in range(3):
            angle = self.anim_time * 2 + i * 2.1
            vx = sx + math.cos(angle) * self.size * 0.6
            vy = sy + math.sin(angle) * self.size * 0.6 + body_offset
            pygame.draw.circle(screen, (20, 0, 20, 100), (int(vx), int(vy)), 3)

        # Eyes
        for ex in [-self.size * 0.3, self.size * 0.3]:
            ex_s = sx + ex
            ey_s = sy - self.size * 0.2 + body_offset
            pygame.draw.circle(screen, RED, (int(ex_s), int(ey_s)), 3)
            pygame.draw.circle(screen, (200, 0, 0), (int(ex_s), int(ey_s)), 1.5)

        # HP bar
        bar_w = self.size * 2
        bar_h = 3
        bar_x = sx - bar_w // 2
        bar_y = sy - self.size - 8
        pygame.draw.rect(screen, (40, 20, 20), (bar_x, bar_y, bar_w, bar_h))
        fill = int(bar_w * (self.hp / self.max_hp))
        if fill > 0:
            fill_color = (60, 220, 60) if self.hp / self.max_hp > 0.5 else \
                (220, 220, 60) if self.hp / self.max_hp > 0.25 else (220, 60, 60)
            pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill, bar_h))

        # Name
        nf = pygame.font.Font(None, 14)
        name_surf = nf.render(self.name, True, (180, 180, 180))
        screen.blit(name_surf, (sx - name_surf.get_width() // 2, bar_y - 12))

    def take_damage(self, amount):
        self.hp -= amount
        return self.hp <= 0


class Creature:
    def __init__(self, x, y, species=0):
        data = CREATURES[species % len(CREATURES)]
        self.x = x
        self.y = y
        self.name = data["name"]
        self.color = data["color"]
        self.type = data["type"]
        self.evolves_at = data["evolves_at"]
        self.level = 1
        self.exp = 0
        self.hp = 40
        self.max_hp = 40
        self.attack = 5
        self.defense = 3
        self.speed = 2.5
        self.size = 10
        self.anim_time = random.uniform(0, 6.28)
        self.state = "idle"
        self.tamed = False
        self.owner_x = 0
        self.owner_y = 0
        self.follow_dist = 40
        self.glow_t = random.uniform(0, 6.28)

    def update(self, dt, player_x, player_y):
        self.anim_time += dt
        self.glow_t += dt

        if self.tamed:
            self.owner_x = player_x
            self.owner_y = player_y
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > self.follow_dist:
                angle = math.atan2(dy, dx)
                self.x += math.cos(angle) * self.speed
                self.y += math.sin(angle) * self.speed
                if dist > self.follow_dist + 20:
                    self.state = "running"
                else:
                    self.state = "following"
            else:
                self.state = "idle"
                if random.random() < 0.01:
                    self.x += random.uniform(-5, 5)
                    self.y += random.uniform(-5, 5)
        else:
            if random.random() < 0.005:
                angle = random.uniform(0, 6.28)
                self.x += math.cos(angle) * 2
                self.y += math.sin(angle) * 2
            self.state = "wild"

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 40), (sx - 8, sy + 6, 16, 5))

        # Glow
        glow_r = 15 + int(math.sin(self.glow_t) * 2)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        glow_color = (*self.color[:3], int(40 + math.sin(self.glow_t * 1.5) * 20))
        pygame.draw.circle(glow_surf, glow_color, (glow_r, glow_r), glow_r)
        screen.blit(glow_surf, (sx - glow_r, sy - glow_r))

        # Body
        bounce = int(math.sin(self.anim_time * 4) * 2) if self.state == "following" or self.state == "running" else 0
        pygame.draw.circle(screen, self.color, (sx, sy + bounce), self.size)

        # Ears/features
        if self.type == "forest":
            for ex, ey in [(-6, -6), (6, -6)]:
                pygame.draw.circle(screen, self.color, (sx + ex, sy + ey + bounce), 4)
            pygame.draw.circle(screen, (255, 200, 200), (sx, sy + bounce + 1), 3)
        elif self.type == "crystal":
            pygame.draw.polygon(screen, CRYSTAL, [(sx, sy - 10 + bounce),
                                (sx - 4, sy - 3 + bounce), (sx + 4, sy - 3 + bounce)])
            pygame.draw.circle(screen, CRYSTAL, (sx, sy + bounce), self.size * 0.8, 2)
        elif self.type == "mech":
            pygame.draw.rect(screen, (200, 180, 100), (sx - 6, sy - 6 + bounce, 12, 12), 2)
            pygame.draw.circle(screen, (255, 100, 50), (sx, sy + bounce), 3)
        elif self.type == "spirit":
            for i in range(3):
                a = self.anim_time * 2 + i * 2.1
                px = sx + math.cos(a) * self.size * 1.2
                py = sy + math.sin(a) * self.size * 0.5 + bounce
                pygame.draw.circle(screen, (*self.color[:3], 100), (int(px), int(py)), 3)
        elif self.type == "nature":
            pygame.draw.circle(screen, (60, 140, 40), (sx, sy - 4 + bounce), 5)

        # Eyes
        for ex in [-3, 3]:
            pygame.draw.circle(screen, (50, 50, 50), (sx + ex, sy - 1 + bounce), 2)
            pygame.draw.circle(screen, WHITE, (sx + ex, sy - 1 + bounce), 1)

        # Tamed indicator
        if self.tamed:
            pygame.draw.circle(screen, GOLD, (sx + self.size + 2, sy - self.size - 2 + bounce), 3)
            pygame.draw.circle(screen, (*GOLD[:3], 60), (sx + self.size + 2, sy - self.size - 2 + bounce), 5, 1)

    def tame(self):
        self.tamed = True

    def add_exp(self, amount):
        self.exp += amount
        if self.exp >= self.evolves_at * 10 and self.level < self.evolves_at:
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.attack += 3
            self.defense += 2
            self.size += 1
            return True
        return False
