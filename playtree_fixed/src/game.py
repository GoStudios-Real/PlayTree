import pygame
import math
import random
import sys
import time
import os
import threading
from config import *
from src.player import Player
from src.world import World
from src.entities import Enemy, Creature
from src.enemies_expanded import ExpandedEnemy
from src.systems import CraftingSystem, QuestSystem, CombatSystem, SeasonSystem, DayNightCycle
from src.ui import HUD, Button, xbox_icons, XBOX_BUTTON_MAP
from src.particles import ParticleSystem, GlowEffect, StarField
from src.menu import MainMenu
from src.audio import ProceduralAudio
from src.storm import StormSystem
from src.save_system import save_game, load_game, has_save, save_settings, load_settings, get_go_live_ts
from src.boss import Boss, BossHealthBar, BOSS_TYPES
from src.mounts import Mount
from src.base_building import BaseBuilder, BUILDING_TYPES
from src.battle_pass import BattlePass
from src.multiplayer import MultiplayerManager
from src.account import GoStudiosAccount
from src.touch_controls import TouchControls, IS_MOBILE
from src.tv_support import detect_tv_mode, get_tv_info, get_controller_name
from src.splash import SplashScreen
from src.astro_toilets import AstroToilet, ASTRO_TYPES
from src.skill_tree import SkillTree
from src.achievements import AchievementSystem
from src.fishing import FishingMinigame
from src.weather import WeatherSystem as AdvancedWeather
from src.random_events import RandomEventManager
from src.pet_evolution import PetEvolution
from src.enchanting import EnchantingSystem
from src.equipment import EquipmentSystem
from src.tutorial import Tutorial
from src.daily_rewards import DailyRewards
from src.leaderboards import LeaderboardSystem
from src.update_log import UpdateLog
from src.screenshot import ScreenshotSystem
from src.new_game_plus import NewGamePlus
from src.pet_system import PetManager
from src.legend_features import PlayerCount, DoggoLegend, DancingBots, AdminAbuse
from src.npcs import NPC, DialogueBox, NPC_TYPES


