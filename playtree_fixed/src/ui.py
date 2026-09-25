import pygame
import math
from config import *
from src.particles import GlowEffect


class Button:
    def __init__(self, x, y, w, h, text, color=GREEN_GLOW, hover_color=GOLD, callback=None, font_size=28):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback
        self.hovered = False
        self.anim_t = 0
        self.font = pygame.font.Font(None, font_size)
        self.glow_t = random.uniform(0, 6.28)

    def update(self, dt):
        self.glow_t += dt
        self.anim_t = min(1, self.anim_t + dt * 5) if self.hovered else max(0, self.anim_t - dt * 5)

    def draw(self, screen):
        glow = math.sin(self.glow_t * 2) * 0.3 + 0.7
        c = tuple(int(a + (b - a) * self.anim_t) for a, b in zip(self.color[:3], self.hover_color[:3]))
        c = tuple(min(255, int(v * (1 + glow * 0.1))) for v in c)

        pygame.draw.rect(screen, (*c, 40), self.rect, border_radius=8, width=2)
        inner = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, (*c[:3], 20), inner, border_radius=6, width=1)

        pulse = 1 + math.sin(self.glow_t * 3) * 0.02 * self.anim_t
        fs = int(self.font.get_height() * pulse)
        f = pygame.font.Font(None, fs)
        text_surf = f.render(self.text, True, c)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            if self.callback:
                self.callback()
            return True
        return False


