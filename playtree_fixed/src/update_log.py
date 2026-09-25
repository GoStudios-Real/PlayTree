import pygame
import math
import time
from config import *

UPDATE_LOG = [
    {
        "version": "1.1.0",
        "date": "25/09/2026",
        "title": "PLAYTREE v1.1.0 — Legend Update",
        "changes": [
            "Live player count panel — real players + 100,000,000 bot players",
            "Doggo Legend companion with its own legend screen",
            "Dancing bots on the main menu",
            "Admin Abuse console — press L for cheats and chaos buttons",
            "Single-instance lock — no more duplicate game copies",
            "Crash errors throttled to %TEMP%\\playtree_error.log",
            "Shop hover crash fix and PlayerClass ordering fix",
            "Sign In / Sign Up buttons now respond correctly on all screens",
        ],
    },
    {
        "version": "1.0.0",
        "date": "14/06/2026",
        "title": "PLAYTREE v1.0.0 — Initial Release",
        "changes": [
            "Full game launch with 5 playable classes",
            "4 rounds with unique bosses and story",
            "Daily login rewards system (7-day streak)",
            "Local leaderboards with 6 categories",
            "Skill tree system with 5 skills per class",
            "Equipment and armor system (4 slots)",
            "Enchanting table for weapon upgrades",
            "Fishing minigame with 5 fish rarities",
            "Pet taming and evolution system",
            "Base building with 6 structure types",
            "Weather system (rain, snow, fog, storms)",
            "Mount system (Forest Stag, Crystal Wolf, etc.)",
            "New Game+ mode after completing Round 4",
            "11-step interactive tutorial",
            "USB auto-launch and auto-update support",
            "TV controller support (EKO HOME, Google, Android, Apple TV)",
            "Multiplayer lobby system",
            "Screenshot capture (F12)",
            "GoStudios local account system",
            "5 save slots with auto-save",
            "Background music and sound effects",
            "Dual keyboard + Xbox controller prompts",
            "16 unique world regions with decorations",
            "25 enemy types across all rounds",
        ],
    },
    {
        "version": "0.1.0",
        "date": "01/06/2026",
        "title": "PLAYTREE v0.1.0 — Pre-release",
        "changes": [
            "Initial prototype and testing build",
            "Core movement and combat mechanics",
            "Basic world generation",
            "Controller input support",
        ],
    },
]


class UpdateLog:
    def __init__(self):
        self.scroll_y = 0
        self.max_scroll = 0
        self.selected_entry = 0
        self.status_line = ""
        self.check_btn_rect = None
        self.github_btn_rect = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            elif event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - 40)
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 40)
        elif event.type == pygame.MOUSEWHEEL:
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y - event.y * 30))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.check_btn_rect and self.check_btn_rect.collidepoint(event.pos):
                return "check_updates"
            if self.github_btn_rect and self.github_btn_rect.collidepoint(event.pos):
                return "open_github"
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                return "close"
            elif event.button == 11:
                self.scroll_y = max(0, self.scroll_y - 40)
            elif event.button == 12:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 40)
        return None

    def draw(self, screen):
        t = time.time()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        pw = WIDTH - 200
        ph = HEIGHT - 120
        px = 100
        py = 60

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((12, 14, 22, 240))
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, (*GREEN_GLOW[:3], 50), (px, py, pw, ph), border_radius=12, width=2)

        tf = pygame.font.Font(None, 40)
        ts = tf.render("UPDATE LOG", True, GREEN_GLOW)
        screen.blit(ts, (px + pw // 2 - ts.get_width() // 2, py + 15))

        date_f = pygame.font.Font(None, 20)
        date_s = date_f.render("Latest: 14/06/2026", True, GOLD)
        screen.blit(date_s, (px + pw // 2 - date_s.get_width() // 2, py + 50))

        clip_rect = pygame.Rect(px + 10, py + 75, pw - 20, ph - 95)
        screen.set_clip(clip_rect)

        y_offset = py + 75 - self.scroll_y
        total_h = 0

        title_f = pygame.font.Font(None, 28)
        ver_f = pygame.font.Font(None, 22)
        item_f = pygame.font.Font(None, 18)

        for entry in UPDATE_LOG:
            ver_s = ver_f.render(f"v{entry['version']}  —  {entry['date']}", True, GOLD)
            screen.blit(ver_s, (px + 30, y_offset))
            y_offset += 26
            total_h += 26

            ti_s = title_f.render(entry["title"], True, GREEN_GLOW)
            screen.blit(ti_s, (px + 30, y_offset))
            y_offset += 30
            total_h += 30

            for change in entry["changes"]:
                bullet = item_f.render(f"  {change}", True, (180, 200, 180))
                screen.blit(bullet, (px + 40, y_offset))
                y_offset += 20
                total_h += 20

            y_offset += 15
            total_h += 15

            if entry != UPDATE_LOG[-1]:
                pygame.draw.line(screen, (40, 50, 40), (px + 30, y_offset - 5), (px + pw - 30, y_offset - 5), 1)
                y_offset += 10
                total_h += 10

        self.max_scroll = max(0, total_h - (ph - 95))
        screen.set_clip(None)

        if self.scroll_y > 0:
            arr_s = pygame.font.Font(None, 20).render("^", True, GREEN_GLOW)
            screen.blit(arr_s, (px + pw // 2 - arr_s.get_width() // 2, py + 70))
        if self.scroll_y < self.max_scroll:
            arr_s = pygame.font.Font(None, 20).render("v", True, GREEN_GLOW)
            screen.blit(arr_s, (px + pw // 2 - arr_s.get_width() // 2, py + ph - 25))

        hint = pygame.font.Font(None, 16).render("UP/DOWN to scroll  |  ESC/B to close", True, (80, 100, 80))
        screen.blit(hint, (px + 20, py + ph - 20))

        # Buttons — GitHub update check + open repo (both work in the packaged EXE)
        btn_f = pygame.font.Font(None, 18)
        self.check_btn_rect = pygame.Rect(px + pw - 480, py + ph - 26, 240, 22)
        self.github_btn_rect = pygame.Rect(px + pw - 230, py + ph - 26, 210, 22)
        for rect, label in ((self.check_btn_rect, "CHECK FOR UPDATES"),
                            (self.github_btn_rect, "OPEN GITHUB")):
            mx, my = pygame.mouse.get_pos()
            hover = rect.collidepoint(mx, my)
            pygame.draw.rect(screen, (50, 90, 50) if hover else (30, 55, 30), rect, border_radius=5)
            pygame.draw.rect(screen, GREEN_GLOW, rect, 1, border_radius=5)
            ls = btn_f.render(label, True, (210, 255, 210))
            screen.blit(ls, ls.get_rect(center=rect.center))

        # Status line from the last update check
        if self.status_line:
            st_f = pygame.font.Font(None, 18)
            st_s = st_f.render(self.status_line, True, GOLD)
            screen.blit(st_s, st_s.get_rect(centerx=px + pw // 2, y=py + ph - 56))
