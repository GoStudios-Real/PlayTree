import pygame
import math
from config import *

BUILDING_TYPES = {
    "wooden_wall": {
        "name": "Wooden Wall", "hp": 100, "size": 48, "color": (120, 80, 50),
        "cost": {"Tree Energy": 5}, "category": "defense", "solid": True,
        "desc": "Basic defensive wall",
    },
    "stone_wall": {
        "name": "Stone Wall", "hp": 250, "size": 48, "color": (140, 140, 140),
        "cost": {"Crystal Dust": 8, "Tree Energy": 3}, "category": "defense", "solid": True,
        "desc": "Reinforced stone wall",
    },
    "crystal_wall": {
        "name": "Crystal Wall", "hp": 400, "size": 48, "color": (160, 100, 220),
        "cost": {"Crystal Dust": 15, "Light Fragments": 5}, "category": "defense", "solid": True,
        "desc": "Energized crystal barrier",
    },
    "crafting_table": {
        "name": "Crafting Table", "hp": 80, "size": 48, "color": (160, 120, 60),
        "cost": {"Tree Energy": 10, "Crystal Dust": 3}, "category": "utility", "solid": False,
        "desc": "+10% crafting efficiency",
    },
    "forge": {
        "name": "Forge", "hp": 120, "size": 48, "color": (200, 100, 50),
        "cost": {"Crystal Dust": 12, "Ancient Seeds": 3}, "category": "utility", "solid": False,
        "desc": "Craft weapons with bonus stats",
    },
    "healing_shrine": {
        "name": "Healing Shrine", "hp": 60, "size": 48, "color": (100, 200, 150),
        "cost": {"Light Fragments": 5, "Tree Energy": 8}, "category": "utility", "solid": False,
        "desc": "Slowly regenerates nearby HP",
    },
    "energy_well": {
        "name": "Energy Well", "hp": 60, "size": 48, "color": (80, 160, 255),
        "cost": {"Crystal Dust": 8, "Light Fragments": 3}, "category": "utility", "solid": False,
        "desc": "Slowly regenerates nearby energy",
    },
    "watchtower": {
        "name": "Watchtower", "hp": 150, "size": 48, "color": (100, 90, 70),
        "cost": {"Tree Energy": 12, "Crystal Dust": 5}, "category": "defense", "solid": True,
        "desc": "Extends minimap vision range",
    },
    "turret": {
        "name": "Auto Turret", "hp": 80, "size": 48, "color": (80, 80, 100),
        "cost": {"Crystal Dust": 10, "Light Fragments": 4}, "category": "defense", "solid": False,
        "desc": "Shoots nearby enemies",
        "damage": 8, "range": 150, "cooldown": 2.0,
    },
    "crop_plot": {
        "name": "Crop Plot", "hp": 40, "size": 48, "color": (60, 120, 40),
        "cost": {"Tree Energy": 6, "Ancient Seeds": 2}, "category": "production", "solid": False,
        "desc": "Produces Tree Energy over time",
        "production": "Tree Energy", "rate": 1.0,
    },
    "crystal_extractor": {
        "name": "Crystal Extractor", "hp": 60, "size": 48, "color": (140, 80, 200),
        "cost": {"Crystal Dust": 10, "Tree Energy": 5}, "category": "production", "solid": False,
        "desc": "Produces Crystal Dust over time",
        "production": "Crystal Dust", "rate": 0.5,
    },
    "storage_box": {
        "name": "Storage Box", "hp": 50, "size": 48, "color": (140, 100, 60),
        "cost": {"Tree Energy": 4}, "category": "utility", "solid": True,
        "desc": "+20 inventory slots",
    },
    "bed": {
        "name": "Bed", "hp": 30, "size": 48, "color": (180, 60, 60),
        "cost": {"Tree Energy": 8, "Ancient Seeds": 1}, "category": "utility", "solid": False,
        "desc": "Sets respawn point",
    },
    "gate": {
        "name": "Wooden Gate", "hp": 80, "size": 48, "color": (140, 100, 60),
        "cost": {"Tree Energy": 8}, "category": "defense", "solid": False,
        "desc": "Walk-through door",
    },
    "torch": {
        "name": "Torch", "hp": 20, "size": 48, "color": (255, 180, 50),
        "cost": {"Tree Energy": 2}, "category": "decoration", "solid": False,
        "desc": "Illuminates nearby area",
        "light_radius": 150,
    },
    "banner": {
        "name": "PlayTree Banner", "hp": 15, "size": 48, "color": GREEN_GLOW,
        "cost": {"Tree Energy": 3, "Ancient Seeds": 1}, "category": "decoration", "solid": False,
        "desc": "Shows your allegiance",
    },
}

