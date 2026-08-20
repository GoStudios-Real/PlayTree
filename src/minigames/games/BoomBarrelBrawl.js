// BoomBarrel Brawl: place boom barrels and blast bots off the arena.

import { mulberry32 } from '../../core/MathUtils.js';
import { events } from '../../core/Events.js';
import { BRBot } from '../../br/BRBot.js';

export class BoomBarrelBrawl {
  constructor(game, opts = {}) {
    this.game = game;
    this.id = 'boom_brawl';
    this.name = 'BoomBarrel Brawl';
    this.icon = '💥';
    this.description = 'Detonate barrels to knock out bots. Last survivor wins.';
    this.maxPlayers = 6;
    this.finished = false;
    this.roundTime = 90;
    this.timer = this.roundTime;
    this.score = 0;
    this.bots = [];
    this.placed = 0;
  }

  onStart() {
    const g = this.game;
    g.blockInteraction.setMode('survival');
    g.blockInteractionPriority = 'break';
    g.chat.system('BoomBarrel Brawl: place barrels (F to build). Detonate them by attacking. 90 seconds!');

    // Build arena
    const rng = mulberry32(g.world.seed + 500);
    const cx = 0, cz = 0, oy = g.world.getSurfaceHeight(cx, cz);
    for (let x = -12; x <= 12; x++) for (let z = -12; z <= 12; z++) {
      g.world.setBlockAndRemesh(cx + x, oy, cz + z, x === 12 || x === -12 || z === 12 || z === -12 ? 36 : 40);
    }
    // Spawn bots
    const names = ['Puffy', 'BoomBoi', 'KaboomKate', 'Sizzle', 'Blastus'];
    for (let i = 0; i < 4; i++) {
      const bot = new BRBot(g.world, {
        x: -6 + rng() * 12, y: oy + 2, z: -6 + rng() * 12, name: names[i], team: i + 1,
      });
      bot.health = 100;
      bot.speed = 4;
      g.entities.register(bot);
      this.bots.push(bot);
    }
    g.bots = this.bots;
    g.player.teleport(4, oy + 2, 4);
    g.player.setFlying(false);

    // Give barrels
    g.player.inventory.slots.fill(null);
    g.player.inventory.slots[0] = { id: 47, count: 8 };

    g.ui?.setBRMode?.(this);
    this._interval = setInterval(() => this._tick(), 1000);
    this.start = performance.now();
  }

  _tick() {
    if (this.finished) return;
    this.timer--;
    this.game.ui?.announce(`Time: ${this.timer}s`, `Bots remaining: ${this.bots.length}`, 1500);
    if (this.timer <= 0 || this.bots.length === 0) this._finish();
  }

  update(dt) {
    if (this.finished) return;
    const g = this.game;
    this.bots = this.bots.filter(b => !b.dead);
    for (const bot of this.bots) {
      bot.update(dt, g.world, [g.player, ...this.bots], { inSafeZone: () => true, center: { x: 0, z: 0 } });
    }
    if (g.player.dead) {
      g.ui?.announce('Knocked out!', 'Match over.', 4000);
      this._finish(true);
    }
  }

  onKill(from, target) {
    if (from === this.game.player && target?.kind === 'bot') {
      this.score++;
      this.game.ui?.feed(`You knocked out ${target.name}!`);
    }
  }

  _finish(playerLost = false) {
    if (this.finished) return;
    this.finished = true;
    clearInterval(this._interval);
    const g = this.game;
    if (!playerLost && this.bots.length === 0) {
      g.ui?.announce('VICTORY!', `Knockouts: ${this.score}`, 6000);
      g.xp.addXp(100);
      g.xp.addSeasonXp(60);
    } else {
      g.ui?.announce('Match over!', `Knockouts: ${this.score}`, 5000);
    }
    events.emit('minigame:finished', { game: this.id, score: this.score });
    setTimeout(() => g.returnToMenu(), 6000);
  }

  onStop() {
    clearInterval(this._interval);
    this.bots = [];
    this.game.bots = [];
  }
}

export default BoomBarrelBrawl;