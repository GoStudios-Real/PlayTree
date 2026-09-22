import pygame
import math
import random
from enum import Enum


class PlayerClass(Enum):
    GUARDIAN = 'Guardian'
    RANGER = 'Ranger'
    MAGE = 'Mage'
    MECHANIC = 'Mechanic'
    BEAST_TAMER = 'Beast Tamer'
    SHADOW_ASSASSIN = 'Shadow Assassin'


class GameState(Enum):
    MAIN_MENU = 0
    CHARACTER_CREATE = 1
    PLAYING = 2
    INVENTORY = 3
    CRAFTING = 4
    PAUSED = 5
    GAME_OVER = 6
    SETTINGS = 7
    SHOP = 8
    BATTLE_PASS = 9
    BASE_BUILD = 10
    MULTIPLAYER = 11
    ROUND_INTRO = 12
    END_CREDITS = 13
    LOGIN = 14
    LOBBY = 15


ACHIEVEMENTS = {
    'first_blood': {
        'name': 'First Blood', 'desc': 'Defeat your first enemy', 'reward_gold': 10}, 'boss_slayer': {
            'name': 'Boss Slayer', 'desc': 'Defeat your first boss', 'reward_gold': 50}, 'round_clear': {
                'name': 'Round Clear', 'desc': 'Clear all 4 rounds', 'reward_gold': 200}, 'collector': {
                    'name': 'Collector', 'desc': 'Collect 100 resources', 'reward_gold': 30}, 'craft_master': {
                        'name': 'Craft Master', 'desc': 'Craft 20 items', 'reward_gold': 40}, 'tamer': {
                            'name': 'Tamer', 'desc': 'Tame 5 creatures', 'reward_gold': 30}, 'builder': {
                                'name': 'Builder', 'desc': 'Build 10 structures', 'reward_gold': 40}, 'multiplayer': {
                                    'name': 'Social Butterfly', 'desc': 'Join 5 multiplayer games', 'reward_gold': 25}, 'survivor': {
                                        'name': 'Survivor', 'desc': 'Survive 10 minutes', 'reward_gold': 15}, 'rich': {
                                            'name': 'Rich', 'desc': 'Accumulate 1000 Gold Leaves', 'reward_gold': 50}, 'fisherman': {
                                                'name': 'Fisherman', 'desc': 'Catch 10 fish', 'reward_gold': 20}, 'legendary_gear': {
                                                    'name': 'Legendary Gear', 'desc': 'Own a Legendary weapon', 'reward_gold': 100}, 'full_skill_tree': {
                                                        'name': 'Full Build', 'desc': 'Max out a skill tree', 'reward_gold': 150}, 'new_game_plus': {
                                                            'name': 'New Game+', 'desc': 'Complete New Game+', 'reward_gold': 500}, 'secret_boss': {
                                                                'name': 'Secret Hunter', 'desc': 'Find and defeat a secret boss', 'reward_gold': 200}}
ARMOR_TYPES = {
    'cloth_chest': {
        'name': 'Cloth Tunic', 'slot': 'chest', 'defense': 2, 'hp_bonus': 5, 'color': (
            100, 120, 100), 'cost': 10}, 'leather_chest': {
                'name': 'Leather Vest', 'slot': 'chest', 'defense': 5, 'hp_bonus': 10, 'color': (
                    140, 100, 60), 'cost': 25}, 'iron_chest': {
                        'name': 'Iron Breastplate', 'slot': 'chest', 'defense': 10, 'hp_bonus': 20, 'color': (
                            160, 160, 170), 'cost': 50}, 'crystal_chest': {
                                'name': 'Crystal Plate', 'slot': 'chest', 'defense': 15, 'hp_bonus': 30, 'color': (
                                    180, 140, 220), 'cost': 80}, 'shadow_chest': {
                                        'name': 'Shadow Robe', 'slot': 'chest', 'defense': 8, 'hp_bonus': 15, 'color': (
                                            50, 20, 70), 'cost': 60}, 'dragon_chest': {
                                                'name': 'Dragon Scale', 'slot': 'chest', 'defense': 22, 'hp_bonus': 45, 'color': (
                                                    200, 80, 30), 'cost': 150}, 'cloth_legs': {
                                                        'name': 'Cloth Pants', 'slot': 'legs', 'defense': 1, 'hp_bonus': 3, 'color': (
                                                            90, 110, 90), 'cost': 8}, 'leather_legs': {
                                                                'name': 'Leather Greaves', 'slot': 'legs', 'defense': 3, 'hp_bonus': 8, 'color': (
                                                                    130, 90, 50), 'cost': 20}, 'iron_legs': {
                                                                        'name': 'Iron Leggings', 'slot': 'legs', 'defense': 7, 'hp_bonus': 15, 'color': (
                                                                            150, 150, 160), 'cost': 40}, 'crystal_legs': {
                                                                                'name': 'Crystal Greaves', 'slot': 'legs', 'defense': 10, 'hp_bonus': 20, 'color': (
                                                                                    160, 120, 200), 'cost': 65}, 'cloth_boots': {
                                                                                        'name': 'Cloth Boots', 'slot': 'boots', 'defense': 1, 'hp_bonus': 2, 'speed_bonus': 0.5, 'color': (
                                                                                            80, 100, 80), 'cost': 6}, 'leather_boots': {
                                                                                                'name': 'Leather Boots', 'slot': 'boots', 'defense': 2, 'hp_bonus': 5, 'speed_bonus': 1.0, 'color': (
                                                                                                    120, 80, 40), 'cost': 18}, 'iron_boots': {
                                                                                                        'name': 'Iron Boots', 'slot': 'boots', 'defense': 5, 'hp_bonus': 10, 'speed_bonus': 0, 'color': (
                                                                                                            140, 140, 150), 'cost': 35}, 'swift_boots': {
                                                                                                                'name': 'Swift Boots', 'slot': 'boots', 'defense': 2, 'hp_bonus': 8, 'speed_bonus': 2.5, 'color': (
                                                                                                                    60, 200, 100), 'cost': 55}, 'cloth_helm': {
                                                                                                                        'name': 'Cloth Hood', 'slot': 'head', 'defense': 1, 'hp_bonus': 3, 'color': (
                                                                                                                            110, 130, 110), 'cost': 8}, 'iron_helm': {
                                                                                                                                'name': 'Iron Helmet', 'slot': 'head', 'defense': 6, 'hp_bonus': 12, 'color': (
                                                                                                                                    155, 155, 165), 'cost': 35}, 'crystal_helm': {
                                                                                                                                        'name': 'Crystal Crown', 'slot': 'head', 'defense': 8, 'hp_bonus': 18, 'color': (
                                                                                                                                            200, 160, 240), 'cost': 60}, 'shadow_hood': {
                                                                                                                                                'name': 'Shadow Hood', 'slot': 'head', 'defense': 4, 'hp_bonus': 10, 'color': (
                                                                                                                                                    40, 10, 60), 'cost': 40}}
