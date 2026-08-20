// Battle Royale Mode: drop onto the map, loot, build, survive the Storm.

import { BaseMode } from '../game/modes/BaseMode.js';
import { BRZone } from './BRZone.js';
import { BRBot } from './BRBot.js';
import { CONFIG } from '../core/Config.js';
import { mulberry32, hash2 } from '../core/MathUtils.js';
import { events } from '../core/Events.js';

const LOOT_WEAPONS = [200, 201, 202, 203, 204, 205, 208, 207, 206];
const LOOT_AMMO = [250, 251, 252, 253];
const LOOT_HEALS = [300, 301, 302, 303];

export class BattleRoyaleMode extends BaseMode {
  constructor(game, opts = {}) {
    super(game, opts);
    this.name = 'br';
    this.displayName = 'Battle Royale';
    this.description = 'Drop in, loot up, build up, and be the last one standing.';
    this.icon = '🎯';
    this.teamMode = opts.team || 'solo';
    this.teamSize = CONFIG.br.teams[this.teamMode] || 1;
    this.bots = [];
    this.zone = null;
    this.phase = 'drop';        // drop | active | finished
    this.dropTimer = 0;
    this.kills = 0;
    this.aliveCount = 0;
    this.startedAt = 0;
    this._crates = [];
    this._botCount = opts.bots ?? (this.teamSize === 1 ? 16 : 24);
    this._dropDone = false;
  }

  onStart(opts = {}) {
    const g = this.game;
    g.blockInteraction.setMode('survival');
    g.blockInteractionPriority = 'break';
    g.chat.system(`Battle Royale — ${this.teamMode.toUpperCase()} match starting!`);
    g.chat.system('Drop now! Loot crates, avoid the Storm, be the last standing.');

    // Pick match center near origin but offset so terrain is interesting
    const rng = mulberry32(g.world.seed + 9);
    const centerX = (rng() - 0.5) * 200;
    const centerZ = (rng() - 0.5) * 200;

    // Zone
    this.zone = new BRZone(g);
    this.zone.center = { x: centerX, z: centerZ };
    this.zone.targetCenter = { ...this.zone.center };
    this.zone._rebuildVisual();
    this.zone.startMatch();

    // Scatter loot crates
    const crateCount = CONFIG.br.lootCrates;
    for (let i = 0; i < crateCount; i++) {
      const ang = rng() * Math.PI * 2;
      const rad = Math.sqrt(rng()) * CONFIG.br.zoneRadiusStart * 0.95;
      const x = Math.round(centerX + Math.cos(ang) * rad);
      const z = Math.round(centerZ + Math.sin(ang) * rad);
      const y = g.world.getSurfaceHeight(x, z);
      if (y < 4 || y > 70) continue;
      g.world.setBlockAndRemesh(x, y + 1, z, 39);
      this._crates.push({ x, y: y + 1, z, looted: false });
    }

    // Spawn bots
    const bots = [];
    const teamCount = this.teamSize;
    const teams = Math.ceil(this._botCount / teamCount);
    for (let t = 0; t < teams; t++) {
      for (let m = 0; m < teamCount; m++) {
        if (bots.length >= this._botCount) break;
        const ang = rng() * Math.PI * 2;
        const rad = Math.sqrt(rng()) * CONFIG.br.zoneRadiusStart * 0.9;
        const x = Math.round(centerX + Math.cos(ang) * rad);
        const z = Math.round(centerZ + Math.sin(ang) * rad);
        const bot = new BRBot(g.world, {
          x: x + 0.5, y: CONFIG.br.startHeight, z: z + 0.5, team: t,
        });
        g.entities.register(bot);
        this.bots.push(bot);
      }
    }
    g.bots = this.bots;
    g.world.brCrates = this._crates;

    // Player drop
    const pAng = rng() * Math.PI * 2;
    const pRad = 80;
    g.player.teleport(centerX + Math.cos(pAng) * pRad, CONFIG.br.startHeight, centerZ + Math.sin(pAng) * pRad);
    g.player.vel.y = 0;
    g.player.setFlying(true); // use fly to "parachute" with slowed fall handled by mode
    this.dropTimer = 3;
    this.startedAt = performance.now();

    // HUD
    g.ui?.setBRMode?.(this);

    this._on('player:death', () => this._onEliminated());
    this._on('br:bot-eliminated', (d) => this._onBotEliminated(d));
  }

