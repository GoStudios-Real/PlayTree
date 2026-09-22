import pygame
import random
from config import RANDOM_EVENTS, WIDTH, HEIGHT, GOLD, GREEN_GLOW, ENEMIES


class RandomEventManager:
    def __init__(self):
        self.timer = random.uniform(30, 90)
        self.active_event = None
        self.event_timer = 0
        self.merchant_items = []
        self.treasure_loot = []
        self.notification = None
        self.notification_timer = 0

    def update(self, dt, player, enemies, world):
        if self.notification_timer > 0:
            self.notification_timer -= dt

        if self.active_event:
            self.event_timer -= dt
            if self.event_timer <= 0:
                self.active_event = None
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(30, 90)
            for event in RANDOM_EVENTS:
                if random.random() < event["chance"]:
                    self.trigger_event(event, player, enemies, world)
                    break

    def trigger_event(self, event, player, enemies, world):
        self.active_event = event
        self.event_timer = 10.0
        self.notification = event["name"] + ": " + event["desc"]
        self.notification_timer = 3.0

        if event["type"] == "merchant":
            self.merchant_items = random.sample(list(range(len(ENEMIES))), min(3, len(ENEMIES)))
        elif event["type"] == "treasure":
            gold_amount = random.randint(5, 30)
            player.inventory["resources"]["Gold Leaves"] = player.inventory["resources"].get(
                "Gold Leaves", 0) + gold_amount
            self.treasure_loot = [{"type": "gold", "amount": gold_amount}]
        elif event["type"] == "shrine":
            player.hp = min(player.max_hp, player.hp + 30)
            player.energy = min(player.max_energy, player.energy + 30)
        elif event["type"] == "ambush":
            for _ in range(random.randint(3, 6)):
                tier = min(random.randint(0, 4), len(ENEMIES) - 1)
                ex = player.x + random.uniform(-200, 200)
                ey = player.y + random.uniform(-200, 200)
                from src.entities import Enemy
                enemies.append(Enemy(ex, ey, tier))
        elif event["type"] == "starfall":
            for _ in range(8):
                ex = player.x + random.uniform(-300, 300)
                ey = player.y + random.uniform(-300, 300)
                from src.entities import Enemy
                enemies.append(Enemy(ex, ey, random.randint(2, 4)))

    def draw_notification(self, surface, font, small_font):
        if self.notification_timer > 0 and self.notification:
            alpha = min(1.0, self.notification_timer / 0.5)
            ny = 60
            w = 500
            nx = WIDTH // 2 - w // 2
            overlay = pygame.Surface((w, 44), pygame.SRCALPHA)
            overlay.fill((20, 25, 15, int(200 * alpha)))
            pygame.draw.rect(overlay, (*GOLD[:3], int(180 * alpha)), (0, 0, w, 44), 2, border_radius=6)
            surface.blit(overlay, (nx, ny))
            title = small_font.render(self.notification, True, (*GOLD[:3], int(255 * alpha)))
            surface.blit(title, (nx + 10, ny + 12))
