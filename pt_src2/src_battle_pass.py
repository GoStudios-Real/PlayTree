import pygame
import math
from config import *

SEASONS = {
    0: {
        "name": "Season 0: Awakening",
        "theme": "nature",
        "color": GREEN_GLOW,
        "accent": (60, 200, 100),
        "duration_days": 30,
        "tiers": 50,
    },
    1: {
        "name": "Season 1: Crystal Storm",
        "theme": "crystal",
        "color": CRYSTAL,
        "accent": (180, 120, 255),
        "duration_days": 30,
        "tiers": 50,
    },
    2: {
        "name": "Season 2: Shadow Fall",
        "theme": "shadow",
        "color": PURPLE,
        "accent": (160, 80, 255),
        "duration_days": 30,
        "tiers": 50,
    },
}

TIER_REWARDS = {
    1: {"type": "title", "name": "Novice", "desc": "Title: Novice"},
    2: {"type": "resource", "name": "Tree Energy x20", "desc": "+20 Tree Energy", "resources": {"Tree Energy": 20}},
    3: {"type": "emote", "name": "Wave", "desc": "Emote: Wave"},
    5: {"type": "resource", "name": "Crystal Dust x15", "desc": "+15 Crystal Dust", "resources": {"Crystal Dust": 15}},
    7: {"type": "title", "name": "Explorer", "desc": "Title: Explorer"},
    8: {"type": "resource", "name": "Ancient Seeds x10", "desc": "+10 Ancient Seeds", "resources": {"Ancient Seeds": 10}},
    10: {"type": "weapon_skin", "name": "Emerald Blade", "desc": "Sword skin: Emerald"},
    12: {"type": "resource", "name": "Light Fragments x5", "desc": "+5 Light Fragments", "resources": {"Light Fragments": 5}},
    15: {"type": "mount_skin", "name": "Golden Stag", "desc": "Mount skin: Golden Stag"},
    17: {"type": "resource", "name": "Gold Leaves x100", "desc": "+100 Gold Leaves", "resources": {"Gold Leaves": 100}},
    20: {"type": "title", "name": "Warrior", "desc": "Title: Warrior"},
    22: {"type": "resource", "name": "Shadow Essence x10", "desc": "+10 Shadow Essence", "resources": {"Shadow Essence": 10}},
    25: {"type": "pet_skin", "name": "Crystal Fox", "desc": "Pet skin: Crystal Fox"},
    27: {"type": "resource", "name": "Ancient Root x5", "desc": "+5 Ancient Root", "resources": {"Ancient Root": 5}},
    30: {"type": "weapon", "name": "Seasonal Blade", "desc": "Exclusive: Seasonal Blade"},
    32: {"type": "resource", "name": "Light Fragments x15", "desc": "+15 Light Fragments", "resources": {"Light Fragments": 15}},
    35: {"type": "title", "name": "Champion", "desc": "Title: Champion"},
    37: {"type": "resource", "name": "Gold Leaves x200", "desc": "+200 Gold Leaves", "resources": {"Gold Leaves": 200}},
    40: {"type": "emote", "name": "Victory Dance", "desc": "Emote: Victory Dance"},
    42: {"type": "resource", "name": "Crystal Dust x30", "desc": "+30 Crystal Dust", "resources": {"Crystal Dust": 30}},
    45: {"type": "pet_skin", "name": "Shadow Drake", "desc": "Pet skin: Shadow Drake"},
    47: {"type": "resource", "name": "Ancient Root x10", "desc": "+10 Ancient Root", "resources": {"Ancient Root": 10}},
    50: {"type": "weapon", "name": "PlayTree Legendary", "desc": "Legendary: PlayTree Blade"},
}

