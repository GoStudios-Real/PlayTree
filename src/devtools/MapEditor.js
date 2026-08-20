// Map editor (dev): fly + click to place/remove blocks from any palette slot.

import { getItem } from '../content/items.js';
import { events } from '../core/Events.js';

export class MapEditor {
  constructor(game) {
    this.game = game;
    this.enabled = false;
  }

  enable() {
    const g = this.game;
    if (this.enabled) return;
    this.enabled = true;
    g.player.setFlying(true);
    g.blockInteraction.setMode('creative');
    g.chat?.system?.('Map Editor: fly around; break/place blocks freely. Press V to toggle flight.');
    events.emit('mapeditor:enabled');
  }

  disable() {
    this.enabled = false;
    events.emit('mapeditor:disabled');
  }

  setPalette(items) {
    const inv = this.game.player.inventory;
    inv.slots.fill(null);
    for (let i = 0; i < items.length && i < inv.size; i++) {
      const item = getItem(items[i]);
      if (item) inv.slots[i] = { id: items[i], count: 64 };
    }
  }
}

export default MapEditor;