# Catalog shown by the main-menu GAMES button (mirrors the website games page).
GAMES_CATALOG = [
    {"id": "playtree", "title": "PlayTree", "plat": "Windows / Android / macOS / Linux", "zip": None, "web": True},
    {"id": "dungeon", "title": "PlayTree Dungeon", "plat": "Desktop", "zip": "standalone/PlayTreeDungeon.zip"},
    {"id": "puzzle", "title": "PlayTree Puzzle", "plat": "Desktop", "zip": "standalone/PlayTreePuzzle.zip"},
    {"id": "racing", "title": "PlayTree Racing", "plat": "Desktop", "zip": "standalone/PlayTreeRacing.zip"},
    {"id": "space", "title": "PlayTree Space", "plat": "Desktop", "zip": "standalone/PlayTreeSpace.zip"},
    {"id": "towerdef", "title": "PlayTree Tower Defense", "plat": "Desktop", "zip": "standalone/PlayTreeTowerDef.zip"},
    {"id": "underwater", "title": "PlayTree Underwater", "plat": "Desktop", "zip": "standalone/PlayTreeUnderwater.zip"},
    {"id": "football", "title": "PlayTree Football", "plat": "Desktop", "zip": "standalone/PlayTreeFootBall.zip"},
    {"id": "three-d", "title": "PlayTree 3D", "plat": "Desktop", "zip": "standalone/PlayTree3D.zip"},
]


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        self.time = 0

        self.starfield = StarField(100)

        loaded = load_settings()
        self.settings = dict(DEFAULT_SETTINGS) if loaded is None else {**DEFAULT_SETTINGS, **loaded}

        self.audio = ProceduralAudio(
            sfx_vol=self.settings.get("sfx_volume", 0.5),
            music_vol=self.settings.get("music_volume", 0.3)
        )
        self.particles = ParticleSystem()
        self.account = GoStudiosAccount()

        _is_mobile = sys.platform in ("android", "ios") or hasattr(sys, "getandroidapilevel")
        if _is_mobile:
            if not self.account.current_user:
                self.account.auto_login_guest()
            self.state = GameState.MAIN_MENU
        else:
            self.state = GameState.LOGIN if not self.account.current_user else GameState.MAIN_MENU
        self.main_menu = MainMenu(screen, has_save=has_save())
        self.main_menu.audio = self.audio
        self.season = SeasonSystem()
        self.day_night = DayNightCycle()
        self.storm = StormSystem()
        self.storm_random_timer = random.randint(30, 90)

        self.player = None
        self.world = None
        self.hud = None
        self.crafting = None
        self.quests = None
        self.enemies = []
        self.creatures = []
        self.selected_class = 0
        self.class_cycle = [PlayerClass.GUARDIAN, PlayerClass.RANGER, PlayerClass.MAGE,
                            PlayerClass.MECHANIC, PlayerClass.BEAST_TAMER]
        self.character_name = "Player"
        self.name_input = ""
        self.typing_name = False

        self.inventory_open = False
        self.crafting_open = False
        self.settings_open = False
        self.shop_open = False
        self.marketplace_open = False
        self.profile_open = False
        self.games_open = False
        self.games_selected = 0
        self.games_status = ""
        self._games_rects = {}
        self.menu_buttons = []
        self.message = ""
        self.message_timer = 0
        self.settings_hover = -1
        self.shop_hovered = -1
        self.achievements_open = False
        self.round_intro_timer = 0
        self.tutorial = None
        self.save_exists = has_save()
        self.auto_save_timer = 60

        self.camera_x = 0
        self.camera_y = 0
        self.camera_shake = 0

        self.combo_display = 0
        self.combo_display_timer = 0
        self.damage_numbers = []

        # Boss system
        self.bosses = []
        self.boss_health_bar = BossHealthBar()
        self.boss_spawn_timer = 120
        self.boss_quest_stage = 0

        # Legend features — player count, Doggo, dancing bots, admin abuse
        self.player_count = PlayerCount()
        self.doggo_legend = DoggoLegend()
        self.dancing_bots = DancingBots(12)
        self.admin_abuse = AdminAbuse()
        self.legend_open = False
        self.show_player_count = True

        # Go-live countdown (first launch + GO_LIVE_DAYS) — LIVE unlocks NPCs + Admin Abuse
        self.go_live_ts = get_go_live_ts(GO_LIVE_DAYS, FORCE_LIVE)
        self.is_live = bool(FORCE_LIVE) or time.time() >= self.go_live_ts
        self.go_live_synced = False
        if not FORCE_LIVE and not os.environ.get("PLAYTREE_OFFLINE"):
            threading.Thread(target=self._fetch_go_live, daemon=True).start()
        self._live_announced = False
        self.npcs = []
        self.dialogue_box = DialogueBox()
        self._admin_fx_prev = set()
        self._admin_timers = {"rain": 0.0, "mega": 0.0}
        self._touch_esc_rect = pygame.Rect(WIDTH - 76, 208, 66, 30)

        # Mount system
        self.mount = None
        self.mounts_unlocked = []
        self.selected_mount_type = 0
        self.mount_cycle = ["forest_stag", "crystal_wolf", "shadow_raven", "sky_drake", "ancient_beetle"]

        # Weapon particle trails
        self.trail_particles = []

        # Base building system
        self.base_builder = BaseBuilder()
        self.build_open = False

        # Battle pass system
        self.battle_pass = BattlePass()
        self.battle_pass_open = False

        # Multiplayer system
        self.multiplayer = MultiplayerManager()
        self.lobby_open = False

        # Locker / Dressup system
        self.locker_open = False
        self.cosmetics = {
            "hat": None, "body_color": None, "trail_color": None,
            "aura": None, "title": None, "pet_skin": None,
        }
        self.cosmetics_unlocked = {
            "hat": ["none", "crown", "hood", "helmet", "flower_crown", "shadow_mask"],
            "body_color": ["default", "crimson", "azure", "emerald", "shadow", "gold", "rainbow"],
            "trail_color": ["default", "fire", "ice", "shadow", "nature", "crystal"],
            "aura": ["none", "fire", "ice", "shadow", "nature", "crystal", "golden"],
            "title": ["none", "Warrior", "Explorer", "Champion", "Legendary"],
            "pet_skin": ["none", "crystal", "shadow", "golden", "rainbow"],
        }
        self.locker_tab = "hat"
        self.locker_selected = {}

        # Round system
        self.current_round = 1
        self.max_rounds = 4
        self.round_active = True
        self.round_enemies_killed = 0
        self.round_enemies_needed = 10
        self.round_boss_spawned = False
        self.round_boss_defeated = False
        self.round_transition = False
        self.round_transition_timer = 0
        self.round_data = {
            1: {"name": "The Forest Awakening", "boss": "root_titan",
                "story": "The corruption spreads through the ancient forest.\nYou must cleanse the Root Titan to restore balance.",
                "enemy_tiers": [0], "enemies_needed": 8},
            2: {"name": "Crystal Depths", "boss": "crystal_hydra",
                "story": "Deep in the crystal caves, a hydra stirs.\nIts crystal breath threatens to shatter everything.",
                "enemy_tiers": [1], "enemies_needed": 12},
            3: {"name": "Storm Peaks", "boss": "sky_guardian",
                "story": "High above the clouds, the Sky Guardian guards\nthe last source of pure light.",
                "enemy_tiers": [2], "enemies_needed": 15},
            4: {"name": "The Hollow Throne", "boss": "hollow_king",
                "story": "The final battle awaits. The Hollow King\ncommands the corruption itself. End this.",
                "enemy_tiers": [3, 4], "enemies_needed": 18},
        }

        # End credits
        self.credits_timer = 0
        self.credits_phase = 0
        self.credits_lines = []

        # Expanded enemies
        self.expanded_enemies = []
        self.expanded_enemy_timer = 0
        # Astro Toilets — Skibidi research (Trooper/Rocketeer/Detainer/Assailant/Juggernaut/Duchess/Mothership)
        self.astro_toilets = []
        self.astro_spawn_timer = 7

        # Music state
        self.current_music_type = None

        # Controller support
        self.controller = None
        self.controller_deadzone = 0.2
        self.controller_connected = False
        self._init_controller()

        # Touch controls for mobile
        self.touch_controls = TouchControls(WIDTH, HEIGHT)

        # TV mode detection
        self.tv_info = get_tv_info()
        self.tv_mode = self.tv_info.get("is_tv", False)
        if self.tv_mode:
            self.show_message(f"TV Mode: {self.tv_info.get('tv_type', 'Unknown')} detected", 3)

        # Skill tree
        self.skill_tree = None
        self.skill_tree_open = False

        # Achievements
        self.achievements = AchievementSystem(self.audio)

        # Fishing
        self.fishing = FishingMinigame(self.audio)
        self.fishing_open = False

        # Advanced weather (rain, snow, fog)
        self.adv_weather = AdvancedWeather()

        # Random events
        self.random_events = RandomEventManager()

        # Pet evolution
        self.pet_evolution = PetEvolution()

        # Enchanting
        self.enchanting = EnchantingSystem(self.audio)
        self.enchanting_open = False

        # Emotes
        self.current_emote = None
        self.emote_timer = 0

        # Day/night cycle
        self.day_time = 0.0
        self.is_night = False

        # Daily rewards
        self.daily_rewards = DailyRewards()
        self.daily_rewards_open = False
        self.daily_rewards_shown = False

        # Leaderboards
        self.leaderboards = LeaderboardSystem()
        self.leaderboards_open = False

        # Update Log
        self.update_log = UpdateLog()
        self.update_log_open = False

        # Screenshots
        self.screenshot_sys = ScreenshotSystem()

        # New Game+
        self.new_game_plus = NewGamePlus()
        self.ngp_active = False
        self.ngp_timer = 0
        self.ngp_activated = False

        # Pet manager
        self.pet_manager = PetManager()

        # Studio splash
        self.studio_splash = SplashScreen()
        _is_mobile = sys.platform in ("android", "ios") or hasattr(sys, "getandroidapilevel")
        if _is_mobile:
            self.studio_splash.timer = 7.0
            self.studio_splash.done = True

        # Menu music
        self.menu_music_playing = False

    def _init_controller(self):
        try:
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                self.controller_connected = True
            else:
                self.controller_connected = False
        except Exception:
            self.controller_connected = False

    def __getattr__(self, name):
        # FIX: prevent black-screen crash on missing flags
        if name.endswith("_hovered"):
            return -1
        if name.endswith("_open"):
            return False
        if name.endswith("_timer"):
            return 0
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def _close_all_overlays(self):
        self.inventory_open=False
        self.crafting_open=False
        self.shop_open=False
        self.marketplace_open=False
        self.profile_open=False
        self.locker_open=False
        self.lobby_open=False
        self.build_open=False
        self.battle_pass_open=False
        self.achievements_open=False
        self.daily_rewards_open=False
        self.leaderboards_open=False
        self.update_log_open=False
        self.screenshot_sys.share_menu_open=False

    def _check_controller_connection(self):
        try:
            count = pygame.joystick.get_count()
            if count > 0 and not self.controller_connected:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                self.controller_connected = True
                self.show_message("Xbox controller connected!", 2)
            elif count == 0 and self.controller_connected:
                self.controller_connected = False
                self.controller = None
                self.show_message("Controller disconnected", 2)
        except Exception:
            pass

    def _get_pressed_buttons(self):
        pressed = set()
        if not self.controller_connected or not self.controller:
            return pressed
        try:
            for i in range(min(self.controller.get_numbuttons(), 16)):
                if self.controller.get_button(i) and i in XBOX_BUTTON_MAP:
                    pressed.add(XBOX_BUTTON_MAP[i])
        except Exception:
            pass
        return pressed

    def _get_controller_input(self):
        if not self.controller_connected or not self.controller:
            return None
        try:
            lx = self.controller.get_axis(0)
            ly = self.controller.get_axis(1)
            rx = self.controller.get_axis(2)
            ry = self.controller.get_axis(3)
            if abs(lx) < self.controller_deadzone:
                lx = 0
            if abs(ly) < self.controller_deadzone:
                ly = 0
            if abs(rx) < self.controller_deadzone:
                rx = 0
            if abs(ry) < self.controller_deadzone:
                ry = 0
            buttons = {}
            for i in range(min(self.controller.get_numbuttons(), 16)):
                buttons[i] = self.controller.get_button(i)
            return {"lx": lx, "ly": ly, "rx": rx, "ry": ry, "buttons": buttons}
        except Exception:
            return None

    def start_new_game(self):
        spawn_x = WORLD_W // 2 + random.randint(-200, 200)
        spawn_y = WORLD_H // 2 + random.randint(-200, 200)
        self.player = Player(spawn_x, spawn_y, self.class_cycle[self.selected_class])
        self.player.name = self.character_name if self.character_name.strip() else "Wanderer"
        self.player.equipment = EquipmentSystem(self.player)
        self.world = World()
        self.hud = HUD(self.player)
        self.crafting = CraftingSystem(self.player)
        self.quests = QuestSystem(self.player)
        self.enemies = []
        self.creatures = []
        self.bosses = []
        self.expanded_enemies = []
        self.astro_toilets = []
        self.astro_spawn_timer = 7
        self.mount = None
        self.mounts_unlocked = []
        self.base_builder = BaseBuilder()
        self.battle_pass = BattlePass()
        self.skill_tree = SkillTree(self.class_cycle[self.selected_class], self.audio)
        self.achievements = AchievementSystem(self.audio)
        self.achievements_open = False
        self.tutorial = Tutorial(self.player, self.audio)
        self.day_time = 0.0
        self.is_night = False
        self.pet_manager = PetManager()
        self._spawn_initial_entities()
        self.npcs = []
        if self.is_live:
            self._spawn_live_npcs()
        self.state = GameState.ROUND_INTRO
        self.round_intro_timer = 0
        self.inventory_open = False
        self.crafting_open = False
        self.locker_open = False
        self.shop_open = False
        self.daily_rewards_open = False
        self.leaderboards_open = False
        self.update_log_open = False
        self.show_message("Awaken, " + self.player.name + ". The PlayTree calls to you...", 4)
        self.leaderboards.update_score("level", self.player.name, self.player.level)
        self.leaderboards.update_score("round", self.player.name, self.current_round)

    def _load_game(self):
        try:
            return self._load_game_impl()
        except Exception:
            import traceback
            traceback.print_exc()
            return False

    def _load_game_impl(self):
        data = load_game()
        if not data:
            self.show_message("No save data found!", 2)
            return False
        class_map = {c.value: c for c in self.class_cycle}
        pc = class_map.get(data.get("player_class", "Guardian"), PlayerClass.GUARDIAN)
        self.player = Player(data.get("x", WORLD_W // 2), data.get("y", WORLD_H // 2), pc)
        self.player.name = data.get("name", "Wanderer")
        self.player.level = data.get("level", 1)
        self.player.hp = data.get("hp", self.player.max_hp)
        self.player.max_hp = data.get("max_hp", self.player.max_hp)
        self.player.energy = data.get("energy", self.player.max_energy)
        self.player.max_energy = data.get("max_energy", self.player.max_energy)
        self.player.attack_power = data.get("attack_power", self.player.attack_power)
        self.player.defense = data.get("defense", self.player.defense)
        self.player.speed = data.get("speed", self.player.speed)
        self.player.xp = data.get("xp", 0)
        self.player.xp_to_next = data.get("xp_to_next", 100)
        self.player.weapon_id = data.get("weapon_id")
        if self.player.weapon_id and self.player.weapon_id in WEAPONS:
            self.player.weapon = dict(WEAPONS[self.player.weapon_id])
        inv = data.get("inventory", {})
        self.player.inventory["resources"] = inv.get("resources", {})
        self.player.inventory["items"] = inv.get("items", [])
        self.player.inventory["weapons"] = inv.get("weapons", [])
        self.player.inventory["enchants"] = inv.get("enchants", {})
        self.player.inventory["armor"] = inv.get("armor", [])
        self.player.creatures = data.get("creatures", [])
        self.player.quests = data.get("quests", [])
        # Equipment
        self.player.equipment = EquipmentSystem(self.player)
        eq_data = data.get("equipment", {})
        if eq_data:
            for slot in ("head", "chest", "legs", "boots"):
                aid = eq_data.get(slot)
                if aid and aid in ARMOR_TYPES:
                    self.player.equipment.slots[slot] = aid
            self.player.equipment._recalc()
        self.world = World()
        self.hud = HUD(self.player)
        self.crafting = CraftingSystem(self.player)
        self.enemies = []
        self.creatures = []
        self.bosses = []
        self.mounts_unlocked = data.get("mounts_unlocked", [])
        mount_type = data.get("mounted_type")
        if mount_type and mount_type in MOUNT_TYPES:
            self.mount = Mount(mount_type)
            self.mount.mounted = True
        else:
            self.mount = None
        # Load base buildings
        self.base_builder = BaseBuilder()
        for b_data in data.get("buildings", []):
            from src.base_building import Building
            b = Building(b_data.get("x", 0), b_data.get("y", 0), b_data.get("build_type", "wall"))
            b.hp = b_data.get("hp", b.hp)
            b.owner = b_data.get("owner", "")
            self.base_builder.buildings.append(b)
        # Load battle pass
        bp_data = data.get("battle_pass", {})
        self.battle_pass = BattlePass()
        if bp_data:
            self.battle_pass.tier = bp_data.get("tier", 1)
            self.battle_pass.xp = bp_data.get("xp", 0)
            self.battle_pass.xp_to_next = bp_data.get("xp_to_next", 100)
            self.battle_pass.claimed_rewards = bp_data.get("claimed_rewards", [])
            self.battle_pass.total_xp_earned = bp_data.get("total_xp_earned", 0)
        self.expanded_enemies = []
        self._spawn_initial_entities()
        # Load cosmetics
        self.cosmetics = data.get("wardrobe", data.get("cosmetics", {
            "hat": None, "body_color": None, "trail_color": None,
            "aura": None, "title": None, "pet_skin": None,
        }))
        self.locker_open = False
        self.shop_open = False
        self.lobby_open = False
        self.quests = QuestSystem(self.player)
        # Skill tree
        pc2 = self.class_cycle[self.selected_class] if self.selected_class < len(self.class_cycle) else pc
        self.skill_tree = SkillTree(pc2, self.audio)
        for sid, lvl in data.get("skill_levels", {}).items():
            if sid in self.skill_tree.skills:
                self.skill_tree.skills[sid]["level"] = min(lvl, self.skill_tree.skills[sid].get("max", 1))
        self.skill_tree.skill_points = data.get("skill_points", 3)
        # Achievements
        self.achievements = AchievementSystem(self.audio)
        saved_achs = data.get("achievements", {})
        if saved_achs:
            self.achievements.unlocked = saved_achs
        self.achievements_open = False
        self.tutorial = Tutorial(self.player, self.audio)
        self.current_round = data.get("current_round", 1)
        self.round_active = True
        self.round_enemies_killed = 0
        self.round_boss_spawned = False
        self.round_boss_defeated = False
        self.state = GameState.ROUND_INTRO
        self.round_intro_timer = 0
        self.new_game_plus = NewGamePlus()
        ngp_data = data.get("new_game_plus", {})
        if ngp_data:
            self.new_game_plus.load_save_data(ngp_data)
            self.ngp_activated = self.new_game_plus.active
        self.leaderboards = LeaderboardSystem()
        lb_data = data.get("leaderboards", {})
        if lb_data:
            self.leaderboards.data = lb_data
        self.pet_manager = PetManager()
        self.npcs = []
        if self.is_live:
            self._spawn_live_npcs()
        self.show_message("Welcome back, " + self.player.name + "!", 3)
        return True

    def _spawn_initial_entities(self):
        for _ in range(8):
            ex = random.randint(100, WORLD_W - 100)
            ey = random.randint(100, WORLD_H - 100)
            self.enemies.append(Enemy(ex, ey, random.randint(0, 3)))
        for _ in range(4):
            ex = random.randint(100, WORLD_W - 100)
            ey = random.randint(100, WORLD_H - 100)
            self.expanded_enemies.append(ExpandedEnemy(ex, ey))
        for _ in range(5):
            cx = random.randint(100, WORLD_W - 100)
            cy = random.randint(100, WORLD_H - 100)
            self.creatures.append(Creature(cx, cy, random.randint(0, 4)))

    def show_message(self, text, duration=3):
        self.message = text
        self.message_timer = duration

    def _any_overlay_open(self):
        return any([
            self.inventory_open, self.crafting_open, self.shop_open, self.locker_open,
            self.profile_open, self.marketplace_open, self.lobby_open, self.build_open,
            self.battle_pass_open, self.achievements_open, self.daily_rewards_open,
            self.leaderboards_open, self.update_log_open,
            getattr(self.screenshot_sys, 'share_menu_open', False),
        ])

    def go_live_str(self):
        if self.is_live:
            return "LIVE"
        remaining = max(0, self.go_live_ts - time.time())
        d = int(remaining // 86400)
        h = int(remaining % 86400 // 3600)
        m = int(remaining % 3600 // 60)
        s = int(remaining % 60)
        return f"{d}d {h:02d}:{m:02d}:{s:02d}"

    def _fetch_go_live(self):
        """Pull the go-live instant from the PlayTree GitHub page so the
        in-game countdown always matches the countdown on the website."""
        import urllib.request
        urls = [
            "https://raw.githubusercontent.com/GoStudios-Real/PlayTree/master/index.html",
            "https://gostudios-real.github.io/PlayTree/",
        ]
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": f"PLAYTREE/{VERSION}"})
                with urllib.request.urlopen(req, timeout=5) as resp:
                    html = resp.read().decode("utf-8", "ignore")
                ts = self._parse_go_live(html)
                if ts:
                    self._adopt_go_live(ts)
                    return
            except Exception:
                continue

    @staticmethod
    def _parse_go_live(html):
        import re
        import datetime
        m = re.search(r'name="playtree-go-live"\s+content="([^"]+)"', html)
        if not m:
            m = re.search(r'GO_LIVE_ISO\s*=\s*"([^"]+)"', html)
        if not m:
            return None
        try:
            return datetime.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).timestamp()
        except Exception:
            return None

    def _adopt_go_live(self, ts):
        if not ts or ts <= 0:
            return
        if self.is_live:
            return
        self.go_live_ts = float(ts)
        self.go_live_synced = True
        try:
            cfg = load_settings() or {}
            if cfg.get("go_live_ts") != float(ts):
                cfg["go_live_ts"] = float(ts)
                cfg["go_live_source"] = "github_page"
                save_settings(cfg)
        except Exception:
            pass

    def _check_for_updates(self):
        """Query GitHub for the latest commit — works in the packaged EXE (stdlib only)."""
        ul = self.update_log
        ul.status_line = "Checking GitHub..."
        try:
            import json
            import urllib.request
            req = urllib.request.Request(
                "https://api.github.com/repos/GoStudios-Real/PlayTree/commits?per_page=1",
                headers={"User-Agent": f"PLAYTREE/{VERSION}"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
            c = data[0]
            msg = (c.get("commit", {}).get("message", "") or "").splitlines()[0][:60]
            date = (c.get("commit", {}).get("committer", {}).get("date", "") or "")[:10]
            sha = (c.get("sha", "") or "")[:7]
            ul.status_line = f"GitHub latest: {sha} — {msg} ({date})"
            self.audio.play("collect")
        except Exception:
            ul.status_line = f"Could not reach GitHub — running v{VERSION} (offline?)"
            self.audio.play("menu_hover")

    def _spawn_live_npcs(self):
        if self.npcs:
            return
        if self.player:
            cx, cy = self.player.x, self.player.y
        else:
            cx, cy = WORLD_W // 2, WORLD_H // 2
        types = list(NPC_TYPES.keys())
        for i, npc_type in enumerate(types):
            angle = (i / max(1, len(types))) * math.tau
            dist = 130 + (i % 3) * 70
            nx = max(60, min(WORLD_W - 60, cx + math.cos(angle) * dist))
            ny = max(60, min(WORLD_H - 60, cy + math.sin(angle) * dist))
            self.npcs.append(NPC(nx, ny, npc_type))

    def _go_live_event(self):
        if self.is_live:
            return
        self.is_live = True
        self._live_announced = True
        self.show_message("PLAYTREE IS LIVE!!!", 6)
        self.admin_abuse.log.append("[LIVE] PlayTree went LIVE — ADMIN ABUSE AUTHORIZED")
        self.admin_abuse.chat.append(("WILLOW", "WE'RE LIVE!!! ADMIN ABUSE GO!"))
        self.admin_abuse.chat.append(("RHYS", "Villagers are here. Time to cause problems."))
        self.audio.play("menu_confirm")
        self._spawn_live_npcs()
        # celebration
        try:
            self.admin_abuse.trigger("rain")
            self.admin_abuse.trigger("disco")
        except Exception:
            pass
        if self.state == GameState.MAIN_MENU or self.state == GameState.PLAYING:
            self.admin_abuse.open = True

    def _apply_admin_abuse_effects(self, dt):
        fx = getattr(self.admin_abuse, "effects", {})
        active = set(fx.keys())
        prev = self._admin_fx_prev
        player = self.player

        # on-activate / on-expire handlers
        if "willow" in active and "willow" not in prev and player:
            self._willow_orig_dmg = player.stats.get("damage", 10)
            player.stats["damage"] = self._willow_orig_dmg * 3
        if "willow" not in active and "willow" in prev and player and hasattr(self, "_willow_orig_dmg"):
            player.stats["damage"] = self._willow_orig_dmg
        if "size" in active and "size" not in prev:
            for e in self.enemies:
                if not hasattr(e, "_orig_size"):
                    e._orig_size = e.size
                e.size = e._orig_size * 2
        if "size" not in active and "size" in prev:
            for e in self.enemies:
                if hasattr(e, "_orig_size"):
                    e.size = e._orig_size
        if "tpp" in active and "tpp" not in prev and player:
            for e in self.enemies[:8]:
                ang = random.uniform(0, math.tau)
                e.x = player.x + math.cos(ang) * 160
                e.y = player.y + math.sin(ang) * 160
            self.show_message("TPP ALL! Enemies recalled!", 2)
        if "raid" in active and "raid" not in prev and player:
            for _ in range(6):
                ang = random.uniform(0, math.tau)
                ex = max(50, min(WORLD_W - 50, player.x + math.cos(ang) * 500))
                ey = max(50, min(WORLD_H - 50, player.y + math.sin(ang) * 500))
                self.enemies.append(Enemy(ex, ey, random.randint(0, 3)))
            self.show_message("ASTRO RAID! Hostiles inbound!", 3)
        if "spawn" in active and "spawn" not in prev and player:
            for i in range(4):
                npc_type = random.choice(list(NPC_TYPES.keys()))
                ang = random.uniform(0, math.tau)
                self.npcs.append(NPC(player.x + math.cos(ang) * 140,
                                     player.y + math.sin(ang) * 140, npc_type))
            self.show_message("SPAWN BOTS! More villagers!", 3)
        if "boss" in active and "boss" not in prev:
            self._spawn_round_boss("root_titan")
        if "kick" in active and "kick" not in prev and self.enemies:
            victim = random.choice(self.enemies)
            self.enemies.remove(victim)
            self.show_message("KICK BOT! One less enemy.", 2)
        if "god" in active and player:
            player.invincible = max(getattr(player, "invincible", 0), 0.3)
        if "freeze" in active and "freeze" not in prev:
            self.show_message("FREEZE ALL! Time stopped.", 2)

        # continuous effects
        if "rain" in active and player:
            self._admin_timers["rain"] += dt
            if self._admin_timers["rain"] >= 0.15:
                self._admin_timers["rain"] = 0.0
                ang = random.uniform(0, math.tau)
                dist = random.randint(60, 360)
                self._drop_gold(max(50, player.x + math.cos(ang) * dist),
                                max(50, player.y + math.sin(ang) * dist))
        if "spin" in active and player:
            player.facing += dt * 12
        if "dance" in active and player:
            player.facing += dt * 7
            self.camera_y += math.sin(self.time * 14) * 2
        if "mega" in active and player:
            self._admin_timers["mega"] += dt
            if self._admin_timers["mega"] >= 0.7:
                self._admin_timers["mega"] = 0.0
                nx = max(50, min(WORLD_W - 50, player.x + math.cos(player.facing) * 320))
                ny = max(50, min(WORLD_H - 50, player.y + math.sin(player.facing) * 320))
                player.particles.burst(player.x, player.y, GREEN_GLOW, 14, 4, 30, 4)
                player.x, player.y = nx, ny
                self.camera_shake = 3

        self._admin_fx_prev = active

    def _convert_finger_to_mouse(self, events):
        # SDL sometimes also emulates mouse events from touch — collect them first so
        # we don't synthesize a duplicate click (which would double-toggle buttons).
        native = {"down": [], "up": [], "motion": []}
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", 0) == 1:
                native["down"].append(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and getattr(event, "button", 0) == 1:
                native["up"].append(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                native["motion"].append(event.pos)

        def _has_native(kind, fx, fy, tol=4):
            return any(abs(px - fx) <= tol and abs(py - fy) <= tol
                       for px, py in native[kind])

        converted = []
        for event in events:
            if event.type == pygame.FINGERDOWN:
                surf = pygame.display.get_surface()
                w = surf.get_width() if surf else WIDTH
                h = surf.get_height() if surf else HEIGHT
                mx = int(event.x * w)
                my = int(event.y * h)
                converted.append(event)
                if not _has_native("down", mx, my):
                    converted.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(mx, my)))
            elif event.type == pygame.FINGERUP:
                surf = pygame.display.get_surface()
                w = surf.get_width() if surf else WIDTH
                h = surf.get_height() if surf else HEIGHT
                mx = int(event.x * w)
                my = int(event.y * h)
                converted.append(event)
                if not _has_native("up", mx, my):
                    converted.append(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=(mx, my)))
            elif event.type == pygame.FINGERMOTION:
                surf = pygame.display.get_surface()
                w = surf.get_width() if surf else WIDTH
                h = surf.get_height() if surf else HEIGHT
                mx = int(event.x * w)
                my = int(event.y * h)
                converted.append(event)
                if not _has_native("motion", mx, my):
                    converted.append(pygame.event.Event(pygame.MOUSEMOTION, pos=(mx, my), rel=(0, 0), buttons=(1, 0, 0)))
            else:
                converted.append(event)
        return converted

    def handle_events(self, events):
        events = self._convert_finger_to_mouse(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return

            # Global hotkeys — Legend (L) and Admin Abuse (Shift+A / F9)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F9:
                    if not self.is_live:
                        self.show_message(f"Admin Abuse unlocks when PlayTree goes LIVE — {self.go_live_str()}", 3)
                        continue
                    self.admin_abuse.open = not self.admin_abuse.open
                    self.legend_open = False
                    continue
                if event.key == pygame.K_a and (getattr(event, "mod", 0) & pygame.KMOD_SHIFT):
                    if self.state in (GameState.MAIN_MENU, GameState.PLAYING, GameState.PAUSED) and not self.typing_name:
                        if not self.is_live:
                            self.show_message(f"Admin Abuse unlocks when PlayTree goes LIVE — {self.go_live_str()}", 3)
                            continue
                        self.admin_abuse.open = not self.admin_abuse.open
                        self.legend_open = False
                        continue
                if event.key == pygame.K_l and not self.admin_abuse.open:
                    if self.state in (GameState.MAIN_MENU, GameState.PLAYING, GameState.PAUSED):
                        self.legend_open = not self.legend_open
                        continue
                if self.legend_open:
                    if event.key in (pygame.K_ESCAPE, pygame.K_l):
                        self.legend_open = False
                        continue
                if self.admin_abuse.open:
                    if event.key == pygame.K_ESCAPE:
                        self.admin_abuse.open = False
                        continue
                    # Number keys 1-9 trigger abuse actions
                    num_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
                    if event.key in num_keys:
                        idx = num_keys.index(event.key)
                        if idx < len(self.admin_abuse.ACTIONS):
                            name = self.admin_abuse.trigger(self.admin_abuse.ACTIONS[idx][1])
                            self.show_message(f"ADMIN ABUSE: {name}!", 2)
                        continue

            # Block other input while legend/abuse overlays are open
            if self.admin_abuse.open:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Hit-test abuse buttons
                    mx, my = event.pos
                    pw, ph = 760, 540
                    rect = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2, pw, ph)
                    # Buttons start after title (80) + sub (26) + log (140+12) = ~258
                    y0 = rect.y + 14 + 38 + 26 + 140 + 12
                    cols = 4
                    bw = (pw - 50) // cols
                    bh = 38
                    gap = 8
                    for i, (label, aid) in enumerate(self.admin_abuse.ACTIONS):
                        row, col = divmod(i, cols)
                        bx = rect.x + 16 + col * (bw + gap)
                        by = y0 + row * (bh + gap)
                        brect = pygame.Rect(bx, by, bw, bh)
                        if brect.collidepoint(mx, my):
                            name = self.admin_abuse.trigger(aid)
                            self.show_message(f"ADMIN ABUSE: {name}!", 2)
                            break
                    continue
                continue
            if self.legend_open:
                continue

            # Touch-friendly ESC button shown while gameplay overlays are open
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    and self.state == GameState.PLAYING and self._any_overlay_open()
                    and self._touch_esc_rect.collidepoint(event.pos)):
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, unicode="", mod=0))
                continue

            if self.state == GameState.LOGIN:
                result = self.account.handle_event(event)
                if result == "logged_in":
                    self.state = GameState.MAIN_MENU
                elif result == "back":
                    if has_save() or self.player:
                        self.state = GameState.MAIN_MENU
                    else:
                        self.running = False

            elif self.state == GameState.MAIN_MENU:
                if self.update_log_open:
                    ul_result = self.update_log.handle_event(event)
                    if ul_result == "close":
                        self.update_log_open = False
                    elif ul_result == "check_updates":
                        self._check_for_updates()
                    elif ul_result == "open_github":
                        try:
                            import webbrowser
                            webbrowser.open("https://github.com/GoStudios-Real/PlayTree")
                            self.update_log.status_line = "Opened the PlayTree GitHub page in your browser"
                            self.audio.play("menu_select")
                        except Exception as exc:
                            self.update_log.status_line = f"Could not open browser: {exc}"
                    continue
                # GAMES panel modal (main menu) — swallows input until closed
                if self.games_open:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.games_open = False
                            self.audio.play("menu_select")
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            self.games_selected = (self.games_selected - 1) % len(GAMES_CATALOG)
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.games_selected = (self.games_selected + 1) % len(GAMES_CATALOG)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_g):
                            grect = self._games_rects.get("GET")
                            if grect:
                                self._handle_games_click(grect.center)
                        continue
                    if event.type == pygame.MOUSEMOTION:
                        for gi in range(len(GAMES_CATALOG)):
                            gr = self._games_rects.get("row%d" % gi)
                            if gr and gr.collidepoint(event.pos):
                                self.games_selected = gi
                                break
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self._handle_games_click(event.pos)
                        continue
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 1:
                            self.games_open = False
                        else:
                            grect = self._games_rects.get("GET")
                            if grect:
                                self._handle_games_click(grect.center)
                        continue
                    continue
                result = self.main_menu.handle_event(event)
                if result == "character_create":
                    self.state = GameState.CHARACTER_CREATE
                    user_data = self.account.get_user_data()
                    self.name_input = user_data["name"] if user_data else ""
                    self.typing_name = True
                elif result == "continue":
                    if not self._load_game():
                        pass
                    # _load_game handles message
                elif result == "locker":
                    if self._load_game():
                        self.locker_open = True
                        self.state = GameState.PLAYING
                    else:
                        self.show_message("No save to open locker!", 2)
                elif result == "store":
                    if self._load_game():
                        self.shop_open = True
                        self.state = GameState.PLAYING
                    else:
                        self.show_message("No save to open store!", 2)
                elif result == "marketplace":
                    if self.save_exists and self._load_game():
                        self.marketplace_open = True
                        self.state = GameState.PLAYING
                    else:
                        self.show_message("No save yet — press Play first!", 2)
                elif result == "profile":
                    if self.save_exists and self._load_game():
                        self.profile_open = True
                        self.state = GameState.PLAYING
                    else:
                        self.show_message("No save yet — press Play first!", 2)
                elif result == "settings":
                    self.state = GameState.SETTINGS
                    self.settings_hover = -1
                elif result == "games":
                    self.games_open = True
                    self.games_selected = 0
                    self.games_status = "Select a game — GET downloads it free"
                    self.audio.play("menu_select")
                elif result == "signin":
                    self.state = GameState.LOGIN
                    self.account.state = "login"
                    self.account.input_email = ""
                    self.account.input_password = ""
                    self.account.error_msg = ""
                elif result == "signup":
                    self.state = GameState.LOGIN
                    self.account.state = "register"
                    self.account.input_email = ""
                    self.account.input_password = ""
                    self.account.input_name = ""
                    self.account.input_confirm = ""
                    self.account.error_msg = ""
                elif result == "daily_rewards":
                    self.daily_rewards_open = True
                elif result == "leaderboards":
                    self.leaderboards_open = True
                elif result == "update_log":
                    self.update_log_open = True
                elif result == "quit":
                    self.running = False

            elif self.state == GameState.CHARACTER_CREATE:
                self._handle_character_create(event)

            elif self.state == GameState.PLAYING:
                # FIX: corrupted save — handle ESC / buttons before other overlays
                if not self.world or not self.player:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = GameState.MAIN_MENU
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if hasattr(self, '_corrupt_new_rect') and self._corrupt_new_rect.collidepoint(event.pos):
                            try:
                                from src.save_system import delete_save
                                for s in range(5):
                                    try: delete_save(s)
                                    except: pass
                                import os
                                old = os.path.join(os.path.expanduser("~"), ".playtree", "save.json")
                                if os.path.exists(old):
                                    try: os.remove(old)
                                    except: pass
                            except: pass
                            self.start_new_game()
                            continue
                        if hasattr(self, '_corrupt_menu_rect') and self._corrupt_menu_rect.collidepoint(event.pos):
                            self.state = GameState.MAIN_MENU
                            continue
                    # also allow touch to close
                    continue
                if self.profile_open:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.profile_open = False
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if hasattr(self, '_profile_close_rect') and self._profile_close_rect.collidepoint(event.pos):
                            self.profile_open = False
                            continue
                        if hasattr(self, '_profile_signout_rect') and self._profile_signout_rect.collidepoint(event.pos):
                            self.account.logout()
                            self.profile_open = False
                            self.state = GameState.MAIN_MENU
                            continue
                    continue
                if self.marketplace_open:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.marketplace_open = False
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if hasattr(self, '_market_close_rect') and self._market_close_rect.collidepoint(event.pos):
                            self.marketplace_open = False
                            continue
                        for vname, vrect in getattr(self, '_market_view_rects', []):
                            if vrect.collidepoint(event.pos):
                                self.show_message(f"{vname} — free! 0 Minecoins", 2)
                                self.audio.play("menu_select")
                                continue
                    continue
                if self.daily_rewards_open:
                    dr_result = self.daily_rewards.handle_event(event)
                    if dr_result == "close":
                        self.daily_rewards_open = False
                    elif dr_result and isinstance(dr_result, dict):
                        self._apply_daily_reward(dr_result)
                    continue
                if self.leaderboards_open:
                    lb_result = self.leaderboards.handle_event(event)
                    if lb_result == "close":
                        self.leaderboards_open = False
                    continue
                if self.screenshot_sys.share_menu_open:
                    ss_result = self.screenshot_sys.handle_share_click(
                        event.pos if event.type == pygame.MOUSEBUTTONDOWN else (0, 0))
                    if ss_result == "closed":
                        self.screenshot_sys.share_menu_open = False
                    continue
                if self.touch_controls.enabled:
                    self.touch_controls.handle_event(event)
                if self.multiplayer.typing_chat:
                    self.multiplayer.handle_event(event)
                else:
                    self._handle_gameplay(event)

            elif self.state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                    self.audio.play("menu_confirm")
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    self.state = GameState.SETTINGS
                    self.settings_hover = -1
                    self.audio.play("menu_select")
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    rects = getattr(self, "_pause_rects", {})
                    if rects.get("resume", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        self.state = GameState.PLAYING
                        self.audio.play("menu_confirm")
                    elif rects.get("settings", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        self.state = GameState.SETTINGS
                        self.settings_hover = -1
                        self.audio.play("menu_select")
                    elif rects.get("menu", pygame.Rect(0, 0, 0, 0)).collidepoint(event.pos):
                        self.state = GameState.MAIN_MENU
                        self.audio.play("menu_select")
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 9:  # Start
                        self.state = GameState.PLAYING
                    elif event.button == 1:  # B
                        self.state = GameState.MAIN_MENU

            elif self.state == GameState.ROUND_INTRO:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = GameState.PLAYING
                    self.round_active = True
                    self.round_enemies_killed = 0
                    self.round_boss_spawned = False
                    self.round_boss_defeated = False
                    rd = self.round_data.get(self.current_round, {})
                    self.show_message(f"Round {self.current_round}: {rd.get('name', 'Unknown')}", 3)
                    self.audio.play("menu_confirm")
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A
                        self.state = GameState.PLAYING
                        self.round_active = True
                        self.round_enemies_killed = 0
                        self.round_boss_spawned = False
                        self.round_boss_defeated = False
                        rd = self.round_data.get(self.current_round, {})
                        self.show_message(f"Round {self.current_round}: {rd.get('name', 'Unknown')}", 3)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.round_intro_timer > 1:
                        self.state = GameState.PLAYING
                        self.round_active = True
                        self.round_enemies_killed = 0
                        self.round_boss_spawned = False
                        self.round_boss_defeated = False
                        self.audio.play("menu_confirm")

            elif self.state == GameState.END_CREDITS:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.credits_timer > 3:
                    self.state = GameState.MAIN_MENU
                elif event.type == pygame.JOYBUTTONDOWN and self.credits_timer > 3:
                    self.state = GameState.MAIN_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN and self.credits_timer > 3:
                    self.state = GameState.MAIN_MENU

            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.state = GameState.MAIN_MENU
                    self.audio.play("menu_confirm")
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # A
                        self.state = GameState.MAIN_MENU
                        self.audio.play("menu_confirm")
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.state = GameState.MAIN_MENU
                    self.audio.play("menu_confirm")

            elif self.state == GameState.SETTINGS:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING if self.player else GameState.MAIN_MENU
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_settings_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_settings_hover(event.pos)

            elif self.state == GameState.SHOP:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_shop_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_shop_hover(event.pos)

    def _handle_character_create(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.name_input.strip():
                    self.character_name = self.name_input.strip()
                self.audio.play("menu_confirm")
                self.start_new_game()
            elif event.key == pygame.K_LEFT:
                self.selected_class = (self.selected_class - 1) % len(self.class_cycle)
                self.audio.play("menu_hover")
            elif event.key == pygame.K_RIGHT:
                self.selected_class = (self.selected_class + 1) % len(self.class_cycle)
                self.audio.play("menu_hover")
            elif event.key == pygame.K_BACKSPACE and self.typing_name:
                self.name_input = self.name_input[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU
            elif self.typing_name and event.unicode.isprintable() and len(self.name_input) < 16:
                self.name_input += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < 480:
                if mx < WIDTH // 2:
                    self.selected_class = (self.selected_class - 1) % len(self.class_cycle)
                    self.audio.play("menu_hover")
                else:
                    self.selected_class = (self.selected_class + 1) % len(self.class_cycle)
                    self.audio.play("menu_hover")
            elif 550 <= my <= 600:
                self.typing_name = True
                self.state = GameState.CHARACTER_CREATE
            elif 510 <= my <= 545:
                if self.name_input.strip():
                    self.character_name = self.name_input.strip()
                self.audio.play("menu_confirm")
                self.start_new_game()
            elif my > HEIGHT - 40 and mx < 150:
                self.state = GameState.MAIN_MENU

    def _handle_gameplay(self, event):
        if event.type == pygame.MOUSEMOTION and self.shop_open:
            self._handle_shop_hover(event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self._try_interact()
            elif event.key == pygame.K_i:
                self.inventory_open = not self.inventory_open
                self.crafting_open = False
            elif event.key == pygame.K_c:
                self.crafting_open = not self.crafting_open
                self.inventory_open = False
            elif event.key == pygame.K_q and not self.crafting_open:
                if self.mount and self.mount.mounted:
                    self.mount.use_ability()
                else:
                    self._use_skill("special")
            elif event.key == pygame.K_TAB:
                self._try_tame_nearest()
            elif event.key == pygame.K_ESCAPE:
                if hasattr(self, 'tutorial') and self.tutorial and not self.tutorial.done and self.tutorial.visible:
                    self.tutorial.skip()
                elif self.dialogue_box.active:
                    self.dialogue_box.advance()
                elif self.achievements_open:
                    self.achievements_open = False
                elif self.shop_open:
                    self.shop_open = False
                    self.shop_hovered = -1
                elif self.battle_pass_open:
                    self.battle_pass_open = False
                elif self.build_open:
                    self.build_open = False
                    self.base_builder.build_mode = False
                elif self.inventory_open or self.crafting_open or self.locker_open or self.lobby_open:
                    self.inventory_open = False
                    self.crafting_open = False
                    self.locker_open = False
                    self.lobby_open = False
                else:
                    self.state = GameState.PAUSED
            elif event.key == pygame.K_h:
                self._use_health_potion()
            elif event.key == pygame.K_u:
                self.achievements_open = not self.achievements_open
                if self.achievements_open and hasattr(self, 'achievements') and self.achievements:
                    self.achievements.save()
            elif event.key == pygame.K_t:
                if self.multiplayer.connected:
                    self.multiplayer.typing_chat = True
                    self.multiplayer.chat_visible = True
                elif self.storm.active:
                    self.storm.stop()
                    self.show_message("Storm cleared.", 2)
                else:
                    self.storm.start(25, 0.9)
                    self.show_message("Storm summoned!", 2)
            elif event.key == pygame.K_1:
                self._switch_weapon("sword_iron")
            elif event.key == pygame.K_2:
                self._switch_weapon("sword_crystal")
            elif event.key == pygame.K_3:
                self._switch_weapon("sword_shadow")
            elif event.key == pygame.K_4:
                self._switch_weapon("sword_flame")
            elif event.key == pygame.K_5:
                self._switch_weapon("gun_crystal")
            elif event.key == pygame.K_6:
                self._switch_weapon("gun_root")
            elif event.key == pygame.K_7:
                self._switch_weapon("gun_tech")
            elif event.key == pygame.K_8:
                self._switch_weapon("gun_shadow")
            elif event.key == pygame.K_0:
                self.player.unequip_weapon()
                self.show_message("Equipped: Fists", 1)
            elif event.key == pygame.K_s and not self.crafting_open:
                was=self.shop_open
                self._close_all_overlays()
                self.shop_open = not was
            elif event.key == pygame.K_F5:
                save_game(self.player, self)
                self.show_message("Game saved!", 2)
            elif event.key == pygame.K_m:
                self._try_mount()
            elif event.key == pygame.K_r and self.mount and self.mount.mounted:
                self.mount.sprint(True)
            elif event.key == pygame.K_n:
                self._cycle_mount_selection(-1)
            elif event.key == pygame.K_b:
                self._cycle_mount_selection(1)
            elif event.key == pygame.K_v:
                self.build_open = not self.build_open
                self.base_builder.build_mode = self.build_open
                if self.build_open:
                    if self.controller_connected:
                        self.show_message("BUILD MODE: A to place, B to exit", 3)
                    else:
                        self.show_message("BUILD MODE: Click to place, V to exit", 3)
            elif event.key == pygame.K_F1:
                was3=self.battle_pass_open
                self._close_all_overlays()
                self.battle_pass_open = not was3
            elif event.key == pygame.K_p:
                was2=self.lobby_open
                self._close_all_overlays()
                self.lobby_open = not was2
                self.audio.play("tab_switch")
            elif event.key == pygame.K_F9:
                if self.multiplayer.connected:
                    self.multiplayer.disconnect()
                    self.audio.play("lobby_disconnect")
                    self.show_message("Disconnected from server", 2)
                else:
                    self.multiplayer.host_game(self.player.name)
                    self.audio.play("lobby_connect")
                    self.show_message("Hosting game on port 7777...", 3)
            elif event.key == pygame.K_F10:
                self.daily_rewards_open = not self.daily_rewards_open
                self.audio.play("tab_switch")
            elif event.key == pygame.K_F11:
                self.leaderboards_open = not self.leaderboards_open
                self.audio.play("tab_switch")
            elif event.key == pygame.K_F12:
                path = self.screenshot_sys.take_screenshot(self.screen)
                if path:
                    self.show_message(f"Screenshot: {path}", 3)
                    self.audio.play("screenshot")
            elif event.key == pygame.K_PAGEUP:
                self.pet_manager.cycle_pet(self.player.creatures)
                self.show_message("Pet cycled!", 1)
                self.audio.play("menu_hover")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_r and self.mount:
                self.mount.sprint(False)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.dialogue_box.active:
                self.dialogue_box.advance()
            elif self.build_open:
                self.base_builder.handle_click(event.pos[0], event.pos[1],
                                               int(self.camera_x), int(self.camera_y), self.player)
                self.audio.play("place")
            elif self.shop_open:
                self._handle_shop_click(event.pos)
            elif self.locker_open:
                self._handle_locker_click(event.pos)
            elif self.lobby_open:
                self._handle_lobby_click(event.pos)
            elif self.crafting_open:
                self._handle_craft_click(event.pos)
            elif self.battle_pass_open:
                reward = self.battle_pass.handle_click(event.pos[0], event.pos[1], self.player)
                if reward:
                    self.show_message(f"Claimed: {reward['name']}!", 3)
                    self.audio.play("collect")

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:  # B button - close overlays
                if self.achievements_open:
                    self.achievements_open = False
                elif self.inventory_open or self.crafting_open or self.locker_open or self.lobby_open:
                    self.inventory_open = False
                    self.crafting_open = False
                    self.locker_open = False
                    self.lobby_open = False
                elif self.shop_open:
                    self.shop_open = False
                    self.shop_hovered = -1
                elif self.build_open:
                    self.build_open = False
                    self.base_builder.build_mode = False
                elif self.battle_pass_open:
                    self.battle_pass_open = False
                elif self.state == GameState.PLAYING:
                    self.state = GameState.PAUSED
            elif event.button == 2:  # X button - inventory
                self.inventory_open = not self.inventory_open
                self.crafting_open = False
            elif event.button == 3:  # Y button - achievements
                self.achievements_open = not self.achievements_open
                if self.achievements_open and hasattr(self, 'achievements') and self.achievements:
                    self.achievements.save()
            elif event.button == 7:  # RT - shop
                if not self.crafting_open:
                    was=self.shop_open
                    self._close_all_overlays()
                    self.shop_open = not was
            elif event.button == 4:  # LB - locker
                was4=self.locker_open
                self._close_all_overlays()
                self.locker_open = not was4

    def _try_interact(self):
        # Dialogue first — advance or dismiss
        if self.dialogue_box.active:
            self.dialogue_box.advance()
            return

        # Go-live villagers (spawned when the countdown hits zero)
        if self.player:
            for npc in self.npcs:
                if npc.is_in_range(self.player.x, self.player.y):
                    line = npc.get_dialogue()
                    if line:
                        self.dialogue_box.start(npc.name, line)
                        self.audio.play("menu_hover")
                        return

        # Check bosses
        for boss in self.bosses:
            dx = boss.x - self.player.x
            dy = boss.y - self.player.y
            if math.sqrt(dx * dx + dy * dy) < 60:
                self.show_message(f"{boss.name} glares at you menacingly!", 3)
                return

        self.show_message("You sense the PlayTree energy flowing through this land...", 2)
        self.player.particles.burst(self.player.x, self.player.y, GREEN_GLOW, 10, 3, 25, 4)

    def _try_mount(self):
        if self.mount and self.mount.mounted:
            self.mount.mounted = False
            self.show_message(f"Dismounted {self.mount.name}", 2)
            self.audio.play("dodge")
            return

        mount_type = self.mount_cycle[self.selected_mount_type]
        if mount_type in self.mounts_unlocked:
            self.mount = Mount(mount_type)
            self.mount.mounted = True
            self.player.speed = self.player.stats["speed"] * self.mount.base_speed / 4
            self.show_message(f"Mounted {self.mount.name}!", 2)
            self.audio.play("collect")
        else:
            # Auto-unlock first mount if none unlocked
            if not self.mounts_unlocked:
                self.mounts_unlocked.append("forest_stag")
                self.mount = Mount("forest_stag")
                self.mount.mounted = True
                self.player.speed = self.player.stats["speed"] * self.mount.base_speed / 4
                self.show_message("Unlocked and mounted Forest Stag!", 3)
                self.audio.play("collect")
            else:
                self.show_message("Mount not unlocked yet!", 2)

    def _cycle_mount_selection(self, direction):
        self.selected_mount_type = (self.selected_mount_type + direction) % len(self.mount_cycle)
        mount_type = self.mount_cycle[self.selected_mount_type]
        unlocked = mount_type in self.mounts_unlocked
        status = " (UNLOCKED)" if unlocked else " (LOCKED)"
        self.show_message(f"Mount: {MOUNT_TYPES[mount_type]['name']}{status}", 2)

    def _try_tame_nearest(self):
        for creature in self.creatures:
            dx = creature.x - self.player.x
            dy = creature.y - self.player.y
            if dx * dx + dy * dy < 60 * 60 and not creature.tamed:
                if self.player.inventory["resources"].get("Tree Energy", 0) >= 3:
                    self.player.inventory["resources"]["Tree Energy"] = self.player.inventory["resources"].get(
                        "Tree Energy", 0) - 3
                    creature.tame()
                    self.player.add_creature({
                        "name": creature.name,
                        "color": creature.color,
                        "type": creature.type,
                        "level": 1
                    })
                    self.show_message(f"You tamed a {creature.name}!", 3)
                    self.quests.update_progress("tame", "creature")
                    self.audio.play("collect")
                else:
                    self.show_message("Need 3 Tree Energy to tame!", 2)
                return
        self.show_message("No wild creatures nearby...", 2)

    def _use_skill(self, skill_name):
        if skill_name not in self.player.skills:
            return
        skill = self.player.skills[skill_name]
        if skill["cooldown"] > 0 or self.player.energy < skill["energy_cost"]:
            return
        skill["cooldown"] = skill["max_cd"]
        self.player.energy -= skill["energy_cost"]

        if skill_name == "attack":
            self.player._attack(pygame.mouse.get_pos(), self.camera_x, self.camera_y)
            hits = CombatSystem.check_attack(self.player.x, self.player.y, 35,
                                             self.player.facing, self.enemies, self.player.attack_power)
            for enemy, dead in hits:
                if dead:
                    self.player.add_xp(25)
                    self.quests.update_progress("defeat", "enemy")
                    self._drop_gold(enemy.x, enemy.y)
                    self.enemies.remove(enemy)
                    self.round_enemies_killed += 1
                    self.player.particles.burst(enemy.x, enemy.y, GOLD, 15, 4, 30, 5)
                    self._spawn_new_enemy()
                    self.combo_display += 1
                    self.combo_display_timer = 2
                else:
                    self.damage_numbers.append({"x": enemy.x, "y": enemy.y,
                                               "text": str(self.player.attack_power), "timer": 1,
                                                "color": (255, 200, 50)})

            # Astro Toilets — Skibidi
            for astro in self.astro_toilets[:]:
                dx = astro.x - self.player.x; dy = astro.y - self.player.y
                if math.hypot(dx,dy) < 48:
                    if astro.take_damage(self.player.attack_power):
                        self.astro_toilets.remove(astro)
                        self.player.add_xp(40); self._drop_gold(astro.x, astro.y)
                        self.round_enemies_killed+=1; self.quests.update_progress("defeat","astro")
                        self.player.particles.burst(astro.x, astro.y, (180,200,255), 18, 4, 30, 5)
                        self.camera_shake=2
                    else:
                        self.damage_numbers.append({"x":astro.x,"y":astro.y-12,"text":str(self.player.attack_power),"timer":1,"color":(180,220,255)})

            # Also check boss hits
            for boss in self.bosses:
                if boss.active:
                    dx = boss.x - self.player.x
                    dy = boss.y - self.player.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < 50:
                        boss.take_damage(self.player.attack_power)
                        self.damage_numbers.append({"x": boss.x, "y": boss.y - 20,
                                                   "text": str(self.player.attack_power), "timer": 1,
                                                    "color": (255, 100, 100)})
                        self.camera_shake = 2
                        if not boss.active:
                            self._on_boss_defeated(boss)

            self.audio.play("attack")
        elif skill_name == "dodge":
            pass
        elif skill_name == "special":
            self.player.particles.burst(self.player.x, self.player.y,
                                        CLASS_COLORS[self.player.player_class], 20, 5, 30, 6)
            for enemy in self.enemies[:]:
                dx = enemy.x - self.player.x
                dy = enemy.y - self.player.y
                if dx * dx + dy * dy < 150 * 150:
                    if enemy.take_damage(self.player.attack_power * 2):
                        self.player.add_xp(25)
                        self._drop_gold(enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                        self.round_enemies_killed += 1
                        self._spawn_new_enemy()
                        self.quests.update_progress("defeat", "enemy")

            for astro in self.astro_toilets[:]:
                dx = astro.x - self.player.x; dy = astro.y - self.player.y
                if dx*dx+dy*dy < 150*150:
                    if astro.take_damage(self.player.attack_power*2):
                        self.astro_toilets.remove(astro)
                        self.player.add_xp(40); self._drop_gold(astro.x, astro.y)
                        self.round_enemies_killed+=1; self.quests.update_progress("defeat","astro")
                        self.player.particles.burst(astro.x, astro.y, (180,220,255), 22, 5, 35, 6)
                        self.camera_shake=3
                    else:
                        self.damage_numbers.append({"x":astro.x,"y":astro.y-12,"text":str(self.player.attack_power*2),"timer":1,"color":(180,200,255)})

            # Special hits bosses too
            for boss in self.bosses:
                if boss.active:
                    dx = boss.x - self.player.x
                    dy = boss.y - self.player.y
                    if dx * dx + dy * dy < 150 * 150:
                        boss.take_damage(self.player.attack_power * 2)
                        self.damage_numbers.append({"x": boss.x, "y": boss.y - 20,
                                                   "text": str(self.player.attack_power * 2), "timer": 1,
                                                    "color": (255, 100, 255)})
                        self.camera_shake = 3
                        if not boss.active:
                            self._on_boss_defeated(boss)

            self.audio.play("magic")

    def _on_boss_defeated(self, boss):
        self.player.add_xp(int(boss.xp_reward * self.new_game_plus.get_xp_mult()))
        self._drop_gold(boss.x, boss.y)
        self._drop_gold(boss.x + 20, boss.y - 10)
        self._drop_gold(boss.x - 20, boss.y + 10)
        for drop in boss.drops:
            if drop in RESOURCES:
                self.player.inventory["resources"][drop] = self.player.inventory["resources"].get(drop, 0) + 1
        self.boss_health_bar.hide()
        self.boss_quest_stage += 1
        self.show_message(f"{boss.name} defeated! +{int(boss.xp_reward * self.new_game_plus.get_xp_mult())} XP", 4)
        self.particles.burst(boss.x, boss.y, GOLD, 30, 6, 50, 8)
        self.leaderboards.update_score("kills", self.player.name, self.round_enemies_killed)
        self.leaderboards.update_score("bosses", self.player.name, self.boss_quest_stage)
        self.leaderboards.update_score("level", self.player.name, self.player.level)
        gold = self.player.inventory.get("resources", {}).get("Gold Leaves", 0)
        self.leaderboards.update_score("gold", self.player.name, gold)

        # Unlock new mount on boss kill
        boss_keys = list(BOSS_TYPES.keys())
        if self.boss_quest_stage <= len(boss_keys):
            new_mount = self.mount_cycle[min(self.boss_quest_stage - 1, len(self.mount_cycle) - 1)]
            if new_mount not in self.mounts_unlocked:
                self.mounts_unlocked.append(new_mount)
                self.show_message(f"New mount unlocked: {MOUNT_TYPES[new_mount]['name']}!", 4)

        # Round system: advance round or end credits
        if self.round_active and self.round_boss_spawned:
            self.round_boss_defeated = True
            self.round_boss_spawned = False
            self.round_enemies_killed = 0
            self.audio.play("boss_defeat")
            if self.current_round >= self.max_rounds:
                if not self.ngp_activated:
                    self.new_game_plus.unlocked = True
                    self.new_game_plus.activate()
                    self.ngp_activated = True
                    self.ngp_active = True
                    self.ngp_timer = 0
                    self.state = GameState.END_CREDITS
                    self.credits_timer = 0
                    self.leaderboards.update_score("round", self.player.name, self.current_round)
                    self.audio.play("new_game_plus")
                else:
                    self.credits_timer = 0
                    self.credits_phase = 0
                    self.state = GameState.END_CREDITS
            else:
                self.current_round += 1
                self.round_transition = True
                self.round_transition_timer = 0
                self.state = GameState.ROUND_INTRO
                self.round_intro_timer = 0
                self.audio.play("quest_complete")

    def _use_health_potion(self):
        if "Health Potion" in self.player.inventory["items"]:
            self.player.inventory["items"].remove("Health Potion")
            self.player.heal(30)
            self.show_message("Used Health Potion!", 2)
            self.audio.play("heal")

    def _apply_daily_reward(self, reward):
        if not self.player:
            return
        gold = self.player.inventory.get("resources", {}).get("Gold Leaves", 0)
        self.player.inventory["resources"]["Gold Leaves"] = gold + reward.get("gold", 0)
        for item in reward.get("items", []):
            self.player.inventory["items"].append(item)
        self.show_message(f"Claimed: {reward.get('gold', 0)} Gold + items!", 3)
        self.audio.play("collect")

    def _switch_weapon(self, weapon_id):
        if weapon_id in WEAPONS:
            all_weapons = self.player.inventory.get("weapons", [])
            all_items = self.player.inventory.get("items", [])
            if weapon_id in all_weapons or weapon_id in all_items:
                if self.player.equip_weapon(weapon_id):
                    self.show_message("Equipped: " + WEAPONS[weapon_id]["name"], 1.5)
                    self.audio.play("collect")
                return
            self.show_message("You don't have that weapon!", 1.5)

    def _touch_cycle_weapon(self):
        """WPN touch button — cycle through owned weapons (keyboard 1-8 order)."""
        owned_ids = (self.player.inventory.get("weapons", []) +
                     self.player.inventory.get("items", []))
        owned = [w for w in WEAPONS if w in owned_ids]
        if not owned:
            self.show_message("No weapons owned yet!", 1.5)
            self.audio.play("menu_hover")
            return
        cur = self.player.weapon_id
        idx = owned.index(cur) if cur in owned else -1
        self._switch_weapon(owned[(idx + 1) % len(owned)])

    def _check_projectile_hits(self):
        for proj in self.player.projectiles[:]:
            hit = False
            # Check regular enemies
            for enemy in self.enemies:
                dx = enemy.x - proj["x"]
                dy = enemy.y - proj["y"]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < enemy.size + 6:
                    dead = enemy.take_damage(proj["damage"])
                    self.damage_numbers.append({"x": enemy.x, "y": enemy.y - 15,
                                               "text": str(proj["damage"]), "timer": 1,
                                                "color": proj["color"]})
                    self.particles.burst(proj["x"], proj["y"], proj["color"], 8, 3, 15, 3)
                    if dead:
                        self.player.add_xp(25)
                        self.quests.update_progress("defeat", "enemy")
                        self._drop_gold(enemy.x, enemy.y)
                        self.enemies.remove(enemy)
                        self.round_enemies_killed += 1
                        self.particles.burst(enemy.x, enemy.y, GOLD, 15, 4, 30, 5)
                        self._spawn_new_enemy()
                        self.combo_display += 1
                        self.combo_display_timer = 2
                    hit = True
                    break

            # Check bosses
            if not hit:
                for boss in self.bosses:
                    if boss.active:
                        dx = boss.x - proj["x"]
                        dy = boss.y - proj["y"]
                        dist = math.sqrt(dx * dx + dy * dy)
                        if dist < boss.size + 6:
                            boss.take_damage(proj["damage"])
                            self.damage_numbers.append({"x": boss.x, "y": boss.y - 20,
                                                       "text": str(proj["damage"]), "timer": 1,
                                                        "color": proj["color"]})
                            self.particles.burst(proj["x"], proj["y"], proj["color"], 8, 3, 15, 3)
                            self.camera_shake = 1
                            if not boss.active:
                                self._on_boss_defeated(boss)
                            hit = True
                            break

            # Check Astro Toilets — Skibidi
            if not hit:
                for astro in self.astro_toilets[:]:
                    dx = astro.x - proj["x"]
                    dy = astro.y - proj["y"]
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist < astro.size + 6:
                        dead = astro.take_damage(proj["damage"])
                        self.damage_numbers.append({"x": astro.x, "y": astro.y - 15,
                                                   "text": str(proj["damage"]), "timer": 1,
                                                    "color": proj["color"]})
                        self.particles.burst(proj["x"], proj["y"], proj["color"], 8, 3, 15, 3)
                        if dead:
                            self.astro_toilets.remove(astro)
                            self.player.add_xp(40)
                            self.quests.update_progress("defeat", "astro")
                            self._drop_gold(astro.x, astro.y)
                            self.round_enemies_killed += 1
                            self.particles.burst(astro.x, astro.y, (180,200,255), 15, 4, 30, 5)
                        hit = True
                        break

            if hit or proj["dist_traveled"] > proj["range"]:
                self.player.projectiles.remove(proj)

    def _handle_craft_click(self, pos):
        recipes_list = list(RECIPES.keys())
        start_y = 200
        for i, recipe_name in enumerate(recipes_list):
            ry = start_y + i * 50
            if 150 <= pos[0] <= 450 and ry <= pos[1] <= ry + 40:
                if self.crafting.craft(recipe_name):
                    self.show_message(f"Crafted {recipe_name}!", 2)
                    self.audio.play("craft")
                else:
                    self.show_message("Missing ingredients!", 2)

    def _spawn_new_enemy(self):
        for _ in range(2):
            angle = random.uniform(0, 6.28)
            dist = random.randint(300, 500)
            ex = self.player.x + math.cos(angle) * dist
            ey = self.player.y + math.sin(angle) * dist
            ex = max(50, min(WORLD_W - 50, ex))
            ey = max(50, min(WORLD_H - 50, ey))
            self.enemies.append(Enemy(ex, ey, random.randint(0, 3)))

    def _drop_gold(self, x, y):
        gold = random.randint(5, 15)
        res = self.player.inventory.setdefault("resources", {})
        res["Gold Leaves"] = res.get("Gold Leaves", 0) + gold
        self.damage_numbers.append({"x": x, "y": y - 20,
                                   "text": f"+{gold} Gold", "timer": 1.5,
                                    "color": GOLD})

        # FIX: always show messages (was incorrectly nested in SETTINGS)
        if self.message_timer > 0:
            try:
                font = pygame.font.SysFont(None, 24)
                txt = font.render(self.message, True, WHITE)
                bg = pygame.Surface((txt.get_width() + 20, txt.get_height() + 10), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 160))
                self.screen.blit(bg, (WIDTH // 2 - bg.get_width() // 2, 20))
                self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 25))
            except BaseException:
                pass

    def update(self, dt):
        self.dt = dt
        self._check_controller_connection()
        # Go-live countdown — flip everything LIVE the moment it reaches zero
        if not self.is_live and time.time() >= self.go_live_ts:
            self._go_live_event()
        # on-screen keyboard for touch — show when typing name / login
        try:
            typing = bool(getattr(self, 'typing_name', False) and self.state in [GameState.CHARACTER_CREATE, GameState.LOGIN])
            # also show if account is in text entry
            if hasattr(self, 'account') and getattr(self.account, 'state', '') in ('login','register'):
                typing = self.state == GameState.LOGIN
            self.touch_controls.keyboard.visible = typing and self.touch_controls.enabled
        except: pass
        self.time += dt
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        self.particles.update()
        self.day_night.update(dt)
        self.season.update(dt)
        self.storm.update(dt)
        if self.storm.active and self.storm.flash_alpha > 190:
            self.audio.play("thunder")
        self.message_timer = max(0, self.message_timer - dt)
        self.combo_display_timer = max(0, self.combo_display_timer - dt)
        if self.combo_display_timer <= 0:
            self.combo_display = 0

        self.damage_numbers = [d for d in self.damage_numbers if d["timer"] > 0]
        for d in self.damage_numbers:
            d["timer"] -= dt
            d["y"] -= dt * 30

        self.camera_shake = max(0, self.camera_shake - dt * 10)
        if self.storm.thunder_shake > 0:
            self.camera_shake = max(self.camera_shake, self.storm.thunder_shake)

        self.screenshot_sys.update(dt)
        self.pet_manager.update(dt)

        if self.ngp_active:
            self.ngp_timer += dt

        # Random storm events
        if self.state == GameState.PLAYING and self.player and not self.storm.active:
            self.storm_random_timer -= dt
            if self.storm_random_timer <= 0:
                self.storm.start(random.randint(20, 35), random.uniform(0.5, 1.0))
                self.show_message("A storm rolls in...", 3)
                self.storm_random_timer = random.randint(60, 180)

            self.auto_save_timer -= dt
            if self.auto_save_timer <= 0:
                self.auto_save_timer = 60
                save_game(self.player, self)

        if self.state == GameState.LOGIN:
            self.account.error_timer = max(0, self.account.error_timer - dt * 60)
            self.account.success_timer = max(0, self.account.success_timer - dt * 60)

        if self.state == GameState.MAIN_MENU:
            self.main_menu.update(dt)
            self.dancing_bots.update(dt)
            if self.legend_open:
                self.doggo_legend.update(dt)

        # Always tick these (player count + admin abuse live everywhere)
        self.player_count.update(dt)
        self.admin_abuse.update(dt)
        self._apply_admin_abuse_effects(dt)

        if self.state == GameState.ROUND_INTRO:
            self.round_intro_timer += dt
            if self.round_intro_timer > 5 or (self.round_intro_timer > 1 and keys[pygame.K_RETURN]):
                self.state = GameState.PLAYING
                self.round_active = True
                self.round_enemies_killed = 0
                self.round_boss_spawned = False
                self.round_boss_defeated = False
                rd = self.round_data.get(self.current_round, {})
                self.show_message(f"Round {self.current_round}: {rd.get('name', 'Unknown')}", 3)

        elif self.state == GameState.END_CREDITS:
            self.credits_timer += dt

        elif self.state == GameState.PLAYING and self.player:
            self.player.update(dt, keys, mouse_buttons, mouse_pos, self.world,
                               self.camera_x, self.camera_y)

            if self.player.just_dodged:
                self.audio.play("dodge")
                self.player.just_dodged = False
            if self.player.just_leveled_up:
                self.audio.play("levelup")
                self.show_message(f"Level Up! Now Level {self.player.level}!", 3)
                self.player.just_leveled_up = False
            if self.player.just_collected:
                self.audio.play("collect")
                self.player.just_collected = False
            # Update tutorial
            if hasattr(self, 'tutorial') and self.tutorial and not self.tutorial.done:
                action_triggers = {
                    "attack": any(mouse_buttons),
                    "dodge": keys[pygame.K_SPACE],
                    "special": keys[pygame.K_q],
                    "interact": keys[pygame.K_e],
                    "inventory": keys[pygame.K_i],
                    "craft": keys[pygame.K_c],
                    "tame": keys[pygame.K_TAB],
                    "build": keys[pygame.K_v],
                }
                self.tutorial.update(dt, {k: False for k in range(512)}, action_triggers)

            # Controller support
            ctrl = self._get_controller_input()
            if ctrl:
                lx, ly = ctrl["lx"], ctrl["ly"]
                if abs(lx) > 0.1 or abs(ly) > 0.1:
                    self.player.x += lx * self.player.speed
                    self.player.y += ly * self.player.speed
                    self.player.facing = math.atan2(ly, lx)

                # Controller buttons
                btns = ctrl["buttons"]
                if btns.get(0):  # A button - attack
                    if self.player.attack_timer <= 0:
                        mouse_pos_ctrl = (WIDTH // 2 + int(math.cos(self.player.facing) * 100),
                                          HEIGHT // 2 + int(math.sin(self.player.facing) * 100))
                        self.player._attack(mouse_pos_ctrl, self.camera_x, self.camera_y)
                        self.audio.play("attack")
                if btns.get(1):  # B button - dodge
                    if self.player.dodge_cooldown <= 0 and not self.player.dodging and self.player.energy >= 10:
                        self.player.dodging = True
                        self.player.dodge_timer = 0.3
                        self.player.dodge_cooldown = 1.0
                        self.player.invincible = 0.3
                        self.player.energy -= 10
                        self.audio.play("dodge")
                if btns.get(2):  # X button - interact
                    self._try_interact()
                if btns.get(3):  # Y button - special
                    self._use_skill("special")
                    self.audio.play("controller_btn")
                if btns.get(4):  # LB - inventory
                    self.inventory_open = not self.inventory_open
                    self.audio.play("tab_switch")
                if btns.get(5):  # RB - crafting
                    self.crafting_open = not self.crafting_open
                    self.audio.play("tab_switch")
                if btns.get(6):  # LT - mount
                    self._try_mount()
                    self.audio.play("controller_btn")
                if btns.get(7):  # RT - health potion
                    self._use_health_potion()
                    self.audio.play("controller_btn")
                if btns.get(8):  # Back - menu
                    self.state = GameState.PAUSED
                    self.audio.play("tab_switch")
                if btns.get(9):  # Start - pause
                    self.state = GameState.PAUSED
                    self.audio.play("menu_select")

            # Go-live villagers + dialogue typing
            for npc in self.npcs:
                npc.update(dt)
            self.dialogue_box.update(dt)

            # Touch controls input
            if self.touch_controls.enabled:
                tx, ty = self.touch_controls.get_movement()
                if abs(tx) > 0.1 or abs(ty) > 0.1:
                    self.player.x += tx * self.player.speed
                    self.player.y += ty * self.player.speed
                    self.player.facing = math.atan2(ty, tx)
                if self.touch_controls.attack_btn.is_pressed() and self.player.attack_timer <= 0:
                    mouse_pos_t = (WIDTH // 2 + int(math.cos(self.player.facing) * 100),
                                   HEIGHT // 2 + int(math.sin(self.player.facing) * 100))
                    self.player._attack(mouse_pos_t, self.camera_x, self.camera_y)
                    self.audio.play("attack")
                if self.touch_controls.dodge_btn.just_pressed():
                    if self.player.dodge_cooldown <= 0 and not self.player.dodging and self.player.energy >= 10:
                        self.player.dodging = True
                        self.player.dodge_timer = 0.3
                        self.player.dodge_cooldown = 1.0
                        self.player.invincible = 0.3
                        self.player.energy -= 10
                        self.audio.play("dodge")
                if self.touch_controls.special_btn.just_pressed():
                    self._use_skill("special")
                    self.audio.play("controller_btn")
                if self.touch_controls.interact_btn.just_pressed():
                    self._try_interact()
                if self.touch_controls.potion_btn.just_pressed():
                    self._use_health_potion()
                    self.audio.play("controller_btn")
                if self.touch_controls.inventory_btn.just_pressed():
                    self.inventory_open = not self.inventory_open
                    self.audio.play("tab_switch")
                if self.touch_controls.craft_btn.just_pressed():
                    self.crafting_open = not self.crafting_open
                    self.audio.play("tab_switch")
                if self.touch_controls.mount_btn.just_pressed():
                    self._try_mount()
                    self.audio.play("controller_btn")
                if self.touch_controls.menu_btn.just_pressed():
                    self.state = GameState.PAUSED
                    self.audio.play("menu_select")
                # Extended touchscreen buttons — reuse the exact keyboard actions
                touch_keys = [
                    (self.touch_controls.storm_btn, pygame.K_t),
                    (self.touch_controls.tame_btn, pygame.K_TAB),
                    (self.touch_controls.shop_btn, pygame.K_s),
                    (self.touch_controls.build_btn, pygame.K_v),
                    (self.touch_controls.battlepass_btn, pygame.K_F1),
                    (self.touch_controls.lobby_btn, pygame.K_p),
                    (self.touch_controls.achv_btn, pygame.K_u),
                ]
                for tbtn, tkey in touch_keys:
                    if tbtn.just_pressed():
                        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tkey, mod=0, unicode=""))
                        self.audio.play("tab_switch")
                if self.touch_controls.weapon_btn.just_pressed():
                    self._touch_cycle_weapon()

            # Mount speed boost
            if self.mount and self.mount.mounted:
                if self.mount.sprinting and self.mount.stamina > 0:
                    self.player.speed = self.player.stats["speed"] * \
                        self.mount.base_speed * self.mount.sprint_multiplier / 4
                else:
                    self.player.speed = self.player.stats["speed"] * self.mount.base_speed / 4

            # Camera follow
            target_cx = self.player.x - WIDTH // 2
            target_cy = self.player.y - HEIGHT // 2
            self.camera_x += (target_cx - self.camera_x) * 0.08
            self.camera_y += (target_cy - self.camera_y) * 0.08

            if self.camera_shake > 0:
                self.camera_x += random.uniform(-self.camera_shake, self.camera_shake) * 2
                self.camera_y += random.uniform(-self.camera_shake, self.camera_shake) * 2

            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update(dt, self.player.x, self.player.y)
                if CombatSystem.deal_damage_to_player(enemy, self.player):
                    self.player.particles.burst(self.player.x, self.player.y, RED, 8, 3, 20, 4)
                    self.camera_shake = 3
                    self.audio.play("hit")
                    if self.mount and self.mount.mounted:
                        self.mount.take_damage(enemy.attack)
                    if self.player.hp <= 0:
                        self.state = GameState.GAME_OVER

            # Update bosses
            for boss in self.bosses[:]:
                boss.update(dt, self.player.x, self.player.y)
                if boss.active:
                    if boss.can_attack():
                        dmg = boss.do_attack()
                        if self.player.take_damage(dmg):
                            self.camera_shake = 4
                            self.audio.play("hit")
                            if self.mount and self.mount.mounted:
                                self.mount.take_damage(dmg // 2)
                            if self.player.hp <= 0:
                                self.state = GameState.GAME_OVER
                    if boss.active:
                        self.boss_health_bar.show(boss)
                elif boss.is_dead():
                    self.bosses.remove(boss)

            # Astro Toilets — Skibidi research elite
            self.astro_spawn_timer -= dt
            if self.astro_spawn_timer <= 0 and self.current_round >= 3 and len(self.astro_toilets) < 4 and self.player and self.world:
                ax = max(60, min(WORLD_W-60, self.player.x + random.randint(-500,500)))
                ay = max(60, min(WORLD_H-60, self.player.y + random.randint(-500,500)))
                pool = ["trooper","rocketeer"] if self.current_round==3 else ["detainer","assailant","juggernaut","duchess","mothership"] if self.current_round==4 else ["trooper"]
                at = random.choice(pool)
                self.astro_toilets.append(AstroToilet(ax, ay, at))
                self.astro_spawn_timer = random.uniform(5,9)
            for astro in self.astro_toilets[:]:
                astro.update(self.player, dt)
                if astro.can_shoot() and math.hypot(astro.x - self.player.x, astro.y - self.player.y) < 520:
                    astro.shoot()
                    if self.player.take_damage(max(1, astro.attack//3)):
                        self.camera_shake = 2
                        self.audio.play("hit")
                        if self.player.hp <=0: self.state = GameState.GAME_OVER
                # touch damage
                if math.hypot(astro.x - self.player.x, astro.y - self.player.y) < astro.size+18:
                    if self.player.take_damage(astro.attack):
                        self.camera_shake = 3
                        self.audio.play("hit")
                        if self.player.hp <=0: self.state = GameState.GAME_OVER
                if not astro.alive:
                    self.astro_toilets.remove(astro)
                    self.player.add_xp(45)
                    self._drop_gold(astro.x, astro.y)
                    self.round_enemies_killed += 1
                    self.quests.update_progress("defeat", "astro")
                    self.audio.play("collect")

            # Projectile collision
            self._check_projectile_hits()

            # Update creatures
            for creature in self.creatures:
                creature.update(dt, self.player.x, self.player.y)

            for creature in self.creatures:
                if creature.tamed:
                    self.particles.trail(creature.x, creature.y, creature.color, 0.2, 0.5, 15, 2)

            # Pet combat assist
            for pet_data in self.player.creatures:
                for enemy in self.enemies:
                    dx = enemy.x - self.player.x
                    dy = enemy.y - self.player.y
                    if dx * dx + dy * dy < 100 * 100 and random.random() < 0.005:
                        if enemy.take_damage(pet_data.get("level", 1) * 2):
                            self._drop_gold(enemy.x, enemy.y)
                            self.enemies.remove(enemy)
                            self.round_enemies_killed += 1
                            self._spawn_new_enemy()
                            self.quests.update_progress("defeat", "enemy")
                            self.audio.play("pet_ability")

            # Auto-collect resources near player
            if self.settings.get("auto_collect", True):
                tile = self.world.get_tile(int(self.player.x // TILE_SIZE), int(self.player.y // TILE_SIZE))
                if tile and tile.resource:
                    res = tile.resource
                    self.player.inventory["resources"][res] = self.player.inventory["resources"].get(res, 0) + 1
                    self.player.particles.burst(self.player.x, self.player.y, RESOURCES[res]["color"], 5, 2, 20, 3)
                    self.player.add_xp(5)
                    self.quests.update_progress("collect", res)
                    self.audio.play("collect")
                    tile.resource = None

            region = self.world.get_region_at(self.player.x, self.player.y)
            if region:
                self.quests.update_progress("explore", region["name"])

            if self.quests.completed_this_frame:
                for qname in self.quests.completed_this_frame:
                    self.audio.play("quest_complete")
                    self.show_message(f"Quest Complete: {qname}!", 3)
                self.quests.completed_this_frame = []

            self.hud.update(dt)

            # Mount update
            if self.mount:
                self.mount.update(dt, self.player.x, self.player.y)

            for pet_data in self.player.creatures:
                pet_data["level"] = pet_data.get("level", 1) + 0.001 * dt

            if len(self.enemies) < 7 and random.random() < 0.005:
                self._spawn_new_enemy()
            if len(self.creatures) < 4 and random.random() < 0.002:
                cx = random.randint(100, WORLD_W - 100)
                cy = random.randint(100, WORLD_H - 100)
                self.creatures.append(Creature(cx, cy, random.randint(0, 4)))

            # Round system: spawn boss when enough enemies killed
            if self.round_active and not self.round_boss_spawned and not self.round_boss_defeated:
                rd = self.round_data.get(self.current_round, {})
                needed = rd.get("enemies_needed", 10)
                if self.round_enemies_killed >= needed:
                    boss_type = rd.get("boss", "root_titan")
                    self._spawn_round_boss(boss_type)
                    self.round_boss_spawned = True
                    self.audio.play("boss_appear")
                    self.show_message(f"BOSS: {rd.get('name', 'Unknown')}!", 4)

            # Remove old random boss spawn timer
            # if not self.bosses:
            #     self.boss_spawn_timer -= dt
            #     if self.boss_spawn_timer <= 0:
            #         self._spawn_boss()
            #         self.boss_spawn_timer = random.randint(90, 180)

            # Weapon particle trails
            if self.player.attack_anim > 0 and self.player.weapon["type"] == "sword":
                angle = self.player.facing
                for i in range(3):
                    t = i / 3
                    trail_x = self.player.x + math.cos(angle) * (15 + t * 20)
                    trail_y = self.player.y + math.sin(angle) * (15 + t * 20)
                    self.trail_particles.append({
                        "x": trail_x, "y": trail_y,
                        "vx": math.cos(angle + 1.5) * 0.5,
                        "vy": math.sin(angle + 1.5) * 0.5,
                        "life": 0.3, "max_life": 0.3,
                        "color": self.player.weapon["trail_color"],
                        "size": 3 - t,
                    })

            # Update trail particles
            for p in self.trail_particles[:]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["life"] -= dt
                if p["life"] <= 0:
                    self.trail_particles.remove(p)

            # Update expanded enemies
            for eenemy in self.expanded_enemies[:]:
                eenemy.update(dt, self.player.x, self.player.y)
                if eenemy.attack_cooldown <= 0 and eenemy.state == "attacking":
                    dmg = eenemy.attack
                    if self.player.take_damage(dmg):
                        self.player.particles.burst(self.player.x, self.player.y, RED, 8, 3, 20, 4)
                        self.camera_shake = 3
                        self.audio.play("hit")
                        eenemy.attack_cooldown = 1.5
                        if self.mount and self.mount.mounted:
                            self.mount.take_damage(dmg // 2)
                        if self.player.hp <= 0:
                            self.state = GameState.GAME_OVER

            # Expanded enemy projectile hits
            for proj in self.player.projectiles[:]:
                for eenemy in self.expanded_enemies:
                    dx = eenemy.x - proj["x"]
                    dy = eenemy.y - proj["y"]
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < eenemy.size + 6:
                        dead = eenemy.take_damage(proj["damage"])
                        self.damage_numbers.append({"x": eenemy.x, "y": eenemy.y - 15,
                                                   "text": str(proj["damage"]), "timer": 1,
                                                    "color": proj["color"]})
                        self.particles.burst(proj["x"], proj["y"], proj["color"], 8, 3, 15, 3)
                        if dead:
                            self.player.add_xp(eenemy.xp_reward)
                            self.quests.update_progress("defeat", "enemy")
                            drops = eenemy.get_drops()
                            for drop in drops:
                                self.player.inventory["resources"][drop] = self.player.inventory["resources"].get(
                                    drop, 0) + 1
                            self.audio.play("collect")
                            self._drop_gold(eenemy.x, eenemy.y)
                            self.expanded_enemies.remove(eenemy)
                            self.round_enemies_killed += 1
                            self.particles.burst(eenemy.x, eenemy.y, GOLD, 15, 4, 30, 5)
                            self.combo_display += 1
                            self.combo_display_timer = 2
                        if proj in self.player.projectiles:
                            self.player.projectiles.remove(proj)
                        break

            # Spawn expanded enemies
            if len(self.expanded_enemies) < 5 and random.random() < 0.003:
                angle = random.uniform(0, 6.28)
                dist = random.randint(300, 500)
                ex = self.player.x + math.cos(angle) * dist
                ey = self.player.y + math.sin(angle) * dist
                ex = max(50, min(WORLD_W - 50, ex))
                ey = max(50, min(WORLD_H - 50, ey))
                self.expanded_enemies.append(ExpandedEnemy(ex, ey))

            # Update base buildings
            self.base_builder.update(dt, enemies=self.enemies + self.expanded_enemies, player=self.player)

            # Update battle pass
            self.battle_pass.update(dt)

            # Update multiplayer
            self.multiplayer.update(dt, self.player)

        # Music state management (runs every frame for all states)
        self._update_music()

    def _update_music(self):
        if not self.audio.enabled:
            return

        if self.state == GameState.MAIN_MENU:
            new_type = "menu"
        elif self.state in (GameState.LOGIN, GameState.CHARACTER_CREATE, GameState.SETTINGS):
            new_type = "menu"
        elif self.state == GameState.PLAYING and self.player:
            has_boss = any(b.active for b in self.bosses)
            has_nearby_enemies = False
            for e in self.enemies + self.expanded_enemies:
                dx = e.x - self.player.x
                dy = e.y - self.player.y
                if math.sqrt(dx * dx + dy * dy) < 250:
                    has_nearby_enemies = True
                    break

            if has_boss:
                new_type = "boss"
            elif has_nearby_enemies:
                new_type = "combat"
            else:
                new_type = "ambient"
        else:
            new_type = self.current_music_type

        if new_type and new_type != self.current_music_type:
            self.current_music_type = new_type
            self.audio.play_music(new_type)

    def _spawn_boss(self):
        boss_keys = list(BOSS_TYPES.keys())
        idx = self.boss_quest_stage % len(boss_keys)
        boss_type = boss_keys[idx]
        angle = random.uniform(0, 6.28)
        dist = 400
        bx = self.player.x + math.cos(angle) * dist
        by = self.player.y + math.sin(angle) * dist
        bx = max(100, min(WORLD_W - 100, bx))
        by = max(100, min(WORLD_H - 100, by))
        boss = Boss(bx, by, boss_type)
        self.bosses.append(boss)
        self.show_message(f"A powerful presence approaches... {boss.name}!", 4)
        self.camera_shake = 5

    def _spawn_round_boss(self, boss_type):
        if not self.player:
            return
        angle = random.uniform(0, 6.28)
        dist = 400
        bx = self.player.x + math.cos(angle) * dist
        by = self.player.y + math.sin(angle) * dist
        bx = max(100, min(WORLD_W - 100, bx))
        by = max(100, min(WORLD_H - 100, by))
        boss = Boss(bx, by, boss_type)
        self.bosses.append(boss)
        self.camera_shake = 5

    def draw(self):
        self.screen.fill((0, 0, 0))

        if not self.studio_splash.done:
            self.studio_splash.draw(self.screen)
            return

        if self.state == GameState.LOGIN:
            font = pygame.font.Font(None, 32)
            small_font = pygame.font.Font(None, 22)
            self.account.draw(self.screen, font, small_font)
            # Touchscreen: on-screen keyboard while typing login/register fields
            self.touch_controls.draw_keyboard_only(self.screen)

        elif self.state == GameState.MAIN_MENU:
            self.main_menu.draw()
            # Dancing bots on menu — placed between buttons and bottom UI
            self.dancing_bots.draw(self.screen, base_y=HEIGHT - 160)
            # Live player count — top-center, no overlap with buttons/SignIn
            if self.show_player_count:
                f = pygame.font.Font(None, 22)
                sf = pygame.font.Font(None, 16)
                self.player_count.draw(self.screen, f, sf, y=36)
            if self.account.current_user:
                user_data = self.account.get_user_data()
                if user_data:
                    tiny_f = pygame.font.Font(None, 18)
                    name_txt = f"GoStudios: {user_data['name']}"
                    name_s = tiny_f.render(name_txt, True, (100, 160, 100))
                    self.screen.blit(name_s, (WIDTH - name_s.get_width() - 20, 15))
            # Go-live countdown / LIVE badge — top-right, under the account name
            cl_f = pygame.font.Font(None, 24)
            if self.is_live:
                cl_txt = "● PLAYTREE IS LIVE!"
                cl_col = (80, 255, 120)
            else:
                cl_txt = f"GOES LIVE IN: {self.go_live_str()}"
                cl_col = GOLD
            cl_s = cl_f.render(cl_txt, True, cl_col)
            cl_y = 38 if self.account.current_user else 14
            cl_bg = pygame.Surface((cl_s.get_width() + 16, cl_s.get_height() + 8), pygame.SRCALPHA)
            pulse = int(math.sin(self.time * 4) * 40 + 150) if self.is_live else 150
            cl_bg.fill((10, 15, 10, pulse))
            pygame.draw.rect(cl_bg, (*cl_col[:3], 160), cl_bg.get_rect(), 1, border_radius=6)
            self.screen.blit(cl_bg, (WIDTH - cl_bg.get_width() - 14, cl_y - 4))
            self.screen.blit(cl_s, (WIDTH - cl_s.get_width() - 22, cl_y))
            if self.daily_rewards.can_claim() and not self.daily_rewards_open and not self.leaderboards_open:
                nr_f = pygame.font.Font(None, 20)
                pulse = int(math.sin(self.time * 3) * 30 + 225)
                nr_s = nr_f.render("Daily Reward Available! (F10)", True, (*GOLD[:3], pulse))
                self.screen.blit(nr_s, (WIDTH // 2 - nr_s.get_width() // 2, HEIGHT - 200))
            # Menu messages (e.g. "No save yet") — clear spot above buttons, below logo
            if self.message_timer > 0:
                alpha = int(255 * min(1, self.message_timer))
                msg_font = pygame.font.Font(None, 28)
                msg_surf = msg_font.render(self.message, True, (*GREEN_GLOW[:3], alpha))
                bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
                bg.fill((10, 15, 10, min(180, alpha)))
                self.screen.blit(bg, (WIDTH // 2 - bg.get_width() // 2, 235))
                self.screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 240))
            if self.daily_rewards_open:
                self.daily_rewards.draw(self.screen)
            if self.leaderboards_open:
                self.leaderboards.draw(self.screen)
            if self.update_log_open:
                self.update_log.draw(self.screen)
            if self.games_open:
                self._draw_games_panel()

        elif self.state == GameState.CHARACTER_CREATE:
            self._draw_character_create()
            # Touchscreen: on-screen keyboard while typing the character name
            self.touch_controls.draw_keyboard_only(self.screen)

        elif self.state == GameState.ROUND_INTRO:
            self._draw_game_world()
            self._draw_round_intro()

        elif self.state == GameState.END_CREDITS:
            self._draw_end_credits()

        elif self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER,
                            GameState.INVENTORY, GameState.CRAFTING]:
            self._draw_game_world()
            # FIX: exclusive overlays — stop everything overlapping
            if self.inventory_open:
                self._draw_inventory()
            elif self.crafting_open:
                self._draw_crafting()
            elif self.shop_open:
                self._draw_shop()
            elif self.locker_open:
                self._draw_locker()
            elif self.profile_open:
                self._draw_profile()
            elif self.marketplace_open:
                self._draw_marketplace()
            elif self.lobby_open:
                self._draw_lobby()
            elif self.build_open:
                self.base_builder.draw_build_menu(self.screen, self.player.inventory.get("resources", {}))
                self.base_builder.draw_ghost(self.screen, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1],
                                             int(self.camera_x), int(self.camera_y))
            elif self.battle_pass_open:
                self.battle_pass.draw(self.screen, self.player)
            elif self.achievements_open and hasattr(self, 'achievements') and self.achievements:
                font = pygame.font.Font(None, 32)
                small_font = pygame.font.Font(None, 22)
                self.achievements.draw_screen(self.screen, font, small_font)
            elif self.daily_rewards_open:
                self.daily_rewards.draw(self.screen)
            elif self.leaderboards_open:
                self.leaderboards.draw(self.screen)
            elif self.update_log_open:
                self.update_log.draw(self.screen)
            elif self.screenshot_sys.share_menu_open:
                self.screenshot_sys.draw_share_menu(self.screen)
            elif self.state == GameState.PAUSED:
                self._draw_pause()
            elif self.state == GameState.GAME_OVER:
                self._draw_game_over()
            self.multiplayer.draw(self.screen)
            self.screenshot_sys.draw_flash(self.screen)
            # FIX: touchscreen — don't overlap exclusive overlays
            if not any([self.inventory_open, self.crafting_open, self.shop_open, self.locker_open, self.profile_open, self.marketplace_open, self.lobby_open, self.build_open, self.battle_pass_open, self.achievements_open, self.daily_rewards_open, self.leaderboards_open, self.update_log_open, self.screenshot_sys.share_menu_open]) and self.state not in [GameState.PAUSED, GameState.GAME_OVER]:
                self.touch_controls.draw(self.screen)
            if hasattr(self, 'tutorial') and self.tutorial and not self.tutorial.done:
                tf = pygame.font.Font(None, 28)
                sf = pygame.font.Font(None, 20)
                self.tutorial.draw(self.screen, tf, sf)
            # Live player count during gameplay
            if self.show_player_count and self.state == GameState.PLAYING:
                f = pygame.font.Font(None, 20)
                sf = pygame.font.Font(None, 14)
                self.player_count.draw(self.screen, f, sf, y=HEIGHT - 30)

        elif self.state == GameState.SETTINGS:
            self._draw_settings()

            if self.message_timer > 0:
                alpha = int(255 * min(1, self.message_timer))
                msg_font = pygame.font.Font(None, 28)
                msg_surf = msg_font.render(self.message, True, (*GREEN_GLOW[:3], alpha))
                msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 120))
                bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
                bg.fill((10, 15, 10, min(180, alpha)))
                self.screen.blit(bg, (msg_rect.x - 10, msg_rect.y - 5))
                self.screen.blit(msg_surf, msg_rect)

        # Global overlays — drawn last so they never get overlapped
        font32 = pygame.font.Font(None, 32)
        font22 = pygame.font.Font(None, 22)
        if self.legend_open:
            self.doggo_legend.draw(self.screen, font32, font22)
        if self.admin_abuse.open:
            self.admin_abuse.draw(self.screen, font32, font22)
            # Handle mouse clicks on abuse buttons
            # (handled in handle_events via mouse, but draw buttons here)
        # Hint bar — bottom-center on menu (avoids version text), right in gameplay
        if self.state in (GameState.MAIN_MENU, GameState.PLAYING) and not self.legend_open and not self.admin_abuse.open:
            hf = pygame.font.Font(None, 16)
            hint = hf.render("[L] Legend  [Shift+A] Admin Abuse", True, (70, 100, 70))
            if self.state == GameState.MAIN_MENU:
                hx, hy = WIDTH // 2 - hint.get_width() // 2, HEIGHT - 14
            else:
                hx, hy = WIDTH - hint.get_width() - 12, HEIGHT - 14
            self.screen.blit(hint, (hx, hy))

        # Toast for messages triggered while an overlay covers the world (shop/marketplace/etc.)
        if self.message_timer > 0 and self._any_overlay_open():
            alpha = int(255 * min(1, self.message_timer))
            msg_font = pygame.font.Font(None, 26)
            msg_surf = msg_font.render(self.message, True, (*GREEN_GLOW[:3], alpha))
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, 22))
            bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
            bg.fill((10, 15, 10, min(200, alpha)))
            self.screen.blit(bg, (msg_rect.x - 10, msg_rect.y - 5))
            self.screen.blit(msg_surf, msg_rect)

        # Touch-friendly ESC button while gameplay overlays are open
        if self.state == GameState.PLAYING and self._any_overlay_open():
            r = self._touch_esc_rect
            pygame.draw.rect(self.screen, (50, 18, 18), r, border_radius=6)
            pygame.draw.rect(self.screen, (255, 90, 90), r, 2, border_radius=6)
            esc_s = pygame.font.Font(None, 20).render("ESC X", True, (255, 170, 170))
            self.screen.blit(esc_s, esc_s.get_rect(center=r.center))

        # Admin abuse screen effects (rainbow / disco / glitch)
        fx = getattr(self.admin_abuse, "effects", {})
        if "rainbow" in fx:
            for band in range(6):
                col = pygame.Color(0)
                col.hsva = ((self.time * 80 + band * 60) % 360, 100, 100, 100)
                seg = pygame.Surface((WIDTH, HEIGHT // 6 + 1), pygame.SRCALPHA)
                seg.fill((col.r, col.g, col.b, 36))
                self.screen.blit(seg, (0, band * (HEIGHT // 6)))
        if "disco" in fx:
            disco = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for i in range(4):
                col = pygame.Color(0)
                col.hsva = ((self.time * 130 + i * 90) % 360, 100, 100, 100)
                pygame.draw.circle(disco, (col.r, col.g, col.b, 30),
                                   (int((WIDTH / 4) * (i + 0.5)), HEIGHT // 2), 260)
            self.screen.blit(disco, (0, 0))
        if "glitch" in fx:
            for _ in range(6):
                gy = random.randint(0, HEIGHT - 14)
                gh = random.randint(4, 14)
                gdx = random.randint(-25, 25)
                band = self.screen.subsurface(pygame.Rect(0, gy, WIDTH, gh)).copy()
                self.screen.blit(band, (gdx, gy))
            for _ in range(3):
                gy = random.randint(0, HEIGHT - 6)
                gc = random.choice([(255, 0, 80), (0, 255, 180), (120, 0, 255)])
                gs = pygame.Surface((WIDTH, 4), pygame.SRCALPHA)
                gs.fill((*gc, 60))
                self.screen.blit(gs, (0, gy))

    def _draw_character_create(self):
        GlowEffect.gradient_rect(self.screen, (5, 5, 30), (20, 30, 50), (0, 0, WIDTH, HEIGHT))
        self.starfield.draw(self.screen, self.time)

        title_f = pygame.font.Font(None, 60)
        t = title_f.render("CREATE YOUR LEGEND", True, GOLD)
        self.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 50))

        cls = self.class_cycle[self.selected_class]
        class_name = cls.value
        class_color = CLASS_COLORS[cls]

        preview_x, preview_y = WIDTH // 2, 220
        pygame.draw.circle(self.screen, class_color, (preview_x, preview_y), 50)
        pygame.draw.circle(self.screen, (*class_color[:3], 80), (preview_x, preview_y), 60, 3)

        glow_r = 70 + int(math.sin(self.time * 2) * 5)
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*class_color[:3], 40), (glow_r, glow_r), glow_r)
        self.screen.blit(glow_s, (preview_x - glow_r, preview_y - glow_r))

        nf = pygame.font.Font(None, 50)
        ns = nf.render(class_name, True, GOLD)
        self.screen.blit(ns, (WIDTH // 2 - ns.get_width() // 2, 290))

        stats = CLASS_STATS[cls]
        sf = pygame.font.Font(None, 28)
        stat_names = {"hp": "HP", "energy": "Energy", "attack": "Attack", "defense": "Defense", "speed": "Speed"}
        for i, (sk, sv) in enumerate(stats.items()):
            label = stat_names.get(sk, sk)
            txt = f"{label}: {sv}"
            ts = sf.render(txt, True, (200, 220, 200))
            col_x = 200 if i < 3 else 200
            col_y = 360 + (i if i < 3 else i - 3) * 30
            if i >= 3:
                col_x = 500
            self.screen.blit(ts, (col_x, col_y))

        hf = pygame.font.Font(None, 24)
        if self.controller_connected:
            xbox_icons.draw_dual_prompt(self.screen, WIDTH // 2 - 120, 480, "LB", "LEFT", "Switch Class", 18)
            xbox_icons.draw_dual_prompt(self.screen, WIDTH // 2 + 40, 480, "RB", "RIGHT", "Switch Class", 18)
            h2 = hf.render("Type name, then press A to begin", True, (150, 180, 150))
        else:
            h1 = hf.render("<  LEFT / RIGHT arrows to switch class  >", True, (150, 180, 150))
            self.screen.blit(h1, (WIDTH // 2 - h1.get_width() // 2, 480))
            h2 = hf.render("Type name, then ENTER to begin", True, (150, 180, 150))
        self.screen.blit(h2, (WIDTH // 2 - h2.get_width() // 2, 510))

        nf2 = pygame.font.Font(None, 36)
        name_display = self.name_input if self.name_input else "[ Enter Name ]"
        name_color = GOLD if self.name_input else (120, 120, 120)
        name_surf = nf2.render(name_display, True, name_color)
        name_rect = name_surf.get_rect(center=(WIDTH // 2, 560))
        pygame.draw.rect(self.screen, (20, 30, 20), (name_rect.x - 10, name_rect.y - 5,
                                                     name_rect.width + 20, name_rect.height + 10), border_radius=5)
        pygame.draw.rect(self.screen, (*GREEN_GLOW[:3], 60), (name_rect.x - 10, name_rect.y - 5,
                                                              name_rect.width + 20, name_rect.height + 10), 1)
        self.screen.blit(name_surf, name_rect)
        if self.typing_name and int(self.time * 2) % 2:
            pygame.draw.line(self.screen, GOLD, (name_rect.right + 2, name_rect.y),
                             (name_rect.right + 2, name_rect.bottom), 2)

        if self.controller_connected:
            xbox_icons.draw_dual_prompt(self.screen, 30, HEIGHT - 38, "B", "ESC", "Go Back", 16)
        else:
            eh = hf.render("ESC to go back", True, (100, 120, 100))
            self.screen.blit(eh, (20, HEIGHT - 30))

    def _handle_settings_click(self, pos):
        mx, my = pos
        # must match _draw_settings geometry: iy = 130 + i*45, rows 35px tall
        settings_items = ["music_volume", "sfx_volume", "fullscreen", "show_fps",
                          "screen_shake", "show_damage_numbers", "auto_collect"]
        for i, key in enumerate(settings_items):
            iy = 130 + i * 45
            if not (90 <= mx <= 1190 and iy <= my <= iy + 35):
                continue
            if key in ("music_volume", "sfx_volume"):
                if 340 <= mx <= 680:
                    self.settings[key] = max(0, min(1, (mx - 340) / 340))
                    if key == "music_volume":
                        self.audio.set_music_volume(self.settings[key])
                    else:
                        self.audio.set_sfx_volume(self.settings[key])
            else:
                self.settings[key] = not self.settings[key]
                self.audio.play("menu_select")
                if key == "fullscreen":
                    if self.settings["fullscreen"]:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT))  # FIX: keep render_surface as Game.screen
        save_settings(self.settings)

        # Sign Out button (matches draw: sx+sw-160, sy+sh-45)
        so_x, so_y = 80 + (WIDTH - 160) - 160, 60 + (HEIGHT - 120) - 45
        if self.account.current_user and so_x <= mx <= so_x + 140 and so_y <= my <= so_y + 30:
            self.account.logout()
            self.state = GameState.LOGIN

    def _handle_settings_hover(self, pos):
        self.settings_hover = -1
        settings_items = ["music_volume", "sfx_volume", "fullscreen", "show_fps",
                          "screen_shake", "show_damage_numbers", "auto_collect"]
        for i, key in enumerate(settings_items):
            iy = 130 + i * 45
            if 90 <= pos[0] <= 1190 and iy <= pos[1] <= iy + 35:
                self.settings_hover = i
                break
        # Sign Out hover
        if self.account.current_user:
            so_x, so_y = 80 + (WIDTH - 160) - 160, 60 + (HEIGHT - 120) - 45
            if so_x <= pos[0] <= so_x + 140 and so_y <= pos[1] <= so_y + 30:
                self.settings_hover = 999

    def _handle_shop_click(self, pos):
        mx, my = pos
        items_list = list(SHOP_ITEMS.keys())
        start_y = 100  # matches _draw_shop: sy(40) + 60
        for i, item_name in enumerate(items_list):
            iy = start_y + i * 55
            # BUY button matches draw: sx(60)+sw(1160)-120 = 1100, iy+4, 100x38
            if 1100 <= mx <= 1200 and iy + 4 <= my <= iy + 42:
                item = SHOP_ITEMS[item_name]
                gold = self.player.inventory.get("resources", {}).get("Gold Leaves", 0)
                if gold >= item["price"]:
                    self.player.inventory["resources"]["Gold Leaves"] = gold - item["price"]
                    if item["type"] == "consumable":
                        self.player.inventory["items"].append(item_name)
                    elif item["type"] == "weapon":
                        wid = item["id"]
                        if wid not in self.player.inventory["weapons"]:
                            self.player.inventory["weapons"].append(wid)
                        self.player.inventory["items"].append(wid)
                    elif item["type"] == "pet":
                        creatures_data = [
                            {"name": "Forest Fox", "color": (255, 140, 60), "type": "forest", "level": 1},
                            {"name": "Crystal Dragon", "color": (180, 120, 255), "type": "crystal", "level": 1},
                            {"name": "Mechanical Owl", "color": (200, 180, 100), "type": "mech", "level": 1},
                            {"name": "Spirit Wolf", "color": (150, 200, 255), "type": "spirit", "level": 1},
                            {"name": "Tree Guardian", "color": (80, 180, 60), "type": "nature", "level": 1},
                        ]
                        pet_idx = item.get("id", 0)
                        if pet_idx < len(creatures_data):
                            self.player.add_creature(dict(creatures_data[pet_idx]))
                    self.show_message(f"Bought {item_name}!", 2)
                    self.audio.play("collect")
                else:
                    self.show_message("Not enough Gold Leaves!", 2)

    def _handle_shop_hover(self, pos):
        self.shop_hovered = -1
        items_list = list(SHOP_ITEMS.keys())
        start_y = 100  # matches draw
        for i, item_name in enumerate(items_list):
            iy = start_y + i * 55
            if 70 <= pos[0] <= 1210 and iy <= pos[1] <= iy + 48:
                self.shop_hovered = i
                break

    def _draw_game_world(self):
        if not self.world or not self.player:
            # FIX: Minecraft-style corrupted save panel — GoStudios
            try:
                # wash world behind like menu
                for y in range(HEIGHT):
                    k=y/HEIGHT
                    r=int(110+k*30); g=int(190+k*20); b=255
                    pygame.draw.line(self.screen,(r,g,b),(0,y),(WIDTH,y))
                # dark overlay
                overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                overlay.fill((0,0,0,170))
                self.screen.blit(overlay,(0,0))
                # center stone panel
                bw,bh=560,280
                bx,by=WIDTH//2-bw//2, HEIGHT//2-bh//2
                pygame.draw.rect(self.screen,(32,32,35),(bx,by,bw,bh))
                pygame.draw.rect(self.screen,(0,0,0),(bx,by,bw,bh),2)
                pygame.draw.rect(self.screen,(85,85,85),(bx+2,by+2,bw-4,bh-4),2)
                title=pygame.font.Font(None,28).render("Save Corrupted", True, (255,80,80))
                self.screen.blit(title,(bx+20,by+16))
                msg1=pygame.font.Font(None,18).render("Your save is corrupted or missing.", True, (220,220,220))
                msg2=pygame.font.Font(None,16).render("Delete it and start a new game, or return to menu.", True, (180,180,180))
                self.screen.blit(msg1,(bx+20,by+50))
                self.screen.blit(msg2,(bx+20,by+72))
                # Minecraft stone buttons
                def mc_btn(rect, text):
                    pygame.draw.rect(self.screen,(0,0,0),rect)
                    inner=rect.inflate(-4,-4)
                    pygame.draw.rect(self.screen,(200,200,200),inner)
                    pygame.draw.line(self.screen,(255,255,255),inner.topleft, inner.topright,2)
                    txt=pygame.font.Font(None,18).render(text, True, (30,30,30))
                    self.screen.blit(txt,(rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
                btn1=pygame.Rect(bx+20, by+110, bw-40, 36)
                btn2=pygame.Rect(bx+20, by+160, bw-40, 36)
                btn3=pygame.Rect(bx+20, by+210, bw-40, 28)
                mc_btn(btn1, "Delete Save & New Game")
                mc_btn(btn2, "Back to Menu (ESC)")
                # hint
                hint=pygame.font.Font(None,12).render("GoStudios — corrupted saves auto-moved to .corrupt", True, (120,120,120))
                self.screen.blit(hint,(bx+20, by+bh-16))
                self._corrupt_new_rect=btn1
                self._corrupt_menu_rect=btn2
                self._corrupt_retry_rect=btn3
            except BaseException:
                pass
            return

        sky_color = self.day_night.get_sky_color()
        self.screen.fill(sky_color)

        light = self.day_night.get_light_level()

        self.world.draw(self.screen, int(self.camera_x), int(self.camera_y), self.time)

        # Draw creatures
        for creature in self.creatures:
            creature.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Draw expanded enemies
        for eenemy in self.expanded_enemies:
            eenemy.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Draw Astro Toilets — Skibidi (warp levitators)
        for astro in self.astro_toilets:
            astro.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Draw base buildings
        self.base_builder.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Draw bosses
        for boss in self.bosses:
            boss.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Go-live villagers (spawned when the countdown hits zero)
        for npc in self.npcs:
            npc.draw(self.screen, int(self.camera_x), int(self.camera_y), self.time)
        if not self.dialogue_box.active:
            for npc in self.npcs:
                if npc.is_in_range(self.player.x, self.player.y):
                    npc.draw_interaction(self.screen, self.player.x, self.player.y,
                                         int(self.camera_x), int(self.camera_y))
                    break

        # Draw mount (when not mounted by player)
        if self.mount and not self.mount.mounted:
            self.mount.draw(self.screen, int(self.camera_x), int(self.camera_y), False)

        # Player
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Mount UI when riding
        if self.mount and self.mount.mounted:
            self.mount.draw(self.screen, int(self.camera_x), int(self.camera_y), True)

        # Weapon trail particles
        for p in self.trail_particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            px = int(p["x"] - self.camera_x)
            py = int(p["y"] - self.camera_y)
            if 0 <= px <= WIDTH and 0 <= py <= HEIGHT:
                ps = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(ps, (*p["color"][:3], alpha), (3, 3), int(p["size"]))
                self.screen.blit(ps, (px - 3, py - 3))

        # Player particles
        self.player.particles.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Global particles
        self.particles.draw(self.screen, int(self.camera_x), int(self.camera_y))

        # Day/night overlay
        if light < 1.0:
            darkness = 1.0 - light
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 20, int(darkness * 150)))
            self.screen.blit(overlay, (0, 0))

        # Night stars
        if light < 0.5:
            star_alpha = int((0.5 - light) * 2 * 100)
            for i in range(30):
                sx = (i * 137 + 50) % WIDTH
                sy = (i * 97 + 20) % (HEIGHT // 2)
                sz = (i % 3) + 1
                pygame.draw.circle(self.screen, (*WHITE[:3], star_alpha), (sx, sy), sz)

        # Storm overlay
        self.storm.draw(self.screen, int(self.camera_x), int(self.camera_y))
        if self.storm.active and self.player:
            self.storm.draw_splash(self.screen, self.player.x, self.player.y,
                                   int(self.camera_x), int(self.camera_y))

        # HUD
        if self.state == GameState.PLAYING:
            self.hud.controller_connected = self.controller_connected
            self.hud.draw(self.screen, self.particles)
            self._draw_minimap_quest_markers()
            self._draw_mount_hud()
            if self.controller_connected:
                xbox_icons.draw_gameplay_prompts(self.screen, self._get_pressed_buttons())

        # Boss health bar
        if self.state == GameState.PLAYING:
            self.boss_health_bar.draw(self.screen)

        # Combo display
        if self.combo_display > 1:
            cf = pygame.font.Font(None, 30)
            combo_text = f"COMBO x{self.combo_display}"
            cs = cf.render(combo_text, True, GOLD)
            self.screen.blit(cs, (WIDTH // 2 - cs.get_width() // 2, HEIGHT - 140))

        # Round progress display
        if self.state == GameState.PLAYING and self.round_active and self.player:
            rd = self.round_data.get(self.current_round, {})
            needed = rd.get("enemies_needed", 10)
            rf = pygame.font.Font(None, 22)
            round_label = rf.render(f"Round {self.current_round}/{self.max_rounds}: {rd.get('name', '')}", True, GOLD)
            self.screen.blit(round_label, (10, 10))
            prog = min(self.round_enemies_killed, needed)
            prog_text = f"Enemies: {prog}/{needed}"
            if self.round_boss_spawned and not self.round_boss_defeated:
                prog_text = ">>> BOSS <<<"
                prog_color = RED
            else:
                prog_color = GREEN_GLOW if prog >= needed else (180, 180, 180)
            ps = rf.render(prog_text, True, prog_color)
            self.screen.blit(ps, (10, 30))
            bar_w = 150
            bar_h = 6
            bar_x = 10
            bar_y = 50
            pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, bar_y, bar_w, bar_h))
            fill_w = int(bar_w * min(self.round_enemies_killed / max(1, needed), 1.0))
            fill_color = GREEN_GLOW if not self.round_boss_spawned else RED
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_w, bar_h))

            if self.new_game_plus.ngp_level > 0:
                ngp_f = pygame.font.Font(None, 18)
                ngp_s = ngp_f.render(
                    f"NG+{self.new_game_plus.ngp_level} | x{self.new_game_plus.multiplier:.1f} enemy HP", True, MAGIC_PURPLE)
                self.screen.blit(ngp_s, (10, 62))

            self.pet_manager.draw_pet_bar(self.screen, self.player.creatures, HEIGHT - 100)

        # Chat display
        if self.state == GameState.PLAYING:
            self._draw_gameplay_chat()

        # Damage numbers
        for d in self.damage_numbers:
            dx = int(d["x"] - self.camera_x)
            dy = int(d["y"] - self.camera_y)
            df = pygame.font.Font(None, 24)
            ds = df.render(d["text"], True, d["color"])
            alpha = int(255 * d["timer"])
            ds.set_alpha(alpha)
            self.screen.blit(ds, (dx, dy))

        # Season event indicator
        if self.season.event_active:
            ef = pygame.font.Font(None, 22)
            event_text = f"Event: {self.season.event_type}"
            es = ef.render(event_text, True, (255, 200, 100))
            pygame.draw.rect(self.screen, (30, 20, 10, 180), (10, HEIGHT -
                             130, es.get_width() + 20, 30), border_radius=4)
            self.screen.blit(es, (20, HEIGHT - 125))

        # Storm indicator
        if self.storm.active:
            sf = pygame.font.Font(None, 26)
            t_left = max(0, self.storm.timer)
            intensity_bar = int(40 * self.storm.intensity)
            storm_text = f"STORM {int(t_left)}s"
            sts = sf.render(storm_text, True, (100, 150, 255))
            pygame.draw.rect(self.screen, (10, 15, 35, 200), (10, HEIGHT -
                             160, sts.get_width() + 30, 30), border_radius=4)
            pygame.draw.rect(self.screen, (60, 100, 200, 100), (10, HEIGHT - 160,
                             sts.get_width() + 30, 30), border_radius=4, width=1)
            self.screen.blit(sts, (25, HEIGHT - 157))
            bar_x = 25
            bar_y = HEIGHT - 135
            pygame.draw.rect(self.screen, (30, 30, 50), (bar_x, bar_y, 42, 6), border_radius=3)
            pygame.draw.rect(self.screen, (80, 130, 220), (bar_x, bar_y, intensity_bar, 6), border_radius=3)

        # Boss spawn warning
        if self.bosses and self.state == GameState.PLAYING:
            wf = pygame.font.Font(None, 22)
            for boss in self.bosses:
                dx = boss.x - self.player.x
                dy = boss.y - self.player.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 500 and boss.active:
                    warning = wf.render(f"BOSS: {boss.name} nearby!", True, (255, 80, 80))
                    self.screen.blit(warning, (WIDTH // 2 - warning.get_width() // 2, 50))

        # NPC dialogue box (top of the world, below HUD toasts)
        self.dialogue_box.draw(self.screen)

        # Message (skip when an overlay is open — toast drawn in global section instead)
        if self.message_timer > 0 and not self._any_overlay_open():
            alpha = int(255 * min(1, self.message_timer))
            msg_font = pygame.font.Font(None, 28)
            msg_surf = msg_font.render(self.message, True, (*GREEN_GLOW[:3], alpha))
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 190))
            bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
            bg.fill((10, 15, 10, min(180, alpha)))
            self.screen.blit(bg, (msg_rect.x - 10, msg_rect.y - 5))
            self.screen.blit(msg_surf, msg_rect)

    def _draw_minimap_quest_markers(self):
        mm_size = 150
        mm_x = WIDTH - mm_size - 20
        mm_y = 20
        scale = mm_size / max(WORLD_W, WORLD_H)
        border = 2

        # Minimap background
        pygame.draw.rect(self.screen, (10, 15, 10), (mm_x - border, mm_y - border,
                         mm_size + border * 2, mm_size + border * 2), border_radius=4)
        pygame.draw.rect(self.screen, (*
                                       GREEN_GLOW[:3], 80), (mm_x -
                                                             border, mm_y -
                                                             border, mm_size +
                                                             border *
                                                             2, mm_size +
                                                             border *
                                                             2), border, border_radius=4)

        # Draw terrain on minimap
        if self.world:
            chunk_px = max(1, int(mm_size / 30))
            for cx in range(0, mm_size, chunk_px):
                for cy in range(0, mm_size, chunk_px):
                    wx = int((cx / mm_size) * WORLD_W)
                    wy = int((cy / mm_size) * WORLD_H)
                    tile = self.world.get_tile(int(wx // TILE_SIZE), int(wy // TILE_SIZE))
                    if tile:
                        color = tile.color if hasattr(tile, 'color') else (20, 30, 20)
                        self.screen.set_at((mm_x + cx, mm_y + cy), color)

        # Player dot
        px = mm_x + int(self.player.x * scale)
        py = mm_y + int(self.player.y * scale)
        pygame.draw.circle(self.screen, GREEN_GLOW, (px, py), 4)
        pygame.draw.circle(self.screen, (150, 255, 180), (px, py), 2)

        # Enemy dots (red)
        for enemy in self.enemies:
            ex = mm_x + int(enemy.x * scale)
            ey = mm_y + int(enemy.y * scale)
            if mm_x <= ex <= mm_x + mm_size and mm_y <= ey <= mm_y + mm_size:
                pygame.draw.circle(self.screen, RED, (ex, ey), 2)

        # Expanded enemy dots (dark red)
        for eenemy in self.expanded_enemies:
            ex = mm_x + int(eenemy.x * scale)
            ey = mm_y + int(eenemy.y * scale)
            if mm_x <= ex <= mm_x + mm_size and mm_y <= ey <= mm_y + mm_size:
                pygame.draw.circle(self.screen, (150, 20, 20), (ex, ey), 2)

        # Resource dots (gold/colored)
        if self.world:
            for _ in range(15):
                rx = random.randint(0, WORLD_W - 1)
                ry = random.randint(0, WORLD_H - 1)
                tile = self.world.get_tile(int(rx // TILE_SIZE), int(ry // TILE_SIZE))
                if tile and tile.resource:
                    res_data = RESOURCES.get(tile.resource, {})
                    res_color = res_data.get("color", (200, 200, 100))
                    rmx = mm_x + int(rx * scale)
                    rmy = mm_y + int(ry * scale)
                    if mm_x <= rmx <= mm_x + mm_size and mm_y <= rmy <= mm_y + mm_size:
                        pygame.draw.circle(self.screen, res_color, (rmx, rmy), 1)

        # Creature dots (blue)
        for creature in self.creatures:
            cx2 = mm_x + int(creature.x * scale)
            cy2 = mm_y + int(creature.y * scale)
            if mm_x <= cx2 <= mm_x + mm_size and mm_y <= cy2 <= mm_y + mm_size:
                pygame.draw.circle(self.screen, (100, 150, 255), (cx2, cy2), 2)

        # Boss markers on minimap
        for boss in self.bosses:
            if boss.active:
                bx = mm_x + int(boss.x * scale)
                by = mm_y + int(boss.y * scale)
                pygame.draw.circle(self.screen, RED, (bx, by), 4)
                pygame.draw.circle(self.screen, (255, 100, 100), (bx, by), 6, 1)

    def _draw_mount_hud(self):
        if not self.mount:
            return
        mount_type = self.mount_cycle[self.selected_mount_type]
        unlocked = mount_type in self.mounts_unlocked
        name = MOUNT_TYPES[mount_type]["name"]
        status = "Ready" if unlocked else "Locked"
        color = GREEN_GLOW if unlocked else (100, 100, 100)

        mf = pygame.font.Font(None, 20)
        ms = mf.render(f"[M] Mount: {name} ({status})", True, color)
        self.screen.blit(ms, (WIDTH // 2 - ms.get_width() // 2, HEIGHT - 75))

        if self.mounts_unlocked:
            if self.controller_connected:
                xbox_icons.draw_menu_prompt(self.screen, [("LT", "M", "Mount"), ("LS", "R", "Sprint")], HEIGHT - 58)
            else:
                hint = mf.render("N/B to cycle  |  M to mount/dismount  |  R to sprint", True, (80, 120, 80))
                self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 58))

    def _draw_inventory(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        inv_x, inv_y = WIDTH // 4, HEIGHT // 6
        inv_w, inv_h = WIDTH // 2, HEIGHT * 2 // 3

        pygame.draw.rect(self.screen, (15, 20, 15), (inv_x, inv_y, inv_w, inv_h), border_radius=12)
        pygame.draw.rect(self.screen, (*GREEN_GLOW[:3], 60), (inv_x, inv_y, inv_w, inv_h), border_radius=12, width=2)

        title_f = pygame.font.Font(None, 40)
        title = title_f.render("INVENTORY", True, GOLD)
        self.screen.blit(title, (inv_x + 20, inv_y + 15))

        rf = pygame.font.Font(None, 24)
        ry = inv_y + 70
        rf_small = pygame.font.Font(None, 18)

        # Resources
        rl = rf_small.render("Resources:", True, (150, 200, 150))
        self.screen.blit(rl, (inv_x + 20, ry))
        ry += 25
        for res_name, amount in self.player.inventory.get("resources", {}).items():
            if amount > 0:
                rc = RESOURCES.get(res_name, {}).get("color", (200, 200, 200))
                rs = rf.render(f"  {res_name}: {int(amount)}", True, rc)
                self.screen.blit(rs, (inv_x + 30, ry))
                ry += 25

        # Items
        ry += 10
        il = rf_small.render("Items:", True, (150, 200, 150))
        self.screen.blit(il, (inv_x + 20, ry))
        ry += 25
        for item in self.player.inventory.get("items", []):
            it_s = rf.render(f"  - {item}", True, (200, 200, 150))
            self.screen.blit(it_s, (inv_x + 30, ry))
            ry += 25

        # Pets
        ry += 10
        pl = rf_small.render("Pets:", True, (150, 200, 150))
        self.screen.blit(pl, (inv_x + 20, ry))
        ry += 25
        for pet in self.player.creatures:
            pt_s = rf.render(f"  Lv.{int(pet.get('level', 1))} {pet['name']}", True, pet.get("color", (200, 200, 200)))
            self.screen.blit(pt_s, (inv_x + 30, ry))
            ry += 25

        # Mounts
        ry += 10
        ml = rf_small.render("Mounts:", True, (150, 200, 150))
        self.screen.blit(ml, (inv_x + 20, ry))
        ry += 25
        for mt in self.mount_cycle:
            unlocked = mt in self.mounts_unlocked
            mdata = MOUNT_TYPES[mt]
            mc = GREEN_GLOW if unlocked else (80, 80, 80)
            marker = " [UNLOCKED]" if unlocked else " [LOCKED]"
            ms = rf.render(f"  {mdata['name']}{marker}", True, mc)
            self.screen.blit(ms, (inv_x + 30, ry))
            ry += 25

        # Weapons
        ry += 10
        if self.controller_connected:
            wl = rf_small.render("Weapons:", True, (150, 200, 150))
        else:
            wl = rf_small.render("Weapons (press 1-8 to equip):", True, (150, 200, 150))
        self.screen.blit(wl, (inv_x + 20, ry))
        ry += 25
        weapons = self.player.inventory.get("weapons", [])
        equipped = self.player.weapon_id
        for i, wid in enumerate(weapons):
            if wid in WEAPONS:
                w = WEAPONS[wid]
                wname = w["name"]
                wdmg = w["damage"]
                wtype = w["type"]
                wcolor = w["color"]
                marker = " [EQUIPPED]" if wid == equipped else ""
                txt = f"  {i + 1}. {wname} (DMG:{wdmg} {wtype.upper()}){marker}"
                ws = rf.render(txt, True, wcolor if wid == equipped else (180, 180, 180))
                self.screen.blit(ws, (inv_x + 30, ry))
                ry += 25
        if not weapons:
            ns = rf.render("  No weapons crafted yet", True, (100, 100, 100))
            self.screen.blit(ns, (inv_x + 30, ry))

        # Equipment/Armor
        ry += 10
        el = rf_small.render("Equipment:", True, (150, 200, 150))
        self.screen.blit(el, (inv_x + 20, ry))
        ry += 25
        if hasattr(self.player, 'equipment') and self.player.equipment:
            for slot_name, armor_id in self.player.equipment.slots.items():
                if armor_id:
                    armor_data = ARMOR_TYPES.get(armor_id, {})
                    aname = armor_data.get("name", armor_id)
                    a_color = armor_data.get("color", (200, 200, 200))
                    ew = rf.render(
                        f"  [{
                            slot_name.upper()}] {aname} (DEF:{
                            armor_data.get(
                                'defense',
                                0)} HP:{
                            armor_data.get(
                                'hp_bonus',
                                0)})",
                        True,
                        a_color)
                    self.screen.blit(ew, (inv_x + 30, ry))
                else:
                    ew = rf.render(f"  [{slot_name.upper()}] Empty", True, (80, 80, 80))
                    self.screen.blit(ew, (inv_x + 30, ry))
                ry += 25
        else:
            ew = rf.render("  No equipment", True, (80, 80, 80))
            self.screen.blit(ew, (inv_x + 30, ry))

    def _draw_crafting(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        cr_x, cr_y = WIDTH // 4, HEIGHT // 6
        cr_w, cr_h = WIDTH // 2, HEIGHT * 2 // 3

        pygame.draw.rect(self.screen, (15, 20, 15), (cr_x, cr_y, cr_w, cr_h), border_radius=12)
        pygame.draw.rect(self.screen, (*GOLD[:3], 60), (cr_x, cr_y, cr_w, cr_h), border_radius=12, width=2)

        title_f = pygame.font.Font(None, 40)
        title = title_f.render("CRAFTING", True, GOLD)
        self.screen.blit(title, (cr_x + 20, cr_y + 15))

        cf = pygame.font.Font(None, 22)
        cy = cr_y + 70
        recipes_list = list(RECIPES.keys())
        for i, recipe_name in enumerate(recipes_list):
            recipe = RECIPES[recipe_name]
            can_craft = self.crafting.can_craft(recipe_name)
            color = GREEN_GLOW if can_craft else (120, 120, 120)
            can_text = " [CRAFT]" if can_craft else " [NEED RESOURCES]"

            ry = cy + i * 50
            pygame.draw.rect(self.screen, (25, 30, 25) if can_craft else (20, 20, 20),
                             (cr_x + 15, ry, cr_w - 30, 42), border_radius=6)
            pygame.draw.rect(self.screen, (*color[:3], 40),
                             (cr_x + 15, ry, cr_w - 30, 42), border_radius=6, width=1)

            rs = cf.render(f"{recipe_name}{can_text}", True, color)
            self.screen.blit(rs, (cr_x + 25, ry + 3))
            ings = ", ".join(f"{ing}x{amt}" for ing, amt in recipe["ingredients"].items())
            ing_s = cf.render(ings, True, (150, 150, 150))
            self.screen.blit(ing_s, (cr_x + 25, ry + 23))

    def _draw_settings(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        sx, sy = 80, 60
        sw, sh = WIDTH - 160, HEIGHT - 120
        pygame.draw.rect(self.screen, (15, 20, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(self.screen, (*CYAN[:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 44)
        ts = tf.render("SETTINGS", True, GOLD)
        self.screen.blit(ts, (sx + 20, sy + 15))

        # Account info in settings
        if self.account.current_user:
            user_data = self.account.get_user_data()
            if user_data:
                acct_f = pygame.font.Font(None, 22)
                acct_txt = f"GoStudios: {user_data['name']}  ({user_data['email']})"
                acct_s = acct_f.render(acct_txt, True, (100, 160, 100))
                self.screen.blit(acct_s, (sx + sw - acct_s.get_width() - 20, sy + 22))

        sf = pygame.font.Font(None, 28)
        sf_sm = pygame.font.Font(None, 22)
        sf_xs = pygame.font.Font(None, 18)

        settings_items = ["music_volume", "sfx_volume", "fullscreen", "show_fps",
                          "screen_shake", "show_damage_numbers", "auto_collect"]
        for i, key in enumerate(settings_items):
            iy = sy + 70 + i * 45
            is_hov = i == getattr(self, 'settings_hover', -1)
            if is_hov:
                pygame.draw.rect(self.screen, (*GREEN_GLOW[:3], 30), (sx + 10, iy, sw - 20, 35), border_radius=6)

            label = key.replace("_", " ").title()
            ls = sf.render(label, True, (200, 220, 200) if is_hov else (160, 170, 160))
            self.screen.blit(ls, (sx + 20, iy + 6))

            if key in ("music_volume", "sfx_volume"):
                val = self.settings[key]
                bar_x, bar_y, bar_w = 340, iy + 8, 340
                pygame.draw.rect(self.screen, (40, 40, 50), (bar_x, bar_y, bar_w, 14), border_radius=7)
                fill_w = int(bar_w * val)
                color = CYAN if key == "music_volume" else ORANGE
                pygame.draw.rect(self.screen, color, (bar_x, bar_y, fill_w, 14), border_radius=7)
                pygame.draw.circle(self.screen, WHITE, (bar_x + fill_w, bar_y + 7), 6)
                pct = sf_sm.render(f"{int(val * 100)}%", True, (200, 200, 200))
                self.screen.blit(pct, (bar_x + bar_w + 15, iy + 4))
            else:
                val = self.settings[key]
                on_off = "ON" if val else "OFF"
                color = GREEN_GLOW if val else (150, 60, 60)
                vs = sf.render(on_off, True, color)
                self.screen.blit(vs, (sx + sw - 120, iy + 6))

        ctrl_y = sy + sh - 200
        ch = sf_sm.render("CONTROLS", True, GOLD)
        self.screen.blit(ch, (sx + 20, ctrl_y))
        controls = DEFAULT_SETTINGS["controls"]
        for i, (action, key_bind) in enumerate(controls.items()):
            cx = sx + 30 + (i // 4) * 310
            cy = ctrl_y + 28 + (i % 4) * 22
            act_s = sf_xs.render(f"{action}:", True, (140, 160, 140))
            key_s = sf_xs.render(key_bind, True, (180, 200, 180))
            self.screen.blit(act_s, (cx, cy))
            self.screen.blit(key_s, (cx + 120, cy))

        if self.controller_connected:
            xbox_icons.draw_menu_prompt(self.screen, [("B", "ESC", "Back")], sy + sh - 25)
        else:
            hint = sf_xs.render("ESC to go back  |  Settings saved automatically", True, (80, 100, 80))
            self.screen.blit(hint, (sx + 20, sy + sh - 25))

        # Sign Out button in settings
        if self.account.current_user:
            so_x, so_y = sx + sw - 160, sy + sh - 45
            so_w, so_h = 140, 30
            so_hov = hasattr(self, 'settings_hover') and self.settings_hover == 999
            so_col = (200, 60, 60) if so_hov else (150, 40, 40)
            pygame.draw.rect(self.screen, so_col, (so_x, so_y, so_w, so_h), border_radius=4)
            pygame.draw.rect(self.screen, (255, 80, 80), (so_x, so_y, so_w, so_h), 1, border_radius=4)
            so_lbl = sf_sm.render("Sign Out", True, (255, 200, 200))
            self.screen.blit(so_lbl, (so_x + so_w // 2 - so_lbl.get_width() // 2, so_y + 5))

    def _draw_shop(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        sx, sy = 60, 40
        sw, sh = WIDTH - 120, HEIGHT - 80
        pygame.draw.rect(self.screen, (15, 15, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(self.screen, (*GOLD[:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 44)
        ts = tf.render("DATA STORE", True, GOLD)
        self.screen.blit(ts, (sx + 20, sy + 10))

        gold = self.player.inventory.get("resources", {}).get("Gold Leaves", 0)
        gf = pygame.font.Font(None, 30)
        gs = gf.render(f"Gold Leaves: {gold}", True, GOLD)
        self.screen.blit(gs, (sx + sw - 250, sy + 15))

        sf = pygame.font.Font(None, 24)
        sf_sm = pygame.font.Font(None, 18)

        items_list = list(SHOP_ITEMS.keys())
        start_y = sy + 60
        for i, item_name in enumerate(items_list):
            item = SHOP_ITEMS[item_name]
            iy = start_y + i * 55
            is_hov = i == self.shop_hovered

            if is_hov:
                pygame.draw.rect(self.screen, (*GREEN_GLOW[:3], 25), (sx + 10, iy, sw - 20, 48), border_radius=6)

            icon_c = item.get("icon_color", (200, 200, 200))
            pygame.draw.circle(self.screen, icon_c, (sx + 35, iy + 22), 12)
            pygame.draw.circle(self.screen, (*icon_c[:3], 60), (sx + 35, iy + 22), 16, 2)

            can_buy = gold >= item["price"]
            name_c = (220, 230, 220) if can_buy else (120, 120, 120)
            ns = sf.render(item_name, True, name_c)
            self.screen.blit(ns, (sx + 60, iy + 4))

            ds = sf_sm.render(item["desc"], True, (140, 150, 140))
            self.screen.blit(ds, (sx + 60, iy + 26))

            price_c = GOLD if can_buy else (150, 80, 80)
            ps = sf.render(f"{item['price']} Gold", True, price_c)
            self.screen.blit(ps, (sx + sw - 200, iy + 8))

            buy_color = GREEN_GLOW if can_buy else (80, 80, 80)
            buy_rect = pygame.Rect(sx + sw - 120, iy + 4, 100, 38)
            pygame.draw.rect(self.screen, (*buy_color[:3], 40), buy_rect, border_radius=6)
            pygame.draw.rect(self.screen, (*buy_color[:3], 80), buy_rect, border_radius=6, width=1)
            bs = sf.render("BUY", True, buy_color)
            self.screen.blit(bs, (buy_rect.centerx - bs.get_width() // 2, buy_rect.centery - bs.get_height() // 2))

        if self.controller_connected:
            xbox_icons.draw_menu_prompt(self.screen, [("S", "S", "Close"), ("A", "Click", "Buy")], sy + sh - 25)
        else:
            hint = sf_sm.render("S to close  |  Click BUY to purchase", True, (80, 100, 80))
            self.screen.blit(hint, (sx + 20, sy + sh - 25))

    def _draw_pause(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        pf = pygame.font.Font(None, 60)
        ps = pf.render("PAUSED", True, GOLD)
        self.screen.blit(ps, (WIDTH // 2 - ps.get_width() // 2, HEIGHT // 2 - 80))
        pf2 = pygame.font.Font(None, 28)
        if self.controller_connected:
            ph = pf2.render("START to resume  |  S for Settings", True, (150, 200, 150))
            self.screen.blit(ph, (WIDTH // 2 - ph.get_width() // 2, HEIGHT // 2))
            xbox_icons.draw_menu_prompt(
                self.screen, [
                    ("START", "ESC", "Resume"), ("B", "ESC", "Menu")], HEIGHT // 2 + 60)
        else:
            ph = pf2.render("ESC to resume  |  S for Settings", True, (150, 200, 150))
            self.screen.blit(ph, (WIDTH // 2 - ph.get_width() // 2, HEIGHT // 2))
        pf3 = pygame.font.Font(None, 22)
        if self.controller_connected:
            ps3 = pf3.render("Game auto-saves every 60s", True, (100, 140, 100))
        else:
            ps3 = pf3.render("F5 to save  |  Game auto-saves every 60s", True, (100, 140, 100))
        self.screen.blit(ps3, (WIDTH // 2 - ps3.get_width() // 2, HEIGHT // 2 + 35))

        # Touch/mouse-friendly pause buttons
        btn_w, btn_h = 260, 40
        cx = WIDTH // 2 - btn_w // 2
        self._pause_rects = {
            "resume": pygame.Rect(cx, HEIGHT // 2 + 70, btn_w, btn_h),
            "settings": pygame.Rect(cx, HEIGHT // 2 + 120, btn_w, btn_h),
            "menu": pygame.Rect(cx, HEIGHT // 2 + 170, btn_w, btn_h),
        }
        bf = pygame.font.Font(None, 26)
        for key_name, label in (("resume", "Resume"), ("settings", "Settings"), ("menu", "Main Menu")):
            r = self._pause_rects[key_name]
            pygame.draw.rect(self.screen, (30, 45, 30), r, border_radius=8)
            pygame.draw.rect(self.screen, GREEN_GLOW, r, 2, border_radius=8)
            ls = bf.render(label, True, (220, 255, 220))
            self.screen.blit(ls, ls.get_rect(center=r.center))

    def _draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        gf = pygame.font.Font(None, 80)
        gs = gf.render("FALLEN", True, RED)
        self.screen.blit(gs, (WIDTH // 2 - gs.get_width() // 2, HEIGHT // 2 - 80))

        gf2 = pygame.font.Font(None, 30)
        gh = gf2.render("The corruption overtook you...", True, (200, 200, 200))
        self.screen.blit(gh, (WIDTH // 2 - gh.get_width() // 2, HEIGHT // 2))

        gr = gf2.render("Press ENTER to return to menu", True, (150, 200, 150))
        self.screen.blit(gr, (WIDTH // 2 - gr.get_width() // 2, HEIGHT // 2 + 50))

        if self.controller_connected:
            xbox_icons.draw_menu_prompt(self.screen, [("A", "ENTER", "Return to Menu")], HEIGHT // 2 + 90)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.state = GameState.MAIN_MENU

    def _handle_lobby_click(self, pos):
        mx, my = pos
        lx, ly = WIDTH // 4, HEIGHT // 6
        lw, lh = WIDTH // 2, HEIGHT * 2 // 3

        if not self.multiplayer.connected:
            host_rect = pygame.Rect(lx + 20, ly + 100, 200, 40)
            if host_rect.collidepoint(mx, my):
                self.multiplayer.host_game(self.player.name)
                self.audio.play("lobby_connect")
                self.show_message("Hosting game on port 7777...", 3)
                return

            join_rect = pygame.Rect(lx + 240, ly + 100, 200, 40)
            if join_rect.collidepoint(mx, my):
                self.multiplayer.join_game("localhost", self.player.name)
                self.audio.play("lobby_connect")
                self.show_message("Joining game...", 3)
                return
        else:
            disc_rect = pygame.Rect(lx + 20, ly + 100, 200, 40)
            if disc_rect.collidepoint(mx, my):
                self.multiplayer.disconnect()
                self.audio.play("lobby_disconnect")
                self.show_message("Disconnected from server", 2)
                return

    def _handle_locker_click(self, pos):
        mx, my = pos
        tabs = ["hat", "body_color", "trail_color", "aura", "title", "pet_skin"]
        for i, tab in enumerate(tabs):
            tx = 100 + i * 100
            if tx <= mx <= tx + 80 and 80 <= my <= 105:
                self.locker_tab = tab
                self.audio.play("tab_switch")
                return

        items = self.cosmetics_unlocked.get(self.locker_tab, [])
        for i, item in enumerate(items):
            ix = 100
            iy = 130 + i * 40
            if ix <= mx <= ix + 200 and iy <= my <= iy + 35:
                self.cosmetics[self.locker_tab] = item if item != "none" else None
                self.show_message(f"Equipped: {item.replace('_', ' ').title()}", 2)
                self.audio.play("equip")
                return

    def _draw_locker(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        lx, ly = 60, 40
        lw, lh = WIDTH - 120, HEIGHT - 80
        pygame.draw.rect(self.screen, (15, 15, 25), (lx, ly, lw, lh), border_radius=12)
        pygame.draw.rect(self.screen, (*GOLD[:3], 60), (lx, ly, lw, lh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 44)
        ts = tf.render("LOCKER / DRESSUP", True, GOLD)
        self.screen.blit(ts, (lx + 20, ly + 10))

        tabs = ["hat", "body_color", "trail_color", "aura", "title", "pet_skin"]
        for i, tab in enumerate(tabs):
            tx = lx + 20 + i * 110
            ty = ly + 60
            is_sel = tab == self.locker_tab
            color = GOLD if is_sel else (120, 120, 120)
            tab_f = pygame.font.Font(None, 20)
            tab_s = tab_f.render(tab.replace("_", " ").title(), True, color)
            self.screen.blit(tab_s, (tx, ty))
            if is_sel:
                pygame.draw.line(self.screen, GOLD, (tx, ty + 18), (tx + tab_s.get_width(), ty + 18), 2)

        items = self.cosmetics_unlocked.get(self.locker_tab, [])
        bf = pygame.font.Font(None, 24)
        y = ly + 100
        for i, item in enumerate(items):
            is_sel = self.cosmetics.get(
                self.locker_tab) == item or (
                item == "none" and self.cosmetics.get(
                    self.locker_tab) is None)
            color = GREEN_GLOW if is_sel else (180, 180, 180)
            display = item.replace("_", " ").title() if item != "none" else "None"
            bs = bf.render(display, True, color)
            self.screen.blit(bs, (lx + 30, y))

            if is_sel:
                indicator = bf.render("[EQUIPPED]", True, GREEN_GLOW)
                self.screen.blit(indicator, (lx + 250, y))

            y += 35

        # Preview
        preview_x = lx + lw - 200
        preview_y = ly + lh // 2
        body_color = (200, 180, 160)
        if self.cosmetics.get("body_color"):
            color_map = {
                "crimson": (220, 60, 60), "azure": (60, 120, 220),
                "emerald": (60, 180, 80), "shadow": (80, 60, 120),
                "gold": (220, 180, 50), "rainbow": (200, 100, 200),
            }
            body_color = color_map.get(self.cosmetics["body_color"], body_color)

        glow_r = 50 + int(math.sin(self.time * 2) * 5)
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (*body_color[:3], 30), (glow_r, glow_r), glow_r)
        self.screen.blit(glow_s, (preview_x - glow_r, preview_y - glow_r))

        pygame.draw.circle(self.screen, body_color, (preview_x, preview_y), 30)
        pygame.draw.circle(self.screen, (*body_color[:3], 80), (preview_x, preview_y), 35, 2)

        if self.cosmetics.get("hat"):
            hat_map = {
                "crown": GOLD, "hood": (100, 100, 120),
                "helmet": (150, 150, 160), "flower_crown": PINK,
                "shadow_mask": (40, 20, 60),
            }
            hat_color = hat_map.get(self.cosmetics["hat"], GOLD)
            if self.cosmetics["hat"] == "crown":
                pygame.draw.polygon(self.screen, hat_color, [
                    (preview_x - 12, preview_y - 30), (preview_x - 8, preview_y - 42),
                    (preview_x, preview_y - 36), (preview_x + 8, preview_y - 42),
                    (preview_x + 12, preview_y - 30)
                ])
            elif self.cosmetics["hat"] == "hood":
                pygame.draw.arc(self.screen, hat_color, (preview_x - 18, preview_y - 45, 36, 30), 0, 3.14, 3)
            elif self.cosmetics["hat"] == "helmet":
                pygame.draw.rect(self.screen, hat_color, (preview_x - 14, preview_y - 42, 28, 16))
            elif self.cosmetics["hat"] == "flower_crown":
                for i in range(5):
                    angle = i * 1.26
                    fx = preview_x + math.cos(angle) * 16
                    fy = preview_y - 30 + math.sin(angle) * 6
                    pygame.draw.circle(self.screen, (255, 150, 200), (int(fx), int(fy)), 4)
            elif self.cosmetics["hat"] == "shadow_mask":
                pygame.draw.ellipse(self.screen, hat_color, (preview_x - 12, preview_y - 28, 24, 10))

        if self.cosmetics.get("aura"):
            aura_map = {
                "fire": (255, 100, 30), "ice": (100, 200, 255),
                "shadow": (100, 40, 160), "nature": (60, 200, 80),
                "crystal": CRYSTAL, "golden": GOLD,
            }
            aura_color = aura_map.get(self.cosmetics["aura"], GREEN_GLOW)
            for i in range(3):
                angle = self.time * 2 + i * 2.1
                ax = preview_x + math.cos(angle) * 40
                ay = preview_y + math.sin(angle) * 40
                pygame.draw.circle(self.screen, aura_color, (int(ax), int(ay)), 4)

        pf = pygame.font.Font(None, 22)
        ps = pf.render("PREVIEW", True, (150, 150, 150))
        self.screen.blit(ps, (preview_x - ps.get_width() // 2, preview_y + 45))

        if self.controller_connected:
            xbox_icons.draw_menu_prompt(self.screen, [("A", "Click", "Equip"), ("BACK", "ESC", "Close")], ly + lh - 25)
        else:
            hint = pygame.font.Font(None, 18).render("Click to equip  |  ESC to close", True, (80, 100, 80))
            self.screen.blit(hint, (lx + 20, ly + lh - 25))

    def _draw_lobby(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        lx, ly = WIDTH // 4, HEIGHT // 6
        lw, lh = WIDTH // 2, HEIGHT * 2 // 3
        pygame.draw.rect(self.screen, (15, 20, 30), (lx, ly, lw, lh), border_radius=12)
        pygame.draw.rect(self.screen, (*CYAN[:3], 60), (lx, ly, lw, lh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 44)
        ts = tf.render("LOBBY", True, CYAN)
        self.screen.blit(ts, (lx + 20, ly + 10))

        sf = pygame.font.Font(None, 24)
        sf_sm = pygame.font.Font(None, 20)

        iy = ly + 60
        status = "HOST" if self.multiplayer.is_host else ("CLIENT" if self.multiplayer.is_client else "OFFLINE")
        color = GREEN_GLOW if self.multiplayer.is_host else (CYAN if self.multiplayer.is_client else (120, 120, 120))
        ss = sf.render(f"Status: {status}", True, color)
        self.screen.blit(ss, (lx + 20, iy))

        if self.multiplayer.connected:
            player_count = self.multiplayer.server.get_player_count() if self.multiplayer.server else 0
            pc = sf.render(f"Players: {player_count}", True, GREEN_GLOW)
            self.screen.blit(pc, (lx + lw - 150, iy))

        iy += 40
        if not self.multiplayer.connected:
            # Host button
            host_rect = pygame.Rect(lx + 20, iy, 200, 40)
            pygame.draw.rect(self.screen, (30, 40, 30), host_rect, border_radius=6)
            pygame.draw.rect(self.screen, (*GREEN_GLOW[:3], 60), host_rect, border_radius=6, width=1)
            hs = sf.render("Host Game", True, GREEN_GLOW)
            self.screen.blit(hs, (lx + 60, iy + 8))

            # Join button
            join_rect = pygame.Rect(lx + 240, iy, 200, 40)
            pygame.draw.rect(self.screen, (30, 30, 40), join_rect, border_radius=6)
            pygame.draw.rect(self.screen, (*CYAN[:3], 60), join_rect, border_radius=6, width=1)
            js = sf.render("Join Game", True, CYAN)
            self.screen.blit(js, (lx + 280, iy + 8))
        else:
            disc_rect = pygame.Rect(lx + 20, iy, 200, 40)
            pygame.draw.rect(self.screen, (40, 20, 20), disc_rect, border_radius=6)
            pygame.draw.rect(self.screen, (*RED[:3], 60), disc_rect, border_radius=6, width=1)
            ds = sf.render("Disconnect", True, RED)
            self.screen.blit(ds, (lx + 55, iy + 8))

        iy += 60
        chat_label = sf.render("Chat:", True, GOLD)
        self.screen.blit(chat_label, (lx + 20, iy))
        iy += 25

        chat_bg = pygame.Surface((lw - 40, 120), pygame.SRCALPHA)
        chat_bg.fill((10, 10, 20, 180))
        self.screen.blit(chat_bg, (lx + 20, iy))

        if self.multiplayer.client:
            for msg in self.multiplayer.client.chat_messages[-5:]:
                ms = sf_sm.render(f"{msg['from']}: {msg['text']}", True, (180, 180, 200))
                self.screen.blit(ms, (lx + 25, iy + 5))
                iy += 20

        iy += 130
        if self.controller_connected:
            xbox_icons.draw_menu_prompt(self.screen, [("A", "Click", "Host/Join"), ("B", "ESC", "Close")], ly + lh - 25)
        else:
            hint = sf_sm.render("F9 to quick host  |  ESC to close", True, (80, 100, 80))
            self.screen.blit(hint, (lx + 20, ly + lh - 25))

    def _draw_profile(self):
        # Minecraft-style Profile — dark overlay + centered stone panel with Steve
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        bw, bh = 560, 420
        bx, by = WIDTH//2 - bw//2, HEIGHT//2 - bh//2
        # panel like Minecraft login
        pygame.draw.rect(self.screen, (32, 32, 35), (bx, by, bw, bh))
        pygame.draw.rect(self.screen, (0, 0, 0), (bx, by, bw, bh), 2)
        pygame.draw.rect(self.screen, (85, 85, 85), (bx+2, by+2, bw-4, bh-4), 2)
        # Title PLAYTREE Profile
        title = pygame.font.Font(None, 36).render("Profile", True, (255, 255, 255))
        self.screen.blit(title, (bx + 20, by + 14))
        # Steve-like character
        cx, cy = bx + 90, by + 120
        pygame.draw.rect(self.screen, (222,180,140), (cx-20, cy, 40, 36)) # head
        pygame.draw.rect(self.screen, (80,60,30), (cx-20, cy, 40, 10)) # hair
        pygame.draw.rect(self.screen, (60,180,180), (cx-18, cy+36, 36, 40)) # body
        pygame.draw.rect(self.screen, (60,60,180), (cx-16, cy+76, 14, 28))
        pygame.draw.rect(self.screen, (60,60,180), (cx+4, cy+76, 14, 28))
        # GoStudios account info
        user = self.account.get_user_data() if hasattr(self, 'account') else None
        name = user.get("name", "Steve") if user else "Steve"
        email = user.get("email", "guest@playtree.local") if user else "Not signed in"
        f = pygame.font.Font(None, 22)
        nf = f.render(name, True, (255,255,255))
        self.screen.blit(nf, (bx+170, by+90))
        ef = pygame.font.Font(None, 16).render(email, True, (180,180,180))
        self.screen.blit(ef, (bx+170, by+116))
        # GoStudios badge
        badge = pygame.font.Font(None, 14).render("GoStudios Account", True, (80,255,120))
        self.screen.blit(badge, (bx+170, by+140))
        # Buttons like Minecraft stone
        def mc_btn(rect, text):
            pygame.draw.rect(self.screen, (0,0,0), rect)
            inner = rect.inflate(-4,-4)
            pygame.draw.rect(self.screen, (200,200,200), inner)
            pygame.draw.line(self.screen, (255,255,255), inner.topleft, inner.topright, 2)
            txt = pygame.font.Font(None, 18).render(text, True, (30,30,30))
            self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
        btn_w, btn_h = 200, 32
        mc_btn(pygame.Rect(bx+170, by+180, btn_w, btn_h), "Sign Out")
        self._profile_signout_rect = pygame.Rect(bx+170, by+180, btn_w, btn_h)
        mc_btn(pygame.Rect(bx+170, by+222, btn_w, btn_h), "Change Skin")
        self._profile_skin_rect = pygame.Rect(bx+170, by+222, btn_w, btn_h)
        mc_btn(pygame.Rect(bx+170, by+264, btn_w, btn_h), "Close")
        self._profile_close_rect = pygame.Rect(bx+170, by+264, btn_w, btn_h)
        # version
        ver = pygame.font.Font(None, 12).render("PlayTree Corporation • GoStudios", True, (120,120,120))
        self.screen.blit(ver, (bx+20, by+bh-16))

    def _draw_marketplace(self):
        # Minecraft Marketplace — dark overlay + grid of featured PlayTree content
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))
        bw, bh = 900, 520
        bx, by = WIDTH//2 - bw//2, HEIGHT//2 - bh//2
        pygame.draw.rect(self.screen, (32,32,35), (bx, by, bw, bh))
        pygame.draw.rect(self.screen, (0,0,0), (bx, by, bw, bh), 2)
        pygame.draw.rect(self.screen, (85,85,85), (bx+2, by+2, bw-4, bh-4), 2)
        title = pygame.font.Font(None, 34).render("Marketplace", True, (255,255,255))
        self.screen.blit(title, (bx+20, by+14))
        sub = pygame.font.Font(None, 14).render("PlayTree Corporation • GoConsole Game Studios — Featured", True, (180,200,180))
        self.screen.blit(sub, (bx+20, by+42))
        # Featured grid 3x2 like Minecraft
        items = [
            ("Forest Pack", "Biomes + Trees", (80,180,90)),
            ("Crystal Caverns", "World Template", (120,140,200)),
            ("Shadow Skins", "12 Skins", (80,60,120)),
            ("GoConsole Bundle", "Mounts + Pets", (200,170,80)),
            ("Starter Kit", "Tools + Gold", (180,120,60)),
            ("Beta Access", "Chapter 0", (200,80,80)),
        ]
        self._market_view_rects = []
        for i, (name, desc, col) in enumerate(items):
            x = bx+20 + (i%3)*285
            y = by+70 + (i//3)*190
            card = pygame.Rect(x, y, 270, 170)
            pygame.draw.rect(self.screen, col, card)
            pygame.draw.rect(self.screen, (0,0,0), card, 2)
            # icon placeholder
            pygame.draw.rect(self.screen, (255,255,255,60), (x+10, y+10, 50, 50))
            ntxt = pygame.font.Font(None, 18).render(name, True, (255,255,255))
            self.screen.blit(ntxt, (x+70, y+18))
            dtxt = pygame.font.Font(None, 12).render(desc, True, (230,230,230))
            self.screen.blit(dtxt, (x+70, y+38))
            # Minecoins price
            price = pygame.font.Font(None, 14).render("0 Minecoins", True, (255,220,80))
            self.screen.blit(price, (x+10, y+140))
            # View button
            btn = pygame.Rect(x+150, y+135, 110, 24)
            pygame.draw.rect(self.screen, (80,200,80), btn)
            pygame.draw.rect(self.screen, (0,0,0), btn, 1)
            btxt = pygame.font.Font(None, 14).render("View", True, (20,30,20))
            self.screen.blit(btxt, (btn.centerx - btxt.get_width()//2, btn.centery - btxt.get_height()//2))
            self._market_view_rects.append((name, btn))
        # Close
        close = pygame.Rect(bx+bw//2 - 100, by+bh-40, 200, 32)
        pygame.draw.rect(self.screen, (200,200,200), close)
        pygame.draw.rect(self.screen, (0,0,0), close, 2)
        ctxt = pygame.font.Font(None, 18).render("Close", True, (30,30,30))
        self.screen.blit(ctxt, (close.centerx - ctxt.get_width()//2, close.centery - ctxt.get_height()//2))
        self._market_close_rect = close

    def _draw_games_panel(self):
        s = self.screen
        panel = pygame.Rect((WIDTH - 760) // 2, 70, 760, 560)
        dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        s.blit(dim, (0, 0))
        pygame.draw.rect(s, (14, 19, 32), panel, border_radius=14)
        pygame.draw.rect(s, (89, 196, 143), panel, 2, border_radius=14)
        f32 = pygame.font.Font(None, 34)
        f22 = pygame.font.Font(None, 22)
        f20 = pygame.font.Font(None, 20)
        title = f32.render("PLAYTREE GAMES", True, (89, 255, 157))
        s.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 14))
        sub = f20.render("Rate, favourite and chat on the website — install games here", True, (143, 183, 160))
        s.blit(sub, (panel.centerx - sub.get_width() // 2, panel.y + 52))
        self._games_rects = {}
        rows_y = panel.y + 86
        for i, g in enumerate(GAMES_CATALOG):
            r = pygame.Rect(panel.x + 24, rows_y + i * 38, panel.w - 48, 34)
            sel = (i == self.games_selected)
            pygame.draw.rect(s, (44, 110, 79) if sel else (30, 42, 66), r, border_radius=7)
            pygame.draw.rect(s, (89, 255, 157) if sel else (60, 76, 100), r, 1, border_radius=7)
            s.blit(f22.render(g["title"], True, (234, 255, 242)), (r.x + 12, r.y + 7))
            plat = f20.render(g["plat"], True, (143, 183, 160))
            s.blit(plat, (r.right - plat.get_width() - 12, r.y + 9))
            self._games_rects["row%d" % i] = r
        by = rows_y + len(GAMES_CATALOG) * 38 + 14
        btns = [
            ("GET", panel.x + 24, (255, 215, 90)),
            ("WEBSITE", panel.x + 150, (89, 196, 143)),
            ("CLOSE", panel.right - 130, (200, 90, 90)),
        ]
        for name, bx, col in btns:
            rect = pygame.Rect(bx, by, 118, 40)
            pygame.draw.rect(s, col, rect, border_radius=8)
            txt = f22.render(name, True, (14, 19, 32))
            s.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))
            self._games_rects[name] = rect
        if self.games_status:
            st = f20.render(self.games_status, True, (255, 215, 90))
            s.blit(st, (panel.centerx - st.get_width() // 2, by + 50))
        hint = f20.render("Arrows/Enter or tap — ESC closes · GET downloads the game free", True, (120, 140, 160))
        s.blit(hint, (panel.centerx - hint.get_width() // 2, by + 76))

    def _handle_games_click(self, pos):
        for i in range(len(GAMES_CATALOG)):
            r = self._games_rects.get("row%d" % i)
            if r and r.collidepoint(pos):
                self.games_selected = i
                self.games_status = GAMES_CATALOG[i]["title"] + " selected"
                self.audio.play("menu_hover")
                return True
        g = GAMES_CATALOG[self.games_selected]
        if self._games_rects.get("GET") and self._games_rects["GET"].collidepoint(pos):
            try:
                import webbrowser
                url = "https://raw.githubusercontent.com/GoStudios-Real/PlayTree/master/" + (g["zip"] or "standalone/PLAYTREE.exe")
                webbrowser.open(url)
                self.games_status = "Downloading " + g["title"] + " ..."
                self.audio.play("menu_select")
            except Exception as exc:
                self.games_status = "Could not open browser: %s" % exc
            return True
        if self._games_rects.get("WEBSITE") and self._games_rects["WEBSITE"].collidepoint(pos):
            try:
                import webbrowser
                webbrowser.open("https://github.com/GoStudios-Real/PlayTree")
                self.games_status = "Opened the PlayTree Games page"
                self.audio.play("menu_select")
            except Exception as exc:
                self.games_status = "Could not open browser: %s" % exc
            return True
        if self._games_rects.get("CLOSE") and self._games_rects["CLOSE"].collidepoint(pos):
            self.games_open = False
            self.audio.play("menu_select")
            return True
        return False

    def _draw_round_intro(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        self.screen.blit(overlay, (0, 0))

        rd = self.round_data.get(self.current_round, {})
        t = self.round_intro_timer

        # Round number
        rf = pygame.font.Font(None, 80)
        rs = rf.render(f"ROUND {self.current_round}", True, GOLD)
        alpha = min(255, int(t * 120))
        rs.set_alpha(alpha)
        self.screen.blit(rs, (WIDTH // 2 - rs.get_width() // 2, HEIGHT // 3 - 60))

        # Round name
        nf = pygame.font.Font(None, 40)
        ns = nf.render(rd.get("name", "Unknown"), True, GREEN_GLOW)
        alpha2 = min(255, max(0, int((t - 0.8) * 120)))
        ns.set_alpha(alpha2)
        self.screen.blit(ns, (WIDTH // 2 - ns.get_width() // 2, HEIGHT // 3))

        # Story text
        sf = pygame.font.Font(None, 26)
        story_lines = rd.get("story", "").split("\n")
        for i, line in enumerate(story_lines):
            ss = sf.render(line, True, (180, 200, 180))
            alpha3 = min(255, max(0, int((t - 1.6 - i * 0.3) * 100)))
            ss.set_alpha(alpha3)
            self.screen.blit(ss, (WIDTH // 2 - ss.get_width() // 2, HEIGHT // 3 + 60 + i * 30))

        # Boss preview
        if t > 2.5:
            boss_name = BOSS_TYPES.get(rd.get("boss", ""), {}).get("name", "???")
            bf = pygame.font.Font(None, 32)
            bs = bf.render(f"Boss: {boss_name}", True, RED)
            alpha4 = min(255, int((t - 2.5) * 100))
            bs.set_alpha(alpha4)
            self.screen.blit(bs, (WIDTH // 2 - bs.get_width() // 2, HEIGHT // 3 + 140))

            # Enemy count
            ef = pygame.font.Font(None, 24)
            needed = rd.get("enemies_needed", 10)
            es = ef.render(f"Defeat {needed} enemies to summon the boss", True, (150, 150, 150))
            es.set_alpha(alpha4)
            self.screen.blit(es, (WIDTH // 2 - es.get_width() // 2, HEIGHT // 3 + 180))

        # Hint
        if t > 1:
            if self.controller_connected:
                xbox_icons.draw_dual_prompt(self.screen, WIDTH // 2 - 30, HEIGHT - 80, "A", "ENTER", "Begin", 18)
            else:
                hf = pygame.font.Font(None, 20)
                hs = hf.render("Press ENTER to begin or wait...", True, (100, 100, 100))
                hs.set_alpha(min(255, int((t - 1) * 60)))
                self.screen.blit(hs, (WIDTH // 2 - hs.get_width() // 2, HEIGHT - 80))

    def _draw_end_credits(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 250))
        self.screen.blit(overlay, (0, 0))

        t = self.credits_timer

        credits_data = [
            (0.0, 3.0, "THE END", GOLD, 60),
            (3.5, 6.5, "The corruption has been vanquished.", (180, 200, 180), 30),
            (7.0, 10.0, "Balance is restored to the world.", (180, 200, 180), 30),
            (10.5, 13.5, "The PlayTree blooms once more.", GREEN_GLOW, 30),
            (14.5, 17.0, "Thank you for playing.", (200, 200, 200), 36),
            (18.0, 22.0, "PLAYTREE", GOLD, 70),
            (22.5, 25.5, "A game by", (150, 150, 150), 24),
            (26.0, 29.0, "GoConsole Game Studios", (200, 180, 140), 40),
            (29.5, 32.5, "GoStudios", (180, 200, 220), 40),
            (33.0, 36.0, "PLAYTREE GAMES", GREEN_GLOW, 40),
            (37.0, 40.0, "Special Thanks", (150, 150, 150), 28),
            (40.5, 43.5, "To all who played and believed", (180, 180, 200), 26),
        ]

        if self.new_game_plus.unlocked:
            credits_data.append((35.0, 40.0, f"NEW GAME+ {self.new_game_plus.ngp_level} UNLOCKED!", MAGIC_PURPLE, 36))
            credits_data.append(
                (41.0, 44.0, f"Enemy HP x{
                    self.new_game_plus.multiplier:.1f} | Player XP x{
                    self.new_game_plus.get_xp_mult():.2f}", (180, 140, 255), 22))
            credits_data.append((44.5, 47.5, "Enemies grow stronger... but so do you.", (200, 180, 255), 24))

        credits_data.append(
            (48.0, 999.0, "Press ENTER to return to menu" if not self.controller_connected else "", (100, 120, 100), 22))

        for start, end, text, color, size in credits_data:
            if start <= t < end:
                f = pygame.font.Font(None, size)
                s = f.render(text, True, color)
                if t - start < 0.5:
                    s.set_alpha(int((t - start) * 2 * 255))
                elif end - t < 0.5 and end < 48:
                    s.set_alpha(int((end - t) * 2 * 255))
                else:
                    s.set_alpha(255)
                self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 - size // 2 + 40))

        scroll_lines = [
            "GoConsole Game Studios",
            "GoStudios",
            "PLAYTREE GAMES",
            "Thank you for playing PLAYTREE",
        ]
        sf = pygame.font.Font(None, 18)
        for i, line in enumerate(scroll_lines):
            y = HEIGHT - 50 + i * 22 - int(t * 15) % (len(scroll_lines) * 22 + HEIGHT)
            if -20 < y < HEIGHT + 20:
                ss = sf.render(line, True, (60, 80, 60))
                self.screen.blit(ss, (WIDTH // 2 - ss.get_width() // 2, y))

        if t > 48:
            if self.controller_connected:
                xbox_icons.draw_menu_prompt(self.screen, [("A", "ENTER", "Return to Menu")], HEIGHT - 80)
            else:
                hf_end = pygame.font.Font(None, 22)
                hs_end = hf_end.render("Press ENTER to return to menu", True, (100, 120, 100))
                self.screen.blit(hs_end, (WIDTH // 2 - hs_end.get_width() // 2, HEIGHT - 80))

    def _draw_gameplay_chat(self):
        if not self.multiplayer.connected:
            return
        chat_x = 10
        chat_y = HEIGHT - 180
        chat_w = 300
        chat_h = 120

        bg = pygame.Surface((chat_w, chat_h), pygame.SRCALPHA)
        bg.fill((10, 10, 20, 140))
        self.screen.blit(bg, (chat_x, chat_y))

        cf = pygame.font.Font(None, 18)

        messages = []
        if self.multiplayer.client:
            messages = self.multiplayer.client.chat_messages[-6:]
        elif self.multiplayer.server and self.multiplayer.server.local_messages:
            messages = self.multiplayer.server.local_messages[-6:]

        for i, msg in enumerate(messages):
            name = msg.get("from", "???")
            text = msg.get("text", "")
            ts = cf.render(f"{name}: {text}", True, (180, 200, 220))
            self.screen.blit(ts, (chat_x + 5, chat_y + 5 + i * 17))

        if self.multiplayer.typing_chat:
            input_bg = pygame.Surface((chat_w, 22), pygame.SRCALPHA)
            input_bg.fill((20, 20, 40, 200))
            self.screen.blit(input_bg, (chat_x, chat_y + chat_h - 24))
            prompt = f"> {self.multiplayer.chat_input}_"
            ps = cf.render(prompt, True, GREEN_GLOW)
            self.screen.blit(ps, (chat_x + 5, chat_y + chat_h - 20))
        elif self.multiplayer.connected:
            hint_f = pygame.font.Font(None, 15)
            if self.controller_connected:
                hs = hint_f.render("Press [T] to chat", True, (80, 90, 100))
            else:
                hs = hint_f.render("Press T to chat", True, (80, 90, 100))
            self.screen.blit(hs, (chat_x + 5, chat_y + chat_h - 18))
