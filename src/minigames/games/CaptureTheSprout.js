// Capture the Sprout: capture the flag against bots in a small arena.

import { mulberry32 } from '../../core/MathUtils.js';
import { events } from '../../core/Events.js';
import { BRBot } from '../../br/BRBot.js';
import * as THREE from '../../../vendor/three.module.js';

export class CaptureTheSprout {
  constructor(game, opts = {}) {
    this.game = game;
    this.id = 'capture_the_sprout';
    this.name = 'Capture the Sprout';
    this.icon = '🚩';
    this.description = 'Steal the Sprout from the enemy base and bring it home.';
    this.maxPlayers = 8;
    this.finished = false;
    this.score = 0;
    this.timeLimit = 120;
    this.timer = this.timeLimit;
    this.bots = [];
    this.sprout = { x: 0, y: 0, z: 0, heldBy: null, home: { x: 0, y: 0, z: 0 }, returned: true };
  }

  onStart() {
    const g = this.game;
    g.blockInteraction.setMode('survival');
    g.chat.system('Capture the Sprout: grab the glowing Sprout from the enemy shrine and bring it to your shrine!');

    const oy = g.world.getSurfaceHeight(0, 0);
    // Two shrines
    this.home = { x: -14, y: oy + 1, z: 0 };
    this.enemy = { x: 14, y: oy + 1, z: 0 };
    this._shrine(this.home.x, this.home.y, this.home.z, 0x59c48f);
    this._shrine(this.enemy.x, this.enemy.y, this.enemy.z, 0xff7a59);
    // Sprout at enemy base
    this.sprout = { x: this.enemy.x, y: this.enemy.y + 1, z: this.enemy.z, heldBy: null, home: this.home, returned: true };

    // Bots
    const names = ['Rush', 'Dash', 'Swift', 'Blaze'];
    const rng = mulberry32(g.world.seed + 42);
    for (let i = 0; i < 4; i++) {
      const bot = new BRBot(g.world, {
        x: -8 + rng() * 16, y: oy + 2, z: -8 + rng() * 16, name: names[i], team: i % 2,
      });
      bot.health = 100;
      bot.speed = 6;
      g.entities.register(bot);
      this.bots.push(bot);
    }
    g.bots = this.bots;
    g.player.teleport(this.home.x, oy + 2, this.home.z + 3);
    g.player.setFlying(false);
    g.player.inventory.slots.fill(null);
    g.player.inventory.slots[0] = { id: 39, count: 8 };

    this._sproutMesh = this._makeSprout();
    this._interval = setInterval(() => this._tick(), 1000);
  }

  _shrine(x, y, z, color) {
    const g = this.game;
    for (let dx = -1; dx <= 1; dx++) for (let dz = -1; dz <= 1; dz++) {
      g.world.setBlockAndRemesh(x + dx, y, z + dz, 40);
      g.world.setBlockAndRemesh(x + dx, y + 1, z + dz, 40);
    }
    g.world.setBlockAndRemesh(x, y + 2, z, 43);
    g.world.setBlockAndRemesh(x, y + 3, z, 46);
  }

  _makeSprout() {
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(0.4, 12, 12),
      new THREE.MeshLambertMaterial({ color: 0x59c48f, emissive: 0x1f4f2f })
    );
    mesh.position.set(this.enemy.x, this.enemy.y + 1, this.enemy.z);
    this.game.engine.scene.add(mesh);
    return mesh;
  }

  _tick() {
    if (this.finished) return;
    this.timer--;
    if (this.timer <= 0) {
      this.game.ui?.announce('Time up!', `Captures: ${this.score}`, 5000);
      this._end();
    }
  }

  update(dt) {
    if (this.finished) return;
    const g = this.game;
    this.bots = this.bots.filter(b => !b.dead);
    for (const bot of this.bots) {
      bot.update(dt, g.world, [g.player, ...this.bots], { inSafeZone: () => true, center: { x: 0, z: 0 } });
    }
    // Sprout pickup
    const p = g.player;
    const d = Math.hypot(p.pos.x - this.sprout.x, p.pos.z - this.sprout.z);
    if (!this.sprout.heldBy && d < 2) {
      this.sprout.heldBy = p;
      g.ui?.toast('You grabbed the Sprout! Bring it home!', 2500);
      g.engine.audio?.pickup();
    }
    if (this.sprout.heldBy) {
      this._sproutMesh.position.set(p.pos.x, p.pos.y + 2.2, p.pos.z);
      // Capture if at home shrine
      const hd = Math.hypot(p.pos.x - this.home.x, p.pos.z - this.home.z);
      if (hd < 3) {
        this.score++;
        g.ui?.announce('CAPTURED!', `Score: ${this.score}`, 4000);
        g.engine.audio?.questComplete();
        g.xp.addXp(50);
        g.xp.addSeasonXp(30);
        this.sprout.heldBy = null;
        this.sprout.x = this.enemy.x; this.sprout.y = this.enemy.y + 1; this.sprout.z = this.enemy.z;
        this._sproutMesh.position.set(this.enemy.x, this.enemy.y + 1, this.enemy.z);
        if (this.score >= 3) this._end(true);
      }
    }
    if (g.player.dead) {
      if (this.sprout.heldBy === g.player) this.sprout.heldBy = null;
    }
  }

  _end(victory = false) {
    if (this.finished) return;
    this.finished = true;
    clearInterval(this._interval);
    if (victory) {
      this.game.ui?.announce('VICTORY!', 'You captured the Sprout 3 times!', 6000);
    } else {
      this.game.ui?.announce('Match over!', `Captures: ${this.score}`, 5000);
    }
    events.emit('minigame:finished', { game: this.id, score: this.score });
    setTimeout(() => this.game.returnToMenu(), 6000);
  }

  onStop() {
    clearInterval(this._interval);
    if (this._sproutMesh) this.game.engine.scene.remove(this._sproutMesh);
    this.bots = [];
    this.game.bots = [];
  }
}

export default CaptureTheSprout;