class HUD:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 20)
        self.anim_time = 0
        self.controller_connected = False

    def update(self, dt):
        self.anim_time += dt

    def draw(self, screen, particles):
        self._draw_hp_bar(screen)
        self._draw_energy_bar(screen)
        self._draw_minimap(screen)
        self._draw_quest_tracker(screen)
        self._draw_party_status(screen)
        self._draw_resources(screen)
        self._draw_equipped_weapon(screen)
        self._draw_skills(screen)

    def _draw_bar(self, screen, x, y, w, h, current, max_val, color1, color2, label=""):
        bg_rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(screen, (30, 30, 40), bg_rect, border_radius=4)
        pygame.draw.rect(screen, (*color1[:3], 80), bg_rect, border_radius=4, width=1)
        ratio = max(0, current / max_val)
        fill_w = int(w * ratio)
        if fill_w > 0:
            fill_rect = pygame.Rect(x + 2, y + 2, max(0, fill_w - 4), h - 4)
            for i in range(fill_rect.width):
                t = i / fill_rect.width
                c = tuple(int(a + (b - a) * t) for a, b in zip(color1[:3], color2[:3]))
                pygame.draw.line(screen, c, (fill_rect.x + i, fill_rect.y), (fill_rect.x + i, fill_rect.bottom))
            pulse = math.sin(self.anim_time * 3) * 0.15 + 1
            GlowEffect.draw_glow(screen, x + fill_w, y + h // 2, color1, 8, 40)
        label_surf = self.font.render(f"{label}: {int(current)}/{int(max_val)}", True, (220, 220, 230))
        screen.blit(label_surf, (x + w + 10, y + 2))

    def _draw_hp_bar(self, screen):
        self._draw_bar(screen, 20, 20, 250, 22, self.player.hp, self.player.max_hp,
                       (60, 200, 60), (200, 60, 60), "HP")

    def _draw_energy_bar(self, screen):
        self._draw_bar(screen, 20, 50, 250, 22, self.player.energy, self.player.max_energy,
                       (80, 180, 255), (180, 80, 255), "Energy")

    def _draw_minimap(self, screen):
        mm_size = 150
        mm_x = WIDTH - mm_size - 20
        mm_y = 20
        # Background
        pygame.draw.rect(screen, (15, 15, 30, 200), (mm_x, mm_y, mm_size, mm_size), border_radius=6)
        pygame.draw.rect(screen, (60, 180, 80, 80), (mm_x, mm_y, mm_size, mm_size), border_radius=6, width=1)
        # Player-centred local zoom (world is 10^25 — global scale is meaningless)
        view = 3000.0
        scale = mm_size / (2 * view)
        cxp = mm_x + mm_size // 2
        cyp = mm_y + mm_size // 2
        # Player position (centre)
        pygame.draw.circle(screen, GREEN_GLOW, (cxp, cyp), 4)
        pygame.draw.circle(screen, (*GREEN_GLOW[:3], 80), (cxp, cyp), 6, 2)
        # Nearby resources (random dots inside the local window)
        for res in self.player.inventory.get("resources", []):
            rx = cxp + int((random.random() - 0.5) * 2 * view * scale)
            ry = cyp + int((random.random() - 0.5) * 2 * view * scale)
            pygame.draw.circle(screen, (255, 200, 50), (rx, ry), 1)
        # Label
        lbl = self.title_font.render("MINIMAP", True, (100, 200, 120))
        screen.blit(lbl, (mm_x + 5, mm_y + 2))

    def _draw_quest_tracker(self, screen):
        qx = 20
        qy = HEIGHT - 200
        pygame.draw.rect(screen, (15, 15, 30, 200), (qx, qy, 280, 180), border_radius=6)
        pygame.draw.rect(screen, (60, 180, 80, 60), (qx, qy, 280, 180), border_radius=6, width=1)
        title = self.title_font.render("QUESTS", True, (100, 200, 120))
        screen.blit(title, (qx + 10, qy + 5))
        if hasattr(self.player, 'quests') and self.player.quests:
            for i, quest in enumerate(self.player.quests[:3]):
                color = GOLD if quest.get("complete") else (200, 200, 200)
                txt = f"{'[x]' if quest.get('complete') else '[ ]'} {quest['name']}"
                surf = self.font.render(txt, True, color)
                screen.blit(surf, (qx + 10, qy + 30 + i * 25))
                if quest.get("progress"):
                    prog = self.font.render(f"  {quest['progress']}", True, (150, 150, 150))
                    screen.blit(prog, (qx + 15, qy + 30 + i * 25 + 14))
        else:
            noq = self.font.render("No active quests", True, (120, 120, 130))
            screen.blit(noq, (qx + 10, qy + 40))

    def _draw_party_status(self, screen):
        if hasattr(self.player, 'creatures') and self.player.creatures:
            px = 20
            py = HEIGHT - 230
            title = self.title_font.render("PETS", True, (100, 200, 120))
            screen.blit(title, (px, py))
            for i, pet in enumerate(self.player.creatures[:4]):
                cx = px + 10 + i * 45
                cy = py + 25
                pygame.draw.circle(screen, pet.get("color", (255, 140, 60)), (cx, cy), 10)
                pygame.draw.circle(screen, (*pet.get("color", (255, 140, 60))[:3], 60), (cx, cy), 14, 2)
                name = self.font.render(pet["name"][:6], True, (200, 200, 200))
                screen.blit(name, (cx - 15, cy + 14))

    def _draw_resources(self, screen):
        rx = WIDTH - 200
        ry = 190
        title = self.title_font.render("RESOURCES", True, (100, 200, 120))
        screen.blit(title, (rx, ry))
        resources = self.player.inventory.get("resources", {})
        for i, (name, amount) in enumerate(resources.items()):
            if amount > 0:
                color = RESOURCES.get(name, {}).get("color", (200, 200, 200))
                txt = f"{name}: {int(amount)}"
                surf = self.font.render(txt, True, color)
                screen.blit(surf, (rx, ry + 25 + i * 22))

    def _draw_skills(self, screen):
        sx = 20
        sy = 80
        skills = self.player.skills if hasattr(self.player, 'skills') else {}
        for i, (name, info) in enumerate(skills.items()):
            icon_x = sx + i * 55
            icon_y = sy
            cd = info.get("cooldown", 0)
            ready = cd <= 0
            color = GREEN_GLOW if ready else (80, 80, 80)
            pygame.draw.rect(screen, (20, 20, 35), (icon_x, icon_y, 45, 45), border_radius=6)
            pygame.draw.rect(screen, color, (icon_x, icon_y, 45, 45), border_radius=6, width=2 if ready else 1)
            if not ready:
                overlay = pygame.Surface((45, 45), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                screen.blit(overlay, (icon_x, icon_y))
                cd_surf = self.font.render(f"{cd:.1f}", True, (200, 200, 200))
                screen.blit(cd_surf, (icon_x + 8, icon_y + 14))
            letter = name[0].upper()
            ls = self.big_font.render(letter, True, color)
            screen.blit(ls, (icon_x + 14, icon_y + 8))

    def _draw_equipped_weapon(self, screen):
        weapon = self.player.weapon
        wx = 20
        wy = 130
        w_color = weapon.get("color", (200, 200, 200))
        w_name = weapon.get("name", "Fists")
        w_type = weapon.get("type", "sword")
        w_dmg = weapon.get("damage", 5)
        pygame.draw.rect(screen, (15, 20, 15, 200), (wx, wy, 220, 45), border_radius=6)
        pygame.draw.rect(screen, (*w_color[:3], 60), (wx, wy, 220, 45), border_radius=6, width=1)
        icon_x = wx + 20
        icon_y = wy + 22
        if w_type == "sword":
            pygame.draw.line(screen, w_color, (icon_x - 8, icon_y + 8), (icon_x + 8, icon_y - 8), 3)
            pygame.draw.line(screen, w_color, (icon_x - 4, icon_y + 4), (icon_x - 12, icon_y + 4), 2)
        else:
            pygame.draw.line(screen, (50, 50, 60), (icon_x - 10, icon_y), (icon_x + 10, icon_y), 4)
            pygame.draw.line(screen, w_color, (icon_x - 10, icon_y), (icon_x + 10, icon_y), 2)
            pygame.draw.circle(screen, w_color, (icon_x + 12, icon_y), 3)
        nf = self.font.render(w_name, True, w_color)
        screen.blit(nf, (wx + 40, wy + 6))
        df = self.title_font.render(f"DMG: {w_dmg}  |  [{w_type.upper()}]", True, (150, 150, 150))
        screen.blit(df, (wx + 40, wy + 24))
        if self.controller_connected:
            xbox_icons.draw_dual_prompt(screen, wx + 40, wy + 56, "LB", "1-8", "Equip", 14)
            xbox_icons.draw_dual_prompt(screen, wx + 140, wy + 56, "Y", "0", "Unequip", 14)
        else:
            hint = self.title_font.render("Keys 1-8 equip  |  0 unequip", True, (80, 120, 80))
            screen.blit(hint, (wx, wy + 48))


XBOX_COLORS = {
    "A": (76, 175, 80),     # Green
    "B": (244, 67, 54),     # Red
    "X": (33, 150, 243),    # Blue
    "Y": (255, 193, 7),     # Yellow
    "LB": (120, 120, 120),  # Gray
    "RB": (120, 120, 120),  # Gray
    "LT": (120, 120, 120),  # Gray
    "RT": (120, 120, 120),  # Gray
    "BACK": (100, 100, 100),
    "START": (100, 100, 100),
    "LS": (100, 100, 100),
    "RS": (100, 100, 100),
}

XBOX_BUTTON_MAP = {
    0: "A", 1: "B", 2: "X", 3: "Y",
    4: "LB", 5: "RB", 6: "LT", 7: "RT",
    8: "BACK", 9: "START",
}

XBOX_PROMPT_LAYOUTS = {
    "gameplay": [
        {"btn": "A", "label": "Attack", "x": -60, "y": 0},
        {"btn": "B", "label": "Dodge", "x": 0, "y": -30},
        {"btn": "X", "label": "Interact", "x": -30, "y": 30},
        {"btn": "Y", "label": "Special", "x": 30, "y": 0},
    ],
    "gameplay_extra": [
        {"btn": "LB", "label": "Inventory", "x": -90, "y": 0},
        {"btn": "RB", "label": "Crafting", "x": 90, "y": 0},
        {"btn": "LT", "label": "Mount", "x": -60, "y": -18},
        {"btn": "RT", "label": "Potion", "x": 60, "y": -18},
        {"btn": "BACK", "label": "Locker", "x": 0, "y": -18},
        {"btn": "START", "label": "Pause", "x": 0, "y": 18},
    ],
}


class XboxButtonIcon:
    def __init__(self):
        self.font_cache = {}
        self.label_cache = {}

    def _get_font(self, size):
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.Font(None, size)
        return self.font_cache[size]

    def draw_button(self, screen, x, y, btn_name, size=24, pressed=False):
        color = XBOX_COLORS.get(btn_name, (120, 120, 120))
        radius = size // 2

        if btn_name in ("LB", "RB", "LT", "RT"):
            rect = pygame.Rect(x - radius, y - radius // 2, size, radius)
            if pressed:
                pygame.draw.rect(screen, color, rect, border_radius=4)
            else:
                pygame.draw.rect(screen, (*color[:3], 180), rect, border_radius=4, width=2)
            f = self._get_font(int(size * 0.55))
            ts = f.render(btn_name, True, (255, 255, 255) if pressed else color)
            screen.blit(ts, (x - ts.get_width() // 2, y - ts.get_height() // 2))
        elif btn_name in ("BACK", "START"):
            if btn_name == "BACK":
                pygame.draw.polygon(screen, color if pressed else (*color[:3], 180),
                                    [(x - radius // 2, y), (x, y - radius // 3), (x + radius // 2, y), (x, y + radius // 3)])
            else:
                pygame.draw.circle(screen, color if pressed else (
                    *color[:3], 180), (x, y), radius // 2, 2 if not pressed else 0)
                f = self._get_font(int(size * 0.45))
                ts = f.render("||", True, (255, 255, 255) if pressed else color)
                screen.blit(ts, (x - ts.get_width() // 2, y - ts.get_height() // 2))
        else:
            bg_color = (*color[:3], 220) if not pressed else color
            pygame.draw.circle(screen, (30, 30, 30), (x, y), radius + 2)
            pygame.draw.circle(screen, bg_color, (x, y), radius)
            f = self._get_font(int(size * 0.7))
            ts = f.render(btn_name, True, (255, 255, 255))
            screen.blit(ts, (x - ts.get_width() // 2, y - ts.get_height() // 2))

    def draw_prompt(self, screen, x, y, btn_name, label, size=20, pressed=False):
        self.draw_button(screen, x, y, btn_name, size, pressed)
        lf = self._get_font(16)
        ls = lf.render(label, True, (180, 180, 200))
        screen.blit(ls, (x + size // 2 + 6, y - ls.get_height() // 2))

    def draw_dual_prompt(self, screen, x, y, btn_name, kb_key, label, size=18, pressed=False):
        self.draw_button(screen, x, y, btn_name, size, pressed)
        lf = self._get_font(13)
        kb_s = lf.render(f"[{kb_key}]", True, (140, 160, 140))
        screen.blit(kb_s, (x + size // 2 + 4, y - kb_s.get_height() // 2))
        kb_w = kb_s.get_width()
        lf2 = self._get_font(14)
        ls = lf2.render(label, True, (160, 160, 180))
        screen.blit(ls, (x + size // 2 + 4 + kb_w + 4, y - ls.get_height() // 2))

    def draw_dual_text(self, screen, x, y, kb_key, kb_text, btn_name, kb_color=(140, 160, 140)):
        lf = self._get_font(18)
        if btn_name:
            self.draw_button(screen, x, y, btn_name, 14)
            kb_s = lf.render(f"[{kb_key}] {kb_text}", True, kb_color)
            screen.blit(kb_s, (x + 12, y - kb_s.get_height() // 2))
        else:
            kb_s = lf.render(f"[{kb_key}] {kb_text}", True, kb_color)
            screen.blit(kb_s, (x, y - kb_s.get_height() // 2))

    def draw_gameplay_prompts(self, screen, pressed_buttons=None):
        if pressed_buttons is None:
            pressed_buttons = set()
        cx = WIDTH // 2
        cy = HEIGHT - 80

        kb_keys = {"A": "SPACE", "B": "SHIFT", "X": "E", "Y": "Q"}

        layout = XBOX_PROMPT_LAYOUTS["gameplay"]
        for item in layout:
            px = cx + item["x"]
            py = cy + item["y"]
            is_pressed = XBOX_BUTTON_MAP.get(item["btn"], "") in pressed_buttons
            kb = kb_keys.get(item["btn"], "")
            self.draw_dual_prompt(screen, px, py, item["btn"], kb, item["label"], 18, is_pressed)

        extra = XBOX_PROMPT_LAYOUTS["gameplay_extra"]
        kb_extra = {"LB": "TAB", "RB": "C", "LT": "M", "RT": "R", "BACK": "I", "START": "ESC"}
        left_x = cx - 200
        right_x = cx + 200
        ey = cy - 10
        for item in extra:
            if item["btn"] in ("LB", "LT", "BACK"):
                px = left_x
                left_x += 85
            elif item["btn"] in ("RB", "RT", "START"):
                px = right_x
                right_x += 85
            else:
                px = cx
            is_pressed = XBOX_BUTTON_MAP.get(item["btn"], "") in pressed_buttons
            kb = kb_extra.get(item["btn"], "")
            lf = self._get_font(12)
            ls = lf.render(f"[{kb}] {item['label']}", True, (110, 120, 140))
            screen.blit(ls, (px - ls.get_width() // 2, ey + 14))
            self.draw_button(screen, px, ey, item["btn"], 16, is_pressed)

    def draw_menu_prompt(self, screen, prompts, y=None):
        if y is None:
            y = HEIGHT - 40
        total_w = len(prompts) * 100
        start_x = WIDTH // 2 - total_w // 2
        for i, (btn, kb_key, label) in enumerate(prompts):
            px = start_x + i * 100 + 30
            self.draw_button(screen, px, y, btn, 16)
            lf = self._get_font(12)
            ls = lf.render(f"[{kb_key}] {label}", True, (150, 150, 170))
            screen.blit(ls, (px - ls.get_width() // 2, y + 14))


xbox_icons = XboxButtonIcon()