  update(dt) {
    const g = this.game;
    if (!this.zone) return;

    // Drop phase: slow-fall + auto move toward zone
    if (!this._dropDone) {
      this.dropTimer -= dt;
      const groundY = g.world.getSurfaceHeight(g.player.pos.x, g.player.pos.z);
      if (g.player.pos.y > groundY + 2) {
        g.player.pos.y -= 26 * dt;   // parachute fall
        g.player.vel.y = 0;
        g.player.entityGroup.position.set(g.player.pos.x, g.player.pos.y, g.player.pos.z);
        g.player.avatar.update(dt, false, 0);
        this._moveTowardDrop();
      } else {
        g.player.pos.y = groundY + 1.2;
        g.player.setFlying(false);
        g.player.vel.y = 0;
        this._dropDone = true;
        g.chat.system('Landed! Find weapons — the Storm is coming.');
        g.ui?.announce('Loot up!', 'The Storm will shrink soon.', 3000);
      }
      return;
    }

    this.zone.update(dt, g.player.pos);

    // Bots
    for (const bot of this.bots) {
      bot.update(dt, g.world, [g.player, ...this.bots], this.zone);
    }
    this.bots = this.bots.filter(b => !b.dead);

    // Check win
    this.aliveCount = 1 + this.bots.length;
    if (this.aliveCount <= 1 && !g.player.dead && this.phase === 'active') {
      this._onWin();
    }
    if (this.phase === 'drop' && this._dropDone) this.phase = 'active';

    // Match time limit
    const elapsed = (performance.now() - this.startedAt) / 1000;
    if (elapsed > CONFIG.br.matchLengthMinutes * 60 && this.phase === 'active') {
      // Most damage wins — declare based on kills
      this._onWin(true);
    }
  }

  _moveTowardDrop() {
    // gentle drift toward zone center while falling
    const p = this.game.player;
    const dz = this.zone.center.x - p.pos.x;
    const ddz = this.zone.center.z - p.pos.z;
    p.pos.x += dz * 0.02;
    p.pos.z += ddz * 0.02;
  }

  onCrateOpen(x, y, z) {
    const crate = this._crates.find(c => c.x === x && c.y === y && c.z === z && !c.looted);
    if (!crate) return;
    crate.looted = true;
    this.game.world.setBlockAndRemesh(x, y, z, 0);
    // Roll loot
    const r = mulberry32(Math.floor(x * 31 + y * 17 + z * 7 + this.game.world.seed));
    const weapon = LOOT_WEAPONS[Math.floor(r() * LOOT_WEAPONS.length)];
    this.game.player.inventory.add(weapon, 1);
    this.game.player.inventory.add(LOOT_AMMO[Math.floor(r() * LOOT_AMMO.length)], 24 + Math.floor(r() * 40));
    if (r() < 0.6) this.game.player.inventory.add(LOOT_HEALS[Math.floor(r() * LOOT_HEALS.length)], 1 + Math.floor(r() * 3));
    if (r() < 0.3) this.game.player.addShield(25);
    this.game.ui?.toast('Loot acquired!', 2000);
    this.game.engine.audio?.pickup();
    events.emit('br:crate-opened', { crate, items: [weapon] });
  }

  _onBotEliminated(d) {
    const g = this.game;
    const killerName = d.source === g.player ? 'You' : d.source?.name || 'Someone';
    g.ui?.feed(`${killerName} eliminated ${d.bot.name}`);
    g.ui?.updateBRPlayers?.(1 + this.bots.length);
    if (d.source === g.player) {
      this.kills++;
      g.xp.addStat('brKills');
      g.xp.addXp(30);
      g.xp.addSeasonXp(40);
    }
  }

  _onEliminated() {
    const g = this.game;
    g.xp.addStat('deaths');
    g.ui?.announce('Eliminated!', `You placed #${1 + this.bots.length}`, 4000);
    g.chat.system('You were eliminated. Returning to the lobby...');
    g.player.dead = true;
    setTimeout(() => {
      g.returnToMenu();
    }, 5000);
  }

  _onWin(byTime = false) {
    if (this.phase === 'finished') return;
    this.phase = 'finished';
    const g = this.game;
    if (byTime) {
      g.ui?.announce('Match over!', `Most eliminations wins. Your eliminations: ${this.kills}`, 6000);
    } else {
      g.ui?.announce('VICTORY!', 'Last Sprout Standing!', 8000);
      g.xp.addStat('brWins');
      g.xp.recordWin();
    }
    g.chat.system('Match complete. Returning to the lobby...');
    setTimeout(() => g.returnToMenu(), 7000);
  }

  onStop() {
    super.onStop();
    if (this.zone) this.zone.dispose();
    this.bots = [];
    this.game.bots = [];
    this.game.world.brCrates = [];
    this._crates = [];
  }
}

export default BattleRoyaleMode;