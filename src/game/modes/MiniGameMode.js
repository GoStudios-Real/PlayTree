// Mini-Game Mode: hosts any registered mini-game.

import { BaseMode } from './BaseMode.js';
import { getMiniGame, registerMiniGame } from '../../minigames/MiniGameRegistry.js';
import { ObstacleCourse } from '../../minigames/games/ObstacleCourse.js';
import { BoomBarrelBrawl } from '../../minigames/games/BoomBarrelBrawl.js';
import { CaptureTheSprout } from '../../minigames/games/CaptureTheSprout.js';

// Register built-in mini-games
registerMiniGame('obstacle_course', { id: 'obstacle_course', name: 'Canopy Dash', icon: '🏃', description: 'Race across floating platforms to the finish line.', class: ObstacleCourse });
registerMiniGame('boom_brawl', { id: 'boom_brawl', name: 'BoomBarrel Brawl', icon: '💥', description: 'Place barrels and blast bots out of the arena.', class: BoomBarrelBrawl });
registerMiniGame('capture_the_sprout', { id: 'capture_the_sprout', name: 'Capture the Sprout', icon: '🚩', description: 'Steal the Sprout and bring it home. 3 captures win.', class: CaptureTheSprout });

export class MiniGameMode extends BaseMode {
  constructor(game, opts = {}) {
    super(game, opts);
    this.name = 'minigame';
    this.displayName = 'Mini-Games';
    this.description = 'Quick rounds of original PlayTree mini-games.';
    this.icon = '🎮';
    this.active = null;
  }

  onStart(opts = {}) {
    const def = getMiniGame(opts.minigame);
    if (!def) {
      this.game.ui?.toast('Mini-game not found.', 2000);
      this.game.returnToMenu();
      return;
    }
    this.game.blockInteraction.setMode('survival');
    this.active = new def.class(this.game, opts);
    this.active.onStart(opts);
  }

  update(dt) {
    if (this.active) this.active.update(dt);
  }

  onKill(from, target) {
    if (this.active?.onKill) this.active.onKill(from, target);
  }

  onStop() {
    if (this.active?.onStop) this.active.onStop();
  }
}

export default MiniGameMode;