QUEST_CHALLENGES = {
    "daily": [
        {"name": "Defeat 10 enemies", "type": "defeat", "target": "enemy", "needed": 10, "xp": 50},
        {"name": "Collect 20 resources", "type": "collect", "target": "any", "needed": 20, "xp": 30},
        {"name": "Explore 3 regions", "type": "explore", "target": "region", "needed": 3, "xp": 40},
        {"name": "Craft 2 items", "type": "craft", "target": "any", "needed": 2, "xp": 35},
        {"name": "Defeat a boss", "type": "defeat", "target": "boss", "needed": 1, "xp": 100},
        {"name": "Tame a creature", "type": "tame", "target": "creature", "needed": 1, "xp": 45},
    ],
    "weekly": [
        {"name": "Defeat 50 enemies", "type": "defeat", "target": "enemy", "needed": 50, "xp": 200},
        {"name": "Collect 100 resources", "type": "collect", "target": "any", "needed": 100, "xp": 150},
        {"name": "Explore all regions", "type": "explore", "target": "all_regions", "needed": 5, "xp": 300},
        {"name": "Craft 10 items", "type": "craft", "target": "any", "needed": 10, "xp": 180},
        {"name": "Defeat 3 bosses", "type": "defeat", "target": "boss", "needed": 3, "xp": 400},
        {"name": "Build 5 structures", "type": "build", "target": "any", "needed": 5, "xp": 200},
    ],
    "season": [
        {"name": "Reach level 20", "type": "level", "target": "player", "needed": 20, "xp": 500},
        {"name": "Defeat 200 enemies", "type": "defeat", "target": "enemy", "needed": 200, "xp": 800},
        {"name": "Collect 500 resources", "type": "collect", "target": "any", "needed": 500, "xp": 600},
        {"name": "Build 25 structures", "type": "build", "target": "any", "needed": 25, "xp": 500},
        {"name": "Tame 5 creatures", "type": "tame", "target": "creature", "needed": 5, "xp": 400},
        {"name": "Defeat all 5 bosses", "type": "defeat", "target": "boss", "needed": 5, "xp": 1000},
    ],
}


