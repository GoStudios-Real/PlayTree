# PlayTree — Game Modes

Modes are classes registered with `registerMode(name, cls)` (in `src/main.js`) and
instantiated by `Game.launchWorld` (`MODES[modeName] || MODES.adventure`). Each mode
extends `BaseMode` and implements `onStart(opts)`, `update(dt)`, and optionally
`onStop`, `onKill(from, target)`.

Registered modes:

| Key          | Class                | Description |
|--------------|----------------------|-------------|
| `adventure`  | `AdventureMode`      | Open sandbox-adventure in The Heartwood Grove (default). |
| `survival`   | `SurvivalMode`       | Health/hunger survival with enemies and day/night. |
| `creative`   | `CreativeMode`       | Free building, no survival pressure. |
| `br`         | `BattleRoyaleMode`   | Battle-royale drop into a shrinking zone with AI bots. |
| `minigame`   | `MiniGameMode`       | Hosts any registered mini-game (pick with `opts.minigame`). |

## `src/game/modes/`

- `BaseMode.js` — shared lifecycle helpers.
- `AdventureMode.js` — builds the village/town around spawn (via `Structures` +
  chunk re-mesh), sets the day, greets the player.
- `SurvivalMode.js` — enables hunger and enemy spawning.
- `CreativeMode.js` — flying + unrestricted building.
- `BattleRoyaleMode.js` — `BRZone` shrinking zone, bus drop, bots (`BRBot`), loot
  crates, eliminations and placements.

## Mini-games — `src/minigames/`

Registered through `registerMiniGame(id, def)` into `MiniGameRegistry`.
`getMiniGame(id)` returns the definition; with no id it returns the first registered
game (so a bare `setMode('minigame')` always launches something).

| Id                    | Name                    | Description |
|-----------------------|-------------------------|-------------|
| `obstacle_course`     | Canopy Dash             | Race floating platforms to the finish. |
| `boom_brawl`          | BoomBarrel Brawl        | Barrel arena brawl vs 4 bots. |
| `capture_the_sprout`  | Capture the Sprout      | Capture-the-flag vs 4 bots. |

Mini-games run their own `update(dt)` loops (which drive the bots) and manage their
own timers/intervals (cleared in `onStop`).

## Bot conventions

- Bots are `BRBot` instances pushed onto `game.bots`.
- The hosting mode is responsible for calling `bot.update(dt, world, players, zone)`
  with full arguments; `BRBot.update` early-returns when `world` is missing so the
  generic `Game.updateBots` hook (which passes only `dt`) is harmless.

## Notes

- Register names must match the keys used by the mode-select UI (`br`, `minigame`).
- A mode that tears the world down internally (e.g. "not found" → `returnToMenu`)
  must not let `launchWorld` continue using a nulled `this.world`.