import pygame
import math
from config import *

MOUNT_TYPES = {
    "forest_stag": {
        "name": "Forest Stag", "speed": 2.5, "hp": 50, "size": 16,
        "color": (100, 160, 80), "accent": (60, 120, 50),
        "ability": None, "sprint_multiplier": 1.8,
    },
    "crystal_wolf": {
        "name": "Crystal Wolf", "speed": 3.2, "hp": 70, "size": 14,
        "color": (120, 180, 220), "accent": (200, 230, 255),
        "ability": "howl_buff", "sprint_multiplier": 1.5,
    },
    "shadow_raven": {
        "name": "Shadow Raven", "speed": 2.8, "hp": 40, "size": 12,
        "color": (50, 40, 70), "accent": (160, 100, 255),
        "ability": "flight", "sprint_multiplier": 2.0,
    },
    "sky_drake": {
        "name": "Sky Drake", "speed": 3.5, "hp": 90, "size": 18,
        "color": (150, 180, 220), "accent": (255, 255, 200),
        "ability": "glide", "sprint_multiplier": 1.6,
    },
    "ancient_beetle": {
        "name": "Ancient Beetle", "speed": 1.8, "hp": 150, "size": 20,
        "color": (80, 60, 40), "accent": (180, 140, 60),
        "ability": "armor_plating", "sprint_multiplier": 1.3,
    },
}


