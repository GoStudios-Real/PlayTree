"""PlayTree Rich Presence — Shows 'Playing PlayTree' on your Discord profile"""
import pypresence
import time
import json
import os
import sys
import psutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import GAMES, STATS_FILE

CLIENT_ID = "1548510077055537184"

GAME_EXES = {g["exe"].lower().replace(".exe", ""): g for g in GAMES}
GAME_PROCESS_NAMES = {
    "playtree": "PLAYTREE",
    "playtree 3d": "PlayTree 3D",
    "playtree football": "PlayTree FootBall",
    "playtree puzzle": "PlayTree Puzzle",
    "playtree racing": "PlayTree Racing",
    "playtree dungeon": "PlayTree Dungeon",
    "playtree space": "PlayTree Space",
    "playtree tower defense": "PlayTree Tower Defense",
    "playtree underwater": "PlayTree Underwater",
    "playtree game collection": "PlayTree Game Collection",
    "playtree game collection v4": "PlayTree Game Collection v4",
}

LARGE_IMAGE = "playtree_large"
LARGE_TEXT = "PlayTree Game Collection"
SMALL_IMAGE = "playtree_small"
SMALL_TEXT = "GoStudios"


def detect_running_game():
    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info["name"].lower().replace(".exe", "")
            if name in GAME_PROCESS_NAMES:
                return GAME_PROCESS_NAMES[name]
        except Exception:
            pass
    return None


def load_total_stats():
    try:
        with open(STATS_FILE) as f:
            stats = json.load(f)
        total = sum(stats.get("launches", {}).values())
        return total
    except Exception:
        return 0


def main():
    print("PlayTree Rich Presence starting...")
    print("Make sure Discord is running!")

    try:
        rpc = pypresence.Presence(CLIENT_ID)
        rpc.connect()
        print("Connected to Discord!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("Make sure Discord is running and you have Discord open.")
        return

    start_time = int(time.time())
    current_game = None

    print("Rich Presence active! You'll see 'Playing PlayTree' on your profile.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            detected = detect_running_game()
            total_launches = load_total_stats()

            if detected:
                details = f"Playing {detected}"
                state = f"{total_launches} total launches"
                large_image = LARGE_IMAGE
                large_text = detected
            else:
                details = "Browse 9 games"
                state = f"{total_launches} total launches | GoStudios"
                large_image = LARGE_IMAGE
                large_text = LARGE_TEXT

            if detected != current_game:
                current_game = detected
                if detected:
                    print(f"  Now showing: Playing {detected}")
                else:
                    print("  Back to idle presence")

            try:
                rpc.update(
                    details=details,
                    state=state,
                    large_image=large_image,
                    large_text=large_text,
                    small_image=SMALL_IMAGE,
                    small_text=SMALL_TEXT,
                    start=start_time,
                    buttons=[
                        {"label": "PlayTree Collection", "url": "https://gostudios-real.github.io/GoStudios-Real-playtree.github.io/"},
                        {"label": "GitHub", "url": "https://github.com/GoStudios-Real/PlayTree"},
                    ],
                )
            except Exception:
                pass

            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping Rich Presence...")
    finally:
        try:
            rpc.close()
        except Exception:
            pass
        print("Done.")


if __name__ == "__main__":
    main()
