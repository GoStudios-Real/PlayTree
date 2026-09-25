import pygame
import math
import random
from config import *

EXPANDED_ENEMIES = [
    # Tier 1 - Forest enemies
    {"name": "Corrupted Sapling", "color": (40, 100, 30), "hp": 20, "attack": 3, "speed": 2.0, "tier": 1,
     "drops": ["Tree Energy"], "drop_chance": 0.5, "xp": 10, "behavior": "chase"},
    {"name": "Vine Crawler", "color": (60, 140, 40), "hp": 35, "attack": 5, "speed": 1.8, "tier": 1,
     "drops": ["Tree Energy", "Ancient Seeds"], "drop_chance": 0.3, "xp": 15, "behavior": "ambush"},
    {"name": "Moss Golem", "color": (80, 120, 60), "hp": 60, "attack": 8, "speed": 1.2, "tier": 1,
     "drops": ["Crystal Dust", "Tree Energy"], "drop_chance": 0.4, "xp": 25, "behavior": "patrol"},

    # Tier 2 - Crystal enemies
    {"name": "Crystal Bat", "color": (180, 100, 220), "hp": 25, "attack": 6, "speed": 3.5, "tier": 2,
     "drops": ["Crystal Dust"], "drop_chance": 0.6, "xp": 20, "behavior": "swoop"},
    {"name": "Crystal Golem", "color": (150, 80, 200), "hp": 80, "attack": 10, "speed": 1.0, "tier": 2,
     "drops": ["Crystal Dust", "Crystal Dust"], "drop_chance": 0.5, "xp": 35, "behavior": "guard"},
    {"name": "Prism Lurker", "color": (200, 140, 255), "hp": 40, "attack": 7, "speed": 2.5, "tier": 2,
     "drops": ["Crystal Dust", "Light Fragments"], "drop_chance": 0.2, "xp": 30, "behavior": "teleport"},

    # Tier 3 - Sky enemies
    {"name": "Storm Hawk", "color": (100, 150, 200), "hp": 35, "attack": 8, "speed": 4.0, "tier": 3,
     "drops": ["Light Fragments"], "drop_chance": 0.4, "xp": 30, "behavior": "dive"},
    {"name": "Wind Spirit", "color": (180, 220, 255), "hp": 30, "attack": 6, "speed": 3.8, "tier": 3,
     "drops": ["Light Fragments", "Ancient Seeds"], "drop_chance": 0.3, "xp": 25, "behavior": "phasing"},
    {"name": "Thunder Bison", "color": (120, 130, 160), "hp": 100, "attack": 12, "speed": 2.2, "tier": 3,
     "drops": ["Light Fragments", "Crystal Dust"], "drop_chance": 0.5, "xp": 45, "behavior": "charge"},

    # Tier 4 - Desert enemies
    {"name": "Sand Scarab", "color": (200, 180, 100), "hp": 45, "attack": 7, "speed": 2.8, "tier": 4,
     "drops": ["Ancient Seeds"], "drop_chance": 0.5, "xp": 25, "behavior": "swarm"},
    {"name": "Dune Worm", "color": (180, 150, 80), "hp": 90, "attack": 14, "speed": 1.5, "tier": 4,
     "drops": ["Ancient Seeds", "Ancient Seeds"], "drop_chance": 0.4, "xp": 50, "behavior": "burrow"},
    {"name": "Sun Sentinel", "color": (220, 200, 100), "hp": 70, "attack": 11, "speed": 2.0, "tier": 4,
     "drops": ["Ancient Seeds", "Light Fragments"], "drop_chance": 0.3, "xp": 40, "behavior": "ranged"},

    # Tier 5 - Ruins enemies
    {"name": "Phantom Knight", "color": (100, 80, 120), "hp": 80, "attack": 12, "speed": 2.0, "tier": 5,
     "drops": ["Shadow Essence", "Ancient Root"], "drop_chance": 0.3, "xp": 45, "behavior": "teleport"},
    {"name": "Rune Golem", "color": (140, 120, 160), "hp": 120, "attack": 15, "speed": 1.0, "tier": 5,
     "drops": ["Shadow Essence", "Light Fragments"], "drop_chance": 0.4, "xp": 55, "behavior": "guard"},
    {"name": "Void Wisp", "color": (60, 40, 80), "hp": 30, "attack": 9, "speed": 3.5, "tier": 5,
     "drops": ["Shadow Essence"], "drop_chance": 0.6, "xp": 30, "behavior": "phasing"},

    # Elite enemies
    {"name": "Corrupted Elder", "color": (120, 40, 40), "hp": 150, "attack": 18, "speed": 1.8, "tier": 3,
     "drops": ["Light Fragments", "Ancient Root", "Crystal Dust"], "drop_chance": 0.7, "xp": 80, "behavior": "elite"},
    {"name": "Shadow Assassin", "color": (40, 20, 60), "hp": 100, "attack": 22, "speed": 3.5, "tier": 4,
     "drops": ["Shadow Essence", "Ancient Root"], "drop_chance": 0.6, "xp": 70, "behavior": "stealth"},
    {"name": "Crystal Wyrm", "color": (180, 60, 220), "hp": 200, "attack": 20, "speed": 2.0, "tier": 5,
     "drops": ["Crystal Dust", "Crystal Dust", "Light Fragments"], "drop_chance": 0.8, "xp": 100, "behavior": "elite"},
]


