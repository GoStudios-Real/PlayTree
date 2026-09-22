import pygame
import os
import json
import time
import math
from config import *

LEADERBOARD_FILE = os.path.join(os.path.expanduser("~"), ".playtree", "leaderboards.json")

LEADERBOARD_CATEGORIES = [
    {"id": "level", "name": "Highest Level", "icon": "LVL", "color": GOLD},
    {"id": "gold", "name": "Most Gold", "icon": "GLD", "color": GOLD},
    {"id": "kills", "name": "Most Kills", "icon": "KLL", "color": RED},
    {"id": "bosses", "name": "Bosses Defeated", "icon": "BOS", "color": (255, 100, 100)},
    {"id": "playtime", "name": "Most Playtime", "icon": "TM", "color": CYAN},
    {"id": "round", "name": "Furthest Round", "icon": "RND", "color": GREEN_GLOW},
]


class LeaderboardSystem:
    def __init__(self):
        self.data = self._load()
        self.selected_category = 0
        self.tab = "local"

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(LEADERBOARD_FILE), exist_ok=True)

    def _load(self):
        try:
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"entries": {}}

    def _save(self):
        self._ensure_dir()
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def update_score(self, category_id, player_name, score):
        if "entries" not in self.data:
            self.data["entries"] = {}
        if category_id not in self.data["entries"]:
            self.data["entries"][category_id] = []

        entries = self.data["entries"][category_id]
        existing = None
        for e in entries:
            if e["name"] == player_name:
                existing = e
                break

        if existing:
            if category_id == "playtime":
                existing["score"] = max(existing.get("score", 0), score)
            else:
                existing["score"] = max(existing.get("score", 0), score)
            existing["time"] = time.time()
        else:
            entries.append({
                "name": player_name,
                "score": score,
                "time": time.time(),
            })

        entries.sort(key=lambda e: e["score"], reverse=True)
        self.data["entries"][category_id] = entries[:50]
        self._save()

    def get_entries(self, category_id, limit=20):
        entries = self.data.get("entries", {}).get(category_id, [])
        return entries[:limit]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            if event.key == pygame.K_LEFT:
                self.selected_category = (self.selected_category - 1) % len(LEADERBOARD_CATEGORIES)
            if event.key == pygame.K_RIGHT:
                self.selected_category = (self.selected_category + 1) % len(LEADERBOARD_CATEGORIES)
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                return "close"
            if event.button == 11:
                self.selected_category = (self.selected_category - 1) % len(LEADERBOARD_CATEGORIES)
            if event.button == 12:
                self.selected_category = (self.selected_category + 1) % len(LEADERBOARD_CATEGORIES)
        return None

    def draw(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        px, py = WIDTH // 4, HEIGHT // 6
        pw, ph = WIDTH // 2, HEIGHT * 2 // 3
        pygame.draw.rect(screen, (15, 15, 25), (px, py, pw, ph), border_radius=12)
        pygame.draw.rect(screen, (*GOLD[:3], 60), (px, py, pw, ph), border_radius=12, width=2)

        tf = pygame.font.Font(None, 44)
        ts = tf.render("LEADERBOARDS", True, GOLD)
        screen.blit(ts, (px + pw // 2 - ts.get_width() // 2, py + 15))

        sf = pygame.font.Font(None, 22)
        sf_sm = pygame.font.Font(None, 18)
        sf_xs = pygame.font.Font(None, 14)

        cat_y = py + 60
        for i, cat in enumerate(LEADERBOARD_CATEGORIES):
            cx = px + 20 + i * (pw - 40) // len(LEADERBOARD_CATEGORIES)
            is_sel = i == self.selected_category
            color = GOLD if is_sel else (120, 120, 120)
            cs = sf_sm.render(cat["name"], True, color)
            screen.blit(cs, (cx, cat_y))
            if is_sel:
                pygame.draw.line(screen, GOLD, (cx, cat_y + 16), (cx + cs.get_width(), cat_y + 16), 2)

        cat = LEADERBOARD_CATEGORIES[self.selected_category]
        entries = self.get_entries(cat["id"])

        header_y = cat_y + 30
        rank_h = sf_sm.render("Rank", True, GOLD)
        name_h = sf_sm.render("Name", True, GOLD)
        score_h = sf_sm.render("Score", True, GOLD)
        screen.blit(rank_h, (px + 30, header_y))
        screen.blit(name_h, (px + 100, header_y))
        screen.blit(score_h, (px + pw - 120, header_y))
        pygame.draw.line(screen, (60, 60, 70), (px + 20, header_y + 18), (px + pw - 20, header_y + 18), 1)

        list_y = header_y + 25
        if not entries:
            empty = sf.render("No records yet. Play to set a high score!", True, (100, 120, 100))
            screen.blit(empty, (px + pw // 2 - empty.get_width() // 2, list_y + 30))
        else:
            for i, entry in enumerate(entries[:15]):
                ey = list_y + i * 24
                rank_colors = [GOLD, (200, 200, 200), (180, 140, 60)]
                rank_color = rank_colors[i] if i < 3 else (140, 140, 140)
                rs = sf_sm.render(f"#{i + 1}", True, rank_color)
                screen.blit(rs, (px + 30, ey))
                ns = sf_sm.render(entry["name"], True, (180, 200, 180))
                screen.blit(ns, (px + 100, ey))

                score = entry["score"]
                if cat["id"] == "playtime":
                    score_str = f"{score:.1f}h"
                elif cat["id"] == "gold":
                    score_str = f"{int(score):,}"
                else:
                    score_str = f"{int(score):,}"
                ss = sf_sm.render(score_str, True, cat["color"])
                screen.blit(ss, (px + pw - 120, ey))

        hint = sf_xs.render("LEFT/RIGHT to switch category  |  ESC/B to close", True, (80, 100, 80))
        screen.blit(hint, (px + 20, py + ph - 25))
