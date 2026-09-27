"""Daily quests — three date-seeded challenges that rotate every day.

The same date yields the same quests for every player (like a live-service
daily). Progress uses the same event vocabulary as QuestSystem.update_progress
("defeat", "collect", "tame", "explore") plus "boss" and "round" events fed
from game.py. Rewards are granted by the caller (game layer owns the player).
"""
import json
import os
import time
import zlib

DAILIES_FILE = os.path.join(os.path.expanduser("~"), ".playtree", "dailies.json")

DAILY_POOL = [
    {"id": "kill10", "name": "Defeat enemies", "desc": "Defeat 10 enemies",
     "objective": "defeat", "target": None, "needed": 10,
     "reward_xp": 60, "reward_gold": 25},
    {"id": "kill18", "name": "Defeat enemies", "desc": "Defeat 18 enemies",
     "objective": "defeat", "target": None, "needed": 18,
     "reward_xp": 90, "reward_gold": 40},
    {"id": "kill_boss", "name": "Defeat a boss", "desc": "Defeat any boss",
     "objective": "boss", "target": None, "needed": 1,
     "reward_xp": 120, "reward_gold": 60},
    {"id": "tree8", "name": "Collect Tree Energy", "desc": "Collect 8 Tree Energy",
     "objective": "collect", "target": "Tree Energy", "needed": 8,
     "reward_xp": 50, "reward_gold": 20},
    {"id": "crystal6", "name": "Collect Crystal Dust", "desc": "Collect 6 Crystal Dust",
     "objective": "collect", "target": "Crystal Dust", "needed": 6,
     "reward_xp": 55, "reward_gold": 25},
    {"id": "any15", "name": "Gather resources", "desc": "Collect 15 of any resource",
     "objective": "collect", "target": None, "needed": 15,
     "reward_xp": 65, "reward_gold": 30},
    {"id": "tame1", "name": "Tame a creature", "desc": "Tame 1 wild creature",
     "objective": "tame", "target": "creature", "needed": 1,
     "reward_xp": 80, "reward_gold": 35},
    {"id": "tame2", "name": "Tame creatures", "desc": "Tame 2 wild creatures",
     "objective": "tame", "target": "creature", "needed": 2,
     "reward_xp": 110, "reward_gold": 50},
    {"id": "round1", "name": "Clear a round", "desc": "Defeat a round boss to clear a round",
     "objective": "round", "target": None, "needed": 1,
     "reward_xp": 100, "reward_gold": 45},
    {"id": "explore2", "name": "Explore regions", "desc": "Visit 2 different regions",
     "objective": "explore", "target": None, "needed": 2,
     "reward_xp": 70, "reward_gold": 30},
]


def _today():
    return time.strftime("%Y-%m-%d")


def _ensure_dir():
    os.makedirs(os.path.dirname(DAILIES_FILE), exist_ok=True)


class DailyQuestSystem:
    def __init__(self):
        self.quests = []
        self.completed_this_frame = []
        self.date = None
        self._load()
        self._ensure_today()

    # ---------- persistence ----------
    def _load(self):
        try:
            if os.path.exists(DAILIES_FILE):
                with open(DAILIES_FILE, "r") as f:
                    data = json.load(f)
                self.date = data.get("date")
                self.quests = data.get("quests", [])
        except Exception:
            self.date = None
            self.quests = []

    def save(self):
        try:
            _ensure_dir()
            with open(DAILIES_FILE, "w") as f:
                json.dump({"date": self.date, "quests": self.quests}, f, indent=2)
        except Exception:
            pass

    # ---------- daily rotation ----------
    def _ensure_today(self):
        """Regenerate quests when the calendar day rolls over.

        Selection uses a Lehmer LCG seeded from crc32(date) so the website
        (see index.html dailyPicks) can reproduce the exact same three
        quests without importing Python's Mersenne Twister.
        """
        today = _today()
        if self.date == today and len(self.quests) == 3:
            return False
        self.date = today
        seed = zlib.crc32(today.encode("utf-8")) % 2147483647 or 1
        idx = []
        while len(idx) < 3:
            seed = (seed * 48271) % 2147483647
            j = seed % len(DAILY_POOL)
            if j not in idx:
                idx.append(j)
        picks = [DAILY_POOL[j] for j in idx]
        self.quests = [dict(p, count=0, complete=False) for p in picks]
        self.completed_this_frame = []
        self.save()
        return True

    # ---------- progress ----------
    def on_event(self, objective, target=None, amount=1):
        """Feed a game event. Returns list of quests completed by this event."""
        self._ensure_today()
        done = []
        for q in self.quests:
            if q.get("complete"):
                continue
            if q.get("objective") != objective:
                continue
            if q.get("target") and q.get("target") != target:
                continue
            q["count"] = min(q.get("needed", 1), q.get("count", 0) + amount)
            if q["count"] >= q.get("needed", 1):
                q["complete"] = True
                done.append(q)
        if done:
            self.completed_this_frame.extend(q["name"] for q in done)
            self.save()
        return done

    # ---------- queries ----------
    def get_status(self):
        self._ensure_today()
        done = sum(1 for q in self.quests if q.get("complete"))
        return {"date": self.date, "done": done, "total": len(self.quests)}

    def summary_lines(self):
        """Compact rows for HUD/profile: [{name, progress, complete}]."""
        self._ensure_today()
        out = []
        for q in self.quests:
            out.append({
                "name": q.get("name", ""),
                "desc": q.get("desc", ""),
                "progress": f"{q.get('count', 0)}/{q.get('needed', 1)}",
                "complete": bool(q.get("complete")),
                "reward_gold": q.get("reward_gold", 0),
                "reward_xp": q.get("reward_xp", 0),
            })
        return out

    def first_incomplete(self):
        for q in self.quests:
            if not q.get("complete"):
                return q
        return None
