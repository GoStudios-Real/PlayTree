"""PlayTree Launcher — Java + Bedrock + All Versions + Mods
Minecraft Launcher research applied — pixel underwater Home look."""
import sys, os, json, math, random, time, subprocess, threading
from pathlib import Path

# --- setup paths ---
ROOT = Path(__file__).parent
STORE = ROOT / "launcher_profiles.json"
CACHE = ROOT / "versions_cache.json"

try:
    import pygame
except ImportError:
    print("Need pygame: pip install pygame")
    sys.exit(1)

# optional requests
try:
    import requests
except ImportError:
    requests = None
    import urllib.request, urllib.error

WIDTH, HEIGHT = 1280, 720
TITLE = "PlayTree Launcher"

# Colors matching screenshot
DEEP = (10, 47, 86)
MID = (18, 92, 140)
CYAN = (43, 201, 226)
LIME = (126, 211, 33)
LIME_DARK = (90, 174, 15)
LIME_BORDER = (47, 107, 0)
SHADOW = (30, 70, 10)
WHITE = (255,255,255)
BLACK = (0,0,0)
PANEL = (0,0,0,140)
TEXT_DIM = (160,200,160)

# Pixel font helper — use pygame default with bold for pixel feel
def get_font(size, bold=False):
    try:
        return pygame.font.SysFont("Courier New", size, bold=bold)
    except:
        return pygame.font.Font(None, size)

def fetch_versions():
    """Fetch version_manifest_v2.json with cache, returns list of dicts"""
    urls = [
        "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
        "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json",
    ]
    # cache valid 1h
    if CACHE.exists():
        try:
            data = json.loads(CACHE.read_text())
            if time.time() - data.get("_fetched", 0) < 3600:
                return data["versions"], data["latest"]
        except: pass
    versions, latest = None, None
    for u in urls:
        try:
            if requests:
                r = requests.get(u, timeout=8)
                r.raise_for_status()
                j = r.json()
            else:
                import urllib.request, json as js
                with urllib.request.urlopen(u, timeout=8) as resp:
                    j = js.loads(resp.read().decode())
            versions = j["versions"]
            latest = j["latest"]
            CACHE.write_text(json.dumps({"_fetched": time.time(), "versions": versions, "latest": latest}))
            return versions, latest
        except Exception as e:
            print(f"fetch {u} failed {e}")
            continue
    # fallback mock all versions + GoConsoleOS
    mock = [
        {"id": "1.21.11", "type": "release"},
        {"id": "1.21.10", "type": "release"},
        {"id": "1.20.6", "type": "release"},
        {"id": "1.19.4", "type": "release"},
        {"id": "26.2", "type": "release"},
        {"id": "26.3-snapshot-9", "type": "snapshot"},
        {"id": "b1.7.3", "type": "old_beta"},
        {"id": "a1.2.6", "type": "old_alpha"},
        {"id": "rd-161348", "type": "old_alpha"},
        {"id": "GoConsoleOS 1.0.0", "type": "release"},
        {"id": "GoConsoleOS 1.0.1", "type": "release"},
        {"id": "GoConsoleOS Preview 26.50.26", "type": "snapshot"},
    ]
    return mock, {"release": "1.21.11", "snapshot": "26.3-snapshot-9", "goconsoleos": "GoConsoleOS 1.0.0"}

def load_profiles():
    if STORE.exists():
        try: return json.loads(STORE.read_text())
        except: pass
    return {
        "profiles": {
            "java_latest": {"name": "PlayTree Java Latest", "edition": "java", "version": "1.21.11", "type": "latest-release", "lastUsed": ""},
            "bedrock_latest": {"name": "PlayTree Bedrock Latest", "edition": "bedrock", "version": "1.21.110", "type": "latest-release", "lastUsed": ""},
            "goconsole_latest": {"name": "PlayTree GoConsoleOS Latest", "edition": "goconsoleos", "version": "GoConsoleOS 1.0.0", "type": "latest-release", "lastUsed": ""},
        },
        "settings": {"historical": False, "keepOpen": True, "snapshots": True},
        "selected": "java_latest"
    }

def save_profiles(data):
    STORE.write_text(json.dumps(data, indent=2))