BLACK = (0, 0, 0)
BLUE = (50, 120, 255)
BROWN = (120, 80, 50)
CHAPTER = 'Chapter 0'
CHUNK_SIZE = 10
CLASS_COLORS = {
    PlayerClass.GUARDIAN: (
        60, 120, 255), PlayerClass.RANGER: (
            60, 200, 80), PlayerClass.MAGE: (
                180, 60, 255), PlayerClass.MECHANIC: (
                    255, 160, 40), PlayerClass.BEAST_TAMER: (
                        255, 200, 60), PlayerClass.SHADOW_ASSASSIN: (
                            120, 40, 160)}
CLASS_STATS = {
    PlayerClass.GUARDIAN: {
        'hp': 120, 'energy': 80, 'attack': 12, 'defense': 15, 'speed': 4.0}, PlayerClass.RANGER: {
            'hp': 85, 'energy': 100, 'attack': 15, 'defense': 8, 'speed': 5.5}, PlayerClass.MAGE: {
                'hp': 70, 'energy': 140, 'attack': 18, 'defense': 5, 'speed': 4.5}, PlayerClass.MECHANIC: {
                    'hp': 95, 'energy': 110, 'attack': 14, 'defense': 12, 'speed': 4.0}, PlayerClass.BEAST_TAMER: {
                        'hp': 90, 'energy': 120, 'attack': 10, 'defense': 10, 'speed': 5.0}, PlayerClass.SHADOW_ASSASSIN: {
                            'hp': 65, 'energy': 130, 'attack': 22, 'defense': 4, 'speed': 7.0}}
CREATURES = [
    {
        'name': 'Forest Fox', 'color': (
            255, 140, 60), 'type': 'forest', 'evolves_at': 5}, {
                'name': 'Crystal Dragon', 'color': (
                    180, 120, 255), 'type': 'crystal', 'evolves_at': 10}, {
                        'name': 'Mechanical Owl', 'color': (
                            200, 180, 100), 'type': 'mech', 'evolves_at': 7}, {
                                'name': 'Spirit Wolf', 'color': (
                                    150, 200, 255), 'type': 'spirit', 'evolves_at': 8}, {
                                        'name': 'Tree Guardian', 'color': (
                                            80, 180, 60), 'type': 'nature', 'evolves_at': 12}]
CRYSTAL = (180, 120, 255)
CYAN = (0, 200, 255)
DARK_BLUE = (10, 10, 40)
DARK_GREEN = (20, 60, 30)
DAY_NIGHT_CYCLE_SECONDS = 300
DEFAULT_SETTINGS = {
    'music_volume': 0.7,
    'sfx_volume': 0.8,
    'fullscreen': False,
    'show_fps': False,
    'screen_shake': True,
    'show_damage_numbers': True,
    'auto_collect': True,
    'controls': {
        'move': 'WASD / Arrow Keys',
        'attack': 'Left Click',
        'dodge': 'Space',
        'special': 'Q / 3',
        'inventory': 'I',
        'crafting': 'C',
        'tame': 'Tab',
        'health_potion': 'H',
        'weapon_1-8': 'Keys 1-8',
        'unequip': '0',
        'storm': 'T',
        'interact': 'E',
        'pause': 'Escape',
        'mount': 'M',
        'mount_sprint': 'R',
        'mount_cycle': 'N / B'}}