class Building:
    def __init__(self, x, y, build_type):
        data = BUILDING_TYPES[build_type]
        self.x = x
        self.y = y
        self.build_type = build_type
        self.name = data["name"]
        self.hp = data["hp"]
        self.max_hp = data["hp"]
        self.size = data["size"]
        self.color = data["color"]
        self.solid = data.get("solid", False)
        self.category = data.get("category", "misc")
        self.production = data.get("production")
        self.production_rate = data.get("rate", 0)
        self.light_radius = data.get("light_radius", 0)
        self.turret_damage = data.get("damage", 0)
        self.turret_range = data.get("range", 0)
        self.turret_cooldown = data.get("cooldown", 2.0)
        self.turret_timer = 0
        self.production_timer = 0
        self.anim_time = 0
        self.flash_timer = 0
        self.owner = None

    def update(self, dt, enemies=None, player=None):
        self.anim_time += dt
        self.flash_timer = max(0, self.flash_timer - dt)
        self.turret_timer = max(0, self.turret_timer - dt)

        if self.production and player:
            self.production_timer += dt
            if self.production_timer >= 30.0:
                self.production_timer = 0
                player.inventory["resources"][self.production] = \
                    player.inventory["resources"].get(self.production, 0) + 1

        if self.category == "defense" and self.turret_damage > 0 and enemies:
            self.turret_timer -= dt
            if self.turret_timer <= 0:
                for enemy in enemies:
                    dx = enemy.x - self.x
                    dy = enemy.y - self.y
                    if math.sqrt(dx*dx + dy*dy) < self.turret_range:
                        enemy.take_damage(self.turret_damage)
                        self.turret_timer = self.turret_cooldown
                        break

    def take_damage(self, amount):
        self.hp -= amount
        self.flash_timer = 0.15
        return self.hp <= 0

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if sx < -60 or sx > WIDTH + 60 or sy < -60 or sy > HEIGHT + 60:
            return

        draw_color = (255, 100, 100) if self.flash_timer > 0 else self.color

        if self.category == "defense":
            if self.build_type in ("wooden_wall", "stone_wall", "crystal_wall"):
                pygame.draw.rect(screen, draw_color, (sx - self.size//2, sy - self.size//2, self.size, self.size))
                pygame.draw.rect(screen, (max(0, draw_color[0]-30), max(0, draw_color[1]-30), max(0, draw_color[2]-30)),
                               (sx - self.size//2, sy - self.size//2, self.size, self.size), 2)
                if self.build_type == "crystal_wall":
                    glow = pygame.Surface((self.size + 10, self.size + 10), pygame.SRCALPHA)
                    pulse = int(30 + 20 * math.sin(self.anim_time * 2))
                    pygame.draw.rect(glow, (*draw_color[:3], pulse), glow.get_rect(), border_radius=4)
                    screen.blit(glow, (sx - self.size//2 - 5, sy - self.size//2 - 5))
            elif self.build_type == "watchtower":
                pygame.draw.rect(screen, draw_color, (sx - 8, sy - 20, 16, 40))
                pygame.draw.rect(screen, draw_color, (sx - 14, sy - 24, 28, 8))
            elif self.build_type == "turret":
                pygame.draw.circle(screen, draw_color, (sx, sy), 14)
                pygame.draw.circle(screen, (60, 60, 80), (sx, sy), 10)
                angle = self.anim_time * 0.5
                pygame.draw.line(screen, (80, 80, 100), (sx, sy),
                               (sx + math.cos(angle) * 18, sy + math.sin(angle) * 18), 3)
            elif self.build_type == "gate":
                pygame.draw.rect(screen, draw_color, (sx - self.size//2, sy - self.size//2, self.size, self.size))
                pygame.draw.rect(screen, (80, 60, 40), (sx - 8, sy - self.size//2, 16, self.size))

        elif self.category == "utility":
            if self.build_type == "crafting_table":
                pygame.draw.rect(screen, draw_color, (sx - 16, sy - 10, 32, 20))
                pygame.draw.rect(screen, (120, 80, 40), (sx - 18, sy + 6, 4, 8))
                pygame.draw.rect(screen, (120, 80, 40), (sx + 14, sy + 6, 4, 8))
            elif self.build_type == "forge":
                pygame.draw.ellipse(screen, draw_color, (sx - 16, sy - 12, 32, 24))
                glow = pygame.Surface((20, 12), pygame.SRCALPHA)
                flicker = int(150 + 50 * math.sin(self.anim_time * 8))
                pygame.draw.ellipse(glow, (255, min(255, flicker), 50, 180), (0, 0, 20, 12))
                screen.blit(glow, (sx - 10, sy - 2))
            elif self.build_type == "healing_shrine":
                pygame.draw.circle(screen, draw_color, (sx, sy), 16)
                pulse = int(40 + 30 * math.sin(self.anim_time * 2))
                glow_s = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(glow_s, (100, 255, 150, pulse), (25, 25), 25)
                screen.blit(glow_s, (sx - 25, sy - 25))
                for i in range(3):
                    angle = self.anim_time + i * 2.1
                    px = sx + math.cos(angle) * 12
                    py = sy + math.sin(angle) * 12
                    pygame.draw.circle(screen, (200, 255, 200), (int(px), int(py)), 2)
            elif self.build_type == "energy_well":
                pygame.draw.circle(screen, draw_color, (sx, sy), 16)
                for i in range(4):
                    angle = self.anim_time * 1.5 + i * 1.57
                    px = sx + math.cos(angle) * 20
                    py = sy + math.sin(angle) * 20
                    pygame.draw.circle(screen, (100, 180, 255), (int(px), int(py)), 2)
            elif self.build_type == "storage_box":
                pygame.draw.rect(screen, draw_color, (sx - 14, sy - 10, 28, 20))
                pygame.draw.rect(screen, (100, 70, 40), (sx - 2, sy - 2, 4, 4))
            elif self.build_type == "bed":
                pygame.draw.rect(screen, draw_color, (sx - 16, sy - 6, 32, 12))
                pygame.draw.rect(screen, (200, 100, 100), (sx - 16, sy - 10, 10, 8))

        elif self.category == "production":
            if self.build_type == "crop_plot":
                pygame.draw.rect(screen, draw_color, (sx - 16, sy - 12, 32, 24))
                for i in range(3):
                    gx = sx - 8 + i * 8
                    gy = sy - 8 + int(math.sin(self.anim_time * 2 + i) * 2)
                    pygame.draw.line(screen, (40, 140, 30), (gx, sy + 8), (gx, gy), 2)
                    pygame.draw.circle(screen, (80, 200, 60), (gx, gy), 3)
            elif self.build_type == "crystal_extractor":
                pygame.draw.rect(screen, draw_color, (sx - 14, sy - 10, 28, 20))
                for i in range(2):
                    cx = sx - 6 + i * 12
                    cy = sy - 6 + int(math.sin(self.anim_time * 3 + i) * 3)
                    pygame.draw.circle(screen, CRYSTAL, (cx, cy), 4)

        elif self.category == "decoration":
            if self.build_type == "torch":
                pygame.draw.rect(screen, (80, 60, 40), (sx - 2, sy - 2, 4, 14))
                flame_color = (255, int(180 + 40 * math.sin(self.anim_time * 10)), 50)
                pygame.draw.circle(screen, flame_color, (sx, sy - 6), 5)
                glow = pygame.Surface((40, 40), pygame.SRCALPHA)
                pulse = int(30 + 15 * math.sin(self.anim_time * 6))
                pygame.draw.circle(glow, (255, 200, 100, pulse), (20, 20), 20)
                screen.blit(glow, (sx - 20, sy - 20))
            elif self.build_type == "banner":
                pygame.draw.rect(screen, (80, 60, 40), (sx - 2, sy - 16, 4, 32))
                pygame.draw.rect(screen, draw_color, (sx + 2, sy - 14, 16, 12))
                wave = int(math.sin(self.anim_time * 3) * 2)
                pygame.draw.polygon(screen, draw_color, [
                    (sx + 2, sy - 14), (sx + 18, sy - 14 + wave),
                    (sx + 18, sy - 2 + wave), (sx + 2, sy - 2)
                ])

        if self.production:
            progress = self.production_timer / 30.0
            bar_w = 30
            bar_x = sx - bar_w // 2
            bar_y = sy + self.size // 2 + 4
            pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_w, 4))
            pygame.draw.rect(screen, GREEN_GLOW, (bar_x, bar_y, int(bar_w * progress), 4))

        if self.hp < self.max_hp:
            hp_ratio = self.hp / self.max_hp
            bar_w = self.size
            bar_x = sx - bar_w // 2
            bar_y = sy - self.size // 2 - 8
            pygame.draw.rect(screen, (40, 20, 20), (bar_x, bar_y, bar_w, 4))
            fill = int(bar_w * hp_ratio)
            hp_color = GREEN_GLOW if hp_ratio > 0.5 else GOLD if hp_ratio > 0.25 else RED
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, fill, 4))


class BaseBuilder:
    def __init__(self):
        self.buildings = []
        self.build_mode = False
        self.selected_build = "wooden_wall"
        self.build_category = "all"
        self.build_rotation = 0
        self.ghost_pos = None

    def toggle_build_mode(self):
        self.build_mode = not self.build_mode
        return self.build_mode

    def set_category(self, cat):
        self.build_category = cat

    def get_available_builds(self):
        if self.build_category == "all":
            return list(BUILDING_TYPES.keys())
        return [k for k, v in BUILDING_TYPES.items() if v.get("category") == self.build_category]

    def can_build(self, build_type, player_resources):
        cost = BUILDING_TYPES.get(build_type, {}).get("cost", {})
        for res, amt in cost.items():
            if player_resources.get(res, 0) < amt:
                return False
        return True

    def build(self, x, y, build_type, player):
        if not self.can_build(build_type, player.inventory.get("resources", {})):
            return False
        cost = BUILDING_TYPES[build_type]["cost"]
        for res, amt in cost.items():
            player.inventory["resources"][res] = player.inventory["resources"].get(res, 0) - amt
        building = Building(x, y, build_type)
        building.owner = player.name
        self.buildings.append(building)
        return True

    def remove_building(self, x, y):
        for b in self.buildings[:]:
            dx = b.x - x
            dy = b.y - y
            if abs(dx) < b.size and abs(dy) < b.size:
                self.buildings.remove(b)
                return True
        return False

    def update(self, dt, enemies=None, player=None):
        for building in self.buildings:
            building.update(dt, enemies, player)
        self.buildings = [b for b in self.buildings if b.hp > 0]

    def draw(self, screen, camera_x, camera_y):
        for building in self.buildings:
            building.draw(screen, camera_x, camera_y)

    def draw_ghost(self, screen, mouse_x, mouse_y, camera_x, camera_y):
        if not self.build_mode:
            return
        wx = mouse_x + camera_x
        wy = mouse_y + camera_y
        snap_x = int(wx // 48) * 48 + 24
        snap_y = int(wy // 48) * 48 + 24
        self.ghost_pos = (snap_x, snap_y)

        sx = int(snap_x - camera_x)
        sy = int(snap_y - camera_y)

        build_data = BUILDING_TYPES.get(self.selected_build, {})
        color = build_data.get("color", (200, 200, 200))

        ghost = pygame.Surface((48, 48), pygame.SRCALPHA)
        ghost.fill((*color[:3], 80))
        screen.blit(ghost, (sx - 24, sy - 24))
        pygame.draw.rect(screen, (*color[:3], 120), (sx - 24, sy - 24, 48, 48), 2)

        nf = pygame.font.Font(None, 16)
        ns = nf.render(build_data.get("name", ""), True, WHITE)
        screen.blit(ns, (sx - ns.get_width()//2, sy - 36))

        cost_text = ", ".join(f"{v} {k}" for k, v in build_data.get("cost", {}).items())
        cs = nf.render(cost_text, True, GOLD)
        screen.blit(cs, (sx - cs.get_width()//2, sy + 28))

    def draw_build_menu(self, screen, player_resources):
        if not self.build_mode:
            return

        menu_w = 280
        menu_h = HEIGHT - 100
        menu_x = WIDTH - menu_w - 10
        menu_y = 50

        bg = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        bg.fill((15, 20, 15, 220))
        pygame.draw.rect(bg, (*GREEN_GLOW[:3], 60), bg.get_rect(), border_radius=8, width=2)
        screen.blit(bg, (menu_x, menu_y))

        tf = pygame.font.Font(None, 28)
        ts = tf.render("BUILD", True, GOLD)
        screen.blit(ts, (menu_x + 10, menu_y + 8))

        categories = ["all", "defense", "utility", "production", "decoration"]
        cf = pygame.font.Font(None, 18)
        for i, cat in enumerate(categories):
            cx = menu_x + 10 + i * 52
            cy = menu_y + 40
            is_sel = cat == self.build_category
            color = GOLD if is_sel else (120, 120, 120)
            cs = cf.render(cat.title(), True, color)
            screen.blit(cs, (cx, cy))

        builds = self.get_available_builds()
        bf = pygame.font.Font(None, 18)
        y = menu_y + 65
        for build_type in builds:
            bd = BUILDING_TYPES[build_type]
            can = self.can_build(build_type, player_resources)
            color = GREEN_GLOW if can else (80, 80, 80)

            is_sel = build_type == self.selected_build
            if is_sel:
                pygame.draw.rect(screen, (*GREEN_GLOW[:3], 30), (menu_x + 5, y - 2, menu_w - 10, 42), border_radius=4)

            bs = bf.render(bd["name"], True, color)
            screen.blit(bs, (menu_x + 15, y))

            cost = bd.get("cost", {})
            cost_text = ", ".join(f"{v}{k[:3]}" for k, v in cost.items())
            cs = bf.render(cost_text, True, (140, 140, 140) if can else (80, 80, 80))
            screen.blit(cs, (menu_x + 15, y + 16))

            y += 44
            if y > menu_y + menu_h - 40:
                break

        try:
            ctrl = pygame.joystick.get_count() > 0
        except Exception:
            ctrl = False
        if ctrl:
            from src.ui import xbox_icons
            xbox_icons.draw_menu_prompt(screen, [("A", "Click", "Select"), ("X", "E", "Place"), ("B", "V", "Exit")], menu_y + menu_h - 25)
        else:
            hint = bf.render("Click to select, E to place", True, (80, 120, 80))
            screen.blit(hint, (menu_x + 10, menu_y + menu_h - 25))

    def handle_click(self, mouse_x, mouse_y, camera_x, camera_y, player):
        if not self.build_mode or not self.ghost_pos:
            return False
        wx, wy = self.ghost_pos
        return self.build(wx, wy, self.selected_build, player)

    def handle_menu_click(self, mx, my, player_resources):
        if not self.build_mode:
            return False

        builds = self.get_available_builds()
        y_offset = 115
        for i, build_type in enumerate(builds):
            if 0 <= my - y_offset - i * 44 < 42:
                self.selected_build = build_type
                return True
        return False
