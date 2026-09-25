"""PlayTree Creator Studio — build your own PlayTree games.

Cross-platform (Windows / macOS / Linux): paint a world, place the player
spawn, coins, enemies, hazards and the goal, playtest instantly, then export
a standalone game (zip with launchers) anyone can play.

Controls
  Left click / drag  paint selected tile
  Right click        erase
  1-9,0              pick tile
  P                  playtest (ESC returns to the editor)
  Ctrl+S             save
"""
import os
import sys
import shutil
import zipfile

import pygame

from runtime import (EMPTY, GROUND, STONE, WATER, LAVA, TREE, COIN, ENEMY, GOAL, SPAWN,
                     TILE_COLORS, TILE_NAMES, new_project, save_project, load_project,
                     PlayGame, run as run_game)

W, H = 1280, 720
if getattr(sys, "frozen", False):
    BASE = os.path.dirname(os.path.abspath(sys.executable))
    DATA = getattr(sys, "_MEIPASS", BASE)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    DATA = BASE
PROJECTS = os.path.join(BASE, "projects")
EXPORTS = os.path.join(BASE, "exports")

TOOLBAR = [("New", 8), ("Open", 76), ("Save", 144), ("Playtest", 212), ("Export", 300), ("Quit", 376)]
PALETTE_TOP = 64


def runtime_source_path():
    p = os.path.join(DATA, "runtime.py")
    if os.path.exists(p):
        return p
    p = os.path.join(BASE, "runtime.py")
    if os.path.exists(p):
        return p
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime.py")


