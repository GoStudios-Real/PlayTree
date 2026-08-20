// Passive animals + wildlife. Wander, flee from threats, can be farmed.

import * as THREE from '../../vendor/three.module.js';
import { LivingEntity } from './LivingEntity.js';
import { hash2, dist2d } from '../core/MathUtils.js';

const DEFS = {
  herd:  { name: 'Grovestrider', color: 0xc8a46b, sub: 0xe8d8b0, hp: 20, speed: 2.4, width: 0.9, height: 1.3, drops: [301, 2, 2], tame: false },
  hare:  { name: 'Moss Hare', color: 0xb8a27a, sub: 0xffffff, hp: 8, speed: 4.2, width: 0.5, height: 0.5, drops: [300, 2, 3], tame: true },
  fox:   { name: 'Ember Fox', color: 0xd4703a, sub: 0xfff2e0, hp: 12, speed: 5.0, width: 0.6, height: 0.7, drops: [300, 1, 2], tame: true },
  owl:   { name: 'Moonowl', color: 0x7a5a4a, sub: 0xefe6d8, hp: 10, speed: 3.4, width: 0.6, height: 0.9, drops: [400, 1, 2], tame: true },
};

export class Mob extends LivingEntity {
  constructor(world, type, x, y, z, opts = {}) {
    const def = DEFS[type] || DEFS.herd;
    super(world, {
      kind: 'mob', name: opts.name || def.name, x, y, z,
      width: def.width, height: def.height, health: def.hp, speed: def.speed,
    });
    this.type = type;
    this.def = def;
    this.tamed = false;
    this.state = 'wander';   // wander | flee
    this.wanderTarget = null;
    this.wanderTimer = 0;
    this.fleeTimer = 0;
    this.seed = (hash2(Math.floor(x), Math.floor(z), world.seed) * 4294967296) >>> 0;
    this._build();
  }

  _build() {
    const d = this.def;
    const g = new THREE.Group();
    const body = this._box(this.width * 0.7, this.height * 0.55, this.width * 0.5, d.color, 0, this.height * 0.4, 0);
    const head = this._box(Math.max(0.3, this.width * 0.4), this.height * 0.3, Math.max(0.3, this.width * 0.4), d.sub, 0, this.height * 0.8, 0);
    const legL = this._box(0.12, 0.3, 0.12, d.color, -this.width * 0.2, 0.15, 0);
    const legR = this._box(0.12, 0.3, 0.12, d.color, this.width * 0.2, 0.15, 0);
    if (this.type === 'herd') {
      const hornL = this._box(0.08, 0.1, 0.08, 0x6b553a, -0.16, this.height, -0.05);
      const hornR = this._box(0.08, 0.1, 0.08, 0x6b553a, 0.16, this.height, -0.05);
      g.add(hornL, hornR);
    }
    g.add(body, head, legL, legR);
    this.group.add(g);
    this._limbs = { legL, legR, head };
  }

  update(dt, threats = []) {
    if (this.dead) return;
    // Flee logic
    if (threats.length) {
      let near = null, bestD = Infinity;
      for (const t of threats) {
        const d = dist2d(this.pos.x, this.pos.z, t.x, t.z);
        if (d < 12 && d < bestD) { bestD = d; near = t; }
      }
      if (near) {
        this.state = 'flee';
        this.fleeTimer = 1.2;
        const dir = Math.atan2(this.pos.x - near.x, this.pos.z - near.z);
        this._moveTowards(dir, this.def.speed * 1.6, dt);
      } else if (this.fleeTimer <= 0) {
        this.state = 'wander';
      }
    }
    if (this.state === 'wander') {
      this.wanderTimer -= dt;
      if (this.wanderTimer <= 0 || !this.wanderTarget) {
        const a = (this.seed + this._n) / 65536;
        this._n = (this._n + 7) % 65536;
        const ang = a * Math.PI * 2;
        this.wanderTarget = { x: this.pos.x + Math.cos(ang) * (4 + this.seed % 6), z: this.pos.z + Math.sin(ang) * (4 + this.seed % 6) };
        this.wanderTimer = 2 + (this.seed % 40) / 10;
      }
      const dx = this.wanderTarget.x - this.pos.x, dz = this.wanderTarget.z - this.pos.z;
      if (Math.hypot(dx, dz) < 1) { this.wanderTarget = null; }
      else this._moveTowards(Math.atan2(dx, dz), this.def.speed * 0.5, dt);
    }
    this.fleeTimer = Math.max(0, this.fleeTimer - dt);

    super.update(dt);
    // limb animation
    if (this._limbs && Math.hypot(this.vel.x, this.vel.z) > 0.3) {
      const s = Math.sin(performance.now() * 0.02);
      this._limbs.legL.rotation.x = s * 0.5;
      this._limbs.legR.rotation.x = -s * 0.5;
      this._limbs.head.rotation.y = s * 0.2;
    }
  }

  _moveTowards(angle, speed, dt) {
    this.vel.x = Math.cos(angle) * speed;
    this.vel.z = Math.sin(angle) * speed;
    this.yaw = angle;
  }

  onDeath(source) {
    for (const [id, min, max] of (this.def.drops || [])) {
      const n = min + Math.floor(Math.random() * (max - min + 1));
      for (let i = 0; i < n; i++) {
        this.world.loot?.spawn(this.pos.x, this.pos.y + 0.5, this.pos.z, id);
      }
    }
  }
}

export default Mob;