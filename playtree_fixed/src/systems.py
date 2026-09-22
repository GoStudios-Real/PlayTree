import pygame
import math
import random
from config import *


class CraftingSystem:
    def __init__(self, player):
        self.player = player
        self.recipes = RECIPES

    def can_craft(self, recipe_name):
        if recipe_name not in self.recipes:
            return False
        recipe = self.recipes[recipe_name]
        for ingredient, amount in recipe["ingredients"].items():
            if self.player.inventory["resources"].get(ingredient, 0) < amount:
                return False
        return True

    def craft(self, recipe_name):
        if not self.can_craft(recipe_name):
            return False
        recipe = self.recipes[recipe_name]
        for ingredient, amount in recipe["ingredients"].items():
            self.player.inventory["resources"][ingredient] -= amount
        item = recipe["result"]
        self.player.inventory["items"].append(item)
        if item in WEAPONS:
            if not self.player.inventory.get("weapons"):
                self.player.inventory["weapons"] = []
            self.player.inventory["weapons"].append(item)
            self.player.equip_weapon(item)
        self.player.add_xp(20)
        return True


class QuestSystem:
    def __init__(self, player):
        self.player = player
        self.quests = []
        self.completed_this_frame = []
        self._generate_starter_quests()

    def _generate_starter_quests(self):
        self.quests = [{"name": "Awakening",
                        "desc": "Gather 5 Tree Energy from the forest",
                        "objective": "collect",
                        "target": "Tree Energy",
                        "count": 0,
                        "needed": 5,
                        "complete": False,
                        "reward_xp": 50,
                        "reward_item": "Health Potion"},
                       {"name": "Crystal Seeker",
                        "desc": "Find 3 Crystal Dust in the caves",
                        "objective": "collect",
                        "target": "Crystal Dust",
                        "count": 0,
                        "needed": 3,
                        "complete": False,
                        "reward_xp": 75,
                        "reward_item": "Energy Elixir"},
                       {"name": "First Creature",
                        "desc": "Tame a wild creature to join you",
                        "objective": "tame",
                        "target": "creature",
                        "count": 0,
                        "needed": 1,
                        "complete": False,
                        "reward_xp": 100,
                        "reward_item": "Pet Treat"},
                       {"name": "Region Explorer",
                        "desc": "Visit 3 different regions",
                        "objective": "explore",
                        "target": "region",
                        "count": 0,
                        "needed": 3,
                        "complete": False,
                        "reward_xp": 150,
                        "reward_item": "Ancient Seeds"},
                       {"name": "Corruption Cleanser",
                        "desc": "Defeat 5 corrupted enemies",
                        "objective": "defeat",
                        "target": "enemy",
                        "count": 0,
                        "needed": 5,
                        "complete": False,
                        "reward_xp": 200,
                        "reward_item": "Guardian Blade"},
                       ]
        self.player.quests = self.quests

    def update_progress(self, objective_type, target=None, amount=1):
        for quest in self.quests:
            if quest["complete"]:
                continue
            if quest["objective"] != objective_type:
                continue
            if target and quest.get("target") != target:
                continue
            if objective_type == "explore":
                visited = set()
                for q in self.quests:
                    if q["objective"] == "explore":
                        visited.add(q.get("visited_region"))
                if target not in visited:
                    quest["count"] = len(visited) + (1 if target else 0)
                    if target:
                        quest["visited_region"] = target
            else:
                quest["count"] += amount
            if quest["count"] >= quest["needed"]:
                if not quest["complete"]:
                    self.completed_this_frame.append(quest["name"])
                quest["complete"] = True
                self.player.add_xp(quest["reward_xp"])
                if quest.get("reward_item"):
                    self.player.inventory["items"].append(quest["reward_item"])


class CombatSystem:
    @staticmethod
    def check_attack(player_x, player_y, attack_range, facing, enemies, damage):
        hits = []
        for enemy in enemies:
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > attack_range + enemy.size:
                continue
            angle_to_enemy = math.atan2(dy, dx)
            angle_diff = abs(angle_to_enemy - facing)
            while angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff
            if angle_diff < 1.0:
                dead = enemy.take_damage(damage)
                hits.append((enemy, dead))
        return hits

    @staticmethod
    def deal_damage_to_player(enemy, player):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < enemy.attack_range + player.size and enemy.attack_cooldown <= 0:
            player.take_damage(enemy.attack)
            return True
        return False


class SeasonSystem:
    def __init__(self):
        self.season = 0
        self.chapter = 0
        self.week = 0
        self.event_active = False
        self.event_type = None
        self.event_timer = 0

    def update(self, dt):
        self.week += dt / 3600
        self.event_timer = max(0, self.event_timer - dt)
        if self.event_timer <= 0 and self.event_active:
            self.event_active = False
        if random.random() < 0.0001:
            self._trigger_random_event()

    def _trigger_random_event(self):
        events = ["crystal_storm", "world_invasion", "giant_boss", "holiday_event"]
        self.event_type = random.choice(events)
        self.event_active = True
        self.event_timer = 120


class DayNightCycle:
    def __init__(self):
        self.time = 6
        self.day_length = 300
        self.is_night = False

    def update(self, dt):
        self.time += dt / self.day_length * 24
        if self.time >= 24:
            self.time -= 24
        self.is_night = self.time < 6 or self.time > 20

    def get_light_level(self):
        if 6 <= self.time <= 8:
            return (self.time - 6) / 2
        elif 8 <= self.time <= 18:
            return 1.0
        elif 18 <= self.time <= 20:
            return 1.0 - (self.time - 18) / 2
        else:
            return 0.15

    def get_sky_color(self):
        if 6 <= self.time < 8:
            t = (self.time - 6) / 2
            return tuple(int(a + (b - a) * t) for a, b in zip((20, 10, 50), (100, 150, 255)))
        elif 8 <= self.time < 18:
            return (100, 150, 255)
        elif 18 <= self.time < 20:
            t = (self.time - 18) / 2
            return tuple(int(a + (b - a) * t) for a, b in zip((100, 150, 255), (255, 150, 80)))
        else:
            return (10, 5, 30)
