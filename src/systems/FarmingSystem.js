// Farming system: crop growth, harvesting, seeds, farmland.

import { events } from '../core/Events.js';
import { getItem } from '../content/items.js';
import { getBlock as getBlockDef } from '../content/blocks.js';

// seedItemId -> { cropBlock, harvestItem, growTime, yieldMin, yieldMax }
export const CROPS = {
  350: { cropBlock: 26, harvestItem: 300, growTime: 30, yieldMin: 1, yieldMax: 3, name: 'Sprout' },
  351: { cropBlock: 27, harvestItem: 27, growTime: 45, yieldMin: 1, yieldMax: 1, name: 'Pumpkin' },
  352: { cropBlock: 31, harvestItem: 31, growTime: 50, yieldMin: 1, yieldMax: 2, name: 'Glowcap' },
};

export class FarmingSystem {
  constructor(game) {
    this.game = game;
    this.crops = new Map(); // "x,y,z" -> { stage, growth, cropDef, seedItem }
    this._handler = (d) => this._onPlaced(d);
    events.on('block:placed', this._handler);
    this._plantHandler = (d) => this._onPlanted(d);
    events.on('farming:plant', this._plantHandler);
  }

  _onPlaced(d) { /* for pumpkin/glowcap natural spawns nothing to do */ }

  // Called when a seed item is used on ground.
  plantSeed(player, blockX, blockY, blockZ, seedItemId) {
    const crop = CROPS[seedItemId];
    if (!crop) return false;
    // Must target a solid block below
    const groundId = this.game.world.getBlock(blockX, blockY, blockZ);
    if (!getBlockDef(groundId).solid) return false;
    // Convert ground to farmland (dirt -> tilled)
    if (groundId === 1 || groundId === 2) {
      this.game.world.setBlockAndRemesh(blockX, blockY, blockZ, 34);
    }
    const y = blockY + 1;
    const existing = this.game.world.getBlock(blockX, y, blockZ);
    if (existing !== 0 && existing !== 26) return false;
    this.game.world.setBlockAndRemesh(blockX, y, blockZ, crop.cropBlock);
    const key = `${blockX},${y},${blockZ}`;
    this.crops.set(key, { stage: 0, growth: 0, cropDef: crop, seedItem: seedItemId });
    player.inventory.removeFromSlot(player.inventory.selected, 1);
    events.emit('farming:planted', { itemId: seedItemId, count: 1, x: blockX, y, z: blockZ });
    this.game.xp?.addStat?.('cropsPlanted');
    return true;
  }

  harvest(player, x, y, z) {
    const key = `${x},${y},${z}`;
    const crop = this.crops.get(key);
    if (!crop) return false;
    if (crop.stage < 3) {
      this.game.ui?.toast('Not ready to harvest yet.', 1500);
      return false;
    }
    const yieldCount = crop.cropDef.yieldMin + Math.floor(Math.random() * (crop.cropDef.yieldMax - crop.cropDef.yieldMin + 1));
    this.game.player.inventory.add(crop.cropDef.harvestItem, yieldCount);
    // Small chance to recover seed
    if (Math.random() < 0.4) this.game.player.inventory.add(crop.seedItem, 1);
    this.crops.delete(key);
    this.game.world.setBlockAndRemesh(x, y, z, 0);
    events.emit('farming:harvested', { blockId: crop.cropDef.cropBlock, count: yieldCount, x, y, z });
    this.game.xp?.addStat?.('cropsHarvested');
    this.game.ui?.toast(`Harvested ${crop.cropDef.name} x${yieldCount}`, 2000);
    this.game.engine.audio?.pickup();
    return true;
  }

  update(dt, player) {
    const now = performance.now();
    // Growth needs daylight + farmland below
    for (const [key, crop] of this.crops) {
      const [x, y, z] = key.split(',').map(Number);
      const below = this.game.world.getBlock(x, y - 1, z);
      const hasFarmland = below === 34;
      // Check sky / daylight
      const hour = this.game.dayNight?.getHour() || 12;
      const daytime = hour > 6 && hour < 18;
      if (hasFarmland && daytime) {
        crop.growth += dt;
        const newStage = Math.min(3, Math.floor(crop.growth / crop.cropDef.growTime * 4));
        if (newStage > crop.stage) {
          crop.stage = newStage;
          // Visual growth: swap to stage-variant block colors via particle hint
          if (newStage === 3 && player) {
            this.game.engine.particles?.spawn(x + 0.5, y + 0.5, z + 0.5, { count: 4, color: [0.4, 0.9, 0.4], life: 0.6 });
          }
        }
      }
      if (!hasFarmland) {
        // wither back if no farmland
        crop.growth = Math.max(0, crop.growth - dt * 0.5);
      }
    }
  }

  isCropBlock(x, y, z) {
    return this.crops.has(`${x},${y},${z}`);
  }

  dispose() {
    events.off('block:placed', this._handler);
    events.off('farming:plant', this._plantHandler);
  }
}

export default FarmingSystem;