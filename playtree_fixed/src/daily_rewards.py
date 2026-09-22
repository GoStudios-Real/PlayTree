import pygame
import os
import json
import time
import math
from config import *

REWARDS_FILE = os.path.join(os.path.expanduser("~"), ".playtree", "daily_rewards.json")

DAILY_REWARDS = {
    1: {"gold": 50, "items": ["Health Potion"], "desc": "Welcome back!"},
    2: {"gold": 75, "items": [], "desc": "Day 2 streak!"},
    3: {"gold": 100, "items": ["Energy Elixir"], "desc": "3 days strong!"},
    4: {"gold": 125, "items": [], "desc": "Almost there!"},
    5: {"gold": 150, "items": ["Health Potion", "Health Potion"], "desc": "5 day streak!"},
}


class DailyRewards:
    def __init__(self):
        self.data = self._load()
        self.claimed_today = False
        self.streak = 0
        self.last_claim = 0
        self.selected_day = 0
        self.notification_shown = False
        self._check_streak()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(REWARDS_FILE), exist_ok=True)

    def _load(self):
        try:
            if os.path.exists(REWARDS_FILE):
                with open(REWARDS_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"streak": 0, "last_claim": 0, "total_claims": 0, "best_streak": 0}

    def _save(self):
        self._ensure_dir()
        with open(REWARDS_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def _check_streak(self):
        now = time.time()
        last = self.data.get("last_claim", 0)
        self.streak = self.data.get("streak", 0)
        self.last_claim = last

        if last == 0:
            self.claimed_today = False
            return

        hours_since = (now - last) / 3600
        if hours_since >= 48:
            self.streak = 0
            self.data["streak"] = 0
            self._save()
        elif hours_since >= 24:
            self.claimed_today = False
        else:
            self.claimed_today = True

    def can_claim(self):
        return not self.claimed_today

    def claim(self):
        if not self.can_claim():
            return None
        now = time.time()
        last = self.data.get("last_claim", 0)
        hours_since = (now - last) / 3600 if last > 0 else 999

        if hours_since >= 24 or last == 0:
            self.streak += 1
        elif hours_since < 24:
            return None

        if self.streak > 5:
            self.streak = 1

        self.data["streak"] = self.streak
        self.data["last_claim"] = now
        self.data["total_claims"] = self.data.get("total_claims", 0) + 1
        if self.streak > self.data.get("best_streak", 0):
            self.data["best_streak"] = self.streak
        self._save()
        self.claimed_today = True
        return DAILY_REWARDS.get(self.streak, DAILY_REWARDS[1])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hasattr(self, 'claim_rect') and self.claim_rect.collidepoint(event.pos):
                return self.claim()
            for i in range(1, 6):
                rect = getattr(self, f'day_{i}_rect', None)
                if rect and rect.collidepoint(event.pos):
                    self.selected_day = i
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            if event.key == pygame.K_RETURN and self.can_claim():
                return self.claim()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                return "close"
            if event.button == 0 and self.can_claim():
                return self.claim()
        return None

    def draw(self, screen):
        t = time.time()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        pw = WIDTH - 120
        ph = 420
        px = 60
        py = (HEIGHT - ph) // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((15, 15, 30, 240))
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, (*GOLD[:3], 80), (px, py, pw, ph), border_radius=12, width=2)

        tf = pygame.font.Font(None, 38)
        ts = tf.render("DAILY LOGIN REWARDS", True, GOLD)
        screen.blit(ts, (px + pw // 2 - ts.get_width() // 2, py + 12))

        sf = pygame.font.Font(None, 20)
        sf_xs = pygame.font.Font(None, 14)

        streak_text = f"Streak: {self.streak} / 5"
        ss = sf.render(streak_text, True, GREEN_GLOW)
        screen.blit(ss, (px + pw // 2 - ss.get_width() // 2, py + 48))

        best = self.data.get("best_streak", 0)
        bs = sf_xs.render(f"Best streak: {best}", True, (120, 140, 120))
        screen.blit(bs, (px + pw // 2 - bs.get_width() // 2, py + 68))

        inner_pad = 15
        card_gap = 6
        card_w = (pw - inner_pad * 2 - card_gap * 4) // 5
        card_h = 130
        start_x = px + inner_pad
        card_y = py + 90

        for day in range(1, 6):
            cx = start_x + (day - 1) * (card_w + card_gap)
            reward = DAILY_REWARDS[day]
            is_claimed = day <= self.streak and self.claimed_today
            is_current = day == self.streak + 1 and self.can_claim()
            is_selected = day == self.selected_day

            if is_claimed:
                bg_color = (20, 50, 20)
                border_color = (80, 180, 80)
            elif is_current:
                pulse = int(math.sin(t * 3) * 20 + 60)
                bg_color = (30, 30, 50)
                border_color = (*GOLD[:3], pulse + 80)
            elif is_selected:
                bg_color = (25, 25, 40)
                border_color = CYAN
            else:
                bg_color = (20, 20, 25)
                border_color = (60, 60, 70)

            rect = pygame.Rect(cx, card_y, card_w, card_h)
            setattr(self, f'day_{day}_rect', rect)
            pygame.draw.rect(screen, bg_color, rect, border_radius=6)
            pygame.draw.rect(screen, border_color, rect, border_radius=6, width=2)

            df = pygame.font.Font(None, 18)
            ds = df.render(f"Day {day}", True, GOLD if is_current else (180, 180, 180))
            screen.blit(ds, (cx + card_w // 2 - ds.get_width() // 2, card_y + 8))

            gf = pygame.font.Font(None, 20)
            gs = gf.render(f"{reward['gold']} Gold", True, GOLD)
            screen.blit(gs, (cx + card_w // 2 - gs.get_width() // 2, card_y + 28))

            if reward["items"]:
                for j, item in enumerate(reward["items"][:2]):
                    short = item.replace("Health Potion", "HP Pot").replace("Energy Elixir", "E. Elixir")
                    its = sf_xs.render(short, True, (160, 180, 160))
                    screen.blit(its, (cx + card_w // 2 - its.get_width() // 2, card_y + 55 + j * 14))

            desc_short = reward["desc"][:12]
            desc_s = sf_xs.render(desc_short, True, (120, 140, 160))
            screen.blit(desc_s, (cx + card_w // 2 - desc_s.get_width() // 2, card_y + 95))

            if is_claimed:
                check = df.render("CLAIMED", True, GREEN_GLOW)
                screen.blit(check, (cx + card_w // 2 - check.get_width() // 2, card_y + 112))

        claim_y = card_y + card_h + 15
        if self.can_claim():
            self.claim_rect = pygame.Rect(px + pw // 2 - 90, claim_y, 180, 40)
            pulse = int(math.sin(t * 3) * 15 + 40)
            pygame.draw.rect(screen, (20, 40, 20), self.claim_rect, border_radius=8)
            pygame.draw.rect(screen, (*GREEN_GLOW[:3], pulse + 80), self.claim_rect, border_radius=8, width=2)
            cf = pygame.font.Font(None, 26)
            cs = cf.render("CLAIM REWARD", True, GREEN_GLOW)
            screen.blit(cs, (self.claim_rect.centerx - cs.get_width() //
                        2, self.claim_rect.centery - cs.get_height() // 2))
        else:
            self.claim_rect = None
            nf = pygame.font.Font(None, 22)
            ns = nf.render("Already claimed today! Come back tomorrow.", True, (150, 150, 150))
            screen.blit(ns, (px + pw // 2 - ns.get_width() // 2, claim_y + 8))

        hint = sf_xs.render("ESC/B close | Click day | ENTER/A claim", True, (80, 100, 80))
        screen.blit(hint, (px + 15, py + ph - 20))