EMOTES = {
    'wave': {
        'name': 'Wave', 'duration': 1.0, 'color': (
            255, 255, 200)}, 'dance': {
                'name': 'Dance', 'duration': 2.0, 'color': (
                    255, 200, 100)}, 'laugh': {
                        'name': 'Laugh', 'duration': 1.0, 'color': (
                            255, 200, 200)}, 'cry': {
                                'name': 'Cry', 'duration': 1.5, 'color': (
                                    100, 150, 255)}, 'flex': {
                                        'name': 'Flex', 'duration': 1.5, 'color': (
                                            255, 180, 100)}, 'sit': {
                                                'name': 'Sit', 'duration': 3.0, 'color': (
                                                    150, 150, 150)}, 'point': {
                                                        'name': 'Point', 'duration': 1.0, 'color': (
                                                            255, 255, 255)}, 'cheer': {
                                                                'name': 'Cheer', 'duration': 1.5, 'color': (
                                                                    255, 215, 0)}}
ENCHANTMENTS = {
    'fire_damage': {
        'name': 'Fire Damage',
        'desc': '+25% attack, burn DoT',
        'cost': 30,
        'stat': 'attack',
        'bonus': 0.25},
    'frost_shield': {
        'name': 'Frost Shield',
        'desc': '+20% defense, slow on hit',
        'cost': 25,
        'stat': 'defense',
        'bonus': 0.2},
    'swift_feet': {
        'name': 'Swift Feet',
                'desc': '+15% speed',
                'cost': 20,
                'stat': 'speed',
                'bonus': 0.15},
    'life_steal': {
        'name': 'Life Steal',
        'desc': 'Heal 10% of damage dealt',
        'cost': 40,
        'stat': 'lifesteal',
        'bonus': 0.1},
    'crit_chance': {
        'name': 'Critical Strike',
        'desc': '+20% crit chance',
        'cost': 35,
        'stat': 'crit',
        'bonus': 0.2},
    'mana_return': {
        'name': 'Mana Return',
        'desc': 'Regen 5 energy/sec',
        'cost': 30,
        'stat': 'regen',
        'bonus': 5}}
ENEMIES = [
    {
        'name': 'Corrupted Beast', 'color': (
            100, 20, 40), 'hp': 30, 'attack': 5, 'speed': 2.5}, {
                'name': 'Shadow Root', 'color': (
                    40, 0, 60), 'hp': 45, 'attack': 7, 'speed': 1.5}, {
                        'name': 'Thorn Viper', 'color': (
                            60, 120, 40), 'hp': 25, 'attack': 6, 'speed': 3.0}, {
                                'name': 'Murk Slime', 'color': (
                                    40, 60, 30), 'hp': 20, 'attack': 3, 'speed': 1.2}, {
                                        'name': 'Forest Wraith', 'color': (
                                            30, 80, 50), 'hp': 35, 'attack': 8, 'speed': 2.8}, {
                                                'name': 'Crystal Monster', 'color': (
                                                    200, 50, 150), 'hp': 50, 'attack': 8, 'speed': 2.0}, {
                                                        'name': 'Crystal Golem', 'color': (
                                                            160, 80, 200), 'hp': 80, 'attack': 12, 'speed': 0.8}, {
                                                                'name': 'Prism Moth', 'color': (
                                                                    220, 180, 255), 'hp': 30, 'attack': 10, 'speed': 4.0}, {
                                                                        'name': 'Crystal Scorpion', 'color': (
                                                                            120, 40, 180), 'hp': 55, 'attack': 14, 'speed': 2.5}, {
                                                                                'name': 'Gem Spider', 'color': (
                                                                                    180, 100, 220), 'hp': 40, 'attack': 9, 'speed': 3.0}, {
                                                                                        'name': 'Ancient Guardian', 'color': (
                                                                                            150, 120, 80), 'hp': 80, 'attack': 12, 'speed': 1.0}, {
                                                                                                'name': 'Storm Hawk', 'color': (
                                                                                                    180, 180, 220), 'hp': 50, 'attack': 10, 'speed': 5.0}, {
                                                                                                        'name': 'Cloud Serpent', 'color': (
                                                                                                            200, 210, 240), 'hp': 100, 'attack': 15, 'speed': 2.5}, {
                                                                                                                'name': 'Tempest Mage', 'color': (
                                                                                                                    120, 140, 200), 'hp': 60, 'attack': 18, 'speed': 2.0}, {
                                                                                                                        'name': 'Thunder Beast', 'color': (
                                                                                                                            160, 160, 80), 'hp': 90, 'attack': 20, 'speed': 1.5}, {
                                                                                                                                'name': 'Boss Titan', 'color': (
                                                                                                                                    200, 30, 30), 'hp': 500, 'attack': 25, 'speed': 0.8}, {
                                                                                                                                        'name': 'Dark Knight', 'color': (
                                                                                                                                            60, 20, 40), 'hp': 120, 'attack': 18, 'speed': 3.0}, {
                                                                                                                                                'name': 'Shadow Mage', 'color': (
                                                                                                                                                    80, 10, 60), 'hp': 70, 'attack': 22, 'speed': 2.5}, {
                                                                                                                                                        'name': 'Void Stalker', 'color': (
                                                                                                                                                            30, 0, 40), 'hp': 90, 'attack': 20, 'speed': 4.0}, {
                                                                                                                                                                'name': 'Inferno Hound', 'color': (
                                                                                                                                                                    200, 60, 20), 'hp': 110, 'attack': 25, 'speed': 3.5}, {
                                                                                                                                                                        'name': 'Frost Giant', 'color': (
                                                                                                                                                                            100, 180, 240), 'hp': 200, 'attack': 28, 'speed': 1.0}, {
                                                                                                                                                                                'name': 'Lava Elemental', 'color': (
                                                                                                                                                                                    240, 80, 20), 'hp': 180, 'attack': 30, 'speed': 1.5}, {
                                                                                                                                                                                        'name': 'Venom Queen', 'color': (
                                                                                                                                                                                            80, 200, 40), 'hp': 150, 'attack': 22, 'speed': 3.0}, {
                                                                                                                                                                                                'name': 'Death Reaper', 'color': (
                                                                                                                                                                                                    40, 0, 0), 'hp': 250, 'attack': 35, 'speed': 2.0}, {
                                                                                                                                                                                                        'name': 'Elder Dragon', 'color': (
                                                                                                                                                                                                            180, 100, 40), 'hp': 350, 'attack': 40, 'speed': 1.8}]
