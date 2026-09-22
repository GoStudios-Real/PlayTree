import pygame
import math
from config import PET_EVOLUTIONS, WIDTH, HEIGHT, GOLD, GREEN_GLOW


class PetEvolution:
    def __init__(self):
        self.notifications = []

    def check_evolution(self, creature):
        name = creature.get("name", "")
        level = creature.get("level", 1)
        evo = PET_EVOLUTIONS.get(name)
        if not evo:
            return False

        if level >= evo.get("stage3_level", 99) and creature.get("stage", 1) < 3:
            creature["name"] = evo["stage3"]
            creature["stage"] = 3
            creature["color"] = self._evolved_color(evo["stage3"])
            creature["hp"] = creature.get("hp", 50) + 40
            creature["attack"] = creature.get("attack", 5) + 8
            self.notifications.append({
                "text": f"{evo['stage3']} evolved from {evo['stage2']}!",
                "timer": 3.0,
                "color": GOLD,
            })
            return True

        if level >= evo.get("evolve_level", 99) and creature.get("stage", 1) < 2:
            creature["name"] = evo["stage2"]
            creature["stage"] = 2
            creature["color"] = self._evolved_color(evo["stage2"])
            creature["hp"] = creature.get("hp", 50) + 20
            creature["attack"] = creature.get("attack", 5) + 4
            self.notifications.append({
                "text": f"{evo['stage2']} evolved from {name}!",
                "timer": 3.0,
                "color": GREEN_GLOW,
            })
            return True

        return False

    def _evolved_color(self, name):
        colors = {
            "Ember Wolf": (255, 100, 30),
            "Inferno Fenrir": (255, 50, 0),
            "Prism Wyrm": (200, 150, 255),
            "Aether Dragon": (100, 200, 255),
            "War Hawk": (220, 180, 60),
            "Iron Phoenix": (255, 160, 40),
            "Frost Direwolf": (100, 180, 255),
            "Void Cerberus": (80, 40, 160),
            "Elder Ent": (60, 120, 40),
            "World Tree": (40, 200, 80),
        }
        return colors.get(name, (180, 180, 180))

    def update(self, dt):
        for n in self.notifications:
            n["timer"] -= dt
        self.notifications = [n for n in self.notifications if n["timer"] > 0]

    def draw_notifications(self, surface, font):
        for i, n in enumerate(self.notifications):
            alpha = min(1.0, n["timer"])
            ny = 120 + i * 40
            txt = font.render(n["text"], True, (*n["color"][:3], int(255 * alpha)))
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, ny))
