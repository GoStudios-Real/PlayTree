// NetSimulation: offline "other players" that make the world feel multiplayer.
// They wander, chat occasionally, and use the same avatar rendering. A real
// server would replace these with actual remote players via NetClient.

import { Avatar } from '../player/Avatar.js';
import { events } from '../core/Events.js';
import { mulberry32 } from '../core/MathUtils.js';

const NAMES = ['LeafRider', 'BloomFox', 'RootMaster99', 'SunKnight', 'SproutPip', 'GroveWarden', 'PetalProwler', 'CragCrusher'];
const CHAT_LINES = ['hi!', 'this grove is huge', 'lets build a bridge', 'gg', 'found diamonds??', 'storm incoming', 'anyone at the shrine?'];

export class SimPlayer {
  constructor(world, opts = {}) {
    this.world = world;
    this.id = opts.id || 'sim_' + Math.random().toString(36).slice(2, 7);
    this.nickname = opts.nickname || NAMES[Math.floor(Math.random() * NAMES.length)];
    this.pos = { x: opts.x, y: opts.y, z: opts.z };
    this.yaw = 0;
    this.pitch = 0;
    this.avatar = new Avatar({ shirt: opts.color || 0x4aa8ff, skin: 0xf0c8a0, pants: 0x3a4a66, hair: 0x4a3828 });
    this.avatar.group.position.set(this.pos.x, this.pos.y, this.pos.z);
    world.engine.scene.add(this.avatar.group);
    this.rand = mulberry32(Math.floor(Math.random() * 2 ** 32));
    this.target = null;
    this.timer = 0;
    this.chatTimer = 15 + this.rand() * 30;
    this.speed = 1.5 + this.rand() * 2;
    this.dead = false;
  }

  update(dt, world) {
    if (!this.target || this.timer <= 0) {
      this.timer = 4 + this.rand() * 8;
      const gy = world.getSurfaceHeight(this.pos.x, this.pos.z);
      const ang = this.rand() * Math.PI * 2;
      this.target = { x: this.pos.x + Math.cos(ang) * (6 + this.rand() * 12), z: this.pos.z + Math.sin(ang) * (6 + this.rand() * 12), y: gy };
    }
    this.timer -= dt;
    const dx = this.target.x - this.pos.x, dz = this.target.z - this.pos.z;
    const d = Math.hypot(dx, dz);
    if (d < 1.5) { this.target = null; }
    else {
      const gy = world.getSurfaceHeight(this.pos.x, this.pos.z);
      this.yaw = Math.atan2(dx, dz);
      this.pos.x += (dx / d) * this.speed * dt;
      this.pos.z += (dz / d) * this.speed * dt;
      this.pos.y = gy + 1.8;
      this.avatar.group.position.set(this.pos.x, this.pos.y, this.pos.z);
      this.avatar.group.rotation.y = this.yaw;
      this.avatar.update(dt, true, 0.5);
    }
    // Occasional chat
    this.chatTimer -= dt;
    if (this.chatTimer <= 0) {
      this.chatTimer = 20 + this.rand() * 40;
      this.world.game?.chat?.send(this.nickname, CHAT_LINES[Math.floor(this.rand() * CHAT_LINES.length)]);
    }
  }

  emote(emote) { this.avatar.playEmote(emote); }

  dispose() {
    this.world.engine.scene.remove(this.avatar.group);
  }
}

export class NetSimulation {
  constructor(game, count = 3) {
    this.game = game;
    this.count = count;
    this.players = [];
    this._spawned = false;
  }

  _spawn(count) {
    const w = this.game.world;
    if (!w) return false;
    for (let i = 0; i < count; i++) {
      const x = (Math.random() - 0.5) * 40;
      const z = (Math.random() - 0.5) * 40;
      const gy = w.getSurfaceHeight(x, z);
      const sp = new SimPlayer(w, { x, y: gy + 1.8, z });
      this.players.push(sp);
    }
    this.game.otherPlayers = this.players;
    this._spawned = true;
    return true;
  }

  update(dt) {
    if (!this._spawned && this.game.world) this._spawn(this.count);
    for (const p of this.players) p.update(dt, this.game.world);
  }

  chat(name, text) {
    const p = this.players.find(x => x.nickname === name);
    if (p) p.emote(Math.random() < 0.5 ? 'wave' : 'dance');
  }

  dispose() {
    for (const p of this.players) p.dispose();
    this.players = [];
    this.game.otherPlayers = [];
  }
}

export default NetSimulation;