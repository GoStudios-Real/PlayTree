import pygame
import json
import os
from config import ACHIEVEMENTS, WIDTH, HEIGHT, GOLD, GREEN_GLOW

ACHIEVEMENTS_FILE = "achievements.json"


class AchievementSystem:
    def __init__(self, audio=None):
        self.unlocked = {}
        self.notifications = []
        self.audio = audio
        self.load()

    def load(self):
        try:
            if os.path.exists(ACHIEVEMENTS_FILE):
                with open(ACHIEVEMENTS_FILE, "r") as f:
                    self.unlocked = json.load(f)
        except Exception:
            self.unlocked = {}

    def save(self):
        try:
            with open(ACHIEVEMENTS_FILE, "w") as f:
                json.dump(self.unlocked, f, indent=2)
        except Exception:
            pass

    def unlock(self, achievement_id):
        if achievement_id not in self.unlocked:
            self.unlocked[achievement_id] = True
            data = ACHIEVEMENTS.get(achievement_id, {})
            self.notifications.append({
                "id": achievement_id,
                "name": data.get("name", achievement_id),
                "desc": data.get("desc", ""),
                "gold": data.get("reward_gold", 0),
                "timer": 3.0,
            })
            self.save()
            if self.audio:
                self.audio.play("quest_complete")
            return data.get("reward_gold", 0)
        return 0

    def is_unlocked(self, achievement_id):
        return achievement_id in self.unlocked

    def update(self, dt):
        for n in self.notifications:
            n["timer"] -= dt
        self.notifications = [n for n in self.notifications if n["timer"] > 0]

    def draw_notifications(self, surface, font, small_font):
        for i, n in enumerate(self.notifications):
            alpha = min(1.0, n["timer"])
            ny = 80 + i * 60
            w = 320
            nx = WIDTH // 2 - w // 2
            overlay = pygame.Surface((w, 50), pygame.SRCALPHA)
            overlay.fill((20, 30, 20, int(200 * alpha)))
            pygame.draw.rect(overlay, (*GOLD[:3], int(200 * alpha)), (0, 0, w, 50), 2, border_radius=6)
            surface.blit(overlay, (nx, ny))
            title = small_font.render(f"Achievement: {n['name']}", True, (*GOLD[:3], int(255 * alpha)))
            surface.blit(title, (nx + 10, ny + 6))
            desc = small_font.render(n["desc"], True, (*GREEN_GLOW[:3], int(200 * alpha)))
            surface.blit(desc, (nx + 10, ny + 24))
            gold_txt = small_font.render(f"+{n['gold']} Gold", True, (*GOLD[:3], int(255 * alpha)))
            surface.blit(gold_txt, (nx + w - 80, ny + 14))

    def draw_screen(self, surface, font, small_font, dailies=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        sx, sy = 80, 50
        sw, sh = WIDTH - 160, HEIGHT - 100
        pygame.draw.rect(surface, (15, 20, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(surface, (*GOLD[:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        title = font.render("ACHIEVEMENTS", True, GOLD)
        surface.blit(title, (sx + 20, sy + 12))

        total = len(ACHIEVEMENTS)
        done = len(self.unlocked)
        pct = small_font.render(f"{done}/{total} Unlocked", True, GREEN_GLOW)
        surface.blit(pct, (sx + sw - 180, sy + 18))

        y = sy + 50
        # Tighter rows when the list would otherwise overflow the panel
        row_h = max(34, min(44, (sh - 90) // max(1, len(ACHIEVEMENTS))))
        for ach_id, data in ACHIEVEMENTS.items():
            unlocked = ach_id in self.unlocked
            color = GREEN_GLOW if unlocked else (80, 80, 80)
            icon = "[X]" if unlocked else "[ ]"
            ic = small_font.render(icon, True, color)
            surface.blit(ic, (sx + 20, y))
            nm = small_font.render(data["name"], True, color)
            surface.blit(nm, (sx + 60, y))
            ds = small_font.render(data["desc"], True, (120, 120, 120) if not unlocked else (160, 180, 160))
            surface.blit(ds, (sx + 60, y + 16))
            gd = small_font.render(f"+{data['reward_gold']}g", True, GOLD if unlocked else (80, 80, 60))
            surface.blit(gd, (sx + sw - 80, y + 4))
            y += row_h
            if y > sy + sh - 40:
                break

        # Right column — today's daily quests
        if dailies:
            dx = sx + sw // 2 + 60
            dt = font.render("DAILY QUESTS", True, (255, 200, 90))
            surface.blit(dt, (dx, sy + 12))
            st = dailies.get_status()
            sub = small_font.render(f"{st['done']}/{st['total']} done • resets at midnight",
                                    True, (160, 160, 140))
            surface.blit(sub, (dx, sy + 44))
            dy = sy + 80
            for q in dailies.summary_lines():
                color = GREEN_GLOW if q["complete"] else (200, 200, 200)
                icon = "[x]" if q["complete"] else "[ ]"
                ic = small_font.render(icon, True, color)
                surface.blit(ic, (dx, dy))
                nm = small_font.render(q["name"], True, color)
                surface.blit(nm, (dx + 40, dy))
                pg = small_font.render(q["progress"], True,
                                       GREEN_GLOW if q["complete"] else (255, 210, 110))
                surface.blit(pg, (dx + 300, dy))
                ds = small_font.render(q["desc"], True, (120, 120, 120))
                surface.blit(ds, (dx + 40, dy + 18))
                rw = small_font.render(f"+{q['reward_xp']}xp  +{q['reward_gold']}g",
                                       True, GOLD if q["complete"] else (80, 80, 60))
                surface.blit(rw, (dx + 300, dy + 18))
                dy += 50
                if dy > sy + sh - 40:
                    break

        hint = small_font.render("ESC to close", True, (80, 100, 80))
        surface.blit(hint, (sx + 20, sy + sh - 30))
