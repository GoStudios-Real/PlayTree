// Quest system: tracks active/complete quests, listens to gameplay events to
// progress objectives, hands out rewards on completion.

import { QUESTS } from '../content/quests.js';
import { getItem } from '../content/items.js';
import { events } from '../core/Events.js';
import { Storage } from '../core/Storage.js';

const QUEST_SAVE = 'pt.quests.v1';

const OBJECTIVE_EVENTS = {
  kill: 'enemy:defeated',
  mine: 'block:broken',
  place: 'block:placed',
  craft: 'item:crafted',
  collect: 'inventory:changed',
  talk: 'npc:talked',
  explore: 'location:reached',
  plant: 'farming:planted',
  harvest: 'farming:harvested',
};

export class QuestSystem {
  constructor(game) {
    this.game = game;
    this.quests = QUESTS;
    this.active = [];      // quests with progress
    this.completed = [];   // quest ids
    this.unlocked = new Set();
    this.objectiveCounts = new Map(); // questId -> objective index -> count
    this._handlers = [];
    this._bind();
    this.load();
  }

  _bind() {
    for (const [type, ev] of Object.entries(OBJECTIVE_EVENTS)) {
      const h = (data) => this._onEvent(type, data);
      events.on(ev, h);
      this._handlers.push([ev, h]);
    }
  }

  _onEvent(type, data) {
    // Determine target key(s)
    let target = null, amount = 1;
    switch (type) {
      case 'kill': target = data.enemy?.type; amount = 1; break;
      case 'mine': target = data.id; amount = 1; break;
      case 'place': target = data.blockId; amount = 1; break;
      case 'craft': target = data.itemId; amount = data.count || 1; break;
      case 'collect': {
        // inventory changed — check each active collect objective vs current count
        this._checkCollect();
        return;
      }
      case 'talk': target = data.npc?.type; amount = 1; break;
      case 'explore': target = data.locationId; amount = 1; break;
      case 'plant': target = data.itemId; amount = data.count || 1; break;
      case 'harvest': target = data.blockId; amount = 1; break;
    }
    this._progress(target, amount, type);
  }

  _checkCollect() {
    for (const q of this.active) {
      for (let i = 0; i < q.def.objectives.length; i++) {
        const o = q.def.objectives[i];
        if (o.type === 'collect') {
          const have = this.game.player.inventory.countOf(o.target);
          const cur = this._getCount(q.id, i);
          if (have > cur) {
            this._setCount(q.id, i, Math.min(have, o.count));
            this._checkComplete(q);
          }
        }
      }
    }
  }

  _progress(target, amount, type) {
    for (const q of this.active) {
      for (let i = 0; i < q.def.objectives.length; i++) {
        const o = q.def.objectives[i];
        if (o.type !== type) continue;
        if (o.target !== undefined && String(o.target) !== String(target)) continue;
        const cur = this._getCount(q.id, i);
        this._setCount(q.id, i, Math.min(o.count, cur + amount));
        if (this._isComplete(q)) this._checkComplete(q);
      }
    }
  }

  _getCount(qid, i) {
    const key = qid + '|' + i;
    return this.objectiveCounts.get(key) || 0;
  }
  _setCount(qid, i, n) {
    this.objectiveCounts.set(qid + '|' + i, n);
    events.emit('quest:progress', { questId: qid, objective: i, count: n });
  }

  _isComplete(q) {
    return q.def.objectives.every((o, i) => this._getCount(q.id, i) >= o.count);
  }

  startQuest(qid) {
    const def = this.quests.find(q => q.id === qid);
    if (!def || this.completed.includes(qid)) return null;
    if (this.active.some(q => q.id === qid)) return null;
    if (def.rewards?.level && this.game.player.level < def.rewards.level) return null;
    const quest = { id: qid, def, startedAt: Date.now() };
    this.active.push(quest);
    events.emit('quest:started', { quest: quest.def });
    this.game.ui?.toast(`Quest started: ${def.title}`, 3500);
    return quest;
  }

  _checkComplete(q) {
    if (!this._isComplete(q)) return;
    this.active = this.active.filter(x => x.id !== q.id);
    this.completed.push(q.id);
    const r = q.def.rewards || {};
    // Grant rewards
    if (r.xp) this.game.xp.addXp(r.xp);
    if (r.seasonXp) this.game.xp.addSeasonXp(r.seasonXp);
    if (r.coins) this.game.player.inventory.add(500, r.coins);
    for (const [id, count] of (r.items || [])) this.game.player.inventory.add(id, count);
    if (r.title) this.game.player.title = r.title;
    events.emit('quest:completed', { quest: q.def, rewards: r });
    this.game.ui?.toast(`Quest complete: ${q.def.title}!`, 4500);
    this.game.engine.audio?.questComplete();
    this.save();
  }

  addProgress(qid, objectiveIndex, amount) {
    const q = this.active.find(x => x.id === qid);
    if (!q) return;
    const cur = this._getCount(qid, objectiveIndex);
    this._setCount(qid, objectiveIndex, Math.min(q.def.objectives[objectiveIndex].count, cur + amount));
    this._checkComplete(q);
  }

  isUnlocked(qid) { return this.unlocked.has(qid) || !this.quests.find(q => q.id === qid)?.optional; }

  activeDefs() {
    return this.active.map(q => ({ ...q.def, progress: q.def.objectives.map((o, i) => this._getCount(q.id, i)) }));
  }

  getActive(qid) { return this.active.find(q => q.id === qid); }

  save() {
    Storage.set(QUEST_SAVE, { completed: this.completed, counts: Array.from(this.objectiveCounts.entries()) });
  }

  load() {
    const data = Storage.get(QUEST_SAVE);
    if (data) {
      this.completed = data.completed || [];
      if (data.counts) this.objectiveCounts = new Map(data.counts);
    }
  }

  reset() {
    this.active = [];
    this.completed = [];
    this.objectiveCounts.clear();
    this.save();
  }

  dispose() {
    for (const [ev, h] of this._handlers) events.off(ev, h);
  }
}

export default QuestSystem;