FISH_TYPES = [
    {
        'name': 'Common Fish', 'color': (
            150, 180, 200), 'xp': 5, 'gold': 2, 'rarity': 'common'}, {
                'name': 'Golden Koi', 'color': (
                    255, 215, 0), 'xp': 15, 'gold': 10, 'rarity': 'uncommon'}, {
                        'name': 'Crystal Eel', 'color': (
                            160, 120, 255), 'xp': 25, 'gold': 20, 'rarity': 'rare'}, {
                                'name': 'Shadow Catfish', 'color': (
                                    80, 40, 120), 'xp': 40, 'gold': 35, 'rarity': 'epic'}, {
                                        'name': 'Leviathan', 'color': (
                                            200, 60, 60), 'xp': 100, 'gold': 80, 'rarity': 'legendary'}]
FPS = 60
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)
GREEN_GLOW = (100, 255, 150)

HATS = [
    'none',
    'crown',
    'hood',
    'helmet',
    'flower_crown',
    'shadow_mask',
    'halo',
    'witch_hat',
    'viking_horn',
    'cat_ears',
    'pirate_hat',
    'chef_hat']
HEIGHT = 720
MAGIC_BLUE = (60, 180, 255)
MAGIC_GOLD = (255, 220, 50)
MAGIC_GREEN = (80, 255, 120)
MAGIC_PURPLE = (180, 80, 255)
MOUNT_TYPES = {
    'forest_stag': {
        'name': 'Forest Stag', 'speed': 2.5, 'hp': 50, 'size': 16, 'color': (
            100, 160, 80), 'accent': (
                60, 120, 50)}, 'crystal_wolf': {
                    'name': 'Crystal Wolf', 'speed': 3.2, 'hp': 70, 'size': 14, 'color': (
                        120, 180, 220), 'accent': (
                            200, 230, 255)}, 'shadow_raven': {
                                'name': 'Shadow Raven', 'speed': 2.8, 'hp': 40, 'size': 12, 'color': (
                                    50, 40, 70), 'accent': (
                                        160, 100, 255)}, 'sky_drake': {
                                            'name': 'Sky Drake', 'speed': 3.5, 'hp': 90, 'size': 18, 'color': (
                                                150, 180, 220), 'accent': (
                                                    255, 255, 200)}, 'ancient_beetle': {
                                                        'name': 'Ancient Beetle', 'speed': 1.8, 'hp': 150, 'size': 20, 'color': (
                                                            80, 60, 40), 'accent': (
                                                                180, 140, 60)}}
NATURE_GREEN = (60, 180, 80)
NIGHT_ENEMY_MULTIPLIER = 1.5
NIGHT_SPAWN_RATE = 2.0
ORANGE = (255, 140, 0)
PET_EVOLUTIONS = {
    'Forest Fox': {
        'stage2': 'Ember Wolf', 'stage3': 'Inferno Fenrir', 'evolve_level': 8, 'stage3_level': 16}, 'Crystal Dragon': {
            'stage2': 'Prism Wyrm', 'stage3': 'Aether Dragon', 'evolve_level': 10, 'stage3_level': 20}, 'Mechanical Owl': {
                'stage2': 'War Hawk', 'stage3': 'Iron Phoenix', 'evolve_level': 9, 'stage3_level': 18}, 'Spirit Wolf': {
                    'stage2': 'Frost Direwolf', 'stage3': 'Void Cerberus', 'evolve_level': 10, 'stage3_level': 20}, 'Tree Guardian': {
                        'stage2': 'Elder Ent', 'stage3': 'World Tree', 'evolve_level': 12, 'stage3_level': 24}}
PINK = (255, 100, 200)
PURPLE = (120, 50, 200)

RANDOM_EVENTS = [
    {
        'name': 'Wandering Merchant', 'desc': 'A merchant appears with rare goods!', 'type': 'merchant', 'chance': 0.02}, {
            'name': 'Treasure Chest', 'desc': 'You found a treasure chest!', 'type': 'treasure', 'chance': 0.03}, {
                'name': 'Shrining Blessing', 'desc': 'An ancient shrine grants power!', 'type': 'shrine', 'chance': 0.015}, {
                    'name': 'Ambush!', 'desc': 'Enemies ambush you!', 'type': 'ambush', 'chance': 0.025}, {
                        'name': 'Starfall', 'desc': 'Meteors rain down!', 'type': 'starfall', 'chance': 0.01}]
