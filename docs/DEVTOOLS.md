# PlayTree — DevTools & Testing Hooks

## Debug hooks

- `window.g` is set in `src/main.js` for console/devtools access to the whole game
  (`game`, `world`, `player`, `mode`, `engine`, `entities`, ...). Drive the game
  from the console:
  ```js
  window.g.setMode('adventure');       // launch a mode
  window.g.setMode('minigame', { minigame: 'boom_brawl' });
  window.g.player.teleport(8, 45.6, 8);
  ```
- `src/devtools/`:
  - `DebugOverlay.js` — on-screen FPS / state overlay.
  - `DevConsole.js` — in-game console for running expressions.
  - `MapEditor.js` / `SpawnTool.js` — world editing helpers.

## Engine safeguards

- Each engine updater runs in its own try/catch; a failing updater logs
  `updater error` but does not kill the game loop.
- `Engine.fps` exposes a rolling frame-rate readout.

## Headless verification

The game can be booted and driven entirely headlessly:

1. Start the server: `node server/server.mjs` (port 8080).
2. Launch headless Edge with remote debugging:
   ```
   msedge --headless --disable-gpu --no-sandbox --remote-debugging-port=9222 \
     --user-data-dir=<tmp> http://localhost:8080/
   ```
3. Drive it over the Chrome DevTools Protocol (`ws://127.0.0.1:9222/devtools/page/...`)
   via `Runtime.evaluate`, and watch `Runtime.exceptionThrown` and
   `Runtime.consoleAPICalled` (type `error`) for regressions.

PowerShell CDP helpers (WebSocket single-flight receive, `[void]` on
`GetAwaiter().GetResult()`, id-matched responses) live in the temp tooling under
`%TEMP%\opencode\cdp-drive.ps1`.

## Static checks

- `npm run check` runs `scripts/check-syntax.mjs` (parses every module, verifies
  imports) and `scripts/check-exports.mjs` (dynamically imports each module and
  verifies every named import resolves — catches missing/renamed exports).
- Unit tests: `npm test` (see `docs/TESTING.md`).