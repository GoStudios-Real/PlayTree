// Daily quests: three date-seeded picks per day, tracked from cumulative
// XP stats with per-day baselines. Mirrors the desktop shell's daily pool
// cadence (LCG seeded by crc32 of the local date) with web-trackable goals.

import { events } from '../core/Events.js';
import { Storage } from '../core/Storage.js';

const SAVE_KEY = 'pt.daily.v1';

export const DAILY_POOL = [
  { id: 'd_mine10',  desc: 'Mine 10 blocks',    stat: 'blocksMined',   needed: 10,  xp: 50 },
  { id: 'd_mine30',  desc: 'Mine 30 blocks',    stat: 'blocksMined',   needed: 30,  xp: 90 },
  { id: 'd_place20', desc: 'Place 20 blocks',   stat: 'blocksPlaced',  needed: 20,  xp: 65 },
  { id: 'd_craft4',  desc: 'Craft 4 items',     stat: 'itemsCrafted',  needed: 4,   xp: 60 },
  { id: 'd_kill5',   desc: 'Defeat 5 enemies',  stat: 'enemiesKilled', needed: 5,   xp: 70 },
  { id: 'd_kill12',  desc: 'Defeat 12 enemies', stat: 'enemiesKilled', needed: 12,  xp: 110 },
  { id: 'd_boss1',   desc: 'Defeat a boss',     stat: 'bossesKilled',  needed: 1,   xp: 150 },
  { id: 'd_walk800', desc: 'Walk 800 blocks',   stat: 'distance',      needed: 800, xp: 75 },
];

const CRC_TABLE = (() => {
  const t = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(str) {
  const bytes = new TextEncoder().encode(str);
  let c = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}

function todayKey() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export function dailyPicks(dateStr) {
  let seed = crc32(dateStr) % 2147483647 || 1;
  const idx = [];
  while (idx.length < 3) {
    seed = (seed * 48271) % 2147483647;
    const j = seed % DAILY_POOL.length;
    if (!idx.includes(j)) idx.push(j);
  }
  return idx.map(j => DAILY_POOL[j]);
}

export class DailyQuestSystem {
  constructor(game) {
    this.game = game;
    this.save = Storage.get(SAVE_KEY) || null;
    this._ensureToday();
    this._onStat = (d) => this._onStatChanged(d);
    events.on('stat:changed', this._onStat);
  }

  _ensureToday() {
    const today = todayKey();
    if (this.save && this.save.date === today) return;
    const stats = this.game.xp?.stats || {};
    this.save = {
      date: today,
      quests: dailyPicks(today).map(def => ({
        id: def.id,
        base: stats[def.stat] || 0,
        done: false,
      })),
    };
    this.persist();
  }

  persist() {
    Storage.set(SAVE_KEY, this.save);
  }

  _def(id) {
    return DAILY_POOL.find(d => d.id === id);
  }

  _progress(q) {
    const def = this._def(q.id);
    if (!def) return 0;
    const value = this.game.xp?.stats?.[def.stat] || 0;
    return Math.max(0, Math.min(def.needed, Math.floor(value - (q.base || 0))));
  }

  _onStatChanged() {
    this._ensureToday();
    let changed = false;
    for (const q of this.save.quests) {
      if (q.done) continue;
      const def = this._def(q.id);
      if (!def) continue;
      if (this._progress(q) >= def.needed) {
        q.done = true;
        changed = true;
        this.game.xp?.addXp?.(def.xp || 0);
        const coins = Math.round((def.xp || 0) * 0.5);
        if (coins) this.game.store?.addCoins?.(coins);
        this.game.ui?.toast(`Daily complete: ${def.desc} (+${def.xp} XP${coins ? `, +${coins} coins` : ''})`, 5000);
        this.game.engine.audio?.questComplete();
        events.emit('daily:completed', { quest: def, date: this.save.date });
      }
    }
    if (changed) this.persist();
  }

  // [{ id, desc, current, count, done }] for the HUD quest tracker.
  summary() {
    this._ensureToday();
    return this.save.quests.map(q => {
      const def = this._def(q.id);
      if (!def) return null;
      return { id: q.id, desc: def.desc, current: this._progress(q), count: def.needed, done: !!q.done };
    }).filter(Boolean);
  }

  doneCount() {
    return this.save.quests.filter(q => q.done).length;
  }

  dispose() {
    events.off('stat:changed', this._onStat);
  }
}

export default DailyQuestSystem;
