import pygame
import math
import random
from config import *

BOSS_TYPES = {
    "root_titan": {
        "name": "Root Titan", "color": (100, 80, 50), "accent": (60, 180, 60),
        "hp": 500, "damage": 25, "speed": 0.7, "size": 35,
        "phase2_hp": 250, "phase3_hp": 100,
        "attack_range": 70, "attack_cooldown": 2.0,
        "xp_reward": 500, "gold_reward": 100,
        "drops": ["Ancient Root", "Light Fragment", "Crystal Dust"],
        "abilities": ["root_slam", "root_tendrils", "enrage"],
    },
    "crystal_hydra": {
        "name": "Crystal Hydra", "color": (100, 160, 220), "accent": (200, 230, 255),
        "hp": 450, "damage": 20, "speed": 1.2, "size": 30,
        "phase2_hp": 225, "phase3_hp": 90,
        "attack_range": 60, "attack_cooldown": 1.5,
        "xp_reward": 450, "gold_reward": 90,
        "drops": ["Crystal Dust", "Crystal Dust", "Ancient Seed"],
        "abilities": ["crystal_breath", "split_heads", "shard_rain"],
    },
    "shadow_wraith": {
        "name": "Shadow Wraith", "color": (40, 30, 60), "accent": (160, 80, 255),
        "hp": 350, "damage": 30, "speed": 1.8, "size": 25,
        "phase2_hp": 175, "phase3_hp": 70,
        "attack_range": 50, "attack_cooldown": 1.0,
        "xp_reward": 400, "gold_reward": 80,
        "drops": ["Shadow Essence", "Shadow Essence", "Ancient Root"],
        "abilities": ["shadow_teleport", "fear_pulse", "soul_drain"],
    },
    "sky_guardian": {
        "name": "Sky Guardian", "color": (180, 200, 240), "accent": (255, 255, 200),
        "hp": 400, "damage": 22, "speed": 1.5, "size": 28,
        "phase2_hp": 200, "phase3_hp": 80,
        "attack_range": 80, "attack_cooldown": 1.8,
        "xp_reward": 420, "gold_reward": 85,
        "drops": ["Wind Essence", "Light Fragment", "Ancient Seed"],
        "abilities": ["wind_gust", "lightning_strike", "sky_dive"],
    },
    "hollow_king": {
        "name": "The Hollow King", "color": (60, 20, 80), "accent": (255, 50, 50),
        "hp": 1000, "damage": 40, "speed": 0.9, "size": 45,
        "phase2_hp": 500, "phase3_hp": 200,
        "attack_range": 90, "attack_cooldown": 2.5,
        "xp_reward": 2000, "gold_reward": 500,
        "drops": ["Light Fragment", "Light Fragment", "Ancient Root", "Shadow Essence", "Ancient Seed"],
        "abilities": ["void_beam", "summon_minions", "corruption_wave", "enrage"],
    },
}


class BossHealthBar:
    def __init__(self):
        self.boss = None
        self.visible = False
        self.pulse = 0

    def show(self, boss):
        self.boss = boss
        self.visible = True
        self.pulse = 0

    def hide(self):
        self.visible = False
        self.boss = None

    def update(self, dt):
        if self.visible:
            self.pulse += dt * 3

    def draw(self, screen):
        if not self.visible or not self.boss:
            return
        boss = self.boss
        bar_w = 400
        bar_h = 24
        bar_x = (WIDTH - bar_w) // 2
        bar_y = 20

        bg = pygame.Surface((bar_w + 6, bar_h + 6), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0, 0, 0, 200), bg.get_rect(), border_radius=5)
        screen.blit(bg, (bar_x - 3, bar_y - 3))

        hp_ratio = max(0, boss.hp / boss.max_hp)
        fill_w = int(bar_w * hp_ratio)

        phase = 3
        if hp_ratio > 0.66:
            phase = 1
            hp_color = GREEN_GLOW
        elif hp_ratio > 0.33:
            phase = 2
            hp_color = GOLD
        else:
            phase = 3
            hp_color = (255, 80, 80)

        if phase == 3:
            pulse_alpha = int(180 + 75 * math.sin(self.pulse))
            hp_surface = pygame.Surface((fill_w, bar_h), pygame.SRCALPHA)
            hp_surface.fill((*hp_color[:3], pulse_alpha))
            screen.blit(hp_surface, (bar_x, bar_y))
        else:
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, fill_w, bar_h), border_radius=4)

        for i in range(3):
            seg_x = bar_x + int(bar_w * (i / 3))
            pygame.draw.line(screen, (60, 60, 60), (seg_x, bar_y), (seg_x, bar_y + bar_h))

        nf = pygame.font.Font(None, 28)
        ns = nf.render(f"{boss.name} — Phase {phase}", True, (255, 255, 255))
        screen.blit(ns, (WIDTH // 2 - ns.get_width() // 2, bar_y - 22))

        hf = pygame.font.Font(None, 20)
        hs = hf.render(f"{int(boss.hp)}/{int(boss.max_hp)}", True, (200, 200, 200))
        screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, bar_y + 3))


