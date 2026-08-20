// Player progression: XP/levels + seasonal battle-pass progression.

import { CONFIG } from '../core/Config.js';
import { events } from '../core/Events.js';
import { Storage } from '../core/Storage.js';
import { getItem } from '../content/items.js';

export const SEASON_TIERS = 10;
export const SEASON_XP_PER_TIER = 500;

export const SEASON_REWARDS = [
  { tier: 1, cosmetic: 'shirt_dusk' },
  { tier: 2, cosmetic: 'hat_beret' },
  { tier: 3, cosmetic: 'emote_dance' },
  { tier: 4, cosmetic: 'hat_crown' },
  { tier: 5, cosmetic: 'shirt_verdant' },
  { tier: 6, cosmetic: 'emote_point' },
  { tier: 7, cosmetic: 'hat_hood' },
  { tier: 8, cosmetic: 'shirt_ember' },
  { tier: 9, cosmetic: 'emote_wave' },
  { tier: 10, cosmetic: 'glider_groveleaf' },
];

export class XPProgress {
  constructor(game, player) {
    this.game = game;
    this.player = player;
    this.level = 1;
    this.xp = 0;
    this.seasonXp = 0;
    this.seasonTier = 1;
    this.prestige = 0;
    this.stats = {
      kills: 0, deaths: 0, blocksMined: 0, blocksPlaced: 0,
      itemsCrafted: 0, questsCompleted: 0, playtime: 0,
      enemiesKilled: 0, bossesKilled: 0, wins: 0,
      distance: 0,
    };
    this._load();
  }

  xpToNext() {
    return Math.round(CONFIG.gameplay.xpToLevelBase * Math.pow(CONFIG.gameplay.xpToLevelGrowth, this.level - 1));
  }

  addXp(amount) {
    this.xp += amount;
    events.emit('xp:changed', { level: this.level, xp: this.xp, toNext: this.xpToNext() });
    while (this.xp >= this.xpToNext() && this.level < CONFIG.gameplay.maxLevel) {
      this.xp -= this.xpToNext();
      this.level++;
      events.emit('level:up', { level: this.level });
      this.game.ui?.toast(`Level up! You are now level ${this.level}.`, 3500);
      this.game.engine.audio?.levelUp();
      if (this.level >= 100) {
        this.prestige++;
        this.level = 1;
        this.xp = 0;
        events.emit('prestige:up', { prestige: this.prestige });
      }
    }
    this._save();
  }

  addSeasonXp(amount) {
    this.seasonXp += amount;
    events.emit('season:xp', { seasonXp: this.seasonXp, tier: this.seasonTier });
    while (this.seasonXp >= SEASON_XP_PER_TIER && this.seasonTier < SEASON_TIERS) {
      this.seasonXp -= SEASON_XP_PER_TIER;
      this.seasonTier++;
      const reward = SEASON_REWARDS[this.seasonTier - 1];
      events.emit('season:tier', { tier: this.seasonTier, reward });
      this.game.ui?.toast(`Season Tier ${this.seasonTier} unlocked: ${reward.cosmetic}!`, 4500);
      this.game.engine.audio?.questComplete();
    }
    this._save();
  }

  addStat(name, amount = 1) {
    this.stats[name] = (this.stats[name] || 0) + amount;
    events.emit('stat:changed', { name, value: this.stats[name] });
  }

  recordKill(enemyType, xp, seasonXp) {
    this.addStat('enemiesKilled');
    this.addStat('kills');
    this.addXp(xp);
    this.addSeasonXp(seasonXp);
  }

  recordWin() { this.addStat('wins'); this.addSeasonXp(200); }

  _save() {
    Storage.set('pt.progress.v1', {
      level: this.level, xp: this.xp, seasonXp: this.seasonXp, seasonTier: this.seasonTier,
      prestige: this.prestige, stats: this.stats,
    });
  }

  _load() {
    const d = Storage.get('pt.progress.v1');
    if (d) {
      this.level = d.level || 1;
      this.xp = d.xp || 0;
      this.seasonXp = d.seasonXp || 0;
      this.seasonTier = d.seasonTier || 1;
      this.prestige = d.prestige || 0;
      this.stats = { ...this.stats, ...(d.stats || {}) };
    }
  }
}

export default XPProgress;