class ExpandedEnemy:
    def __init__(self, x, y, enemy_type=None):
        if enemy_type is None:
            enemy_type = random.randint(0, len(EXPANDED_ENEMIES) - 1)
        enemy_type = enemy_type % len(EXPANDED_ENEMIES)
        data = EXPANDED_ENEMIES[enemy_type]
        self.x = x
        self.y = y
        self.name = data["name"]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.attack = data["attack"]
        self.speed = data["speed"]
        self.color = data["color"]
        self.tier = data["tier"]
        self.drops = list(data["drops"])
        self.drop_chance = data["drop_chance"]
        self.xp_reward = data["xp"]
        self.behavior = data["behavior"]
        self.enemy_type = enemy_type
        self.size = 12 + data["tier"] * 2
        self.anim_time = random.uniform(0, 6.28)
        self.aggro_range = 180 + data["tier"] * 20
        self.attack_range = 25 + (15 if data["behavior"] in ["ranged", "swoop"] else 0)
        self.attack_cooldown = 0
        self.state = "idle"
        self.state_timer = 0
        self.vx = 0
        self.vy = 0
        self.glow_t = random.uniform(0, 6.28)
        self.stealthed = False
        self.stealth_timer = 0
        self.charge_timer = 0
        self.teleport_cooldown = 0
        self.summon_timer = 0

    def update(self, dt, player_x, player_y):
        self.anim_time += dt
        self.glow_t += dt
        self.state_timer = max(0, self.state_timer - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.teleport_cooldown = max(0, self.teleport_cooldown - dt)
        self.stealth_timer = max(0, self.stealth_timer - dt)
        self.charge_timer = max(0, self.charge_timer - dt)
        self.summon_timer = max(0, self.summon_timer - dt)

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if self.behavior == "stealth":
            if dist > self.aggro_range:
                self.stealthed = True
            elif dist < 80:
                self.stealthed = False
                self.stealth_timer = 3.0

        if self.behavior == "teleport" and self.teleport_cooldown <= 0 and dist < self.aggro_range:
            angle = random.uniform(0, 6.28)
            tdist = random.randint(40, 80)
            self.x += math.cos(angle) * tdist
            self.y += math.sin(angle) * tdist
            self.teleport_cooldown = 3.0

        if self.behavior == "burrow":
            if self.state_timer <= 0:
                if self.state == "idle":
                    self.state = "burrowed"
                    self.state_timer = 2.0
                elif self.state == "burrowed":
                    self.state = "emerge"
                    self.x = player_x + random.randint(-30, 30)
                    self.y = player_y + random.randint(-30, 30)
                    self.state_timer = 0.5
                else:
                    self.state = "idle"
                    self.state_timer = random.uniform(1, 3)

        if self.behavior == "swarm" and self.summon_timer <= 0 and dist < self.aggro_range:
            self.summon_timer = 10.0

        if dist < self.aggro_range:
            if self.behavior == "dive" and self.state != "diving":
                self.state = "diving"
                self.charge_timer = 1.5
            elif self.behavior == "charge" and self.charge_timer <= 0:
                self.state = "charging"
                self.charge_timer = 2.0
            elif dist < self.attack_range and self.attack_cooldown <= 0:
                # cooldown is set by the game loop when the hit lands
                self.state = "attacking"
            elif self.behavior != "burrow":
                self.state = "chasing"
        else:
            if self.state_timer <= 0:
                self.state = random.choice(["idle", "wander"])
                self.state_timer = random.uniform(1, 3)
                if self.state == "wander":
                    angle = random.uniform(0, 6.28)
                    self.vx = math.cos(angle) * self.speed * 0.5
                    self.vy = math.sin(angle) * self.speed * 0.5

        if self.state == "chasing" and self.behavior != "burrow":
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed
            self.vx = math.cos(angle) * self.speed
            self.vy = math.sin(angle) * self.speed
        elif self.state == "charging":
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed * 3
            self.y += math.sin(angle) * self.speed * 3
        elif self.state == "diving":
            if self.charge_timer > 0:
                self.y -= self.speed * 2
            else:
                angle = math.atan2(dy, dx)
                self.x += math.cos(angle) * self.speed * 4
                self.y += math.sin(angle) * self.speed * 4
                if dist < 30:
                    self.state = "chasing"
        elif self.state == "wander":
            self.x += self.vx
            self.y += self.vy
        elif self.state == "emerge":
            self.y -= self.speed

        self.x = max(10, min(WORLD_W - 10, self.x))
        self.y = max(10, min(WORLD_H - 10, self.y))

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if sx < -50 or sx > WIDTH + 50 or sy < -50 or sy > HEIGHT + 50:
            return

        if self.stealthed and self.stealth_timer <= 0:
            ghost = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ghost, (*self.color[:3], 40), (self.size, self.size), self.size)
            screen.blit(ghost, (sx - self.size, sy - self.size))
            return

        pygame.draw.ellipse(screen, (0, 0, 0, 50), (sx - self.size, sy +
                            self.size * 0.5, self.size * 2, self.size * 0.5))

        glow_r = self.size + 8 + int(math.sin(self.glow_t * 2) * 3)
        glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        glow_color = (*self.color[:3], int(30 + math.sin(self.glow_t) * 15))
        pygame.draw.circle(glow_surf, glow_color, (glow_r, glow_r), glow_r)
        screen.blit(glow_surf, (sx - glow_r, sy - glow_r))

        body_offset = int(math.sin(self.anim_time * 3) * 2) if self.state == "chasing" else 0

        if self.behavior == "burrow" and self.state == "burrowed":
            pygame.draw.ellipse(screen, self.color, (sx - self.size, sy + 5, self.size * 2, 8))
        elif self.behavior == "swarm":
            for i in range(3):
                offset_x = math.cos(self.anim_time * 4 + i * 2.1) * 8
                offset_y = math.sin(self.anim_time * 4 + i * 2.1) * 4
                pygame.draw.circle(screen, self.color, (int(sx + offset_x),
                                   int(sy + offset_y + body_offset)), self.size // 2)
        else:
            pygame.draw.circle(screen, self.color, (sx, sy + body_offset), self.size)

            if self.behavior == "elite":
                for i in range(3):
                    angle = self.anim_time * 2 + i * 2.1
                    ex = sx + math.cos(angle) * (self.size + 5)
                    ey = sy + math.sin(angle) * (self.size + 5) + body_offset
                    pygame.draw.circle(screen, (255, 200, 50), (int(ex), int(ey)), 3)

            if self.behavior == "stealth" and not self.stealthed:
                pygame.draw.circle(screen, (80, 0, 120), (sx, sy + body_offset), self.size + 4, 2)

        for i in range(3):
            angle = self.anim_time * 2 + i * 2.1
            vx = sx + math.cos(angle) * self.size * 0.6
            vy = sy + math.sin(angle) * self.size * 0.6 + body_offset
            pygame.draw.circle(screen, (20, 0, 20, 100), (int(vx), int(vy)), 3)

        for ex_pos in [-self.size * 0.3, self.size * 0.3]:
            ex_s = sx + ex_pos
            ey_s = sy - self.size * 0.2 + body_offset
            eye_color = (255, 50, 50) if self.tier >= 3 else RED
            pygame.draw.circle(screen, eye_color, (int(ex_s), int(ey_s)), 3)
            pygame.draw.circle(screen, (200, 0, 0), (int(ex_s), int(ey_s)), 1.5)

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

        nf = pygame.font.Font(None, 14)
        name_surf = nf.render(self.name, True, (180, 180, 180))
        screen.blit(name_surf, (sx - name_surf.get_width() // 2, bar_y - 12))

    def take_damage(self, amount):
        if self.stealthed and self.stealth_timer <= 0:
            amount = int(amount * 1.5)
        self.hp -= amount
        return self.hp <= 0

    def get_drops(self):
        drops = []
        for drop in self.drops:
            if random.random() < self.drop_chance:
                drops.append(drop)
        if random.random() < 0.1:
            drops.append("Gold Leaves")
        return drops
