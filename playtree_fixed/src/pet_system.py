import pygame
import math
import random
import time
from config import *

PET_ABILITIES = {
    "forest": [
        {"name": "Quick Dash", "desc": "Dash to target, dealing 1.5x damage", "cooldown": 5, "damage_mult": 1.5},
        {"name": "Nature Heal", "desc": "Heal owner 15% max HP", "cooldown": 15, "heal_pct": 0.15},
    ],
    "crystal": [
        {"name": "Crystal Barrage", "desc": "Fire 3 crystal shards", "cooldown": 6, "damage_mult": 1.2},
        {"name": "Prism Shield", "desc": "Absorb next hit", "cooldown": 20, "shield": True},
    ],
    "mech": [
        {"name": "Overdrive", "desc": "+50% attack speed for 5s", "cooldown": 12, "buff": "speed"},
        {"name": "Repair", "desc": "Heal owner 20 HP", "cooldown": 10, "heal": 20},
    ],
    "spirit": [
        {"name": "Soul Drain", "desc": "Damage enemy, heal 50% dealt", "cooldown": 8, "lifesteal": 0.5},
        {"name": "Phase", "desc": "Become untargetable 2s", "cooldown": 18, "untargetable": 2.0},
    ],
    "nature": [
        {"name": "Entangle", "desc": "Root nearby enemies 2s", "cooldown": 10, "root": 2.0},
        {"name": "Growth", "desc": "+30% pet damage 8s", "cooldown": 15, "buff_damage": 0.3},
    ],
}

PET_EVOLUTION_VISUALS = {
    1: {"size": 8, "glow": 20, "particles": 3},
    2: {"size": 12, "glow": 35, "particles": 6},
    3: {"size": 18, "glow": 50, "particles": 10},
}


class PetManager:
    def __init__(self):
        self.active_pet_index = -1
        self.pet_cooldowns = {}
        self.pet_buffs = []
        self.pet_xp = {}

    def get_active_pet(self, player_creatures):
        if 0 <= self.active_pet_index < len(player_creatures):
            return player_creatures[self.active_pet_index]
        return None

    def cycle_pet(self, player_creatures):
        if not player_creatures:
            self.active_pet_index = -1
            return None
        self.active_pet_index = (self.active_pet_index + 1) % len(player_creatures)
        return player_creatures[self.active_pet_index]

    def use_ability(self, pet_data, pet_type):
        abilities = PET_ABILITIES.get(pet_type, [])
        if not abilities:
            return None
        ability = abilities[0]
        key = f"{pet_type}_0"
        cd = self.pet_cooldowns.get(key, 0)
        if cd > 0:
            return None
        self.pet_cooldowns[key] = ability["cooldown"]
        return ability

    def update(self, dt):
        for key in list(self.pet_cooldowns.keys()):
            self.pet_cooldowns[key] = max(0, self.pet_cooldowns[key] - dt)
        for buff in self.pet_buffs[:]:
            buff["timer"] -= dt
            if buff["timer"] <= 0:
                self.pet_buffs.remove(buff)

    def add_xp(self, pet_id, amount):
        current = self.pet_xp.get(pet_id, 0)
        self.pet_xp[pet_id] = current + amount

    def check_evolution(self, pet_data, pet_type):
        level = pet_data.get("level", 1)
        stage = pet_data.get("stage", 1)
        evo = PET_EVOLUTIONS.get(pet_data["name"], {})
        if stage == 1 and level >= evo.get("evolve_level", 10):
            return evo.get("stage2"), 2
        elif stage == 2 and level >= evo.get("stage3_level", 20):
            return evo.get("stage3"), 3
        return None, stage

    def draw_pet_info(self, screen, pet_data, x, y):
        pf = pygame.font.Font(None, 20)
        pf_sm = pygame.font.Font(None, 16)

        stage = pet_data.get("stage", 1)
        visuals = PET_EVOLUTION_VISUALS.get(stage, PET_EVOLUTION_VISUALS[1])

        name = pet_data.get("name", "Unknown")
        level = int(pet_data.get("level", 1))
        pet_type = pet_data.get("type", "forest")
        color = pet_data.get("color", (200, 200, 200))

        glow_s = pygame.Surface((visuals["glow"] * 2, visuals["glow"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*color[:3], 30), (visuals["glow"], visuals["glow"]), visuals["glow"])
        screen.blit(glow_s, (x - visuals["glow"] + 20, y - visuals["glow"] + 20))

        pygame.draw.circle(screen, color, (x + 20, y + 20), visuals["size"])

        for i in range(visuals["particles"]):
            angle = time.time() * 2 + i * (6.28 / max(1, visuals["particles"]))
            px = x + 20 + math.cos(angle) * (visuals["size"] + 5)
            py = y + 20 + math.sin(angle) * (visuals["size"] + 5)
            pygame.draw.circle(screen, (*color[:3], 150), (int(px), int(py)), 2)

        ns = pf.render(f"Lv.{level} {name}", True, color)
        screen.blit(ns, (x + 45, y + 8))

        abilities = PET_ABILITIES.get(pet_type, [])
        if abilities:
            ab = abilities[0]
            key = f"{pet_type}_0"
            cd = self.pet_cooldowns.get(key, 0)
            cd_text = f"  {ab['name']}: {ab['desc'][:25]}"
            if cd > 0:
                cd_text += f" ({cd:.0f}s)"
            as_ = pf_sm.render(cd_text, True, (140, 160, 140) if cd <= 0 else (100, 100, 100))
            screen.blit(as_, (x + 45, y + 26))

        evo_name, new_stage = self.check_evolution(pet_data, pet_type)
        if evo_name:
            es = pf_sm.render(f"Evolves to {evo_name} at next level!", True, MAGIC_GOLD)
            screen.blit(es, (x + 45, y + 40))

    def draw_pet_bar(self, screen, player_creatures, y):
        if not player_creatures:
            return

        pf = pygame.font.Font(None, 18)
        start_x = 10

        for i, pet in enumerate(player_creatures):
            is_active = i == self.active_pet_index
            px = start_x + i * 160
            color = pet.get("color", (200, 200, 200))
            border = GREEN_GLOW if is_active else (60, 60, 60)

            bg = pygame.Surface((155, 25), pygame.SRCALPHA)
            bg.fill((15, 15, 20, 160))
            screen.blit(bg, (px, y))
            pygame.draw.rect(screen, border, (px, y, 155, 25), 1, border_radius=4)

            pygame.draw.circle(screen, color, (px + 12, y + 12), 6)
            name = pet.get("name", "?")[:12]
            level = int(pet.get("level", 1))
            ns = pf.render(f"{name} Lv.{level}", True, color if is_active else (140, 140, 140))
            screen.blit(ns, (px + 22, y + 4))

            key = f"{pet.get('type', 'forest')}_0"
            cd = self.pet_cooldowns.get(key, 0)
            if cd > 0:
                cd_s = pf.render(f"CD:{cd:.0f}", True, (180, 60, 60))
                screen.blit(cd_s, (px + 130, y + 4))
