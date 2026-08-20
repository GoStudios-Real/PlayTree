// Base living entity: health, movement, rendering, AABB physics for entities.

import * as THREE from '../../vendor/three.module.js';
import { AABB, boxCollide } from '../core/MathUtils.js';
import { events } from '../core/Events.js';
import { getBlock } from '../content/blocks.js';

export class LivingEntity {
  constructor(world, opts = {}) {
    this.world = world;
    this.id = opts.id || (Math.random().toString(36).slice(2));
    this.kind = opts.kind || 'entity';
    this.name = opts.name || 'Creature';
    this.pos = { x: opts.x ?? 0, y: opts.y ?? 50, z: opts.z ?? 0 };
    this.vel = { x: 0, y: 0, z: 0 };
    this.width = opts.width ?? 0.8;
    this.height = opts.height ?? 1.2;
    this.health = opts.health ?? 20;
    this.maxHealth = this.health;
    this.speed = opts.speed ?? 2;
    this.dead = false;
    this.despawnTimer = 0;
    this.spawned = false;
    this.yaw = 0;
    this.onGround = false;
    this.simple = false;

    this.color = opts.color ?? 0x7a8f5a;
    this.group = new THREE.Group();
    this._body = this._buildBody();
    this.group.add(this._body);
    if (opts.parent) opts.parent.add(this.group);
    this.world.engine.scene.add(this.group);
  }

  _box(w, h, d, color, x = 0, y = 0, z = 0) {
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      new THREE.MeshLambertMaterial({ color })
    );
    m.position.set(x, y, z);
    return m;
  }

  _buildBody() {
    const g = new THREE.Group();
    g.add(this._box(0.7, 0.6, 0.5, 0x6b7d4f, 0, 0.8, 0));
    g.add(this._box(0.5, 0.45, 0.45, 0x8a9a6b, 0, 1.35, 0));
    return g;
  }

  getAABB() {
    return AABB.fromPosSize(this.pos.x, this.pos.y, this.pos.z, this.width, this.height, this.width);
  }

  damage(amount, source = {}) {
    if (this.dead) return 0;
    this.health -= amount;
    events.emit('entity:hurt', { entity: this, amount, source });
    if (this.health <= 0) {
      this.health = 0;
      this.die(source);
    }
    return amount;
  }

  die(source) {
    this.dead = true;
    events.emit('entity:death', { entity: this, source });
    if (this.onDeath) this.onDeath(source);
    this.dispose();
  }

  faceTowards(x, z) {
    this.yaw = Math.atan2(this.pos.x - x, this.pos.z - z);
  }

  update(dt) {
    if (this.dead) return;
    // Gravity + collision
    const bb = this.getAABB();
    const blocks = (x, y, z) => {
      const id = this.world.getBlock(x, y, z);
      return getBlock(id).solid;
    };
    this.vel.y -= 28 * dt;
    const prevVelY = this.vel.y;
    this.vel = boxCollide(bb, blocks, this.vel, dt);
    this.pos.x = bb.cx;
    this.pos.y = bb.minY;
    this.pos.z = bb.cz;
    this.onGround = Math.abs(this.vel.y) < 0.001;
    if (this.onGround && prevVelY < -12 && prevVelY !== this.vel.y) {
      // landing
    }

    this.group.position.set(this.pos.x, this.pos.y, this.pos.z);
    this.group.rotation.y = this.yaw;
  }

  dispose() {
    this.world.engine.scene.remove(this.group);
    this.group.traverse(o => { if (o.geometry) o.geometry.dispose(); });
    if (this._disposed) return;
    this._disposed = true;
  }
}

export default LivingEntity;