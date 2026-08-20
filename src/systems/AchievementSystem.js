// Achievement system: tracks stats and awards achievements.

import { ACHIEVEMENTS } from '../content/achievements.js';
import { events } from '../core/Events.js';
import { Storage } from '../core/Storage.js';

const SAVE = 'pt.achievements.v1';

export class AchievementSystem {
  constructor(game) {
    this.game = game;
    this.defs = ACHIEVEMENTS;
    this.unlocked = new Set(Storage.get(SAVE) || []);
    this._last = {};
    events.on('stat:changed', (d) => this._checkStat(d));
    events.on('level:up', (d) => this._checkStat({ name: 'level', value: d.level }));
    events.on('quest:completed', () => {
      const c = this.game.quests.completed.length;
      this._checkStat({ name: 'questsCompleted', value: c });
    });
    events.on('enemy:defeated', (d) => {
      if (d.enemy?.boss) this._checkStat({ name: 'bossesKilled', value: (this.game.xp.stats.bossesKilled || 0) });
    });
  }

  _checkStat(d) {
    for (const a of this.defs) {
      if (this.unlocked.has(a.id)) continue;
      const val = d.name === a.stat ? d.value : (this.game.xp.stats[a.stat] || 0);
      if (val >= a.threshold) this.unlock(a);
    }
  }

  unlock(def) {
    this.unlocked.add(def.id);
    Storage.set(SAVE, Array.from(this.unlocked));
    this.game.xp.addXp(def.xp || 0);
    this.game.ui?.toast(`Achievement unlocked: ${def.name} (+${def.xp} XP)`, 4500);
    this.game.engine.audio?.achievement();
    events.emit('achievement:unlocked', def);
  }

  isUnlocked(id) { return this.unlocked.has(id); }
}

export default AchievementSystem;