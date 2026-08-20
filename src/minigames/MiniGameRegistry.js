// Mini-game registry: easy to extend — register a new game by name.
// Each game: { id, name, icon, description, class, maxPlayers }

const REGISTRY = new Map();

export function registerMiniGame(id, def) {
  REGISTRY.set(id, def);
}

export function getMiniGame(id) {
  if (id) return REGISTRY.get(id);
  return REGISTRY.values().next().value;
}
export function listMiniGames() { return Array.from(REGISTRY.values()); }

export default { registerMiniGame, getMiniGame, listMiniGames };