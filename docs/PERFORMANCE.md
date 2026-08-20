# PlayTree — Performance

## Rendering

- Quality levels are set via `Engine.applyQuality()` (called after the sun is
  created) and read from `engine.settings.get('quality')`. On `low` quality the
  weather system is disabled.
- Chunk meshing is batched per chunk; only changed chunks are re-meshed
  (`World.remeshChunk` skips chunks that are not `ready`).
- Beyond-render-distance chunks are unloaded and their geometries disposed to bound
  GPU memory.

## Streaming & sync work

- `Game.launchWorld` pre-builds only the 3×3 spawn area synchronously
  (`buildChunkSync`) so the player spawns safely without generating the whole world.
- Normal world streaming is per-frame and distance-driven; heavy structure builds
  (village) re-mesh the affected chunks once.

## Physics

- `moveWithCollision` resolves axes independently and clamps the penetrated face —
  fast, deterministic, and free of the "large vertical penetration" tunneling bug.
- Block lookups during physics go through `World.getBlock`; chunks in
  `meshing`/`lighting` return real data so physics never sees phantom air (avoids
  falling through the ground during remesh storms).

## Data

- Content databases are module-level plain objects (no per-frame allocation).
- Voxel data lives in typed arrays inside each `Chunk`.

## Measuring

- `Engine.fps` + `DebugOverlay` for a live readout.
- Headless CDP runs report `fps`, chunk count, exceptions, and console errors at the
  end of a test sweep — use those numbers as the regression baseline (adventure
  target: 30+ fps headless, 0 exceptions, 0 console errors).
- Keep synchronous work inside `update` minimal; expensive generation stays in the
  per-chunk pipeline.