RECIPES = {
    'Health Potion': {
        'ingredients': {
            'Tree Energy': 3, 'Crystal Dust': 1}, 'result': 'potion_hp'}, 'Energy Elixir': {
                'ingredients': {
                    'Tree Energy': 2, 'Light Fragments': 1}, 'result': 'elixir_energy'}, 'Pet Treat': {
                        'ingredients': {
                            'Ancient Seeds': 2, 'Tree Energy': 1}, 'result': 'pet_treat'}, 'Iron Sword': {
                                'ingredients': {
                                    'Crystal Dust': 3, 'Tree Energy': 2}, 'result': 'sword_iron'}, 'Crystal Blade': {
                                        'ingredients': {
                                            'Crystal Dust': 6, 'Light Fragments': 2}, 'result': 'sword_crystal'}, 'Shadow Edge': {
                                                'ingredients': {
                                                    'Ancient Seeds': 4, 'Crystal Dust': 5}, 'result': 'sword_shadow'}, 'Flame Sword': {
                                                        'ingredients': {
                                                            'Ancient Seeds': 6, 'Light Fragments': 5}, 'result': 'sword_flame'}, 'Crystal Blaster': {
                                                                'ingredients': {
                                                                    'Crystal Dust': 4, 'Light Fragments': 3}, 'result': 'gun_crystal'}, 'Root Rifle': {
                                                                        'ingredients': {
                                                                            'Tree Energy': 6, 'Ancient Seeds': 3}, 'result': 'gun_root'}, 'Tech Pistol': {
                                                                                'ingredients': {
                                                                                    'Crystal Dust': 5, 'Light Fragments': 4}, 'result': 'gun_tech'}, 'Shadow Cannon': {
                                                                                        'ingredients': {
                                                                                            'Ancient Seeds': 5, 'Light Fragments': 6, 'Crystal Dust': 4}, 'result': 'gun_shadow'}, 'Frozen Shard Blade': {
                                                                                                'ingredients': {
                                                                                                    'Frozen Shards': 8, 'Crystal Dust': 3}, 'result': 'sword_frozen'}, 'Volcanic Hammer': {
                                                                                                        'ingredients': {
                                                                                                            'Volcanic Ash': 10, 'Ancient Root': 3}, 'result': 'sword_volcanic'}, 'Shadow Rifle': {
                                                                                                                'ingredients': {
                                                                                                                    'Shadow Essence': 6, 'Ancient Root': 4}, 'result': 'gun_shadow_rifle'}, 'Frost Potion': {
                                                                                                                        'ingredients': {
                                                                                                                            'Frozen Shards': 3, 'Tree Energy': 2}, 'result': 'potion_frost'}, 'Firebomb': {
                                                                                                                                'ingredients': {
                                                                                                                                    'Volcanic Ash': 4, 'Ancient Seeds': 2}, 'result': 'bomb_fire'}, 'Shield Totem': {
                                                                                                                                        'ingredients': {
                                                                                                                                            'Ancient Root': 5, 'Light Fragments': 3}, 'result': 'totem_shield'}, 'Speed Boots': {
                                                                                                                                                'ingredients': {
                                                                                                                                                    'Frozen Shards': 4, 'Crystal Dust': 3}, 'result': 'boots_speed'}, 'Mana Crystal': {
                                                                                                                                                        'ingredients': {
                                                                                                                                                            'Crystal Dust': 8, 'Light Fragments': 2}, 'result': 'crystal_mana'}}
RED = (220, 40, 40)
REGIONS = [
    {
        'name': 'Emerald Roots Forest', 'color': (
            40, 120, 60), 'ambient': (
                20, 60, 30), 'tier': 1}, {
                    'name': 'Crystal Hollow', 'color': (
                        120, 60, 180), 'ambient': (
                            20, 10, 40), 'tier': 2}, {
                                'name': 'Skyroot Peaks', 'color': (
                                    60, 120, 200), 'ambient': (
                                        10, 20, 50), 'tier': 3}, {
                                            'name': 'Fallen Core Desert', 'color': (
                                                200, 160, 80), 'ambient': (
                                                    40, 30, 10), 'tier': 4}, {
                                                        'name': 'Whispering Ruins', 'color': (
                                                            140, 120, 160), 'ambient': (
                                                                30, 25, 40), 'tier': 5}, {
                                                                    'name': 'Frozen Spire', 'color': (
                                                                        180, 210, 240), 'ambient': (
                                                                            20, 30, 50), 'tier': 3}, {
                                                                                'name': 'Volcanic Core', 'color': (
                                                                                    180, 60, 30), 'ambient': (
                                                                                        40, 10, 5), 'tier': 6}, {
                                                                                            'name': 'Shadowfen Swamp', 'color': (
                                                                                                60, 100, 50), 'ambient': (
                                                                                                    15, 25, 15), 'tier': 4}, {
                                                                                                        'name': 'Starfall Meadows', 'color': (
                                                                                                            80, 140, 180), 'ambient': (
                                                                                                                10, 20, 35), 'tier': 2}, {
                                                                                                                    'name': 'Thornwood Wilds', 'color': (
                                                                                                                        50, 90, 40), 'ambient': (
                                                                                                                            15, 30, 10), 'tier': 2}, {
                                                                                                                                'name': 'Celestial Gardens', 'color': (
                                                                                                                                    160, 140, 200), 'ambient': (
                                                                                                                                        25, 20, 45), 'tier': 4}, {
                                                                                                                                            'name': 'Ironforge Depths', 'color': (
                                                                                                                                                100, 90, 80), 'ambient': (
                                                                                                                                                    25, 20, 15), 'tier': 3}, {
                                                                                                                                                        'name': 'Mistwood Hollow', 'color': (
                                                                                                                                                            70, 110, 90), 'ambient': (
                                                                                                                                                                15, 25, 20), 'tier': 2}, {
                                                                                                                                                                    'name': 'Sunfire Oasis', 'color': (
                                                                                                                                                                        220, 180, 100), 'ambient': (
                                                                                                                                                                            45, 35, 15), 'tier': 5}, {
                                                                                                                                                                                'name': 'Duskfall Cemetery', 'color': (
                                                                                                                                                                                    80, 70, 100), 'ambient': (
                                                                                                                                                                                        20, 15, 30), 'tier': 6}, {
                                                                                                                                                                                            'name': 'Sapphire Depths', 'color': (
                                                                                                                                                                                                40, 100, 180), 'ambient': (
                                                                                                                                                                                                    10, 20, 45), 'tier': 4}]
