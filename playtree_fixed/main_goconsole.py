"""PLAYTREE GoConsoleOS Edition — TV + Controller optimized"""
import sys, os, tempfile
# handle GoConsoleOS flag early
IS_GOCONSOLE = "--goconsoleos" in sys.argv
if IS_GOCONSOLE:
    os.environ["PLAYTREE_GOCONSOLEOS"] = "1"

# Single-instance guard
_lock_path = os.path.join(tempfile.gettempdir(), "playtree_goconsole.lock" if IS_GOCONSOLE else "playtree.lock")
try:
    import msvcrt
    _lock_file = open(_lock_path, "w")
    try:
        msvcrt.locking(_lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, "PlayTree GoConsoleOS is already running!" if IS_GOCONSOLE else "PLAYTREE is already running!", "PlayTree", 0x30)
        sys.exit(0)
except Exception:
    pass

if getattr(sys, "frozen", False):
    _base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    try: os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    except: pass
else:
    _base = os.path.dirname(os.path.abspath(__file__))
if _base not in sys.path:
    sys.path.insert(0, _base)

import pygame

def is_mobile():
    return sys.platform in ("android","ios") or hasattr(sys, "getandroidapilevel")

if is_mobile():
    os.environ["SDL_AUDIODRIVER"] = "dummy"

from config import WIDTH, HEIGHT, TITLE, FPS, BLACK
from src.game import Game

def main():
    pygame.init()
    try: pygame.font.init()
    except: pass
    # GoConsoleOS forces TV mode + larger scale
    display = None
    try:
        info = pygame.display.Info()
        monitor_w = getattr(info, "current_w", WIDTH) or WIDTH
        monitor_h = getattr(info, "current_h", HEIGHT) or HEIGHT
        if monitor_w<=0 or monitor_h<=0: monitor_w, monitor_h = 1920,1080
    except: monitor_w, monitor_h = 1920,1080
    flags = pygame.DOUBLEBUF
    if IS_GOCONSOLE:
        # GoConsoleOS: start fullscreen for TV
        try: display = pygame.display.set_mode((WIDTH, HEIGHT), flags | pygame.FULLSCREEN)
        except: display = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        title = "PlayTree GoConsoleOS Edition — Chapter 0 : Season 0"
    else:
        try: display = pygame.display.set_mode((WIDTH, HEIGHT), flags)
        except: display = pygame.display.set_mode((0,0), flags)
        title = f"{TITLE} — {__import__('config').CHAPTER} : {__import__('config').SEASON}"
    pygame.display.set_caption(title)
    try: pygame.display.set_icon(pygame.Surface((32,32)))
    except: pass
    render_surface = pygame.Surface((WIDTH, HEIGHT)).convert()
    game = Game(render_surface)
    # Force TV mode for GoConsoleOS
    if IS_GOCONSOLE and hasattr(game, 'tv_mode'):
        game.tv_mode = True
        try: game.show_message("GoConsoleOS TV Mode", 2)
        except: pass
    clock = pygame.time.Clock()
    running=True
    import traceback as _tb
    _error_log = os.path.join(tempfile.gettempdir(), "playtree_goconsole_error.log" if IS_GOCONSOLE else "playtree_error.log")
    _last = {"msg":""}
    def draw_error(msg):
        try:
            with open(_error_log,"a",encoding="utf-8") as f: f.write(f"\n--- {msg} ---\n"+_tb.format_exc())
        except: pass
        if _last["msg"]!=msg: print(f"[error] {msg}"); _last["msg"]=msg
    while running:
        dt = clock.tick(FPS)/1000.0
        if dt>0.1: dt=0.1
        try: events = pygame.event.get()
        except: events=[]
        for ev in events:
            if ev.type==pygame.QUIT: running=False
        try:
            if hasattr(game,"studio_splash") and not game.studio_splash.done:
                game.studio_splash.update(dt)
            game.handle_events(events)
            game.update(dt)
            game.draw()
        except Exception as e:
            import traceback; traceback.print_exc(); draw_error(f"Game crash: {e}"); continue
        try:
            dw,dh = display.get_size()
            if dw!=WIDTH or dh!=HEIGHT:
                scaled = pygame.transform.smoothscale(render_surface, (dw,dh))
                display.blit(scaled,(0,0))
            else: display.blit(render_surface,(0,0))
            pygame.display.flip()
        except: pass
        if not getattr(game,"running",True): running=False
        try:
            from src.save_system import has_save
            if hasattr(game,"main_menu"): game.main_menu.has_save = has_save()
        except: pass
    pygame.quit()
    try: msvcrt.locking(_lock_file.fileno(), msvcrt.LK_UNLCK, 1); _lock_file.close(); os.remove(_lock_path)
    except: pass
    sys.exit(0)
if __name__=="__main__": main()
