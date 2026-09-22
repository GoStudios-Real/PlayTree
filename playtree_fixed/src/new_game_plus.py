import pygame
import math
import random
import time
from config import *


class NewGamePlus:
    def __init__(self):
        self.active = False
        self.ngp_level = 0
        self.multiplier = 1.0
        self.unlocked = False

    def activate(self):
        self.ngp_level += 1
        self.active = True
        self.multiplier = 1.0 + (self.ngp_level * 0.5)

    def get_enemy_hp_mult(self):
        return self.multiplier

    def get_enemy_dmg_mult(self):
        return self.multiplier

    def get_xp_mult(self):
        return 1.0 + (self.ngp_level * 0.25)

    def get_gold_mult(self):
        return 1.0 + (self.ngp_level * 0.3)

    def get_player_hp_bonus(self):
        return int(self.ngp_level * 20)

    def get_player_atk_bonus(self):
        return int(self.ngp_level * 5)

    def get_player_def_bonus(self):
        return int(self.ngp_level * 3)

    def draw_activation(self, screen, timer):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        screen.blit(overlay, (0, 0))

        t = timer

        sf_title = pygame.font.Font(None, 70)
        sf_sub = pygame.font.Font(None, 36)
        sf_info = pygame.font.Font(None, 24)
        sf_small = pygame.font.Font(None, 18)

        alpha1 = min(255, int(t * 100))
        title = sf_title.render(f"NEW GAME+ {self.ngp_level}", True, MAGIC_PURPLE)
        title.set_alpha(alpha1)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - 60))

        alpha2 = min(255, max(0, int((t - 0.5) * 100)))
        sub = sf_sub.render("The world grows stronger...", True, (200, 180, 255))
        sub.set_alpha(alpha2)
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 3))

        if t > 1.0:
            alpha3 = min(255, int((t - 1.0) * 80))
            bonuses = [
                (f"Enemy HP x{self.multiplier:.1f}", RED),
                (f"Enemy Damage x{self.multiplier:.1f}", RED),
                (f"Player XP x{self.get_xp_mult():.2f}", GREEN_GLOW),
                (f"Player Gold x{self.get_gold_mult():.2f}", GOLD),
                (f"+{self.get_player_hp_bonus()} Max HP", GREEN_GLOW),
                (f"+{self.get_player_atk_bonus()} Attack", GREEN_GLOW),
                (f"+{self.get_player_def_bonus()} Defense", GREEN_GLOW),
            ]
            for i, (text, color) in enumerate(bonuses):
                bs = sf_info.render(text, True, color)
                bs.set_alpha(alpha3)
                screen.blit(bs, (WIDTH // 2 - bs.get_width() // 2, HEIGHT // 3 + 50 + i * 28))

        if t > 3.0:
            alpha4 = min(255, int((t - 3.0) * 80))
            hint = sf_small.render("Press ENTER or A to continue", True, (120, 140, 120))
            hint.set_alpha(alpha4)
            screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 160))

    def get_save_data(self):
        return {
            "active": self.active,
            "ngp_level": self.ngp_level,
            "multiplier": self.multiplier,
            "unlocked": self.unlocked,
        }

    def load_save_data(self, data):
        if data:
            self.active = data.get("active", False)
            self.ngp_level = data.get("ngp_level", 0)
            self.multiplier = data.get("multiplier", 1.0)
            self.unlocked = data.get("unlocked", False)