RESOURCES = {
    'Tree Energy': {
        'color': (
            80, 255, 120), 'rarity': 'common'}, 'Crystal Dust': {
                'color': (
                    180, 120, 255), 'rarity': 'uncommon'}, 'Ancient Seeds': {
                        'color': (
                            255, 200, 60), 'rarity': 'rare'}, 'Light Fragments': {
                                'color': (
                                    255, 255, 200), 'rarity': 'epic'}, 'Shadow Essence': {
                                        'color': (
                                            100, 40, 160), 'rarity': 'rare'}, 'Ancient Root': {
                                                'color': (
                                                    140, 100, 60), 'rarity': 'epic'}, 'Frozen Shards': {
                                                        'color': (
                                                            180, 220, 255), 'rarity': 'uncommon'}, 'Volcanic Ash': {
                                                                'color': (
                                                                    200, 80, 30), 'rarity': 'uncommon'}, 'Gold Leaves': {
                                                                        'color': (
                                                                            255, 215, 0), 'rarity': 'common'}}
SAND = (220, 200, 150)
SEASON = 'Season 0'
SHOP_ITEMS = {
    'Health Potion': {
        'price': 10, 'currency': 'Gold Leaves', 'type': 'consumable', 'desc': 'Restores 30 HP', 'icon_color': (
            60, 220, 60)}, 'Energy Elixir': {
                'price': 15, 'currency': 'Gold Leaves', 'type': 'consumable', 'desc': 'Restores 50 Energy', 'icon_color': (
                    80, 180, 255)}, 'Iron Sword': {
                        'price': 30, 'currency': 'Gold Leaves', 'type': 'weapon', 'id': 'sword_iron', 'desc': 'Sturdy iron blade', 'icon_color': (
                            180, 180, 190)}, 'Crystal Blaster': {
                                'price': 50, 'currency': 'Gold Leaves', 'type': 'weapon', 'id': 'gun_crystal', 'desc': 'Fires crystal shards', 'icon_color': (
                                    180, 120, 255)}, 'Root Rifle': {
                                        'price': 60, 'currency': 'Gold Leaves', 'type': 'weapon', 'id': 'gun_root', 'desc': 'Thorned root bolts', 'icon_color': (
                                            80, 200, 60)}, 'Flame Sword': {
                                                'price': 80, 'currency': 'Gold Leaves', 'type': 'weapon', 'id': 'sword_flame', 'desc': 'Ancient tree fire', 'icon_color': (
                                                    255, 100, 30)}, 'Forest Fox Egg': {
                                                        'price': 40, 'currency': 'Gold Leaves', 'type': 'pet', 'id': 0, 'desc': 'Hatch a forest fox', 'icon_color': (
                                                            255, 140, 60)}, 'Spirit Wolf Egg': {
                                                                'price': 70, 'currency': 'Gold Leaves', 'type': 'pet', 'id': 3, 'desc': 'Hatch a spirit wolf', 'icon_color': (
                                                                    150, 200, 255)}, 'Crystal Dragon Egg': {
                                                                        'price': 120, 'currency': 'Gold Leaves', 'type': 'pet', 'id': 1, 'desc': 'Hatch a crystal dragon', 'icon_color': (
                                                                            180, 120, 255)}, 'Tree Guardian Egg': {
                                                                                'price': 100, 'currency': 'Gold Leaves', 'type': 'pet', 'id': 4, 'desc': 'Hatch a tree guardian', 'icon_color': (
                                                                                    80, 180, 60)}}
