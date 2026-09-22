import pygame
import math
import random
from config import *
from src.particles import ParticleSystem


class Player:
    def __init__(self, x, y, player_class=PlayerClass.GUARDIAN):
        self.x = x
        self.y = y
        self.player_class = player_class
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.stats = dict(CLASS_STATS[player_class])
        self.hp = self.stats["hp"]
        self.max_hp = self.stats["hp"]
        self.energy = self.stats["energy"]
        self.max_energy = self.stats["energy"]
        self.attack_power = self.stats["attack"]
        self.defense = self.stats["defense"]
        self.speed = self.stats["speed"]

        self.facing = 0  # angle in radians
        self.velocity_x = 0
        self.velocity_y = 0
        self.dodging = False
        self.dodge_timer = 0
        self.dodge_cooldown = 0
        self.just_dodged = False
        self.just_leveled_up = False
        self.just_collected = False
        self.attack_timer = 0
        self.attack_cooldown = 0.3
        self.attack_anim = 0
        self.hit_timer = 0
        self.invincible = 0
        self.combo = 0
        self.combo_timer = 0

        self.inventory = {"resources": {}, "items": [], "equipment": {}, "weapons": []}
        self.creatures = []
        self.quests = []
        self.skills = self._init_skills()
        self.particles = ParticleSystem()
        self.size = 16
        self.color = CLASS_COLORS[player_class]

        self.weapon_id = None
        self.weapon = dict(UNARMED)
        self.weapon_switch_cooldown = 0
        self.projectiles = []
        self.slash_anim = 0
        self.glow_t = 0
        self.anim_time = 0

    def _init_skills(self):
        base = {
            "attack": {"cooldown": 0, "max_cd": 0.3, "energy_cost": 0},
            "dodge": {"cooldown": 0, "max_cd": 1.0, "energy_cost": 10},
            "special": {"cooldown": 0, "max_cd": 5.0, "energy_cost": 30},
        }
        class_skills = {
            PlayerClass.GUARDIAN: {"shield_bash": {"cooldown": 0, "max_cd": 3.0, "energy_cost": 20}},
            PlayerClass.RANGER: {"arrow_storm": {"cooldown": 0, "max_cd": 3.0, "energy_cost": 20}},
            PlayerClass.MAGE: {"fireball": {"cooldown": 0, "max_cd": 3.0, "energy_cost": 20}},
            PlayerClass.MECHANIC: {"turret": {"cooldown": 0, "max_cd": 3.0, "energy_cost": 20}},
            PlayerClass.BEAST_TAMER: {"beast_fury": {"cooldown": 0, "max_cd": 3.0, "energy_cost": 20}},
        }
        base.update(class_skills.get(self.player_class, {}))
        return base

    def update(self, dt, keys, mouse_buttons, mouse_pos, world, camera_x, camera_y):
        self.particles.update()
        self.anim_time = getattr(self, 'anim_time', 0) + dt
        self.glow_t = getattr(self, 'glow_t', 0) + dt

        # Cooldowns
        for skill in self.skills.values():
            skill["cooldown"] = max(0, skill["cooldown"] - dt)
        self.invincible = max(0, self.invincible - dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.dodge_cooldown = max(0, self.dodge_cooldown - dt)
        self.hit_timer = max(0, self.hit_timer - dt)
        self.combo_timer = max(0, self.combo_timer - dt)
        self.weapon_switch_cooldown = max(0, self.weapon_switch_cooldown - dt)
        self.slash_anim = max(0, self.slash_anim - dt * 5)
        if self.combo_timer <= 0:
            self.combo = 0

        # Energy regen
        if self.energy < self.max_energy:
            self.energy = min(self.max_energy, self.energy + 2 * dt)

        # Movement
        mx, my = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            my = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            my = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mx = 1

        # Dodge
        if keys[pygame.K_SPACE] and self.dodge_cooldown <= 0 and not self.dodging and self.energy >= 10:
            self.dodging = True
            self.dodge_timer = 0.3
            self.dodge_cooldown = 1.0
            self.invincible = 0.3
            self.energy -= 10
            self.just_dodged = True
            self.particles.burst(self.x, self.y, CLASS_COLORS[self.player_class], 8, 3, 15, 3)

        if self.dodging:
            self.dodge_timer -= dt
            dodge_speed = 8
            self.x += math.cos(self.facing) * dodge_speed
            self.y += math.sin(self.facing) * dodge_speed
            self.particles.trail(self.x, self.y, (200, 200, 255), 0.8, 1, 15, 3)
            if self.dodge_timer <= 0:
                self.dodging = False

        if not self.dodging:
            if mx != 0 or my != 0:
                length = math.sqrt(mx * mx + my * my)
                mx /= length
                my /= length
                self.facing = math.atan2(my, mx)
            self.x += mx * self.speed
            self.y += my * self.speed

        # Clamp to world
        self.x = max(20, min(WORLD_W - 20, self.x))
        self.y = max(20, min(WORLD_H - 20, self.y))

        # Movement particles
        if (mx != 0 or my != 0) and not self.dodging:
            self.particles.trail(self.x, self.y, self.color, 0.3, 0.5, 15, 2)

        # Attack on mouse click
        if mouse_buttons[0] and self.attack_timer <= 0:
            self._attack(mouse_pos, camera_x, camera_y)

        # Attack animation
        if self.attack_anim > 0:
            self.attack_anim -= dt * 5

        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p["life"] > 0]
        for proj in self.projectiles:
            proj["x"] += proj["vx"]
            proj["y"] += proj["vy"]
            proj["life"] -= 1
            self.particles.trail(proj["x"], proj["y"], proj["color"], 0.5, 1, 10, 2)

        # Resource collection
        self._collect_nearby(world)

    def _attack(self, mouse_pos, camera_x, camera_y):
        target_x = mouse_pos[0] + camera_x
        target_y = mouse_pos[1] + camera_y
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.facing = angle
        self.attack_timer = self.weapon["speed"]
        self.attack_anim = 1
        self.slash_anim = 1 if self.weapon["type"] == "sword" else 0
        self.combo += 1
        self.combo_timer = 2.0

        if self.weapon["type"] == "gun":
            speed = self.weapon.get("projectile_speed", 12)
            p_color = self.weapon.get("projectile_color", self.weapon["trail_color"])
            self.projectiles.append({
                "x": self.x + math.cos(angle) * 20,
                "y": self.y + math.sin(angle) * 20,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "damage": self.weapon["damage"],
                "color": p_color,
                "range": self.weapon["range"],
                "dist_traveled": 0,
                "life": 60,
            })
            self.particles.burst(self.x + math.cos(angle) * 18, self.y + math.sin(angle) * 18,
                                 self.weapon["trail_color"], 8, 3, 12, 3)
        else:
            dist = self.weapon["range"]
            ax = self.x + math.cos(angle) * dist * 0.6
            ay = self.y + math.sin(angle) * dist * 0.6
            self.particles.burst(ax, ay, self.weapon["trail_color"], 8, 4, 15, 5)
        self.combo = min(self.combo, 5)

    def _collect_nearby(self, world):
        tile = world.get_tile(int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))
        if tile and tile.resource and random.random() < 0.02:
            res = tile.resource
            self.inventory["resources"][res] = self.inventory["resources"].get(res, 0) + 1
            self.particles.burst(self.x, self.y, RESOURCES[res]["color"], 5, 2, 20, 3)
            self.xp += 5
            tile.resource = None
            self.just_collected = True

    def equip_weapon(self, weapon_id):
        if weapon_id in WEAPONS:
            self.weapon_id = weapon_id
            self.weapon = dict(WEAPONS[weapon_id])
            self.particles.burst(self.x, self.y, self.weapon["trail_color"], 10, 3, 20, 4)
            return True
        return False

    def unequip_weapon(self):
        self.weapon_id = None
        self.weapon = dict(UNARMED)

    def weapon_has_ammo(self):
        if self.weapon["type"] == "gun":
            return True
        return True

    def take_damage(self, amount):
        if self.invincible > 0:
            return False
        dmg = max(1, amount - self.defense // 2)
        self.hp -= dmg
        self.invincible = 0.5
        self.hit_timer = 0.3
        self.particles.burst(self.x, self.y, RED, 10, 4, 20, 4)
        return True

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)
        self.particles.burst(self.x, self.y, GREEN_GLOW, 8, 2, 25, 4)

    def add_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.3)
        self.max_hp += 10
        self.hp = self.max_hp
        self.max_energy += 5
        self.energy = self.max_energy
        self.attack_power += 2
        self.defense += 1
        self.just_leveled_up = True
        self.particles.burst(self.x, self.y, GOLD, 20, 5, 40, 6)

    def add_creature(self, creature):
        if len(self.creatures) < 6:
            self.creatures.append(creature)
            self.particles.burst(self.x, self.y, creature["color"], 15, 4, 30, 5)
            return True
        return False

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if self.hit_timer > 0 and int(self.hit_timer * 10) % 2 == 0:
            return

        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 60), (sx - 12, sy + 10, 24, 8))

        # Dodge effect
        if self.dodging:
            alpha = 100
            for i in range(5):
                trail_x = sx + random.randint(-20, 20)
                trail_y = sy + random.randint(-10, 10)
                pygame.draw.circle(screen, (*self.color[:3], alpha // (i + 1)), (trail_x, trail_y), self.size - i * 2)

        # Player body
        body_color = self.color
        if self.invincible > 0:
            body_color = (255, 255, 255)

        # Class-specific drawing
        pygame.draw.circle(screen, body_color, (sx, sy), self.size)
        pygame.draw.circle(screen, (*body_color[:3], 80), (sx, sy), self.size + 4, 2)

        # Class symbol
        symbol_color = GOLD
        if self.player_class == PlayerClass.GUARDIAN:
            pygame.draw.rect(screen, symbol_color, (sx - 4, sy - 4, 8, 8), 2)
        elif self.player_class == PlayerClass.RANGER:
            pygame.draw.circle(screen, symbol_color, (sx, sy - 4), 4, 2)
        elif self.player_class == PlayerClass.MAGE:
            pygame.draw.polygon(screen, symbol_color, [(sx, sy - 6), (sx - 4, sy + 2), (sx + 4, sy + 2)], 2)
        elif self.player_class == PlayerClass.MECHANIC:
            pygame.draw.rect(screen, symbol_color, (sx - 3, sy - 3, 6, 6))
        elif self.player_class == PlayerClass.BEAST_TAMER:
            pygame.draw.circle(screen, symbol_color, (sx, sy), 5, 2)

        # Eyes
        eye_offset = 5
        eye_dir = (math.cos(self.facing) * 3, math.sin(self.facing) * 3)
        for ex, ey in [(-3, -2), (3, -2)]:
            wx = sx + ex + eye_dir[0]
            wy = sy + ey + eye_dir[1]
            pygame.draw.circle(screen, WHITE, (int(wx), int(wy)), 3)
            pygame.draw.circle(screen, (0, 0, 0), (int(wx + eye_dir[0] * 0.5), int(wy + eye_dir[1] * 0.5)), 1.5)

        # Attack arc
        if self.attack_anim > 0:
            arc_angle = self.facing + math.sin(self.anim_time * 20) * 0.5
            for i in range(5):
                a = arc_angle + (i - 2) * 0.2
                dist = 25 + self.attack_anim * 10
                px = sx + math.cos(a) * dist
                py = sy + math.sin(a) * dist
                alpha = int(200 * self.attack_anim * (1 - abs(i - 2) / 3))
                pygame.draw.circle(screen, (*GOLD[:3], alpha), (int(px), int(py)), 3)

        # Class glow
        glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        glow_color = (*self.color[:3], int(30 + math.sin(self.glow_t * 2) * 15))
        pygame.draw.circle(glow_surf, glow_color, (30, 30), 25)
        screen.blit(glow_surf, (sx - 30, sy - 30))

        # Draw weapon
        self._draw_weapon(screen, sx, sy)

        # Draw projectiles
        for proj in self.projectiles:
            px = int(proj["x"] - camera_x)
            py = int(proj["y"] - camera_y)
            if -10 < px < WIDTH + 10 and -10 < py < HEIGHT + 10:
                p_color = proj["color"]
                glow_s = pygame.Surface((16, 16), pygame.SRCALPHA)
                pygame.draw.circle(glow_s, (*p_color[:3], 80), (8, 8), 8)
                screen.blit(glow_s, (px - 8, py - 8))
                pygame.draw.circle(screen, p_color, (px, py), 4)
                pygame.draw.circle(screen, WHITE, (px, py), 2)

        # HP bar above
        bar_w = 32
        bar_h = 4
        bar_x = sx - bar_w // 2
        bar_y = sy - self.size - 10
        pygame.draw.rect(screen, (40, 20, 20), (bar_x, bar_y, bar_w, bar_h))
        fill = int(bar_w * (self.hp / self.max_hp))
        if fill > 0:
            pygame.draw.rect(screen, (60, 220, 60), (bar_x, bar_y, fill, bar_h))

        # Name
        if hasattr(self, 'name'):
            nf = pygame.font.Font(None, 16)
            n = nf.render(self.name, True, (200, 200, 200))
            screen.blit(n, (sx - n.get_width() // 2, bar_y - 12))

    def _draw_weapon(self, screen, sx, sy):
        w_type = self.weapon["type"]
        w_color = self.weapon["color"]
        t_color = self.weapon["trail_color"]
        angle = self.facing

        if w_type == "sword":
            blade_len = 20
            if self.slash_anim > 0:
                blade_len = 20 + self.slash_anim * 15
                sweep = self.slash_anim * 2.5
            else:
                sweep = 0

            tip_x = sx + math.cos(angle) * blade_len
            tip_y = sy + math.sin(angle) * blade_len
            hilt_x = sx + math.cos(angle) * 5
            hilt_y = sy + math.sin(angle) * 5

            pygame.draw.line(screen, (80, 70, 60), (int(hilt_x), int(hilt_y)), (int(tip_x), int(tip_y)), 3)
            pygame.draw.line(screen, w_color, (int(hilt_x), int(hilt_y)), (int(tip_x), int(tip_y)), 2)
            tip_glow = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(tip_glow, (*t_color[:3], 120), (4, 4), 4)
            screen.blit(tip_glow, (int(tip_x) - 4, int(tip_y) - 4))

            if sweep > 0:
                for i in range(6):
                    a = angle + sweep * (i / 5 - 0.5)
                    sd = blade_len * 0.7
                    spx = sx + math.cos(a) * sd
                    spy = sy + math.sin(a) * sd
                    alpha = int(150 * (1 - i / 6) * self.slash_anim)
                    ss = pygame.Surface((6, 6), pygame.SRCALPHA)
                    pygame.draw.circle(ss, (*t_color[:3], alpha), (3, 3), 3)
                    screen.blit(ss, (int(spx) - 3, int(spy) - 3))

        elif w_type == "gun":
            barrel_len = 18
            perp = angle + math.pi / 2
            bx1 = sx + math.cos(angle) * 10 + math.cos(perp) * 3
            by1 = sy + math.sin(angle) * 10 + math.sin(perp) * 3
            bx2 = bx1 + math.cos(angle) * barrel_len
            by2 = by1 + math.sin(angle) * barrel_len

            pygame.draw.line(screen, (50, 50, 60), (int(bx1), int(by1)), (int(bx2), int(by2)), 5)
            pygame.draw.line(screen, w_color, (int(bx1), int(by1)), (int(bx2), int(by2)), 3)

            muzzle_glow = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(muzzle_glow, (*t_color[:3], int(60 + math.sin(self.anim_time * 8) * 30)), (6, 6), 6)
            screen.blit(muzzle_glow, (int(bx2) - 6, int(by2) - 6))

            if self.attack_anim > 0.5:
                flash_alpha = int(255 * (self.attack_anim - 0.5) * 2)
                flash_s = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(flash_s, (*t_color[:3], min(255, flash_alpha)), (10, 10), 10)
                screen.blit(flash_s, (int(bx2) - 10, int(by2) - 10))

    # Pets
        for i, pet in enumerate(self.creatures):
            pet_x = sx - 20 + i * 15
            pet_y = sy + 20
            pet_color = pet.get("color", (255, 140, 60))
            pygame.draw.circle(screen, pet_color, (pet_x, pet_y), 6)
            pygame.draw.circle(screen, (*pet_color[:3], 60), (pet_x, pet_y), 9, 1)