class Mount:
    def __init__(self, mount_type="forest_stag"):
        data = MOUNT_TYPES[mount_type]
        self.mount_type = mount_type
        self.name = data["name"]
        self.base_speed = data["speed"]
        self.speed = data["speed"]
        self.max_hp = data["hp"]
        self.hp = self.max_hp
        self.size = data["size"]
        self.color = data["color"]
        self.accent = data["accent"]
        self.ability = data["ability"]
        self.sprint_multiplier = data["sprint_multiplier"]
        self.mounted = False
        self.x = 0
        self.y = 0
        self.anim_time = 0
        self.flash_timer = 0
        self.stamina = 100
        self.max_stamina = 100
        self.sprinting = False
        self.ability_active = False
        self.ability_timer = 0
        self.armor_active = False
        self.armor_timer = 0
        self.trail = []

    def update(self, dt, player_x, player_y):
        self.anim_time += dt
        self.flash_timer = max(0, self.flash_timer - dt)

        if self.mounted:
            self.x = player_x
            self.y = player_y

            if self.sprinting and self.stamina > 0:
                self.stamina -= 30 * dt
                if self.stamina <= 0:
                    self.stamina = 0
                    self.sprinting = False
            elif not self.sprinting:
                self.stamina = min(self.max_stamina, self.stamina + 15 * dt)

            if self.ability == "howl_buff" and self.ability_active:
                self.ability_timer -= dt
                if self.ability_timer <= 0:
                    self.ability_active = False

            if self.ability == "armor_plating" and self.armor_active:
                self.ability_timer -= dt
                if self.ability_timer <= 0:
                    self.armor_active = False
                    self.armor_active = False

            self.trail.append((self.x, self.y, self.anim_time))
            if len(self.trail) > 10:
                self.trail.pop(0)

    def take_damage(self, amount):
        if self.armor_active:
            amount = amount // 2
        self.hp -= amount
        self.flash_timer = 0.15
        if self.hp <= 0:
            self.hp = 0
            self.mounted = False

    def sprint(self, on):
        self.sprinting = on and self.stamina > 0

    def use_ability(self):
        if self.ability == "howl_buff":
            self.ability_active = True
            self.ability_timer = 5.0
        elif self.ability == "armor_plating":
            self.armor_active = True
            self.ability_timer = 4.0

    def draw(self, screen, camera_x, camera_y, is_player=False):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if sx < -50 or sx > WIDTH + 50 or sy < -50 or sy > HEIGHT + 50:
            return

        if self.mounted and not is_player:
            return

        draw_color = (255, 100, 100) if self.flash_timer > 0 else self.color

        bob = math.sin(self.anim_time * 6) * (2 if self.sprinting else 1)

        if self.mount_type == "forest_stag":
            self._draw_stag(screen, sx, sy, bob, draw_color)
        elif self.mount_type == "crystal_wolf":
            self._draw_wolf(screen, sx, sy, bob, draw_color)
        elif self.mount_type == "shadow_raven":
            self._draw_raven(screen, sx, sy, bob, draw_color)
        elif self.mount_type == "sky_drake":
            self._draw_drake(screen, sx, sy, bob, draw_color)
        elif self.mount_type == "ancient_beetle":
            self._draw_beetle(screen, sx, sy, bob, draw_color)

        if self.mounted and is_player:
            self._draw_mount_ui(screen)

    def _draw_stag(self, screen, sx, sy, bob, color):
        leg_phase = self.anim_time * 8
        for lx in [-6, 6]:
            leg_off = math.sin(leg_phase + lx) * 3
            pygame.draw.line(screen, color, (sx + lx, sy + 2), (sx + lx + leg_off, sy + 14), 2)

        pygame.draw.ellipse(screen, color, (sx - 10, sy - 4 + bob, 20, 12))
        pygame.draw.circle(screen, color, (sx + 10, sy - 6 + bob), 7)
        pygame.draw.circle(screen, (30, 30, 30), (sx + 13, sy - 7 + bob), 2)
        pygame.draw.line(screen, self.accent, (sx + 10, sy - 12 + bob), (sx + 6, sy - 18 + bob), 2)
        pygame.draw.line(screen, self.accent, (sx + 10, sy - 12 + bob), (sx + 14, sy - 18 + bob), 2)

    def _draw_wolf(self, screen, sx, sy, bob, color):
        leg_phase = self.anim_time * 10
        for lx in [-7, 7]:
            leg_off = math.sin(leg_phase + lx) * 4
            pygame.draw.line(screen, color, (sx + lx, sy + 2), (sx + lx + leg_off, sy + 12), 2)

        pygame.draw.ellipse(screen, color, (sx - 10, sy - 3 + bob, 22, 10))
        pygame.draw.circle(screen, color, (sx + 12, sy - 5 + bob), 6)
        pygame.draw.circle(screen, (30, 30, 30), (sx + 15, sy - 6 + bob), 2)
        pygame.draw.polygon(screen, self.accent, [(sx + 12, sy - 10 + bob),
                            (sx + 9, sy - 16 + bob), (sx + 15, sy - 10 + bob)])
        if self.ability_active:
            pygame.draw.circle(screen, (200, 200, 255), (sx, int(sy + bob)), self.size + 10, 2)

    def _draw_raven(self, screen, sx, sy, bob, color):
        wing = math.sin(self.anim_time * 10) * 8
        pygame.draw.ellipse(screen, color, (sx - 6, sy - 2 + bob, 12, 8))
        pygame.draw.polygon(screen, self.accent, [(sx - 3, sy - 2 + bob),
                            (sx - 10, sy - 4 - wing + bob), (sx + 2, sy + bob)])
        pygame.draw.polygon(screen, self.accent, [(sx + 3, sy - 2 + bob),
                            (sx + 10, sy - 4 - wing + bob), (sx - 2, sy + bob)])
        pygame.draw.circle(screen, color, (sx + 7, sy - 3 + bob), 4)
        pygame.draw.circle(screen, (255, 200, 50), (sx + 9, sy - 3 + bob), 1)

    def _draw_drake(self, screen, sx, sy, bob, color):
        leg_phase = self.anim_time * 8
        for lx in [-8, 8]:
            leg_off = math.sin(leg_phase + lx) * 3
            pygame.draw.line(screen, color, (sx + lx, sy + 4), (sx + lx + leg_off, sy + 16), 3)

        pygame.draw.ellipse(screen, color, (sx - 14, sy - 4 + bob, 28, 14))
        pygame.draw.circle(screen, color, (sx + 14, sy - 6 + bob), 8)
        pygame.draw.circle(screen, (30, 30, 30), (sx + 18, sy - 7 + bob), 2)
        wing = math.sin(self.anim_time * 8) * 10
        pygame.draw.polygon(screen, self.accent, [(sx - 2, sy - 4 + bob),
                            (sx - 12, sy - 10 - wing + bob), (sx + 6, sy + bob)])
        pygame.draw.polygon(screen, self.accent, [(sx + 2, sy - 4 + bob),
                            (sx + 12, sy - 10 - wing + bob), (sx - 6, sy + bob)])
        pygame.draw.line(screen, (255, 200, 100), (sx + 14, sy - 2 + bob), (sx + 22, sy - 1 + bob), 2)

    def _draw_beetle(self, screen, sx, sy, bob, color):
        leg_phase = self.anim_time * 5
        for lx in [-8, 8]:
            leg_off = math.sin(leg_phase + lx) * 2
            pygame.draw.line(screen, color, (sx + lx, sy + 6), (sx + lx + leg_off, sy + 14), 2)

        pygame.draw.ellipse(screen, color, (sx - 12, sy - 6 + bob, 24, 16))
        pygame.draw.ellipse(screen, self.accent, (sx - 4, sy - 10 + bob, 8, 6))
        pygame.draw.line(screen, self.accent, (sx - 4, sy - 4 + bob), (sx + 4, sy - 4 + bob), 2)
        if self.armor_active:
            pygame.draw.rect(screen, self.accent, (sx - 14, sy - 8 + bob, 28, 20), 3, border_radius=6)

    def _draw_mount_ui(self, screen):
        bar_w = 80
        bar_h = 6
        bar_x = WIDTH // 2 - bar_w // 2
        bar_y = HEIGHT - 60

        pygame.draw.rect(screen, (20, 20, 20), (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2))
        stamina_ratio = self.stamina / self.max_stamina
        stamina_color = GREEN_GLOW if stamina_ratio > 0.3 else GOLD
        pygame.draw.rect(screen, stamina_color, (bar_x, bar_y, int(bar_w * stamina_ratio), bar_h))

        sf = pygame.font.Font(None, 18)
        ss = sf.render(f"{self.name}", True, (180, 180, 180))
        screen.blit(ss, (WIDTH // 2 - ss.get_width() // 2, bar_y - 16))

        if self.ability:
            af = pygame.font.Font(None, 16)
            try:
                ctrl = pygame.joystick.get_count() > 0
            except Exception:
                ctrl = False
            if ctrl:
                ab_text = f"[RB] {self.ability.replace('_', ' ').title()}"
            else:
                ab_text = f"[Q] {self.ability.replace('_', ' ').title()}"
            ab_s = af.render(ab_text, True, (160, 160, 160))
            screen.blit(ab_s, (WIDTH // 2 - ab_s.get_width() // 2, bar_y + 10))
