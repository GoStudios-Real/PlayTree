// Networking protocol: message framing + schema for the PlayTree network layer.
// Designed so a real server (see server/server.mjs) can speak the same protocol.

export const MSG = {
  HELLO: 1,          // client -> server: {version, nickname, token}
  WELCOME: 2,        // server -> client: {playerId, worldSeed, worldName, mode}
  JOIN: 3,           // {serverId, mode, password?}
  STATE: 4,          // full player state snapshot
  SPAWN_PLAYER: 5,   // {id, nickname, x,y,z, style}
  DESPAWN_PLAYER: 6, // {id}
  MOVE: 7,           // {id, x,y,z, yaw,pitch, vx,vy,vz, grounded}
  BLOCK_SET: 8,      // {x,y,z,id}
  BLOCK_BREAK: 9,    // {x,y,z}
  PROJECTILE: 10,    // {id, x,y,z, vx,vy,vz, damage, from}
  DAMAGE: 11,        // {targetId, amount, sourceId, type}
  DEATH: 12,         // {id, sourceId}
  CHAT: 13,          // {sender, text, ts}
  CHAT_MOD: 14,      // server moderation result
  PARTY: 15,         // {action, ...}
  PING: 16,          // {t}
  PONG: 17,          // {t}
  SERVER_LIST: 18,   // {servers:[]}
  JOIN_RESULT: 19,   // {ok, reason?, server?}
  ERROR: 20,
  ZONE: 21,          // {cx,cz,radius,phase}
  CRATE: 22,         // {x,y,z,opened}
  EMOTE: 23,         // {id, emote}
  REPORT: 24,        // {targetId, reason, text}
  KICK: 25,          // {reason}
};

export function encode(msgId, data) {
  return JSON.stringify({ m: msgId, d: data, t: Date.now() });
}

export function decode(raw) {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

// Compact position for move packets
export function packPos(x, y, z) {
  return [Math.round(x * 8) / 8, Math.round(y * 8) / 8, Math.round(z * 8) / 8];
}

export function packRot(yaw, pitch) {
  return [Math.round(yaw * 100) / 100, Math.round(pitch * 100) / 100];
}

export default { MSG, encode, decode, packPos, packRot };