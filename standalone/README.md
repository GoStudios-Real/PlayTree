# PlayTree — standalone & install builds

Download links on the PlayTree Games page point here.

## Main game

| Platform | Install |
|---|---|
| Windows | `PLAYTREE.exe` (signed, double-click to play) |
| Android | `GoLiteAndroid/vendor/goconsole/prebuilt/PlayTree.apk` (sideload) |
| macOS | run `playtree_fixed/build_macos.sh` on a Mac (Python 3.10+ & PyInstaller) |
| Linux | run `playtree_fixed/build_linux.sh` on Linux (Python 3.10+ & PyInstaller) |

All builds are free. macOS/Linux builds must be produced on their native OS
(PyInstaller rule) — the scripts install dependencies and output
`dist/PLAYTREE`.

## Mini games (Python + pygame)

Each `PlayTree*.zip` contains a self-contained game:

1. Unzip
2. `pip install pygame`
3. Double-click `run.bat` (Windows) or run `./run.sh` (macOS/Linux)

## PlayTree Creator Studio

See `PlayTreeCreatorStudio/` — build your own PlayTree games, export them as
standalone zips for Windows/macOS/Linux. Its own build scripts produce native
executables on each platform.
