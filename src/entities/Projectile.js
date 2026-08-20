// Projectiles: bullets, arrows, rockets, enemy acid/fireballs.
// Cheap sphere-ray hit tests against entities and voxels.

import * as THREE from '../../vendor/three.module.js';
import { raycastVoxels } from '../core/MathUtils.js';
import { events } from '../core/Events.js';
import { getBlock, isSolid } from '../content/blocks.js';

export class Projectile {
  constructor(world, opts) {
    this.world = world;
    this.from = opts.from;             // entity that fired
    this.target = opts.target || null;
    this.pos = { x: opts.x, y: opts.y, z: opts.z };
    this.vel = { x: opts.vx, y: opts.vy, z: opts.vz };
    this.damage = opts.damage ?? 10;
    this.life = opts.life ?? 4;
    this.gravity = opts.gravity ?? (opts.arc ? 12 : 0);
    this.explosive = opts.explosive || false;
    this.explosionRadius = opts.explosionRadius || 5;
    this.freeze = opts.freeze || false;
    this.pierce = opts.pierce || false;
    this.radius = opts.radius ?? 0.18;
    this.color = opts.color ?? 0xffe0a0;
    this._dead = false;
    this._build();
  }

  _build() {
    const geo = new THREE.SphereGeometry(this.radius, 6, 6);
    const mat = new THREE.MeshBasicMaterial({ color: this.color });
    this.mesh = new THREE.Mesh(geo, mat);
    this.light = new THREE.PointLight(this.color, 0.4, 6);
    this.mesh.add(this.light);
    this.mesh.position.set(this.pos.x, this.pos.y, this.pos.z);
    this.world.engine.scene.add(this.mesh);
  }

  update(dt) {
    if (this._dead) return;
    this.life -= dt;
    if (this.life <= 0) { this._explodeOrDie(false); return; }

    this.vel.y -= this.gravity * dt;
    const steps = 3;
    const step = dt / steps;
    for (let i = 0; i < steps; i++) {
      this.pos.x += this.vel.x * step;
      this.pos.y += this.vel.y * step;
      this.pos.z += this.vel.z * step;
      this.mesh.position.set(this.pos.x, this.pos.y, this.pos.z);

      // Block collision
      const bx = Math.floor(this.pos.x), by = Math.floor(this.pos.y), bz = Math.floor(this.pos.z);
      if (isSolid(getBlock(this.world.getBlock(bx, by, bz)))) {
        this._explodeOrDie(true, { x: bx, y: by, z: bz });
        return;
      }
      if (this.pos.y < 0) { this._explodeOrDie(true); return; }
    }

    // Entity hit (only if we have a target for enemy projectiles, else check players + enemies)
    const hit = this.world.hitEntities?.(this.pos.x, this.pos.y, this.pos.z, this.radius, this.from);
    if (hit) {
      const dmg = hit.entity.applyDamage(this.damage, { source: this.from, type: 'projectile', projectile: this });
      events.emit('combat:projectile-hit', { projectile: this, target: hit.entity, damage: dmg });
      if (this.freeze) this._freeze(hit.entity);
      if (!this.pierce) this._explodeOrDie(true);
      else { this.damage *= 0.7; }
      if (hit.entity.dead) this.world.awardKill?.(this.from, hit.entity);
      return;
    }
  }

  _freeze(entity) {
    entity._frozen = (entity._frozen || 0) + 2.5;
  }

  _explodeOrDie(hitSomething, blockPos) {
    if (this._dead) return;
    this._dead = true;
    if (this.explosive) {
      this.world.explode(this.pos.x, this.pos.y, this.pos.z, this.explosionRadius, this.damage, this.from);
    } else if (hitSomething) {
      this.world.particles?.spawn(this.pos.x, this.pos.y, this.pos.z, { count: 8, color: [1, 0.9, 0.5], speed: 2, life: 0.4 });
      this.world.engine.audio?.arrow();
    }
    this.world.engine.scene.remove(this.mesh);
  }

  get dead() { return this._dead; }

  dispose() {
    this.world.engine.scene.remove(this.mesh);
  }
}

export default Projectile;