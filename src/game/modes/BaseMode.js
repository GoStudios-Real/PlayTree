// Base game mode contract. All modes extend this.

import { events } from '../../core/Events.js';

export class BaseMode {
  constructor(game, opts = {}) {
    this.game = game;
    this.name = 'base';
    this.displayName = 'Base Mode';
    this.description = '';
    this.icon = '🎮';
    this.allowFly = false;
    this.blockInteractionPriority = 'mine'; // 'mine' | 'break'
    this._stopHandlers = [];
  }

  onStart(opts = {}) {
    // override
  }

  update(dt) {
    // override
  }

  onStop() {
    for (const [ev, h] of this._stopHandlers) events.off(ev, h);
  }

  _on(ev, h) {
    events.on(ev, h);
    this._stopHandlers.push([ev, h]);
  }

  onKill(from, target) { }
  onBossDefeated(boss) { }
  onPlayerDeath() { }
}

export default BaseMode;