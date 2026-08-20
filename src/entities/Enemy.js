// Hostile enemies with a simple state machine: idle | chase | attack.
// Bosses get phases (frenzy below 30% HP).

import * as THREE from '../../vendor/three.module.js';
import { LivingEntity } from './LivingEntity.js';
import { dist2d, hash2 } from '../core/MathUtils.js';
import { ENEMIES } from '../content/enemies.js';
import { events } from '../core/Events.js';

export class Enemy extends LivingEntity {
  constructor(world, type, x, y, z, opts = {}) {
    const def = ENEMIES[type] || ENEMIES.grub;
    super(world, {
      kind: 'enemy', name: opts.name || def.name, x, y, z,
      width: def.width, height: def.height, health: def.hp * (opts.hpMul || 1), speed: def.speed,
    });
    this.type = type;
    this.def = def;
    this.boss = !!def.boss;
    this.state = 'idle';
    this.attackTimer = 0;
    this.aggroRange = this.boss ? 40 : 16;
    this.lastAttackTime = 0;
    this.seed = (hash2(Math.floor(x), Math.floor(z), world.seed) * 4294967296) >>> 0;
    this._build();
    this.maxHealth = this.health;
  }

  _build() {
    const d = this.def;
    const g = new THREE.Group();
    const scale = this.boss ? 1.6 : 1;
    const body = this._box(d.width * 0.7 * scale, d.height * 0.5, d.width * 0.5 * scale, d.color, 0, d.height * 0.42, 0);
    const head = this._box(d.width * 0.45 * scale, d.height * 0.28, d.width * 0.4 * scale, d.sub, 0, d.height * 0.8, 0);
    const eye = this._box(d.width * 0.2 * scale, d.height * 0.06, 0.05, 0xff4040, 0, d.height * 0.82, -d.width * 0.21 * scale);
    const armL = this._box(0.18 * scale, d.height * 0.4, 0.18 * scale, d.color, -d.width * 0.45 * scale, d.height * 0.45, 0);
    const armR = this._box(0.18 * scale, d.height * 0.4, 0.18 * scale, d.color, d.width * 0.45 * scale, d.height * 0.45, 0);
    const legL = this._box(0.2 * scale, d.height * 0.35, 0.2 * scale, d.sub, -d.width * 0.2 * scale, d.height * 0.18, 0);
    const legR = this._box(0.2 * scale, d.height * 0.35, 0.2 * scale, d.sub, d.width * 0.2 * scale, d.height * 0.18, 0);
    g.add(body, head, eye, armL, armR, legL, legR);
    this.group.add(g);
    this._limbs = { armL, armR, legL, legR, head };
    if (this.boss) {
      this._healthBar();
    }
  }

  _healthBar() {
    this.hpGroup = new THREE.Group();
    const bg = this._box(2.4, 0.22, 0.1, 0x222222, 0, 0.35, 0);
    this.hpFill = this._box(2.34, 0.16, 0.12, 0xff5c5c, 0, 0.35, 0);
    this.hpGroup.add(bg, this.hpFill);
    this.hpGroup.position.y = this.def.height + 0.5;
    this.group.add(this.hpGroup);
  }

  update(dt, world, players) {
    if (this.dead) return;
    // Find nearest living player
    let target = null, best = Infinity;
    for (const p of players) {
      if (p.dead) continue;
      const d = dist2d(this.pos.x, this.pos.z, p.pos.x, p.pos.z);
      if (d < best) { best = d; target = p; }
    }

    this.attackTimer = Math.max(0, this.attackTimer - dt);

    if (target) {
      const d = best;
      if (d < this.aggroRange) {
        this.state = d <= this.def.attackRange + 0.5 ? 'attack' : 'chase';
      } else {
        this.state = 'idle';
      }
      if (this.state === 'chase') {
        const ang = Math.atan2(target.pos.x - this.pos.x, target.pos.z - this.pos.z);
        this.vel.x = Math.cos(ang) * this.def.speed;
        this.vel.z = Math.sin(ang) * this.def.speed;
        this.yaw = ang;
        if (this._limbs) {
          const s = Math.sin(performance.now() * 0.02);
          this._limbs.legL.rotation.x = s * 0.6;
          this._limbs.legR.rotation.x = -s * 0.6;
        }
      } else if (this.state === 'attack') {
        this.vel.x *= 0.5; this.vel.z *= 0.5;
        this.faceTowards(target.pos.x, target.pos.z);
        if (this.attackTimer <= 0) {
          this._attack(target);
          this.attackTimer = this.def.attackCooldown;
        }
      }
    } else {
      this.state = 'idle';
      this.vel.x = 0; this.vel.z = 0;
    }

    // Boss frenzy
    if (this.boss && this.hpFill) {
      const ratio = Math.max(0, this.health / this.maxHealth);
      this.hpFill.scale.x = ratio;
      this.hpFill.position.x = -1.17 * (1 - ratio);
      this.hpFill.material.color.setHex(ratio < 0.3 ? 0xffcf5c : 0xff5c5c);
      if (ratio < 0.3) this.def.speed = Math.max(this.def.speed, this._baseSpeed * 1.4);
    }
    if (!this._baseSpeed) this._baseSpeed = this.def.speed;

    super.update(dt);
  }

  _attack(target) {
    if (this.def.kind === 'ranged' || this.def.ranged) {
      this.world.spawnProjectile?.({ 
        from: this, target, type: this.def.projectile || 'acid',
        damage: this.def.damage, speed: 22, color: 0x7aff5c,
      });
    } else {
      const d = dist2d(this.pos.x, this.pos.z, target.pos.x, target.pos.z);
      if (d < this.def.attackRange + 0.8) {
        const dmg = target.applyDamage(this.def.damage, { source: this, type: 'enemy' });
        events.emit('combat:hit', { attacker: this, target, damage: dmg });
      }
    }
    this._limbs.armL.rotation.x = -2;
    this._limbs.armR.rotation.x = -2;
    setTimeout(() => { if (this._limbs) { this._limbs.armL.rotation.x = 0; this._limbs.armR.rotation.x = 0; } }, 200);
  }

  onDeath(source) {
    for (const [id, chance] of (this.def.loot || [])) {
      if (Math.random() < chance) this.world.loot?.spawn(this.pos.x, this.pos.y + 0.5, this.pos.z, id, 1);
    }
    if (this.world.game) {
      const xp = this.def.xp || 10;
      const seasonXp = this.def.exp || 20;
      this.world.game.awardKill(this, xp, seasonXp);
      events.emit('enemy:defeated', { enemy: this, source });
      if (this.boss) events.emit('boss:defeated', { boss: this, source });
    }
  }
}

export default Enemy;