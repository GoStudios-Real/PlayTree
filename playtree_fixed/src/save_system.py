import os
import json

SAVE_DIR = os.path.join(os.path.expanduser("~"), ".playtree")
SETTINGS_FILE = os.path.join(SAVE_DIR, "settings.json")
MAX_SLOTS = 5


def _ensure_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def _slot_file(slot):
    return os.path.join(SAVE_DIR, f"save_slot_{slot}.json")


def _old_save_file():
    return os.path.join(SAVE_DIR, "save.json")


def save_game(player, game=None, slot=0):
    _ensure_dir()
    data = {
        "name": player.name,
        "player_class": player.player_class.value,
        "level": player.level,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "energy": player.energy,
        "max_energy": player.max_energy,
        "attack_power": player.attack_power,
        "defense": player.defense,
        "speed": player.speed,
        "x": player.x,
        "y": player.y,
        "xp": player.xp,
        "xp_to_next": player.xp_to_next,
        "weapon_id": player.weapon_id,
        "inventory": {
            "resources": {k: int(v) for k, v in player.inventory.get("resources", {}).items()},
            "items": player.inventory.get("items", []),
            "weapons": player.inventory.get("weapons", []),
            "enchants": player.inventory.get("enchants", {}),
            "armor": player.inventory.get("armor", []),
        },
        "equipment": {
            "head": getattr(player, 'equipment', None) and player.equipment.slots.get("head"),
            "chest": getattr(player, 'equipment', None) and player.equipment.slots.get("chest"),
            "legs": getattr(player, 'equipment', None) and player.equipment.slots.get("legs"),
            "boots": getattr(player, 'equipment', None) and player.equipment.slots.get("boots"),
        },
        "creatures": [
            {"name": c.get("name", ""), "color": c.get("color", (255, 255, 255)),
             "type": c.get("type", ""), "level": c.get("level", 1),
             "stage": c.get("stage", 1)}
            for c in player.creatures
        ],
        "quests": [
            {"name": q.get("name", ""), "desc": q.get("desc", ""),
             "objective": q.get("objective", ""), "target": q.get("target", ""),
             "count": q.get("count", 0), "needed": q.get("needed", 1),
             "complete": q.get("complete", False), "reward_xp": q.get("reward_xp", 0),
             "reward_item": q.get("reward_item", "")}
            for q in player.quests
        ],
        "world_seed": 0,
        "playtime_hours": getattr(game, 'playtime_hours', 0) if game else 0,
        "save_time": getattr(game, 'save_time', 0) if game else 0,
    }
    if game:
        data["mounts_unlocked"] = getattr(game, 'mounts_unlocked', [])
        data["mounted_type"] = game.mount.mount_type if game.mount and game.mount.mounted else None
        data["boss_quest_stage"] = getattr(game, 'boss_quest_stage', 0)
        buildings = []
        for b in getattr(game.base_builder, 'buildings', []):
            buildings.append({"x": b.x, "y": b.y, "build_type": b.build_type, "hp": b.hp, "owner": b.owner})
        data["buildings"] = buildings
        bp = getattr(game, 'battle_pass', None)
        if bp:
            data["battle_pass"] = {"tier": bp.tier, "xp": bp.xp, "xp_to_next": bp.xp_to_next,
                                   "claimed_rewards": bp.claimed_rewards, "total_xp_earned": bp.total_xp_earned}
        else:
            data["battle_pass"] = {}
        data["wardrobe"] = getattr(game, 'cosmetics', {})
        data["current_round"] = getattr(game, 'current_round', 1)
        data["achievements"] = getattr(game, 'achievements', None) and game.achievements.unlocked or {}
        if hasattr(game, 'skill_tree') and game.skill_tree:
            data["skill_points"] = game.skill_tree.skill_points
            data["skill_levels"] = {sid: s["level"] for sid, s in game.skill_tree.skills.items()}
        data["new_game_plus"] = getattr(game, 'new_game_plus', None) and game.new_game_plus.get_save_data() or {}
        data["leaderboards"] = getattr(game, 'leaderboards', None) and game.leaderboards.data or {}
    else:
        data["mounts_unlocked"] = []
        data["mounted_type"] = None
        data["boss_quest_stage"] = 0
        data["buildings"] = []
        data["battle_pass"] = {}
        data["wardrobe"] = {}
        data["current_round"] = 1
        data["achievements"] = {}
        data["skill_points"] = 3
        data["skill_levels"] = {}
    with open(_slot_file(slot), "w") as f:
        json.dump(data, f, indent=2)
    return True


def load_game(slot=0):
    sf = _slot_file(slot)
    if os.path.exists(sf):
        try:
            with open(sf, "r") as f:
                return json.load(f)
        except Exception:
            # FIX: corrupted save — move to .corrupt so it doesn't block
            try:
                os.rename(sf, sf + ".corrupt")
            except:
                try: os.remove(sf)
                except: pass
            pass
    # Fallback to old save.json for slot 0
    if slot == 0:
        old = _old_save_file()
        if os.path.exists(old):
            try:
                with open(old, "r") as f:
                    return json.load(f)
            except Exception:
                try: os.rename(old, old + ".corrupt")
                except:
                    try: os.remove(old)
                    except: pass
                pass
    return None


def has_save(slot=0):
    sf = _slot_file(slot)
    if os.path.exists(sf):
        try:
            with open(sf, "r") as f: json.load(f)
            return True
        except: return False
    if slot == 0:
        old = _old_save_file()
        if os.path.exists(old):
            try:
                with open(old, "r") as f: json.load(f)
                return True
            except: return False
    return False


def any_save_exists():
    for i in range(MAX_SLOTS):
        if has_save(i):
            return True
    if os.path.exists(_old_save_file()):
        return True
    return False


def list_slots():
    slots = []
    for i in range(MAX_SLOTS):
        sf = _slot_file(i)
        if os.path.exists(sf):
            try:
                with open(sf, "r") as f:
                    data = json.load(f)
                slots.append({
                    "slot": i,
                    "name": data.get("name", "Unknown"),
                    "level": data.get("level", 1),
                    "player_class": data.get("player_class", "Unknown"),
                    "current_round": data.get("current_round", 0),
                    "playtime_hours": data.get("playtime_hours", 0),
                })
            except Exception:
                slots.append({"slot": i, "name": "Corrupted", "level": 0, "player_class": "", "current_round": 0})
        elif i == 0 and os.path.exists(_old_save_file()):
            # Legacy save in slot 0
            try:
                with open(_old_save_file(), "r") as f:
                    data = json.load(f)
                slots.append({
                    "slot": i,
                    "name": data.get("name", "Unknown"),
                    "level": data.get("level", 1),
                    "player_class": data.get("player_class", "Unknown"),
                    "current_round": data.get("current_round", 0),
                    "playtime_hours": data.get("playtime_hours", 0),
                })
            except Exception:
                slots.append({"slot": i, "name": "Corrupted", "level": 0, "player_class": "", "current_round": 0})
        else:
            slots.append({"slot": i, "name": None, "level": 0, "player_class": "", "current_round": 0})
    return slots


def delete_save(slot=0):
    sf = _slot_file(slot)
    if os.path.exists(sf):
        os.remove(sf)


def save_settings(settings):
    _ensure_dir()
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return None
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None
