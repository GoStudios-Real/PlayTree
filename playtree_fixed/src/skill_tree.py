import pygame
import math
from config import SKILL_TREES, PlayerClass, WIDTH, HEIGHT, GREEN_GLOW, GOLD, RED


class SkillTree:
    def __init__(self, player_class, audio=None):
        self.player_class = player_class
        self.audio = audio
        self.skills = {}
        tree = SKILL_TREES.get(player_class, {})
        for skill_id, data in tree.items():
            self.skills[skill_id] = {
                "name": data["name"],
                "desc": data["desc"],
                "cost": data["cost"],
                "max": data["max"],
                "requires": data["requires"],
                "level": 0,
            }
        self.skill_points = 3
        self.selected = None

    def can_upgrade(self, skill_id):
        s = self.skills.get(skill_id)
        if not s:
            return False
        if s["level"] >= s["max"]:
            return False
        if s["cost"] > self.skill_points:
            return False
        if s["requires"] and self.skills.get(s["requires"], {}).get("level", 0) == 0:
            return False
        return True

    def upgrade(self, skill_id):
        if self.can_upgrade(skill_id):
            self.skills[skill_id]["level"] += 1
            self.skill_points -= self.skills[skill_id]["cost"]
            return True
        return False

    def get_bonus(self, stat):
        total = 0
        for s in self.skills.values():
            if s["level"] > 0:
                if stat == "stun" and "shield_bash" in [
                        sid for sid, sk in self.skills.items() if sk["name"] == s["name"]]:
                    total += s["level"] * 0.5
        return total

    def has_skill(self, name):
        for s in self.skills.values():
            if s["name"] == name and s["level"] > 0:
                return True
        return False

    def get_skill_level(self, name):
        for s in self.skills.values():
            if s["name"] == name:
                return s["level"]
        return 0

    def draw(self, surface, font, small_font):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        sx, sy = 80, 40
        sw, sh = WIDTH - 160, HEIGHT - 80
        pygame.draw.rect(surface, (15, 20, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(surface, (*GOLD[:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        title = font.render("SKILL TREE", True, GOLD)
        surface.blit(title, (sx + 20, sy + 12))

        pts = small_font.render(f"Points: {self.skill_points}", True, GREEN_GLOW)
        surface.blit(pts, (sx + sw - 150, sy + 18))

        cls_name = self.player_class.value if hasattr(self.player_class, 'value') else str(self.player_class)
        cls_txt = small_font.render(cls_name, True, (150, 170, 150))
        surface.blit(cls_txt, (sx + 200, sy + 18))

        skill_ids = list(self.skills.keys())
        cols = min(5, len(skill_ids))
        node_w = 140
        node_h = 80
        gap_x = 20
        gap_y = 30
        start_x = sx + (sw - cols * (node_w + gap_x)) // 2
        start_y = sy + 60

        node_rects = {}
        for i, sid in enumerate(skill_ids):
            s = self.skills[sid]
            col = i % cols
            row = i // cols
            nx = start_x + col * (node_w + gap_x)
            ny = start_y + row * (node_h + gap_y)
            node_rects[sid] = (nx, ny, node_w, node_h)

            maxed = s["level"] >= s["max"]
            can_up = self.can_upgrade(sid)
            selected = self.selected == sid

            if maxed:
                bg = (20, 50, 30)
                border = (80, 255, 120)
            elif can_up:
                bg = (20, 30, 20)
                border = (100, 200, 100)
            else:
                bg = (15, 15, 20)
                border = (50, 50, 60)

            if selected:
                border = GOLD

            pygame.draw.rect(surface, bg, (nx, ny, node_w, node_h), border_radius=6)
            pygame.draw.rect(surface, border, (nx, ny, node_w, node_h), 1, border_radius=6)

            nm = small_font.render(s["name"], True, border)
            surface.blit(nm, (nx + 8, ny + 6))

            lvl = small_font.render(f"Lv {s['level']}/{s['max']}", True, (150, 150, 150))
            surface.blit(lvl, (nx + 8, ny + 26))

            cost = small_font.render(f"Cost: {s['cost']}", True, (180, 160, 80) if can_up else (80, 80, 80))
            surface.blit(cost, (nx + 8, ny + 46))

            req = s.get("requires")
            if req and self.skills.get(req, {}).get("level", 0) == 0:
                lock = small_font.render("LOCKED", True, (200, 60, 60))
                surface.blit(lock, (nx + 8, ny + 62))

        mx, my = pygame.mouse.get_pos()
        self.selected = None
        for sid, (nx, ny, nw, nh) in node_rects.items():
            if nx <= mx <= nx + nw and ny <= my <= ny + nh:
                self.selected = sid
                s = self.skills[sid]
                tip_x = min(mx + 10, WIDTH - 200)
                tip_y = min(my + 10, HEIGHT - 60)
                pygame.draw.rect(surface, (20, 25, 20), (tip_x, tip_y, 190, 50), border_radius=4)
                pygame.draw.rect(surface, border, (tip_x, tip_y, 190, 50), 1, border_radius=4)
                tip_nm = small_font.render(s["name"], True, GOLD)
                surface.blit(tip_nm, (tip_x + 6, tip_y + 4))
                tip_desc = small_font.render(s["desc"], True, (180, 200, 180))
                surface.blit(tip_desc, (tip_x + 6, tip_y + 22))
                break

        hint = small_font.render("Click to upgrade  |  ESC to close", True, (80, 100, 80))
        surface.blit(hint, (sx + 20, sy + sh - 30))

    def handle_click(self, pos):
        mx, my = pos
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        sw, sh = WIDTH - 160, HEIGHT - 80
        sx, sy = 80, 40
        skill_ids = list(self.skills.keys())
        cols = min(5, len(skill_ids))
        node_w = 140
        node_h = 80
        gap_x = 20
        gap_y = 30
        start_x = sx + (sw - cols * (node_w + gap_x)) // 2
        start_y = sy + 60

        for i, sid in enumerate(skill_ids):
            col = i % cols
            row = i // cols
            nx = start_x + col * (node_w + gap_x)
            ny = start_y + row * (node_h + gap_y)
            if nx <= mx <= nx + node_w and ny <= my <= ny + node_h:
                if self.upgrade(sid):
                    if self.audio:
                        self.audio.play("levelup")
                    return True
        return False
