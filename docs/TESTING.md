# PlayTree — Testing

## Running

```bash
npm test       # runs tests/run-tests.mjs
npm run check  # syntax + named-export integrity checks
```

## Unit tests (`tests/`)

Pure, node-runnable tests (no browser, no WebGL):

- `run-tests.mjs` — discovers and runs `*.test.mjs`; prints per-file results.
- `math.test.mjs` — collision/physics regression tests (fast-fall landing on floor,
  wall collision, no sideways tunneling). This is the guard for the axis-explicit
  `moveWithCollision` rewrite.
- `noise.test.mjs` — terrain noise determinism.
- `content.test.mjs` — content databases (blocks/items/recipes/enemies) sanity.
- `inventory.test.mjs`, `recipes.test.mjs` — inventory & crafting logic.
- `quests.test.mjs`, `xp.test.mjs` — quest rewards and XP/season progression.
- `brzone.test.mjs` — battle-royale zone math.

All 8 test files must pass (`8/8 test files passed.`).

## Static checks (`scripts/`)

- `check-syntax.mjs` — parses every module under `src/` and verifies every
  `import ... from` target resolves. Catches syntax errors and missing files.
- `check-exports.mjs` — dynamically imports every module and verifies each named
  import is actually exported by its source. Catches renamed/removed exports
  (e.g. a missing `hash2` re-export that previously broke boot).

Both are wired into `npm run check`.

## Headless integration testing

Beyond unit tests, verify the full boot + mode sweep in a real browser context via
CDP (see `docs/DEVTOOLS.md`):

1. Boot must print `BOOT_OK` and render the menu.
2. `window.g.setMode(m)` must succeed for every registered mode
   (`adventure`, `survival`, `creative`, `br`, `minigame`).
3. Every mini-game must start with its bots/spawn correct.
4. `EXCEPTIONS: 0` and `CONSOLE_ERRORS: 0` after the sweep, player on the ground
   with `onGround: true`, `vy: 0`, `health: 100`.

## Regression history

Runtime bugs caught by the headless sweep and covered here:

- NaN gravity (read from wrong config key) → Player physics test.
- Fall-through during village re-mesh → `getBlock` status semantics.
- Course platforms not placing → `setBlock` float-coordinate rounding.
- Bots adding `undefined` to the scene → `BRBot._buildBody` must return its group.
- `getMiniGame()` returning undefined → defaults to first registered game.