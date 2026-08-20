// Creative Mode: unlimited building, flight, no damage.

import { BaseMode } from './BaseMode.js';
import { BLOCKS } from '../../content/blocks.js';
import { events } from '../../core/Events.js';

export class CreativeMode extends BaseMode {
  constructor(game, opts = {}) {
    super(game, opts);
    this.name = 'creative';
    this.displayName = 'Creative';
    this.description = 'Build anything, fly anywhere. The world is your canvas.';
    this.icon = '🧱';
    this.allowFly = true;
    this.blockInteractionPriority = 'break';
  }

  onStart(opts = {}) {
    const g = this.game;
    g.blockInteraction.setMode('creative');
    g.blockInteraction.player = g.player;
    g.player.setFlying(true);
    g.chat.system('Creative Mode: break with left click, build with right click. Press V to toggle flight.');
    g.chat.system('Your hotbar holds every block. Open the inventory (E) to grab more.');

    // Fill hotbar with a curated palette of placeable blocks
    const palette = [1, 2, 3, 6, 7, 8, 9, 29, 20, 21, 22, 36, 43, 19, 39, 38, 37, 4];
    const inv = g.player.inventory;
    for (let i = 0; i < 9; i++) {
      inv.slots[i] = { id: palette[i], count: 64 };
    }
    // Fill backpack with remaining blocks
    let k = 9;
    for (const b of BLOCKS) {
      if (k >= inv.size) break;
      if (b.id === 0 || b.liquid || !b.solid && ![22, 31, 32, 44, 48, 49, 50, 23, 24, 25, 26].includes(b.id)) continue;
      if (inv.slots.some(s => s && s.id === b.id)) continue;
      inv.slots[k++] = { id: b.id, count: 64 };
    }
    events.emit('inventory:changed', inv);
  }

  update(dt) {
    const g = this.game;
    // Creative invincibility + full stamina
    g.player.health = g.player.maxHealth;
    g.player.stamina = g.player.maxStamina;
    g.player.fallDamageDisabled = true;
  }

  onPlayerDeath() {
    // Creative players don't die
  }
}

export default CreativeMode;