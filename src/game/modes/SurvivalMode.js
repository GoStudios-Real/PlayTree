// Survival Mode: gather, craft, build, survive the night.

import { BaseMode } from './BaseMode.js';
import { events } from '../../core/Events.js';
import { mulberry32 } from '../../core/MathUtils.js';

export class SurvivalMode extends BaseMode {
  constructor(game, opts = {}) {
    super(game, opts);
    this.name = 'survival';
    this.displayName = 'Survival';
    this.description = 'Gather resources, craft, build shelter, and survive the Withering nights.';
    this.icon = '⛺';
    this.nightsSurvived = 0;
    this._lastDay = 1;
    this._deathPos = null;
  }

  onStart(opts = {}) {
    const g = this.game;
    g.blockInteraction.setMode('survival');
    g.chat.system('Survival Mode: the night brings the Withering. Gather wood and stone first!');
    // Start player with nothing but hands
    g.player.inventory.slots.fill(null);

    this._on('player:death', () => this._onDeath());
    this._on('day:new', (d) => this._trackDays(d));
  }

  update(dt) {
    const g = this.game;
    if (g.player.dead) return;
    // Hunger-ish: slow heal when well fed (berries). Skip hard hunger.
    // Night survival tracking
    const hour = g.dayNight.getHour();
    if (hour > 20 || hour < 6) {
      // nighttime survival stat handled by day:new
    }
  }

  _trackDays(d) {
    if (d.day > this._lastDay) {
      this.nightsSurvived++;
      this._lastDay = d.day;
      this.game.xp.addStat('nightsSurvived');
      this.game.ui?.announce(`Night ${this.nightsSurvived} survived!`, null, 3000);
      this.game.engine.audio?.levelUp();
    }
  }

  _onDeath() {
    const g = this.game;
    this._deathPos = { x: g.player.pos.x, y: g.player.pos.y, z: g.player.pos.z };
    // Drop entire inventory as loot
    const inv = g.player.inventory;
    for (let i = 0; i < inv.slots.length; i++) {
      const s = inv.slots[i];
      if (s) {
        g.entities.spawnLoot(this._deathPos.x, this._deathPos.y + 0.5, this._deathPos.z, s.id, s.count);
        inv.slots[i] = null;
      }
    }
    g.xp.addXp(-Math.round(g.xp.xp * 0.08));
    g.chat.system('You were claimed by the night. Respawn at the grove.');
    g.player.respawn(8.5, g.world.getSurfaceHeight(8, 8) + 2, 8.5);
    g.ui?.toast('You died. Your items were dropped where you fell.', 3500);
  }

  onKill(from, target) {
    if (from === this.game.player && target?.type) {
      this.game.xp.addStat('kills');
    }
  }
}

export default SurvivalMode;