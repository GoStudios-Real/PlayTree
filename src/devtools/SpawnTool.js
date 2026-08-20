// Spawn tool (dev): spawn any enemy/bot at the player's position or look target.

import { ENEMIES } from '../content/enemies.js';
import { events } from '../core/Events.js';

export class SpawnTool {
  constructor(game) {
    this.game = game;
    events.on('devtool:spawn', (type) => this.spawn(type));
  }

  spawn(type) {
    const g = this.game;
    const target = g.blockInteraction?.target || {};
    const x = (target.x ?? Math.floor(g.player.pos.x)) + 0.5;
    const y = (target.y ?? Math.floor(g.player.pos.y)) + 1;
    const z = (target.z ?? Math.floor(g.player.pos.z)) + 0.5;
    g.entities.spawnEnemy(type, x, y, z);
    const def = ENEMIES[type];
    g.chat?.system?.(`Spawned ${def?.name || type} at ${x.toFixed(0)},${y.toFixed(0)},${z.toFixed(0)}`);
  }

  listDefs() { return ENEMIES; }
}

export default SpawnTool;