import pygame
import os
import time
import math
from config import *

SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "PLAYTREE")


class ScreenshotSystem:
    def __init__(self):
        self.screenshot_flash = 0
        self.share_menu_open = False
        self.share_target = None
        self.share_result = ""
        self.share_result_timer = 0
        self.last_screenshot_path = None

    def take_screenshot(self, screen):
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"playtree_{timestamp}.png"
        filepath = os.path.join(SCREENSHOT_DIR, filename)
        try:
            pygame.image.save(screen, filepath)
            self.screenshot_flash = 0.3
            self.last_screenshot_path = filepath
            return filepath
        except Exception:
            return None

    def share_screenshot(self, filepath=None):
        if filepath is None:
            filepath = self.last_screenshot_path
        if not filepath or not os.path.exists(filepath):
            return False
        try:
            os.startfile(filepath)
            return True
        except Exception:
            return False

    def update(self, dt):
        self.screenshot_flash = max(0, self.screenshot_flash - dt)
        self.share_result_timer = max(0, self.share_result_timer - dt)
        if self.share_result_timer <= 0:
            self.share_result = ""

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                return self.take_screenshot(pygame.display.get_surface())
        return None

    def draw_flash(self, screen):
        if self.screenshot_flash > 0:
            alpha = int(self.screenshot_flash / 0.3 * 100)
            flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (0, 0))

            sf = pygame.font.Font(None, 30)
            txt = "Screenshot saved!"
            ts = sf.render(txt, True, GREEN_GLOW)
            bg = pygame.Surface((ts.get_width() + 20, ts.get_height() + 10), pygame.SRCALPHA)
            bg.fill((10, 20, 10, 200))
            screen.blit(bg, (WIDTH // 2 - ts.get_width() // 2 - 10, 15))
            screen.blit(ts, (WIDTH // 2 - ts.get_width() // 2, 20))

    def draw_share_menu(self, screen):
        if not self.share_menu_open:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        sx, sy = WIDTH // 4, HEIGHT // 3
        sw, sh = WIDTH // 2, HEIGHT // 3
        pygame.draw.rect(screen, (15, 20, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(screen, (*CYAN[:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 36)
        ts = tf.render("SHARE SCREENSHOT", True, GOLD)
        screen.blit(ts, (sx + sw // 2 - ts.get_width() // 2, sy + 15))

        sf = pygame.font.Font(None, 26)
        sf_sm = pygame.font.Font(None, 20)

        options = [
            ("Open Screenshot", "Open in default viewer"),
            ("Copy Path", "Copy file path to clipboard"),
            ("Close", "Close share menu"),
        ]

        self.option_rects = []
        for i, (name, desc) in enumerate(options):
            oy = sy + 60 + i * 50
            rect = pygame.Rect(sx + 20, oy, sw - 40, 40)
            self.option_rects.append((rect, name))
            pygame.draw.rect(screen, (25, 30, 35), rect, border_radius=6)
            pygame.draw.rect(screen, (60, 70, 80), rect, border_radius=6, width=1)
            ns = sf.render(name, True, CYAN)
            screen.blit(ns, (sx + 35, oy + 5))
            ds = sf_sm.render(desc, True, (120, 130, 140))
            screen.blit(ds, (sx + 35, oy + 24))

        if self.share_result:
            rs = sf_sm.render(self.share_result, True, GREEN_GLOW)
            screen.blit(rs, (sx + sw // 2 - rs.get_width() // 2, sy + sh - 35))

    def handle_share_click(self, pos):
        if not hasattr(self, 'option_rects'):
            return None
        for rect, name in self.option_rects:
            if rect.collidepoint(pos):
                if name == "Open Screenshot":
                    self.share_screenshot()
                    return "opened"
                elif name == "Copy Path":
                    if self.last_screenshot_path:
                        try:
                            import subprocess
                            subprocess.run(["clip"], input=self.last_screenshot_path.encode(), check=True)
                        except Exception:
                            pass
                    return "copied"
                elif name == "Close":
                    self.share_menu_open = False
                    return "closed"
        return None
