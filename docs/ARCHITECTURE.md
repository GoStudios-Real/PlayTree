# PlayTree — Architecture

PlayTree "Chapter I: Season I" is an original, modular, multiplayer-ready 3D sandbox /
adventure game platform. It is plain ES modules (no build step) with Three.js r0.160
vendored at `vendor/three.module.js`.

## Stack

- **Language:** JavaScript (ESM, `"type": "module"`), no transpilation.
- **3D:** Three.js r0.160, imported everywhere as `../../vendor/three.module.js`.
- **Server:** minimal static HTTP + optional WebSocket endpoint (`node server/server.mjs`).
- **Rendering:** WebGL via Three.js; headless-verifiable through Chrome DevTools Protocol.

## Module layout

```
index.html          entry point; mounts #app (UI) and creates the Engine
vendor/             vendored Three.js
assets/             static art / audio assets
server/             dev static server + optional ws endpoint
src/
  core/             Config, Engine, MathUtils, Events, Noise, Audio
  content/          data-only databases (blocks, items, recipes, enemies, npcs, quests, story, achievements)
  world/            World, Chunk, ChunkMesher, TerrainGenerator, Structures
  entities/         EntityManager, LivingEntity, Enemy, NPC
  player/           Player, Avatar
  systems/          gameplay systems (combat, crafting, farming, day/night, weather, quests, XP, ...)
  ui/               UIManager, HUD, screens
  game/             Game (orchestrator), modes/
  br/               BattleRoyaleMode, BRBot, BRZone
  minigames/        MiniGameRegistry + games/
  net/              NetClient, NetSimulation, Protocol, Matchmaker
  devtools/         DebugOverlay, DevConsole, MapEditor, SpawnTool
tests/              node-based unit tests (no browser needed)
scripts/            check-syntax.mjs, check-exports.mjs
```

## Boot flow

1. `index.html` creates the `#app` UI container and loads `src/main.js`.
2. `main.js` constructs the UI manager, engine, audio, and the `Game` orchestrator,
   registers all modes (`adventure`, `survival`, `creative`, `br`, `minigame`) and
   mini-games, then exposes `window.g = game` for devtools/testing.
3. The engine starts its fixed-step game loop; the main menu renders.

## Game loop

`src/core/Engine.js` runs a `requestAnimationFrame` loop that:
- computes `dt` (clamped), ticks `fps`;
- runs registered updaters in priority order (Game update at priority 10);
- renders the scene through the active camera;
- isolates each updater in try/catch so one failure never kills the loop
  (logged as `updater error`).

`Game.update(dt)` in turn updates world streaming, the player, entities, systems
(day/night, weather, quests, combat, farming...), the active mode, bots, and the UI.

## World pipeline

Each chunk goes through a status pipeline:

```
empty → generating → lighting → meshing → ready
```

- **generating:** TerrainGenerator fills block data and places surface features.
- **lighting:** simple top-down light pass.
- **meshing:** ChunkMesher builds the Three.js geometry.
- **ready:** streamed into the scene.

Streaming is driven by distance from the player; chunks beyond the render distance
are unloaded and their meshes disposed.

### Important semantics

- `World.getBlock(x, y, z)` returns real block data for `lighting`, `meshing` and
  `ready` statuses, and `0` (air) only for `empty`/`generating`. This prevents
  physics fall-through while a chunk is being re-meshed (e.g. during village builds).
- `World.setBlock` and `setBlockAndRemesh` round coordinates to integers, so float
  positions (from procedural course builders) are safe.
- `World.buildChunkSync(cx, cz)` synchronously generates + lights + meshes a chunk;
  `Game.launchWorld` pre-builds the 3×3 spawn area with it so the player never
  spawns into an empty world.
- `World.findSafeSpawn` locates a spawn based on surface height plus a solidity scan.
- World edits made by the player are saved/loaded through `saveEdits`/`loadEdits`.

## Physics

`src/core/MathUtils.js`:

- `moveWithCollision(bb, isSolid, vel, dt)` resolves each axis explicitly —
  horizontal X, then Z, then vertical Y — clamping the penetrated face. This avoids
  the classic tunneling bug where a vertical penetration larger than the horizontal
  overlap would slide a player sideways through the ground.
- Feet clamp: `bb.minY = v.y + 1; bb.maxY = bb.minY + h`.
- Head clamp: `bb.maxY = v.y; bb.minY = bb.maxY - h`.
- `directionFromYaw(yaw)` maps yaw to a direction; yaw 0 faces −Z.
- `AABB` and `boxCollide` remain for entity physics.

### Gravity

`CONFIG.world.gravity = -28` (NOT under `CONFIG.gameplay`). Player physics applies it
as `vel.y += CONFIG.world.gravity * dt`. Reading gravity from `gameplay` produced a
NaN velocity bug — keep it in `CONFIG.world`.

## Game / mode lifecycle

`Game.launchWorld(modeName, opts)`:

1. `_teardownWorld()` — unloads chunks, stops systems, returns to menu state.
2. Creates a fresh `World` (seeded via `opts.seed ?? Date.now()>>>0`).
3. Rebuilds all world-dependent systems and the `Player`.
4. Pre-builds the spawn area synchronously, then spawns the player safely.
5. Instantiates the mode class (`MODES[modeName] || MODES.adventure`), calls
   `onStart`, marks the world played, and shows the HUD.

Modes are registered with `registerMode(name, cls)`; see `docs/GAMEMODES.md`.

## Key invariants

- Pure logic (content databases, math, terrain math, net protocol) must stay
  importable under Node so unit tests never need a browser or WebGL.
- All THREE usage lives in modules that only run in the browser path.
- Named exports are cross-checked by `scripts/check-exports.mjs`; syntax/import
  integrity by `scripts/check-syntax.mjs` (see `docs/TESTING.md`).