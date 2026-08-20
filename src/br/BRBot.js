// Battle Royale bots: AI opponents. Drop from the bus, loot, run to the zone,
// and fight. Uses simple raycast-ish shooting through the projectile system.

import { LivingEntity } from '../entities/LivingEntity.js';
import { dist2d, mulberry32 } from '../core/MathUtils.js';
import { getItem } from '../content/items.js';
import { events } from '../core/Events.js';
import * as THREE from '../../vendor/three.module.js';

const BOT_NAMES = ['LeafRider', 'BloomFox', 'RootMaster99', 'SunKnight', 'SproutPip', 'GroveWarden', 'BarkBro', 'VerdantViper', 'ThornThief', 'MossMarauder', 'CragCrusher', 'EmberEcho', 'WillowWisp', 'DuneDancer', 'ShadeShifter', 'PetalProwler'];
const BOT_COLORS = [0x59c48f, 0x4aa8ff, 0xff7a59, 0xffcf5c, 0xa86bff, 0x8a5ac8, 0x6a9a5a, 0xd4703a];

export class BRBot extends LivingEntity {
  constructor(world, opts = {}) {
    const name = opts.name || BOT_NAMES[Math.floor(Math.random() * BOT_NAMES.length)];
    const color = opts.color || BOT_COLORS[Math.floor(Math.random() * BOT_COLORS.length)];
    super(world, {
      kind: 'bot', name, x: opts.x ?? 0, y: opts.y ?? 200, z: opts.z ?? 0,
      width: 0.6, height: 1.8, health: 100, speed: 6.5, color,
    });
    this.name = name;
    this.color = color;
    this.team = opts.team || 0;
    this.rand = mulberry32((Math.random() * 2 ** 32) >>> 0);
    this.state = 'dropping';   // dropping | looting | roaming | fighting
    this.yaw = this.rand() * Math.PI * 2;
    this.shootTimer = 0;
    this.reloadTimer = 0;
    this.ammo = 30;
    this.shield = 0;
    this.elims = 0;
    this.dropTarget = null;
    this.lootTarget = null;
    this.walkTarget = null;
    this.group.position.set(this.pos.x, this.pos.y, this.pos.z);
  }

