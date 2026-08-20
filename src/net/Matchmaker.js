// Matchmaking: queues the player and (in offline mode) simulates finding a match.

import { events } from '../core/Events.js';
import { CONFIG } from '../core/Config.js';

export class Matchmaker {
  constructor(game) {
    this.game = game;
    this.queuing = false;
    this.queueMode = null;
    this.queueStart = 0;
    this._timer = null;
    this.estimate = 10;
  }

  queue(mode, opts = {}) {
    if (this.queuing) return;
    this.queuing = true;
    this.queueMode = mode;
    this.queueStart = Date.now();
    this.estimate = 8 + Math.floor(Math.random() * 8);
    events.emit('matchmaking:queued', { mode, estimate: this.estimate });
    this.game.ui?.showMatchmaking(mode, this.estimate);

    this._timer = setInterval(() => {
      const elapsed = (Date.now() - this.queueStart) / 1000;
      const progress = Math.min(1, elapsed / this.estimate);
      this.game.ui?.updateMatchmaking(progress);
      if (elapsed >= this.estimate) this._found();
    }, 250);
  }

  _found() {
    this.cancel();
    this.game.ui?.hideMatchmaking();
    events.emit('matchmaking:found', { mode: this.queueMode });
    this.game.serverBrowser.createPrivate(this.queueMode, { name: `Match ${this.queueMode}` });
  }

  cancel() {
    this.queuing = false;
    if (this._timer) clearInterval(this._timer);
    this._timer = null;
    this.game.ui?.hideMatchmaking();
    events.emit('matchmaking:cancelled', {});
  }
}

export default Matchmaker;