class Boss:
    def __init__(self, x, y, boss_type="root_titan"):
        data = BOSS_TYPES[boss_type]
        self.x = x
        self.y = y
        self.boss_type = boss_type
        self.name = data["name"]
        self.color = data["color"]
        self.accent = data["accent"]
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.damage = data["damage"]
        self.speed = data["speed"]
        self.size = data["size"]
        self.attack_range = data["attack_range"]
        self.attack_cooldown = data["attack_cooldown"]
        self.xp_reward = data["xp_reward"]
        self.gold_reward = data["gold_reward"]
        self.drops = list(data["drops"])
        self.abilities = list(data["abilities"])
        self.phase2_hp = data["phase2_hp"]
        self.phase3_hp = data["phase3_hp"]
        self.phase = 1
        self.state = "idle"
        self.state_timer = 0
        self.attack_timer = 0
        self.anim_time = 0
        self.target_x = x
        self.target_y = y
        self.health_bar = BossHealthBar()
        self.active = True
        self.death_timer = 0
        self.particles = []
        self.summons = []
        self.ability_timers = {a: 0 for a in self.abilities}
        self.buffed = False
        self.flash_timer = 0

    def update(self, dt, player_x, player_y, enemies_list=None):
        if not self.active:
            self.death_timer += dt
            return

        self.anim_time += dt
        self.attack_timer = max(0, self.attack_timer - dt)
        self.flash_timer = max(0, self.flash_timer - dt)

        hp_ratio = self.hp / self.max_hp
        new_phase = 1
        if hp_ratio <= 0.33:
            new_phase = 3
        elif hp_ratio <= 0.66:
            new_phase = 2

        if new_phase > self.phase:
            self.phase = new_phase
            if self.phase == 3 and "enrage" in self.abilities and not self.buffed:
                self.buffed = True
                self.speed *= 1.4
                self.damage = int(self.damage * 1.3)

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        chase_dist = 300 if self.phase < 3 else 400

        if dist < chase_dist:
            if dist > self.attack_range:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                self.state = "chase"
            else:
                self.state = "attack"
                self.target_x = player_x
                self.target_y = player_y
        else:
            self.state = "idle"

        for ability, timer in self.ability_timers.items():
            self.ability_timers[ability] = max(0, timer - dt)

        self.update_particles(dt)
        self.health_bar.update(dt)

    def can_attack(self):
        return self.active and self.attack_timer <= 0 and self.state == "attack"

    def do_attack(self):
        self.attack_timer = self.attack_cooldown
        if self.phase == 2 and self.attack_timer <= 0:
            return self.get_ability_damage()
        return self.damage

    def get_ability_damage(self):
        ability = random.choice(self.abilities)
        if ability in ["root_slam", "crystal_breath", "void_beam"]:
            return int(self.damage * 1.5)
        elif ability in ["root_tendrils", "split_heads", "shadow_teleport"]:
            return int(self.damage * 1.2)
        elif ability in ["fear_pulse", "soul_drain", "corruption_wave"]:
            return int(self.damage * 1.8)
        return self.damage

    def take_damage(self, amount):
        if not self.active:
            return
        self.hp -= amount
        self.flash_timer = 0.15
        self.spawn_hit_particles(amount)
        if self.hp <= 0:
            self.hp = 0
            self.active = False

    def spawn_hit_particles(self, damage):
        count = min(15, 3 + damage // 5)
        for _ in range(count):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(1, 4)
            color = random.choice([self.accent, self.color, WHITE])
            self.particles.append({
                "x": self.x + math.cos(angle) * self.size * 0.5,
                "y": self.y + math.sin(angle) * self.size * 0.5,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(0.3, 0.8),
                "max_life": 0.8,
                "color": color,
                "size": random.uniform(2, 5),
            })

    def update_particles(self, dt):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.5 * dt
            p["life"] -= dt
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if sx < -100 or sx > WIDTH + 100 or sy < -100 or sy > HEIGHT + 100:
            return

        if self.active:
            bob = math.sin(self.anim_time * 2) * 2
            size = self.size
            if self.phase == 3:
                size = int(self.size * 1.15)

            shadow = pygame.Surface((size * 2, size * 0.5), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 80), shadow.get_rect())
            screen.blit(shadow, (sx - size, sy + size - 2))

            draw_color = self.accent if self.flash_timer > 0 else self.color

            for i in range(3 if self.phase >= 2 else 1):
                offset_x = math.cos(self.anim_time * 1.5 + i * 2.1) * 4
                offset_y = math.sin(self.anim_time * 1.5 + i * 2.1) * 2
                seg_s = size - i * 4
                seg_c = tuple(min(255, c + i * 20) for c in draw_color[:3])
                pygame.draw.circle(screen, seg_c, (int(sx + offset_x), int(sy + bob + offset_y)), seg_s)

            if self.phase >= 2:
                for i in range(2):
                    angle = self.anim_time * 2 + i * math.pi
                    ex = sx + math.cos(angle) * (size + 8)
                    ey = sy + math.sin(angle) * (size * 0.4)
                    pygame.draw.line(screen, self.accent, (sx, int(sy + bob)), (int(ex), int(ey)), 3)
                    pygame.draw.circle(screen, self.accent, (int(ex), int(ey)), 5)

            if self.buffed:
                aura_alpha = int(60 + 40 * math.sin(self.anim_time * 4))
                aura = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                pygame.draw.circle(aura, (255, 50, 50, aura_alpha), (size * 1.5, size * 1.5), size * 1.5)
                screen.blit(aura, (sx - size * 1.5, sy + bob - size * 1.5))

            eye_y = int(sy + bob - 3)
            for ex in [-8, 8]:
                pygame.draw.circle(screen, (30, 30, 30), (sx + ex, eye_y), 4)
                pygame.draw.circle(screen, self.accent, (sx + ex, eye_y), 2)

            if self.state == "attack" and self.attack_timer < 0.3:
                pygame.draw.circle(screen, self.accent, (sx, int(sy + bob)), size + 10, 3)

        for p in self.particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            ps = int(p["size"])
            pc = (*p["color"][:3], alpha)
            particle_surf = pygame.Surface((ps * 2, ps * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, pc, (ps, ps), ps)
            screen.blit(particle_surf, (int(p["x"] - camera_x - ps), int(p["y"] - camera_y - ps)))

    def is_dead(self):
        return not self.active and self.death_timer > 2.0