def export_project(project, exports_dir=None):
    """Export a standalone game folder + zip. Returns zip path."""
    exports_dir = exports_dir or EXPORTS
    name = "".join(ch for ch in project.get("name", "MyGame") if ch.isalnum() or ch in " -_").strip() or "MyGame"
    folder = os.path.join(exports_dir, name)
    os.makedirs(folder, exist_ok=True)
    save_project(project, os.path.join(folder, "game.json"))
    shutil.copyfile(runtime_source_path(), os.path.join(folder, "runtime.py"))
    with open(os.path.join(folder, "run.bat"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write('@echo off\r\npython "runtime.py"\r\npause\r\n')
    with open(os.path.join(folder, "run.sh"), "w", encoding="utf-8", newline="\n") as f:
        f.write('#!/bin/sh\ncd "$(dirname "$0")"\npython3 "runtime.py"\n')
    os.chmod(os.path.join(folder, "run.sh"), 0o755)
    shutil.copyfile(os.path.join(folder, "run.sh"), os.path.join(folder, "run.command"))
    with open(os.path.join(folder, "README.txt"), "w", encoding="utf-8") as f:
        f.write("{}\n\nMade with PlayTree Creator Studio.\n\n"
                "Play: python runtime.py  (needs Python 3 + pygame)\n"
                "Or double-click run.bat (Windows) / run.command (macOS) / ./run.sh (Linux)\n"
                "Free on desktop and mobile — see PlayTree Games.\n".format(project.get("name", "My Game")))
    zpath = os.path.join(exports_dir, name + "-standalone.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in os.listdir(folder):
            z.write(os.path.join(folder, fn), os.path.join(name, fn))
    return zpath


class Editor:
    def __init__(self, surface):
        self.surf = surface
        self.project = new_project()
        self.selected = GROUND
        self.mode = "edit"
        self.text_kind = None
        self.text_buf = ""
        self.status = "Paint your world — P = playtest, ESC = quit"
        self.toast = ""
        self.toast_t = 0.0
        self._tool_rects = [(pygame.Rect(x + 8, 12, w, 32), label)
                            for label, x, w in
                            [("New", 8, 60), ("Open", 72, 60), ("Save", 136, 60),
                             ("Playtest", 200, 78), ("Export", 284, 70), ("Quit", 360, 60)]]
        self._pal_rects = []
        for i, tname in enumerate(TILE_NAMES):
            self._pal_rects.append((pygame.Rect(8, PALETTE_TOP + i * 58, 150, 50), i))
        self.name_rect = pygame.Rect(W - 330, 12, 320, 32)

    # ---------- geometry ----------
    def grid_metrics(self):
        gx, gy = 170, 64
        cell = min(32, (W - gx - 16) // self.project["cols"],
                   (H - gy - 40) // self.project["rows"])
        return gx, gy, max(8, cell)

    def cell_at(self, pos):
        gx, gy, cell = self.grid_metrics()
        x = (pos[0] - gx) // cell
        y = (pos[1] - gy) // cell
        if 0 <= x < self.project["cols"] and 0 <= y < self.project["rows"]:
            return int(x), int(y)
        return None

    # ---------- editing ----------
    def paint(self, cell_xy, erase=False):
        if not cell_xy:
            return
        x, y = cell_xy
        cells = self.project["cells"]
        if erase:
            if cells[y][x] != EMPTY:
                cells[y][x] = EMPTY
            return
        t = self.selected
        if t == SPAWN:
            for ry in range(self.project["rows"]):
                for rx in range(self.project["cols"]):
                    if cells[ry][rx] == SPAWN:
                        cells[ry][rx] = EMPTY
            self.project["player"] = {"x": x, "y": y}
        cells[y][x] = t

    def set_tile(self, t):
        self.selected = t
        self.status = "Selected: " + TILE_NAMES[t]

    # ---------- actions ----------
    def new_project(self):
        self.project = new_project(name="My PlayTree Game")
        self.status = "New project created."

    def playtest(self):
        self.mode = "play"
        pygame.display.set_caption("PlayTree Creator Studio — PLAYTEST (ESC = back)")
        run_game(self.project, surface=self.surf)
        pygame.display.set_caption("PlayTree Creator Studio")
        self.mode = "edit"
        self.status = "Playtest finished — back to the editor."

    def export(self):
        try:
            zpath = export_project(self.project)
            self.status = "Exported: " + zpath
            self.show_toast("Exported standalone game!")
        except Exception as e:
            self.status = "Export failed: {}".format(e)
            self.show_toast("Export failed — see status bar")

    def save(self, filename=None):
        fn = (filename or self.project["name"])
        fn = "".join(ch for ch in fn if ch.isalnum() or ch in " -_").strip() or "MyGame"
        path = os.path.join(PROJECTS, fn + ".ptproj")
        save_project(self.project, path)
        self.status = "Saved: " + path
        self.show_toast("Project saved!")

    def open(self, filename):
        fn = "".join(ch for ch in filename if ch.isalnum() or ch in " -_").strip()
        path = os.path.join(PROJECTS, fn + ".ptproj")
        if os.path.exists(path):
            self.project = load_project(path)
            self.status = "Opened: " + path
            self.show_toast("Project loaded!")
        else:
            self.status = "Not found: " + path
            self.show_toast("Project not found")

    def show_toast(self, msg):
        self.toast = msg
        self.toast_t = 2.2

    # ---------- input ----------
    def handle_event(self, ev):
        if ev.type == pygame.QUIT:
            return False
        if self.mode == "text":
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    kind, buf = self.text_kind, self.text_buf
                    self.mode, self.text_kind = "edit", None
                    if kind == "name" and buf.strip():
                        self.project["name"] = buf.strip()
                        self.status = "Renamed to " + buf.strip()
                    elif kind == "save":
                        self.save(buf)
                    elif kind == "open":
                        self.open(buf)
                elif ev.key == pygame.K_ESCAPE:
                    self.mode, self.text_kind = "edit", None
                    self.status = "Cancelled."
                elif ev.key == pygame.K_BACKSPACE:
                    self.text_buf = self.text_buf[:-1]
                elif ev.unicode and ev.unicode.isprintable() and len(self.text_buf) < 40:
                    self.text_buf += ev.unicode
            return True
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                return False
            if ev.key == pygame.K_p:
                self.playtest()
                return True
            if ev.key == pygame.K_s and (ev.mod & pygame.KMOD_CTRL):
                self.save()
                return True
            digits = {pygame.K_1: GROUND, pygame.K_2: STONE, pygame.K_3: WATER,
                      pygame.K_4: LAVA, pygame.K_5: TREE, pygame.K_6: COIN,
                      pygame.K_7: ENEMY, pygame.K_8: GOAL, pygame.K_9: SPAWN,
                      pygame.K_0: EMPTY}
            if ev.key in digits:
                self.set_tile(digits[ev.key])
                return True
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button in (1, 3):
            erase = ev.button == 3
            if not erase:
                for rect, label in self._tool_rects:
                    if rect.collidepoint(ev.pos):
                        {"New": self.new_project, "Open": lambda: self.begin_text("open", "Open project:"),
                         "Save": lambda: self.begin_text("save", "Save as:"),
                         "Playtest": self.playtest, "Export": self.export,
                         "Quit": lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))}[label]()
                        return True
                if self.name_rect.collidepoint(ev.pos):
                    self.begin_text("name", "Project name:")
                    return True
                for rect, t in self._pal_rects:
                    if rect.collidepoint(ev.pos):
                        self.set_tile(t)
                        return True
            self.paint(self.cell_at(ev.pos), erase=erase)
            return True
        if ev.type == pygame.MOUSEMOTION and ev.buttons[0]:
            self.paint(self.cell_at(ev.pos))
            return True
        if ev.type == pygame.MOUSEMOTION and ev.buttons[2]:
            self.paint(self.cell_at(ev.pos), erase=True)
            return True
        return False

    def begin_text(self, kind, prompt):
        self.mode = "text"
        self.text_kind = kind
        self.text_prompt = prompt
        self.text_buf = self.project["name"] if kind == "name" else ""

    # ---------- drawing ----------
    def draw(self):
        s = self.surf
        s.fill((14, 19, 32))
        font = pygame.font.Font(None, 24)
        small = pygame.font.Font(None, 20)
        # toolbar
        pygame.draw.rect(s, (19, 26, 44), (0, 0, W, 54))
        pygame.draw.line(s, (36, 48, 73), (0, 54), (W, 54), 2)
        for rect, label in self._tool_rects:
            pygame.draw.rect(s, (30, 42, 66), rect, border_radius=7)
            pygame.draw.rect(s, (89, 196, 143), rect, 1, border_radius=7)
            s.blit(font.render(label, True, (207, 233, 218)), rect.move(10, 7))
        pygame.draw.rect(s, (30, 42, 66), self.name_rect, border_radius=7)
        s.blit(small.render("Project: " + self.project["name"] + "   [click to rename]",
                            True, (143, 183, 160)), self.name_rect.move(10, 8))
        # palette
        pygame.draw.rect(s, (16, 23, 38), (0, 54, 162, H - 54))
        for rect, t in self._pal_rects:
            sel = (t == self.selected)
            pygame.draw.rect(s, TILE_COLORS[t], (rect.x + 6, rect.y + 6, 34, 34), border_radius=6)
            pygame.draw.rect(s, (255, 255, 255) if sel else (60, 76, 100),
                             rect, 2 if sel else 1, border_radius=7)
            s.blit(small.render("{} [{}]".format(TILE_NAMES[t], (t + 1) % 10),
                                True, (230, 255, 235) if sel else (150, 170, 190)),
                   (rect.x + 48, rect.y + 17))
        # grid
        gx, gy, cell = self.grid_metrics()
        cells = self.project["cells"]
        for y in range(self.project["rows"]):
            for x in range(self.project["cols"]):
                r = pygame.Rect(gx + x * cell, gy + y * cell, cell, cell)
                c = cells[y][x]
                col = TILE_COLORS[c] if c != EMPTY else ((30, 40, 58) if (x + y) % 2 else (26, 35, 52))
                pygame.draw.rect(s, col, r)
                if c == COIN:
                    pygame.draw.circle(s, (255, 246, 190), r.center, max(3, cell // 4))
                elif c == ENEMY:
                    pygame.draw.circle(s, (40, 10, 10), r.center, max(3, cell // 4))
                elif c == GOAL:
                    pygame.draw.rect(s, (255, 255, 255), r.inflate(-cell // 2, -cell // 2), 2)
                elif c == SPAWN:
                    pygame.draw.circle(s, (255, 255, 255), r.center, max(3, cell // 4))
                pygame.draw.rect(s, (36, 48, 73), r, 1)
        # status bar
        pygame.draw.rect(s, (19, 26, 44), (0, H - 30, W, 30))
        s.blit(small.render(self.status, True, (143, 183, 160)), (10, H - 24))
        if self.toast_t > 0:
            tw = font.render(self.toast, True, (234, 255, 242))
            box = pygame.Surface((tw.get_width() + 24, 34), pygame.SRCALPHA)
            box.fill((19, 26, 44, 235))
            pygame.draw.rect(box, (89, 255, 157), box.get_rect(), 1, border_radius=8)
            box.blit(tw, (12, 7))
            s.blit(box, (W // 2 - box.get_width() // 2, H - 76))
        # text-input modal
        if self.mode == "text":
            dim = pygame.Surface((W, H), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 150))
            s.blit(dim, (0, 0))
            panel = pygame.Rect(W // 2 - 240, H // 2 - 60, 480, 120)
            pygame.draw.rect(s, (19, 26, 44), panel, border_radius=12)
            pygame.draw.rect(s, (89, 196, 143), panel, 2, border_radius=12)
            s.blit(font.render(getattr(self, "text_prompt", ""), True, (207, 233, 218)),
                   (panel.x + 20, panel.y + 18))
            ibox = pygame.Rect(panel.x + 20, panel.y + 48, panel.w - 40, 34)
            pygame.draw.rect(s, (11, 16, 28), ibox, border_radius=6)
            txt = font.render(self.text_buf + "_", True, (255, 215, 94))
            s.blit(txt, (ibox.x + 8, ibox.y + 7))
            s.blit(small.render("Enter = OK    Esc = Cancel", True, (120, 140, 160)),
                   (panel.x + 20, panel.y + 92))


def main():
    pygame.init()
    surf = pygame.display.set_mode((W, H))
    pygame.display.set_caption("PlayTree Creator Studio")
    editor = Editor(surf)
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000.0
        editor.toast_t = max(0.0, editor.toast_t - dt)
        for ev in pygame.event.get():
            if not editor.handle_event(ev):
                pygame.quit()
                return
        editor.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