  _buildBody() {
    const g = new THREE.Group();
    const torso = this._box(0.5, 0.6, 0.28, this.color, 0, 0.95, 0);
    const head = this._box(0.42, 0.42, 0.42, 0xf0c8a0, 0, 1.42, 0);
    const armL = this._box(0.16, 0.55, 0.16, this.color, -0.34, 0.95, 0);
    const armR = this._box(0.16, 0.55, 0.16, this.color, 0.34, 0.95, 0);
    const legL = this._box(0.2, 0.6, 0.2, 0x3a4a66, -0.12, 0.32, 0);
    const legR = this._box(0.2, 0.6, 0.2, 0x3a4a66, 0.12, 0.32, 0);
    g.add(torso, head, armL, armR, legL, legR);
    this.group.add(g);
    this._limbs = { armL, armR, legL, legR };
    // Name tag
    const canvas = document.createElement('canvas');
    canvas.width = 256; canvas.height = 48;
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 24px sans-serif';
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(0, 0, 256, 48);
    ctx.fillStyle = '#ffffff'; ctx.textAlign = 'center';
    ctx.fillText(this.name, 128, 30);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(canvas), depthTest: false }));
    sprite.position.y = 2.2; sprite.scale.set(2.2, 0.45, 1);
    this.group.add(sprite);
    return g;
  }

  update(dt, world, players, zone) {
    if (this.dead) return;
    if (!world) return; // managed by the active mode's update loop
    this.shootTimer = Math.max(0, this.shootTimer - dt);
    this.reloadTimer = Math.max(0, this.reloadTimer - dt);

    if (this.state === 'dropping') {
      // Parachute descent
      if (this.pos.y > world.getSurfaceHeight(this.pos.x, this.pos.z) + 1.2) {
        this.vel.y = -8;
        this.pos.y += this.vel.y * dt;
        this.group.position.set(this.pos.x, this.pos.y, this.pos.z);
        return;
      }
      this.state = 'roaming';
      this.pos.y = world.getSurfaceHeight(this.pos.x, this.pos.z) + 1.2;
      this.group.position.set(this.pos.x, this.pos.y, this.pos.z);
      return;
    }

    // Find enemies
    const enemies = players.filter(p => p !== this && !p.dead);
    let target = null, best = Infinity;
    for (const p of enemies) {
      const d = dist2d(this.pos.x, this.pos.z, p.pos.x, p.pos.z);
      if (d < best) { best = d; target = p; }
    }

    // Fighting
    if (target && best < 70 && this.reloadTimer <= 0) {
      this.state = 'fighting';
      this._fight(target, best, dt, world);
    } else {
      this.state = 'roaming';
      this._roam(dt, world, zone);
    }

    // Gravity/collision via super
    super.update(dt);
  }

  _roam(dt, world, zone) {
    const safe = zone.inSafeZone(this.pos.x, this.pos.z);
    if (!safe) {
      // Move toward zone center
      this._walkTowards(zone.center.x, zone.center.z, this.speed * 1.25, dt);
      return;
    }
    // Look for loot crates
    const crates = world.brCrates || [];
    if (this.ammo < 15 && crates.length) {
      let best = null, bd = Infinity;
      for (const c of crates) {
        const d = dist2d(this.pos.x, this.pos.z, c.x, c.z);
        if (d < bd && d < 200) { bd = d; best = c; }
      }
      if (best && bd > 2) { this._walkTowards(best.x, best.z, this.speed, dt); return; }
    }
    // Random wander
    if (!this.walkTarget || dist2d(this.pos.x, this.pos.z, this.walkTarget.x, this.walkTarget.z) < 4 || this._wtimer <= 0) {
      this._wtimer = 4 + this.rand() * 6;
      const ang = this.rand() * Math.PI * 2;
      const r = 10 + this.rand() * 40;
      this.walkTarget = { x: this.pos.x + Math.cos(ang) * r, z: this.pos.z + Math.sin(ang) * r };
    }
    this._walkTowards(this.walkTarget.x, this.walkTarget.z, this.speed * 0.6, dt);
  }

  _walkTowards(tx, tz, speed, dt) {
    const ang = Math.atan2(tx - this.pos.x, tz - this.pos.z);
    this.vel.x = Math.cos(ang) * speed;
    this.vel.z = Math.sin(ang) * speed;
    this.yaw = ang;
    if (this._limbs) {
      const s = Math.sin(performance.now() * 0.02);
      this._limbs.legL.rotation.x = s * 0.5;
      this._limbs.legR.rotation.x = -s * 0.5;
    }
  }

  _fight(target, dist, dt, world) {
    const ang = Math.atan2(target.pos.x - this.pos.x, target.pos.z - this.pos.z);
    this.yaw = ang;
    this.vel.x *= 0.4; this.vel.z *= 0.4;
    if (this.shootTimer <= 0 && this.ammo > 0) {
      this.shootTimer = 0.35 + this.rand() * 0.3;
      this.ammo--;
      const accuracy = 0.15;
      const ex = this.pos.x, ey = this.pos.y + 1.5, ez = this.pos.z;
      const tx = target.pos.x + (this.rand() - 0.5) * accuracy * dist;
      const ty = target.pos.y + 1 + (this.rand() - 0.5) * accuracy * dist;
      const tz = target.pos.z + (this.rand() - 0.5) * accuracy * dist;
      const dx = tx - ex, dy = ty - ey, dz = tz - ez;
      const len = Math.hypot(dx, dy, dz) || 1;
      const speed = 60;
      world.spawnProjectile({
        from: this, x: ex, y: ey, z: ez,
        vx: dx / len * speed, vy: dy / len * speed, vz: dz / len * speed,
        damage: 12, life: 2.5, color: 0xffe080,
      });
      world.engine.audio?.shoot();
    }
    if (this.ammo <= 0 && this.reloadTimer <= 0) {
      this.reloadTimer = 2;
      this.ammo = 30;
    }
    if (this._limbs) {
      this._limbs.armR.rotation.x = -1.6;
    }
  }

  onDeath(source) {
    events.emit('br:bot-eliminated', { bot: this, source });
  }
}

export default BRBot;