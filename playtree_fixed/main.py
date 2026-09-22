"""PLAYTREE — Chapter 0 : Season 0 — FIXED main (black-screen patched)"""
from src.game import Game
from config import WIDTH, HEIGHT, TITLE, FPS, BLACK
import pygame
import sys
import os

# Single-instance guard (prevents 27 zombies)
import tempfile
_lock_path = os.path.join(tempfile.gettempdir(), "playtree.lock")
try:
    import msvcrt
    _lock_file = open(_lock_path, "w")
    try:
        msvcrt.locking(_lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "PLAYTREE is already running!", "PLAYTREE", 0x30)
        sys.exit(0)
except Exception:
    pass

if getattr(sys, "frozen", False):
    _base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    try:
        os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    except Exception:
        pass
else:
    _base = os.path.dirname(os.path.abspath(__file__))
if _base not in sys.path:
    sys.path.insert(0, _base)


def is_mobile():
    if sys.platform in ("android", "ios"):
        return True
    return hasattr(sys, "getandroidapilevel")


if is_mobile():
    os.environ["SDL_AUDIODRIVER"] = "dummy"


def main():
    pygame.init()
    try:
        pygame.font.init()
    except Exception:
        pass

    # Robust display init — no swallowed exceptions
    display = None
    monitor_w, monitor_h = WIDTH, HEIGHT
    try:
        info = pygame.display.Info()
        monitor_w = getattr(info, "current_w", WIDTH) or WIDTH
        monitor_h = getattr(info, "current_h", HEIGHT) or HEIGHT
        if monitor_w <= 0 or monitor_h <= 0:
            monitor_w, monitor_h = WIDTH, HEIGHT
    except Exception as e:
        print(f"[warn] display.Info failed: {e}")
        monitor_w, monitor_h = 1920, 1080

    # Try windowed (works on all drivers) — fullscreen is opt-in via settings
    try:
        display = pygame.display.set_mode((WIDTH, HEIGHT))
    except Exception as e:
        print(f"[error] set_mode windowed failed: {e}")
        try:
            display = pygame.display.set_mode((0, 0))
        except Exception as e2:
            print(f"[fatal] set_mode failed: {e2}")
            raise

    pygame.display.set_caption(f"{TITLE} — {__import__('config').CHAPTER} : {__import__('config').SEASON}")
    try:
        pygame.display.set_icon(pygame.Surface((32, 32)))
    except Exception:
        pass

    # FIX: render_surface must be convert() and ALWAYS blitted (black-screen bug was missing blit when dw==WIDTH)
    render_surface = pygame.Surface((WIDTH, HEIGHT)).convert()
    game = Game(render_surface)

    clock = pygame.time.Clock()
    running = True

    # Error logging — no red-screen spam (was looping every frame)
    import traceback as _tb
    _error_log = os.path.join(tempfile.gettempdir(), "playtree_error.log")
    _last_error = {"msg": "", "count": 0}

    def draw_error(msg):
        # silently log, show at most once per 5s to avoid spam
        try:
            with open(_error_log, "a", encoding="utf-8") as f:
                f.write(f"\n--- {msg} ---\n")
                f.write(_tb.format_exc())
        except BaseException:
            pass
        # don't block — just log, don't flip red screen every frame
        if _last_error["msg"] != msg:
            print(f"[error] {msg}")
            _last_error["msg"] = msg
            _last_error["count"] = 1
        else:
            _last_error["count"] += 1

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1:
            dt = 0.1
        try:
            events = pygame.event.get()
        except Exception as e:
            print(f"[warn] event.get failed: {e}")
            events = []

        try:
            for ev in events:
                if ev.type == pygame.QUIT:
                    running = False
            # Let game handle its own events/draw
            # need to pass events each frame — game.handle_events expects list
            # Use render_surface size for finger->mouse conversion inside Game
        except Exception as e:
            import traceback
            traceback.print_exc()
            draw_error(f"Event error: {e}")
            continue

        try:
            # Game loop delegates — keep dt real, not 1/60
            # Update
            if hasattr(game, "studio_splash") and not game.studio_splash.done:
                # Fix: use real dt, not 1/60
                game.studio_splash.update(dt)
            # standard game handling
            game.handle_events(events)
            game.update(dt)
            game.draw()
        except Exception as e:
            import traceback
            traceback.print_exc()
            draw_error(f"Game crash: {e}")
            # don't black screen — show error then continue
            continue

        # FIX: ALWAYS blit render_surface to display (was missing else branch -> black)
        try:
            dw, dh = display.get_size()
            if dw != WIDTH or dh != HEIGHT:
                scaled = pygame.transform.smoothscale(render_surface, (dw, dh))
                display.blit(scaled, (0, 0))
            else:
                display.blit(render_surface, (0, 0))
            pygame.display.flip()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[error] blit/flip failed: {e}")

        if not getattr(game, "running", True):
            running = False

        # keep has_save cache fresh (fixes Continue button stale)
        try:
            from src.save_system import has_save
            if hasattr(game, "main_menu"):
                game.main_menu.has_save = has_save()
        except Exception:
            pass

    pygame.quit()
    try:
        msvcrt.locking(_lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        _lock_file.close()
        os.remove(_lock_path)
    except Exception:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
