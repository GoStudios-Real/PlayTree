# PlayTree — Networking

Networking is designed to work fully offline (simulated) and upgrade to a real
backend when one is available.

## Layers

- `src/net/Protocol.js` — message ids and wire format for the game protocol.
- `src/net/NetClient.js` — client transport: connects to the WebSocket endpoint,
  serializes/deserializes messages, emits events.
- `src/net/NetSimulation.js` — offline/simulated backend used when no server is
  present. Lazy: it spawns only once a world exists (the boot-time `game.world` is
  null), so it must never run before `launchWorld`.
- `src/net/Matchmaker.js` — matchmaking/queueing logic on top of the client.

## Server endpoint

`server/server.mjs` serves the game statically and optionally hosts a WebSocket
endpoint using the `ws` package. If `ws` is not installed the HTTP server still runs
(offline mode is logged). The endpoint:

- sends a `welcome` message on connect `{ playerId, worldSeed, worldName, mode }`;
- echoes `PING`/`PONG`;
- answers join requests with a fake server entry.

This lets multiplayer code paths be exercised without a real multiplayer backend.

## Modes of operation

1. **Offline / simulated** — `NetSimulation` handles everything locally; single
   player behaves identically to a full game.
2. **Local server** — run `npm start` (or `node server/server.mjs`), connect over
   `ws://localhost:8080`.
3. **Production** — swap the `NetClient` transport target to a real gateway; the
   protocol and message shapes stay the same.

## Conventions

- Message ids are defined once in `Protocol.js` and reused by both sides.
- All networked state must be serializable (no THREE objects).
- The simulation must never reference the DOM or WebGL.