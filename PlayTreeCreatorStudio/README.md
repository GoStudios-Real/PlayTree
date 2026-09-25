# PlayTree Creator Studio

Create your own PlayTree games — **Windows, macOS and Linux**.

Paint a tile world, place your spawn, coins, enemies, hazards and the goal,
playtest instantly, then **export a standalone game** (a zip with launchers
anyone can play on desktop; runs on mobile too via Python/pygame).

## Run (development)

```
pip install pygame
python creator_studio.py
```

## Controls

| Input | Action |
|---|---|
| Left click / drag | paint selected tile |
| Right click / drag | erase |
| 1–9, 0 | pick tile (Ground, Stone, Water, Lava, Tree, Coin, Enemy, Goal, Spawn, Empty) |
| P | playtest (ESC returns to the editor) |
| Ctrl+S | save project |
| Click title | rename project |

Projects save as `projects/<name>.ptproj`.
Export writes `exports/<name>/` plus `<name>-standalone.zip`.

## Build a native studio app

| OS | Script |
|---|---|
| Windows | `build_windows.bat` → `dist/PlayTreeCreatorStudio.exe` |
| macOS | `build_macos.sh` → `dist/PlayTreeCreatorStudio` |
| Linux | `build_linux.sh` → `dist/PlayTreeCreatorStudio` |

(PyInstaller must run on the target OS — each script installs its deps.)

## Exported games

Every export contains `game.json`, `runtime.py`, `run.bat`, `run.sh`,
`run.command` and a README — double-click to play, or `python runtime.py`.
Share the zip anywhere; it works fully offline.
