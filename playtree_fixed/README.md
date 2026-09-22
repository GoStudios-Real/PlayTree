# PLAYTREE — Chapter 0 : Season 0

*Stylized multiplayer fantasy adventure — GoConsole Game Studios • GoStudios • PlayTree Corporation • 2026*

![PlayTree](https://gostudios-real.github.io/GoStudios-Real-playtree.github.io/itchio_cover_315.png)

**Play now:** [itch.io](https://playtree-corporation.itch.io/playtree) • [Site](https://gostudios-real.github.io/GoStudios-Real-playtree.github.io/) • [Trailer Fortnite](PlayTree_Trailer_Fortnite.mp4)

## Features — 28 Systems + Astro Toilets
- **World:** 9000×9000, 16 regions, day/night 300s, seasons, weather + storm, base building
- **Combat:** 6 classes (Guardian/Ranger/Mage/Mechanic/Beast Tamer/Shadow Assassin), 12 weapons, armor, enchanting, mounts 5, pets + evolution
- **Elite:** Astro Toilets (Trooper → Mothership warp, Trooper→Mothership 7 types, EMP, detaining claws, photon cannon)
- **Social:** Touch + on-screen keyboard, TV mode, Xbox controller, multiplayer `GoConsoleOS` host 7777, battle pass, leaderboards, daily rewards
- **Tech:** Pygame SDL2 1280×720 60FPS, `Launcher` Java/Bedrock/GoConsoleOS all versions, Mods via Modrinth, cloud save GoStudios

## Install
**Windows:** `PLAYTREE Setup.exe` (signed Valid CN=PlayTree Corporation) → `%LOCALAPPDATA%\PLAYTREE` + Desktop/Start Menu • Portable `PLAYTREE.exe` 27 MB
**GoConsoleOS:** `PlayTree GoConsoleOS.exe` — TV fullscreen
**Launcher:** `PlayTree Launcher.exe` — Java & Bedrock & GoConsoleOS (version_manifest_v2.json) + Store/Mods
**Cloud:** `PlayTree Cloud Gaming.exe` — Fighting/Roleplay/Obby/Tycoon hub (6 PlayTrees)

```bash
pip install pygame
python main.py
# or
PLAYTREE.exe
PLAYTREE.exe --goconsoleos
```

## Controls
`WASD` move • `Click` attack • `Space` dodge • `Q` special • `I` inventory • `C` crafting • `Tab` tame • `H` potion • `M` mount • `V` build • `Esc` pause • `F5` save • `F12` screenshot

## Branding
PlayTree Corporation • GoConsole Game Studios • GoStudios — LIME #7ED321 + underwater pixel homescreen (Minecraft Beta), GoStudios account (not Microsoft)

## Build
```bash
pyinstaller --onefile --windowed --icon assets/app.ico main.py
pyinstaller --onefile --windowed --icon assets/app.ico main_goconsole.py --name "PlayTree GoConsoleOS"
```

## License
MIT — ©2026 PlayTree Corporation

---
*Free on itch.io • Mirrored on GitHub Pages • PlayTree Launcher 1.0.0*