class BattlePass:
    def __init__(self):
        self.current_season = 0
        self.tier = 1
        self.xp = 0
        self.xp_to_next = 100
        self.claimed_rewards = []
        self.challenges = {"daily": [], "weekly": [], "season": []}
        self.challenge_progress = {}
        self.daily_reset_timer = 0
        self.weekly_reset_timer = 0
        self.total_xp_earned = 0
        self._generate_challenges()

    def _generate_challenges(self):
        self.challenges["daily"] = random.sample(QUEST_CHALLENGES["daily"], min(3, len(QUEST_CHALLENGES["daily"])))
        self.challenges["weekly"] = random.sample(QUEST_CHALLENGES["weekly"], min(3, len(QUEST_CHALLENGES["weekly"])))
        self.challenges["season"] = list(QUEST_CHALLENGES["season"])
        for cat in self.challenges:
            for ch in self.challenges[cat]:
                key = f"{cat}_{ch['name']}"
                self.challenge_progress[key] = 0

    def update(self, dt, game_events=None):
        self.daily_reset_timer += dt
        self.weekly_reset_timer += dt

        if self.daily_reset_timer >= 86400:
            self.daily_reset_timer = 0
            self.challenges["daily"] = random.sample(QUEST_CHALLENGES["daily"], min(3, len(QUEST_CHALLENGES["daily"])))
            for ch in self.challenges["daily"]:
                key = f"daily_{ch['name']}"
                self.challenge_progress[key] = 0

        if self.weekly_reset_timer >= 604800:
            self.weekly_reset_timer = 0
            self.challenges["weekly"] = random.sample(QUEST_CHALLENGES["weekly"], min(3, len(QUEST_CHALLENGES["weekly"])))
            for ch in self.challenges["weekly"]:
                key = f"weekly_{ch['name']}"
                self.challenge_progress[key] = 0

        if game_events:
            for event in game_events:
                self._process_event(event)

    def _process_event(self, event):
        event_type = event.get("type", "")
        event_target = event.get("target", "")
        event_amount = event.get("amount", 1)

        for cat in ["daily", "weekly", "season"]:
            for ch in self.challenges[cat]:
                if ch["type"] == event_type:
                    if ch["target"] == event_target or ch["target"] == "any":
                        key = f"{cat}_{ch['name']}"
                        self.challenge_progress[key] = self.challenge_progress.get(key, 0) + event_amount

    def add_xp(self, amount):
        self.xp += amount
        self.total_xp_earned += amount
        while self.xp >= self.xp_to_next and self.tier < 50:
            self.xp -= self.xp_to_next
            self.tier += 1
            self.xp_to_next = int(self.xp_to_next * 1.15)
            return True
        return False

    def claim_reward(self, tier):
        if tier in TIER_REWARDS and tier <= self.tier and tier not in self.claimed_rewards:
            self.claimed_rewards.append(tier)
            return TIER_REWARDS[tier]
        return None

    def get_claimable_rewards(self):
        return [t for t in TIER_REWARDS if t <= self.tier and t not in self.claimed_rewards]

    def get_progress_for_category(self, cat):
        challenges = self.challenges.get(cat, [])
        result = []
        for ch in challenges:
            key = f"{cat}_{ch['name']}"
            progress = self.challenge_progress.get(key, 0)
            result.append({
                **ch,
                "progress": progress,
                "complete": progress >= ch["needed"],
            })
        return result

    def draw(self, screen, player=None):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        season_data = SEASONS[self.current_season]
        sx, sy = 40, 30
        sw, sh = WIDTH - 80, HEIGHT - 60

        pygame.draw.rect(screen, (15, 15, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(screen, (*season_data["color"][:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 40)
        ts = tf.render(season_data["name"], True, season_data["color"])
        screen.blit(ts, (sx + 20, sy + 10))

        pf = pygame.font.Font(None, 26)
        ps = pf.render(f"Tier {self.tier}/50  |  XP: {self.xp}/{self.xp_to_next}", True, GOLD)
        screen.blit(ps, (sx + 20, sy + 55))

        bar_x, bar_y, bar_w = sx + 20, sy + 85, sw - 40
        pygame.draw.rect(screen, (30, 30, 40), (bar_x, bar_y, bar_w, 14), border_radius=7)
        progress = self.xp / self.xp_to_next if self.xp_to_next > 0 else 0
        fill_color = season_data["color"]
        pygame.draw.rect(screen, fill_color, (bar_x, bar_y, int(bar_w * progress), 14), border_radius=7)

        tab_y = sy + 115
        categories = ["daily", "weekly", "season"]
        for i, cat in enumerate(categories):
            tab_x = sx + 20 + i * 120
            is_active = i == 0
            color = GOLD if is_active else (120, 120, 120)
            tab_f = pygame.font.Font(None, 22)
            tab_s = tab_f.render(cat.title(), True, color)
            screen.blit(tab_s, (tab_x, tab_y))

        ch_y = tab_y + 30
        cf = pygame.font.Font(None, 20)
        for cat in categories:
            challenges = self.get_progress_for_category(cat)
            for ch in challenges:
                color = GREEN_GLOW if ch["complete"] else (180, 180, 180)
                cs = cf.render(f"[{'x' if ch['complete'] else ' '}] {ch['name']}", True, color)
                screen.blit(cs, (sx + 30, ch_y))

                prog_bar_x = sx + sw - 200
                prog_w = 100
                pygame.draw.rect(screen, (30, 30, 40), (prog_bar_x, ch_y + 2, prog_w, 10), border_radius=5)
                prog_ratio = min(1, ch["progress"] / ch["needed"])
                pygame.draw.rect(screen, season_data["color"], (prog_bar_x, ch_y + 2, int(prog_w * prog_ratio), 10), border_radius=5)

                prog_text = f"{ch['progress']}/{ch['needed']}"
                pts = cf.render(prog_text, True, (150, 150, 150))
                screen.blit(pts, (prog_bar_x + prog_w + 10, ch_y))

                xp_text = f"+{ch['xp']} XP"
                xps = cf.render(xp_text, True, GOLD)
                screen.blit(xps, (sx + sw - 80, ch_y))

                ch_y += 24
            ch_y += 10

        reward_y = sy + sh - 200
        rf = pygame.font.Font(None, 22)
        rl = rf.render("TIER REWARDS", True, GOLD)
        screen.blit(rl, (sx + 20, reward_y))
        reward_y += 25

        reward_tiers = sorted(TIER_REWARDS.keys())
        for tier in reward_tiers:
            reward = TIER_REWARDS[tier]
            claimed = tier in self.claimed_rewards
            unlocked = tier <= self.tier
            can_claim = unlocked and not claimed

            color = GREEN_GLOW if can_claim else (100, 100, 100) if unlocked else (60, 60, 60)
            if claimed:
                color = (80, 80, 80)

            rs = rf.render(f"Tier {tier}: {reward['name']}", True, color)
            screen.blit(rs, (sx + 30, reward_y))

            if can_claim:
                cr = rf.render("[CLAIM]", True, GOLD)
                screen.blit(cr, (sx + sw - 100, reward_y))

            reward_y += 22
            if reward_y > sy + sh - 40:
                break

        try:
            ctrl = pygame.joystick.get_count() > 0
        except Exception:
            ctrl = False
        if ctrl:
            from src.ui import xbox_icons
            xbox_icons.draw_menu_prompt(screen, [("B", "ESC", "Close"), ("A", "Click", "Claim")], sy + sh - 25)
        else:
            hint = pygame.font.Font(None, 18).render("ESC to close  |  Click CLAIM for rewards", True, (80, 100, 80))
            screen.blit(hint, (sx + 20, sy + sh - 25))

    def handle_click(self, mx, my, player=None):
        reward_y_start = 0
        reward_tiers = sorted(TIER_REWARDS.keys())
        for i, tier in enumerate(reward_tiers):
            ry = reward_y_start + i * 22
            if tier <= self.tier and tier not in self.claimed_rewards:
                if 0 <= my - ry < 22:
                    reward = self.claim_reward(tier)
                    if reward and player and "resources" in reward:
                        for res, amt in reward["resources"].items():
                            player.inventory["resources"][res] = player.inventory["resources"].get(res, 0) + amt
                    return reward
        return None
