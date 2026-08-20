// Leaderboards: local + simulated global rankings.

import { Storage } from '../core/Storage.js';

export class LeaderboardSystem {
  constructor(game) {
    this.game = game;
    this.local = Storage.get('pt.leaderboard.local', []);
  }

  submit(mode, score, meta = {}) {
    this.local.push({
      mode, score, meta, nickname: this.game.social?.profile?.nickname || 'You', ts: Date.now(),
    });
    this.local.sort((a, b) => b.score - a.score);
    this.local = this.local.slice(0, 50);
    Storage.set('pt.leaderboard.local', this.local);
    return this.rank(mode, score);
  }

  rank(mode, score) {
    const scores = this.local.filter(l => l.mode === mode).map(l => l.score);
    return scores.filter(s => s > score).length + 1;
  }

  get(mode, limit = 10) {
    const mine = this.local.filter(l => l.mode === mode).slice(0, limit);
    // Simulated global players
    const simulated = [
      { nickname: 'LeafRider', score: 12000 }, { nickname: 'BloomFox', score: 9800 },
      { nickname: 'RootMaster99', score: 8100 }, { nickname: 'SunKnight', score: 7400 },
      { nickname: 'SproutPip', score: 6200 }, { nickname: 'GroveWarden', score: 5100 },
    ];
    const out = simulated.map((s, i) => ({ rank: i + 1, ...s, mode, local: false }));
    for (const l of mine) {
      out.push({ rank: out.length + 1, nickname: l.nickname, score: l.score, mode, local: true, meta: l.meta });
    }
    return out.sort((a, b) => b.score - a.score).slice(0, limit);
  }
}

export default LeaderboardSystem;