# --- UI widgets ---
class LimeButton:
    def __init__(self, rect, text, small=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.small = small
        self.hover = False
        self.pressed = False
    def draw(self, surf):
        # bevel + shadow like screenshot
        r = self.rect
        shadow = r.move(0, 6)
        pygame.draw.rect(surf, SHADOW, shadow, border_radius=8 if not self.small else 6)
        bg = LIME_DARK if self.pressed else LIME
        # fill
        pygame.draw.rect(surf, bg, r, border_radius=8 if not self.small else 6)
        # border
        pygame.draw.rect(surf, LIME_BORDER, r, 3, border_radius=8 if not self.small else 6)
        # inner highlight
        inner = r.inflate(-6, -6)
        pygame.draw.rect(surf, (255,255,255,40), inner, 1, border_radius=6)
        # text — pixel uppercase
        f = get_font(20 if self.small else 28, bold=True)
        txt = f.render(self.text.upper(), True, BLACK)
        # slight pixel shadow
        sh = f.render(self.text.upper(), True, (30,60,10))
        surf.blit(sh, (r.centerx - txt.get_width()//2 + 1, r.centery - txt.get_height()//2 + 2))
        surf.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))
        # hover
        if self.hover:
            pygame.draw.rect(surf, (255,255,255,30), r, 2, border_radius=8 if not self.small else 6)
    def handle(self, pos, down):
        self.hover = self.rect.collidepoint(pos)
        if down and self.hover:
            self.pressed = True
            return True
        if not down:
            was = self.pressed
            self.pressed = False
            return was and self.hover
        return False

class Dropdown:
    def __init__(self, rect, options, selected=0):
        self.rect = pygame.Rect(rect)
        self.options = options
        self.selected = selected
        self.open = False
        self.scroll = 0
    def draw(self, surf):
        pygame.draw.rect(surf, (15,30,15), self.rect, border_radius=6)
        pygame.draw.rect(surf, LIME_BORDER, self.rect, 2, border_radius=6)
        f = get_font(16, bold=True)
        txt = f.render(self.options[self.selected] if self.options else "", True, WHITE)
        surf.blit(txt, (self.rect.x+10, self.rect.centery - txt.get_height()//2))
        # arrow
        pygame.draw.polygon(surf, LIME, [(self.rect.right-20, self.rect.centery-4),(self.rect.right-10, self.rect.centery-4),(self.rect.right-15, self.rect.centery+4)])
        if self.open:
            list_rect = pygame.Rect(self.rect.x, self.rect.bottom+4, self.rect.w, min(300, len(self.options)*28))
            pygame.draw.rect(surf, (10,20,10), list_rect, border_radius=6)
            pygame.draw.rect(surf, LIME_BORDER, list_rect, 2, border_radius=6)
            # clip
            for i in range(max(0, self.scroll), min(len(self.options), self.scroll+10)):
                y = list_rect.y + (i-self.scroll)*28
                r = pygame.Rect(list_rect.x+4, y+2, list_rect.w-8, 24)
                if i == self.selected:
                    pygame.draw.rect(surf, LIME_DARK, r, border_radius=4)
                txt2 = get_font(14).render(self.options[i], True, WHITE)
                surf.blit(txt2, (r.x+8, r.y+4))
                if r.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(surf, (255,255,255,40), r, 1, border_radius=4)
    def handle(self, pos, down):
        if self.open:
            list_rect = pygame.Rect(self.rect.x, self.rect.bottom+4, self.rect.w, min(300, len(self.options)*28))
            if list_rect.collidepoint(pos) and down:
                idx = (pos[1]-list_rect.y)//28 + self.scroll
                if 0 <= idx < len(self.options):
                    self.selected = idx
                    self.open = False
                    return True
            elif down:
                self.open = False
                return False
        if self.rect.collidepoint(pos) and down:
            self.open = not self.open
            return True
        return False

def draw_underwater(surf, t):
    # gradient + sun rays + pixel blocks
    for y in range(HEIGHT):
        k = y / HEIGHT
        r = int(DEEP[0]*(1-k) + CYAN[0]*k*0.7 + 20*math.sin(k*6))
        g = int(DEEP[1]*(1-k) + CYAN[1]*k*0.7)
        b = int(DEEP[2]*(1-k) + CYAN[2]*k*0.7 + 10)
        pygame.draw.line(surf, (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b))), (0,y), (WIDTH,y))
    # sun rays — vertical translucent strips from top
    for i in range(5):
        x = 180 + i*220 + math.sin(t*0.3 + i)*20
        alpha = 30 - i*4
        s = pygame.Surface((80, HEIGHT), pygame.SRCALPHA)
        for sx in range(80):
            a = int(alpha * (1-abs(sx-40)/40) * 0.5)
            pygame.draw.line(s, (200,240,255,a), (sx,0), (sx,HEIGHT))
        surf.blit(s, (int(x), 0))
    # pixel coral / blocks at bottom
    for i in range(18):
        x = (i*90 + int(t*10 + i*30)) % (WIDTH+100) - 20
        h = 40 + (i%3)*30
        y = HEIGHT - h
        col = [(180,80,120),(60,180,120),(100,120,180),(200,170,80)][i%4]
        pygame.draw.rect(surf, col, (x, y, 70, h))
        pygame.draw.rect(surf, (0,0,0,80), (x, y, 70, h), 2)
        # highlight
        pygame.draw.line(surf, (255,255,255,60), (x,y), (x+70,y))
    # bubbles
    for i in range(18):
        bx = 100 + (i*140 + int(t*40)) % WIDTH
        by = HEIGHT - ((t*30 + i*80) % (HEIGHT+200))
        r = 4 + (i%3)*3
        pygame.draw.circle(surf, (200,240,255,120), (int(bx), int(by)), r)
        pygame.draw.circle(surf, (255,255,255,90), (int(bx), int(by)), r, 1)

def main():
    pygame.init()
    pygame.display.set_caption("PlayTree Launcher — Java & Bedrock & GoConsoleOS")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    # data
    versions, latest = fetch_versions()
    profiles = load_profiles()
    # map versions to ids
    all_ids = [v["id"] for v in versions]
    # filter by settings + edition
    def filtered_ids():
        out = []
        for v in versions:
            # GoConsoleOS edition only shows GoConsoleOS versions
            if edition == "goconsoleos" and not v["id"].startswith("GoConsoleOS"):
                continue
            if edition != "goconsoleos" and v["id"].startswith("GoConsoleOS"):
                continue
            if v["type"] == "snapshot" and not profiles["settings"].get("snapshots", True):
                continue
            if v["type"] in ("old_beta","old_alpha") and not profiles["settings"].get("historical", False):
                continue
            out.append(v["id"])
        return out or all_ids

    edition = "java"  # java | bedrock
    selected_version = profiles["profiles"][profiles["selected"]]["version"] if profiles["selected"] in profiles["profiles"] else all_ids[0]
    # find idx
    fids = filtered_ids()
    sel_idx = fids.index(selected_version) if selected_version in fids else 0

    dropdown = Dropdown((WIDTH//2 -300, 520, 600, 40), fids, sel_idx)
    # buttons like screenshot
    btn_settings = LimeButton((20, 120, 110, 40), "Settings", small=True)
    btn_store = LimeButton((20, 170, 110, 28), "Store", small=True)
    btn_update = LimeButton((WIDTH-300, 200, 260, 56), "Update")
    btn_play = LimeButton((WIDTH-330, 280, 320, 86), "Play")
    btn_mods = LimeButton((WIDTH-300, 390, 260, 56), "Mods")
    # top nav
    nav = ["Home","News","About us"]
    nav_active = 0
    tab = "Home"
    # mods search
    mods_query = ""
    mods_results = []
    # news mock
    news = [
        ("Mounts of Mayhem", "26.2 — Ride the forest stag", "2 days ago"),
        ("PlayTree 1.21.11", "Crystal Depths stable", "1 week ago"),
        ("GoConsole Update", "Touch + keyboard on-screen", "3 days ago"),
    ]
    # settings
    ram = 2
    java_path = "bundled"

    running = True
    t0 = time.time()
    while running:
        dt = clock.tick(60)/1000
        t = time.time() - t0
        events = pygame.event.get()
        mpos = pygame.mouse.get_pos()
        # find play version
        for ev in events:
            if ev.type == pygame.QUIT:
                running=False
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button==1:
                # nav
                for i,name in enumerate(nav):
                    r = pygame.Rect(WIDTH//2 - 180 + i*140, 36, 100, 28)
                    if r.collidepoint(ev.pos):
                        nav_active=i
                        tab = name
                # edition toggle — now 3 editions
                for i, ed in enumerate(["Java","Bedrock","GoConsoleOS"]):
                    r = pygame.Rect(WIDTH//2 -165 + i*110, 480, 100, 30)
                    if r.collidepoint(ev.pos):
                        edition = ed.lower()
                # buttons
                if btn_settings.handle(ev.pos, True): pass
                if btn_store.handle(ev.pos, True): tab="Store"
                if btn_update.handle(ev.pos, True): pass
                if btn_play.handle(ev.pos, True):
                    # launch
                    ver = dropdown.options[dropdown.selected] if dropdown.options else "1.21.11"
                    print(f"Launching PlayTree {edition} {ver}")
                    # save lastUsed
                    sel = profiles["selected"]
                    if sel in profiles["profiles"]:
                        profiles["profiles"][sel]["edition"]=edition
                        profiles["profiles"][sel]["version"]=ver
                        save_profiles(profiles)
                    # spawn dummy (in real, java -jar)
                    # show launching overlay for 1s
                if btn_mods.handle(ev.pos, True): tab="Mods"
                dropdown.handle(ev.pos, True)
                # mods search enter
                if tab=="Mods":
                    # simple: clicking search triggers modrinth
                    pass
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button==1:
                if btn_play.handle(ev.pos, False):
                    # actually launch — handle GoConsoleOS edition
                    ver = dropdown.options[dropdown.selected] if dropdown.options else "1.21.11"
                    try:
                        exe = ROOT.parent / "PLAYTREE.exe"
                        if not exe.exists():
                            exe = Path(r"C:\Users\RhysC\Downloads\NEW\PLAYTREE.exe")
                        if edition == "goconsoleos":
                            gce = ROOT.parent / "PlayTree GoConsoleOS.exe"
                            if not gce.exists():
                                gce = Path(r"C:\Users\RhysC\Downloads\NEW\PlayTree GoConsoleOS.exe")
                            if gce.exists():
                                exe = gce
                            # GoConsoleOS launches with TV mode flag
                        if exe.exists():
                            args = [str(exe)]
                            if edition == "goconsoleos":
                                args.append("--goconsoleos")
                            subprocess.Popen(args, cwd=str(exe.parent))
                    except Exception as e:
                        print(e)
                btn_settings.handle(ev.pos, False)
                btn_store.handle(ev.pos, False)
                btn_update.handle(ev.pos, False)
                btn_mods.handle(ev.pos, False)
            elif ev.type == pygame.KEYDOWN:
                if tab=="Mods":
                    if ev.key==pygame.K_BACKSPACE:
                        mods_query=mods_query[:-1]
                    elif ev.key==pygame.K_RETURN:
                        # search modrinth
                        if mods_query:
                            try:
                                if requests:
                                    r=requests.get(f"https://api.modrinth.com/v2/search?query={mods_query}&limit=6", timeout=6)
                                    mods_results=[h["title"] for h in r.json().get("hits",[])]
                                else:
                                    mods_results=[f"Mod for '{mods_query}' (offline)"]
                            except:
                                mods_results=["No results (offline)"]
                    elif ev.unicode and ev.unicode.isprintable():
                        mods_query+=ev.unicode
                # update dropdown filter
                if dropdown.open and ev.key==pygame.K_ESCAPE:
                    dropdown.open=False

        # update dropdown if filter changed
        new_fids = filtered_ids()
        if new_fids != dropdown.options:
            cur = dropdown.options[dropdown.selected] if dropdown.options and 0 <= dropdown.selected < len(dropdown.options) else None
            dropdown.options = new_fids
            if cur in new_fids:
                dropdown.selected = new_fids.index(cur)
            else:
                dropdown.selected = 0

        # draw
        draw_underwater(screen, t)
        # pixel characters placeholder (simple blocks)
        # left characters like screenshot
        char1 = pygame.Rect(120, 260, 90, 110)
        pygame.draw.rect(screen, (80,180,90), char1, border_radius=8)
        pygame.draw.rect(screen, (0,0,0), char1, 2, border_radius=8)
        pygame.draw.circle(screen, (255,220,150), (char1.centerx, char1.y+26), 22)
        pygame.draw.rect(screen, (180,100,60), (char1.x+12, char1.y+50, 66, 46), border_radius=4)
        # second char
        char2 = pygame.Rect(220, 300, 90, 110)
        pygame.draw.rect(screen, (60,140,180), char2, border_radius=8)
        pygame.draw.rect(screen, (0,0,0), char2, 2, border_radius=8)
        pygame.draw.circle(screen, (255,210,160), (char2.centerx, char2.y+26), 22)
        # fish
        for i in range(3):
            fx = 300 + int(t*60 + i*200) % 400
            fy = 140 + i*30
            pygame.draw.ellipse(screen, (180,180,180), (fx, fy, 50, 22))
            pygame.draw.polygon(screen, (180,180,180), [(fx, fy+11),(fx-12, fy),(fx-12, fy+22)])

        # top bar
        top_bar = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
        top_bar.fill((0,0,0,110))
        screen.blit(top_bar, (0,0))
        title = get_font(22, bold=True).render("PlayTree Launcher", True, (180,220,255))
        screen.blit(title, (30, 24))
        for i,name in enumerate(nav):
            r = pygame.Rect(WIDTH//2 - 180 + i*140, 36, 100, 28)
            active = (i==nav_active)
            col = LIME if active else (200,220,200)
            txt = get_font(18, bold=active).render(name, True, col)
            screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))
            if active:
                pygame.draw.rect(screen, LIME, (r.x+10, r.bottom-2, r.w-20, 2))

        # window controls
        for i,lab in enumerate(["_","□","×"]):
            r = pygame.Rect(WIDTH-90 + i*28, 10, 22, 22)
            pygame.draw.rect(screen, (30,40,30), r, border_radius=3)
            txt = get_font(14, bold=True).render(lab, True, WHITE)
            screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

        # left rail
        btn_settings.draw(screen)
        btn_store.draw(screen)

        # edition toggle — 3 editions
        for i, ed in enumerate(["Java","Bedrock","GoConsoleOS"]):
            r = pygame.Rect(WIDTH//2 -165 + i*110, 480, 100, 30)
            sel = (edition==ed.lower())
            pygame.draw.rect(screen, LIME_DARK if sel else (20,40,20), r, border_radius=8)
            pygame.draw.rect(screen, LIME_BORDER, r, 2, border_radius=8)
            txt = get_font(12 if ed=="GoConsoleOS" else 14, bold=True).render(ed, True, WHITE if sel else TEXT_DIM)
            screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

        # right CTA column like screenshot
        btn_update.draw(screen)
        btn_play.draw(screen)
        btn_mods.draw(screen)

        # version dropdown
        title_map = {"java":"Java","bedrock":"Bedrock","goconsoleos":"GoConsoleOS"}
        ver_label = get_font(14).render(f"Version — PlayTree {title_map.get(edition, edition.title())} Edition", True, (180,220,180))
        screen.blit(ver_label, (WIDTH//2 -300, 500))
        dropdown.draw(screen)

        # bottom socials
        for i,icon in enumerate(["Twitter","Discord"]):
            r = pygame.Rect(20 + i*50, HEIGHT-50, 36, 36)
            pygame.draw.circle(screen, (30,50,30), r.center, 18)
            pygame.draw.circle(screen, LIME_BORDER, r.center, 18, 2)
            txt = get_font(16, bold=True).render(icon[0], True, WHITE)
            screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

        # tab overlays
        if tab=="News":
            panel = pygame.Surface((800, 420), pygame.SRCALPHA)
            panel.fill((0,0,0,170))
            pygame.draw.rect(panel, LIME_BORDER, panel.get_rect(), 2, border_radius=10)
            screen.blit(panel, (WIDTH//2 -400, 120))
            y=140
            for title, desc, when in news:
                f1 = get_font(18, bold=True).render(title, True, LIME)
                f2 = get_font(13).render(desc, True, WHITE)
                f3 = get_font(11).render(when, True, TEXT_DIM)
                screen.blit(f1, (WIDTH//2 -360, y)); screen.blit(f3, (WIDTH//2 + 200, y))
                screen.blit(f2, (WIDTH//2 -360, y+22))
                y+=70
        elif tab=="About us":
            panel = pygame.Surface((860, 300), pygame.SRCALPHA)
            panel.fill((0,0,0,170))
            pygame.draw.rect(panel, LIME_BORDER, panel.get_rect(), 2, border_radius=10)
            screen.blit(panel, (WIDTH//2 -430, 180))
            lines = [
                "PlayTree Launcher — Java & Bedrock for PC",
                "PlayTree Corporation • GoConsole Game Studios • GoStudios • 2026",
                "All versions via piston-meta.mojang.com • Mods via Modrinth",
                "Settings: Java path, RAM (-Xmx), resolution, historical versions",
                "Installations: launcher_profiles.json compatible",
            ]
            y=200
            for ln in lines:
                txt = get_font(14).render(ln, True, WHITE)
                screen.blit(txt, (WIDTH//2 - txt.get_width()//2, y)); y+=36
        elif tab=="Mods":
            panel = pygame.Surface((860, 420), pygame.SRCALPHA)
            panel.fill((0,0,0,175))
            pygame.draw.rect(panel, LIME_BORDER, panel.get_rect(), 2, border_radius=10)
            screen.blit(panel, (WIDTH//2 -430, 120))
            # search bar
            sb = pygame.Rect(WIDTH//2 - 350, 140, 700, 36)
            pygame.draw.rect(screen, (20,30,20), sb, border_radius=8)
            pygame.draw.rect(screen, LIME_BORDER, sb, 2, border_radius=8)
            qtxt = get_font(14).render(mods_query + "|", True, WHITE)
            hint = get_font(12).render("Search Mods — type + Enter (Modrinth)", True, TEXT_DIM)
            screen.blit(qtxt, (sb.x+10, sb.centery - qtxt.get_height()//2))
            screen.blit(hint, (sb.right - hint.get_width() -10, sb.y-18))
            y=190
            for hit in mods_results[:6]:
                txt = get_font(13).render(hit, True, LIME)
                screen.blit(txt, (WIDTH//2 -340, y)); y+=26
            if not mods_results and mods_query:
                txt = get_font(13).render("Press Enter to search", True, TEXT_DIM)
                screen.blit(txt, (WIDTH//2 -100, 220))
        elif tab=="Store":
            panel = pygame.Surface((860, 320), pygame.SRCALPHA)
            panel.fill((0,0,0,170))
            pygame.draw.rect(panel, LIME_BORDER, panel.get_rect(), 2, border_radius=10)
            screen.blit(panel, (WIDTH//2 -430, 180))
            txt = get_font(20, bold=True).render("PlayTree Store — GoConsole", True, LIME)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 210))
            txt2 = get_font(14).render("Skins, Realms, Minecoins — coming soon", True, WHITE)
            screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, 250))
        elif tab=="Settings":
            panel = pygame.Surface((860, 380), pygame.SRCALPHA)
            panel.fill((0,0,0,170))
            pygame.draw.rect(panel, LIME_BORDER, panel.get_rect(), 2, border_radius=10)
            screen.blit(panel, (WIDTH//2 -430, 140))
            y=160
            for k in [f"RAM: {ram}G  (-Xmx{ram}G)", f"Java: {java_path}", f"Historical: {'ON' if profiles['settings'].get('historical') else 'OFF'}", f"Snapshots: {'ON' if profiles['settings'].get('snapshots') else 'OFF'}"]:
                txt = get_font(14).render(k, True, WHITE)
                screen.blit(txt, (WIDTH//2 -340, y)); y+=40

        # footer hint
        hint = get_font(11).render("PlayTree Launcher 1.0.0 • PlayTree Corporation • All versions • Mods via Modrinth", True, (200,220,200))
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-16))

        pygame.display.flip()
    pygame.quit()
    save_profiles(profiles)
    sys.exit(0)

if __name__ == "__main__":
    main()
