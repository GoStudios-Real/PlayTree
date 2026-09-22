import pygame
import math
import random
from config import FISH_TYPES, WIDTH, HEIGHT, GOLD, GREEN_GLOW, BLUE


class FishingMinigame:
    def __init__(self, audio=None):
        self.active = False
        self.audio = audio
        self.phase = "idle"
        self.fish = None
        self.bar_pos = 0.5
        self.bar_speed = 0
        self.fish_pos = 0.5
        self.fish_target = 0.5
        self.catch_progress = 0
        self.timer = 0
        self.difficulty = 1
        self.caught = []
        self.result_msg = ""
        self.result_timer = 0

    def start(self):
        self.active = True
        self.phase = "cast"
        self.timer = 1.0
        if self.audio:
            self.audio.play("place")
        roll = random.random()
        if roll < 0.45:
            self.fish = FISH_TYPES[0]
        elif roll < 0.70:
            self.fish = FISH_TYPES[1]
        elif roll < 0.88:
            self.fish = FISH_TYPES[2]
        elif roll < 0.97:
            self.fish = FISH_TYPES[3]
        else:
            self.fish = FISH_TYPES[4]
        self.difficulty = 1 + ["common", "uncommon", "rare", "epic", "legendary"].index(self.fish["rarity"]) * 0.5
        self.catch_progress = 0
        self.bar_pos = 0.5
        self.fish_pos = 0.5
        self.fish_target = random.uniform(0.2, 0.8)

    def stop(self):
        self.active = False
        self.phase = "idle"

    def update(self, dt, keys_pressed):
        if not self.active:
            return

        if self.phase == "cast":
            self.timer -= dt
            if self.timer <= 0:
                self.phase = "catching"
            return

        if self.phase == "result":
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.active = False
                self.phase = "idle"
            return

        if self.phase == "catching":
            if keys_pressed and keys_pressed[pygame.K_SPACE]:
                self.bar_speed += 0.02
            else:
                self.bar_speed -= 0.015
            self.bar_speed = max(-0.03, min(0.03, self.bar_speed))
            self.bar_pos += self.bar_speed
            self.bar_pos = max(0, min(1, self.bar_pos))

            if random.random() < 0.02 * self.difficulty:
                self.fish_target = random.uniform(0.1, 0.9)
            self.fish_pos += (self.fish_target - self.fish_pos) * dt * 2 * self.difficulty

            dist = abs(self.bar_pos - self.fish_pos)
            if dist < 0.12:
                self.catch_progress += dt * 0.5
            else:
                self.catch_progress -= dt * 0.2

            self.catch_progress = max(0, min(1, self.catch_progress))

            if self.catch_progress >= 1.0:
                self.caught.append(self.fish)
                self.result_msg = f"Caught {self.fish['name']}! +{self.fish['xp']}XP +{self.fish['gold']}g"
                self.result_timer = 2.0
                self.phase = "result"
                if self.audio:
                    self.audio.play("collect")
            elif self.catch_progress <= 0 and self.timer > 5:
                self.result_msg = "The fish got away!"
                self.result_timer = 1.5
                self.phase = "result"
                if self.audio:
                    self.audio.play("menu_confirm")

            self.timer += dt

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.stop()
            return True
        return False

    def draw(self, surface, font, small_font):
        if not self.active:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if self.phase == "cast":
            txt = font.render("Casting...", True, BLUE)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 20))
            dots = "." * (int(pygame.time.get_ticks() / 300) % 4)
            dt2 = small_font.render(dots, True, (100, 150, 200))
            surface.blit(dt2, (WIDTH // 2 + txt.get_width() // 2 + 5, HEIGHT // 2 - 20))
            return

        if self.fish:
            fish_label = small_font.render(f"Fishing: {self.fish['name']}", True, self.fish["color"])
            surface.blit(fish_label, (WIDTH // 2 - fish_label.get_width() // 2, 100))

        bar_x = WIDTH // 2 - 15
        bar_top = 150
        bar_height = 300
        bar_w = 30

        pygame.draw.rect(surface, (30, 40, 50), (bar_x, bar_top, bar_w, bar_height), border_radius=4)
        pygame.draw.rect(surface, (60, 80, 100), (bar_x, bar_top, bar_w, bar_height), 2, border_radius=4)

        fish_y = bar_top + int(self.fish_pos * bar_height)
        pygame.draw.rect(surface, (200, 60, 60), (bar_x - 5, fish_y - 5, bar_w + 10, 10), border_radius=3)

        bar_y = bar_top + int(self.bar_pos * bar_height)
        bar_h = int(bar_height * 0.12)
        pygame.draw.rect(surface, GREEN_GLOW, (bar_x - 3, bar_y - bar_h // 2, bar_w + 6, bar_h), border_radius=4)
        pygame.draw.rect(surface, (150, 255, 180), (bar_x - 3, bar_y -
                         bar_h // 2, bar_w + 6, bar_h), 2, border_radius=4)

        prog_w = 200
        prog_x = WIDTH // 2 - prog_w // 2
        prog_y = bar_top + bar_height + 20
        pygame.draw.rect(surface, (30, 30, 40), (prog_x, prog_y, prog_w, 16), border_radius=8)
        fill = int(prog_w * self.catch_progress)
        prog_color = GREEN_GLOW if self.catch_progress > 0.5 else (200, 200, 60)
        pygame.draw.rect(surface, prog_color, (prog_x, prog_y, fill, 16), border_radius=8)

        hint = small_font.render("Hold SPACE to move bar  |  ESC to quit", True, (80, 100, 100))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 80))

        if self.result_msg:
            res = font.render(self.result_msg, True, GOLD)
            surface.blit(res, (WIDTH // 2 - res.get_width() // 2, HEIGHT // 2 + 100))

    def get_total_gold(self):
        return sum(f["gold"] for f in self.caught)

    def get_total_xp(self):
        return sum(f["xp"] for f in self.caught)