SKILL_TREES = {
    PlayerClass.GUARDIAN: {
        'shield_bash': {
            'name': 'Shield Bash',
            'desc': 'Stun enemy 1.5s',
            'cost': 2,
            'max': 3,
            'requires': None},
        'iron_wall': {
            'name': 'Iron Wall',
            'desc': '+30% defense 5s',
            'cost': 3,
            'max': 3,
            'requires': 'shield_bash'},
        'taunt': {
            'name': 'Taunt',
                    'desc': 'Draw enemy aggro',
                    'cost': 2,
                    'max': 2,
                    'requires': None},
        'holy_light': {
            'name': 'Holy Light',
            'desc': 'Heal 40 HP',
            'cost': 4,
            'max': 2,
            'requires': 'iron_wall'},
        'divine_shield': {
            'name': 'Divine Shield',
            'desc': 'Invincible 3s',
            'cost': 5,
            'max': 1,
            'requires': 'holy_light'}},
    PlayerClass.RANGER: {
        'double_shot': {
            'name': 'Double Shot',
            'desc': 'Fire 2 arrows',
            'cost': 2,
            'max': 3,
            'requires': None},
        'piercing': {
            'name': 'Piercing Arrow',
            'desc': 'Arrow hits all',
            'cost': 3,
            'max': 3,
            'requires': 'double_shot'},
        'trap': {
            'name': 'Trap',
            'desc': 'Root enemy 2s',
            'cost': 2,
            'max': 2,
            'requires': None},
        'eagle_eye': {
            'name': 'Eagle Eye',
            'desc': '+50% crit chance 5s',
            'cost': 4,
            'max': 2,
            'requires': 'piercing'},
        'rain_of_arrows': {
            'name': 'Rain of Arrows',
            'desc': 'AoE arrow barrage',
            'cost': 5,
            'max': 1,
            'requires': 'eagle_eye'}},
    PlayerClass.MAGE: {
        'fireball': {
            'name': 'Fireball',
            'desc': 'Explosive projectile',
            'cost': 2,
            'max': 3,
            'requires': None},
        'ice_shard': {
            'name': 'Ice Shard',
            'desc': 'Slow enemy 50%',
            'cost': 2,
            'max': 3,
            'requires': None},
        'chain_lightning': {
            'name': 'Chain Lightning',
            'desc': 'Hits 3 enemies',
            'cost': 3,
            'max': 3,
            'requires': 'fireball'},
        'mana_shield': {
            'name': 'Mana Shield',
            'desc': 'Absorb dmg with energy',
            'cost': 3,
            'max': 2,
            'requires': 'ice_shard'},
        'meteor': {
            'name': 'Meteor',
            'desc': 'Massive AoE damage',
            'cost': 5,
            'max': 1,
            'requires': 'chain_lightning'}},
    PlayerClass.MECHANIC: {
        'turret': {
            'name': 'Turret',
            'desc': 'Deploy auto-turret',
            'cost': 2,
            'max': 3,
            'requires': None},
        'overclock': {
            'name': 'Overclock',
            'desc': '+40% attack speed 5s',
            'cost': 3,
            'max': 3,
            'requires': 'turret'},
        'mine': {
            'name': 'Land Mine',
            'desc': 'Place explosive mine',
            'cost': 2,
            'max': 2,
            'requires': None},
        'repair_drone': {
            'name': 'Repair Drone',
            'desc': 'Heal 25 HP/sec 5s',
            'cost': 4,
            'max': 2,
            'requires': 'overclock'},
        'mech_suit': {
            'name': 'Mech Suit',
            'desc': 'Heavy armor mode 8s',
            'cost': 5,
            'max': 1,
            'requires': 'repair_drone'}},
    PlayerClass.BEAST_TAMER: {
        'beast_rush': {
            'name': 'Beast Rush',
            'desc': 'Pet charges enemy',
            'cost': 2,
            'max': 3,
            'requires': None},
        'feral_roar': {
            'name': 'Feral Roar',
            'desc': '+30% pet dmg 5s',
            'cost': 3,
            'max': 3,
            'requires': 'beast_rush'},
        'heal_pack': {
            'name': 'Heal Pack',
            'desc': 'Heal all pets + self',
            'cost': 2,
            'max': 2,
            'requires': None},
        'summon_swarm': {
            'name': 'Summon Swarm',
            'desc': 'Call 3 temp pets',
            'cost': 4,
            'max': 2,
            'requires': 'feral_roar'},
        'primal_fury': {
            'name': 'Primal Fury',
            'desc': 'All pets enrage 8s',
            'cost': 5,
            'max': 1,
            'requires': 'summon_swarm'}},
    PlayerClass.SHADOW_ASSASSIN: {
        'backstab': {
            'name': 'Backstab',
            'desc': '2.5x from behind',
            'cost': 2,
            'max': 3,
            'requires': None},
        'shadow_step': {
            'name': 'Shadow Step',
            'desc': 'Teleport behind enemy',
            'cost': 3,
            'max': 3,
            'requires': 'backstab'},
        'poison_blade': {
            'name': 'Poison Blade',
            'desc': 'DoT 3s',
            'cost': 2,
            'max': 2,
            'requires': None},
        'smoke_bomb': {
            'name': 'Smoke Bomb',
            'desc': 'Invisible 3s',
            'cost': 4,
            'max': 2,
            'requires': 'shadow_step'},
        'death_mark': {
            'name': 'Death Mark',
            'desc': 'Exec under 30% HP',
            'cost': 5,
            'max': 1,
            'requires': 'smoke_bomb'}}}
SNOW = (230, 240, 255)
TEAL = (0, 200, 200)
TILE_SIZE = 48
TITLE = 'PLAYTREE'
UNARMED = {'name': 'Fists', 'type': 'sword', 'damage': 5, 'speed': 0.3, 'range': 30,
           'color': (200, 180, 160), 'trail_color': (255, 255, 255), 'desc': 'Bare knuckles'}
VERSION = '1.0.0'
WEAPONS = {
    'sword_iron': {
        'name': 'Iron Sword', 'type': 'sword', 'damage': 12, 'speed': 0.25, 'range': 40, 'color': (
            180, 180, 190), 'trail_color': (
                200, 200, 210), 'desc': 'A sturdy iron blade'}, 'sword_crystal': {
                    'name': 'Crystal Blade', 'type': 'sword', 'damage': 16, 'speed': 0.18, 'range': 42, 'color': (
                        180, 120, 255), 'trail_color': (
                            200, 160, 255), 'desc': 'Crystallized energy forged into a blade'}, 'sword_shadow': {
                                'name': 'Shadow Edge', 'type': 'sword', 'damage': 22, 'speed': 0.22, 'range': 38, 'color': (
                                    80, 0, 120), 'trail_color': (
                                        120, 0, 180), 'desc': 'A blade woven from living shadow'}, 'sword_flame': {
                                            'name': 'Flame Sword', 'type': 'sword', 'damage': 25, 'speed': 0.28, 'range': 44, 'color': (
                                                255, 100, 30), 'trail_color': (
                                                    255, 180, 40), 'desc': 'Burns with ancient tree fire'}, 'sword_frozen': {
                                                        'name': 'Frozen Shard Blade', 'type': 'sword', 'damage': 20, 'speed': 0.2, 'range': 42, 'color': (
                                                            180, 220, 255), 'trail_color': (
                                                                200, 240, 255), 'desc': 'Frozen crystal that slows enemies'}, 'sword_volcanic': {
                                                                    'name': 'Volcanic Hammer', 'type': 'sword', 'damage': 30, 'speed': 0.35, 'range': 36, 'color': (
                                                                        200, 80, 30), 'trail_color': (
                                                                            255, 140, 50), 'desc': 'Molten rock forged into a devastating weapon'}, 'gun_crystal': {
                                                                                'name': 'Crystal Blaster', 'type': 'gun', 'damage': 10, 'speed': 0.4, 'range': 250, 'color': (
                                                                                    180, 120, 255), 'trail_color': (
                                                                                        180, 120, 255), 'projectile_speed': 12, 'projectile_color': (
                                                                                            200, 160, 255), 'desc': 'Fires shards of crystal energy'}, 'gun_root': {
                                                                                                'name': 'Root Rifle', 'type': 'gun', 'damage': 14, 'speed': 0.5, 'range': 280, 'color': (
                                                                                                    120, 80, 50), 'trail_color': (
                                                                                                        60, 180, 80), 'projectile_speed': 10, 'projectile_color': (
                                                                                                            80, 200, 60), 'desc': 'Launches thorned root bolts'}, 'gun_tech': {
                                                                                                                'name': 'Tech Pistol', 'type': 'gun', 'damage': 12, 'speed': 0.3, 'range': 220, 'color': (
                                                                                                                    150, 160, 180), 'trail_color': (
                                                                                                                        255, 140, 0), 'projectile_speed': 14, 'projectile_color': (
                                                                                                                            255, 200, 50), 'desc': 'A compact mechanical blaster'}, 'gun_shadow': {
                                                                                                                                'name': 'Shadow Cannon', 'type': 'gun', 'damage': 30, 'speed': 0.8, 'range': 200, 'color': (
                                                                                                                                    40, 0, 60), 'trail_color': (
                                                                                                                                        100, 0, 160), 'projectile_speed': 8, 'projectile_color': (
                                                                                                                                            160, 0, 220), 'desc': 'Devastating dark energy cannon'}, 'gun_shadow_rifle': {
                                                                                                                                                'name': 'Shadow Rifle', 'type': 'gun', 'damage': 18, 'speed': 0.35, 'range': 300, 'color': (
                                                                                                                                                    60, 20, 80), 'trail_color': (
                                                                                                                                                        120, 40, 180), 'projectile_speed': 13, 'projectile_color': (
                                                                                                                                                            140, 60, 200), 'desc': 'Precision shadow energy rifle'}}
WEAPON_RARITY = {
    'common': {
        'color': (
            180, 180, 180), 'multiplier': 1.0, 'label': 'Common'}, 'uncommon': {
                'color': (
                    80, 200, 80), 'multiplier': 1.25, 'label': 'Uncommon'}, 'rare': {
                        'color': (
                            60, 140, 255), 'multiplier': 1.5, 'label': 'Rare'}, 'epic': {
                                'color': (
                                    180, 80, 255), 'multiplier': 2.0, 'label': 'Epic'}, 'legendary': {
                                        'color': (
                                            255, 200, 50), 'multiplier': 2.75, 'label': 'Legendary'}, 'mythic': {
                                                'color': (
                                                    255, 60, 80), 'multiplier': 3.5, 'label': 'Mythic'}}
WHITE = (255, 255, 255)
WIDTH = 1280
WORLD_H = 9000
WORLD_W = 9000
