// Dropped item pickups on the ground. Float, bob, magnet to players.

import * as THREE from '../../vendor/three.module.js';
import { getItem } from '../content/items.js';
import { getBlock } from '../content/blocks.js';
import { dist3d } from '../core/MathUtils.js';

export class LootDrop {
  constructor(world, x, y, z, itemId, count = 1) {
    this.world = world;
    this.itemId = itemId;
    this.count = count;
    this.pos = { x, y, z };
    this.vel = { x: (Math.random() - 0.5) * 2, y: 4 + Math.random() * 2, z: (Math.random() - 0.5) * 2 };
    this.age = 0;
    this.claimed = false;
    this._build();
  }

  _build() {
    const item = getItem(this.itemId);
    let color = 0x59c48f;
    if (item) {
      if (item.type === 'block') {
        const b = getBlock(item.blockId);
        const c = b.colors.all || b.colors.top || [0.6, 0.6, 0.6];
        color = new THREE.Color(c[0], c[1], c[2]);
      }
    }
    this.mesh = new THREE.Mesh(
      new THREE.BoxGeometry(0.28, 0.28, 0.28),
      new THREE.MeshLambertMaterial({ color })
    );
    this.mesh.position.set(this.pos.x, this.pos.y + 0.3, this.pos.z);
    this.world.engine.scene.add(this.mesh);
  }

  update(dt, players) {
    if (this.claimed) return;
    this.age += dt;
    if (this.age > 120) { this.dispose(); return; }

    // Magnet to nearest player
    let best = null, bestD = Infinity;
    for (const p of players) {
      if (p.dead) continue;
      const d = dist3d(this.pos, { x: p.pos.x, y: p.pos.y + 1, z: p.pos.z });
      if (d < bestD) { bestD = d; best = p; }
    }
    if (best && bestD < 3) {
      const dir = { x: best.pos.x - this.pos.x, y: best.pos.y + 1 - this.pos.y, z: best.pos.z - this.pos.z };
      const len = Math.hypot(dir.x, dir.y, dir.z) || 1;
      this.vel.x = dir.x / len * 10; this.vel.y = dir.y / len * 10; this.vel.z = dir.z / len * 10;
      if (bestD < 0.6) {
        const rem = best.inventory.add(this.itemId, this.count);
        this.claimed = true;
        this.world.engine.audio?.pickup();
        this.world.engine.particles?.spawn(this.pos.x, this.pos.y, this.pos.z, { count: 6, color: [1, 1, 0.6], life: 0.4 });
        if (rem > 0) {
          this.count = rem;
          this.claimed = false;
        } else {
          this.dispose();
        }
        return;
      }
    } else {
      this.vel.x *= 0.9; this.vel.y *= 0.9; this.vel.z *= 0.9;
    }

    this.pos.x += this.vel.x * dt;
    this.pos.y += this.vel.y * dt;
    this.pos.z += this.vel.z * dt;
    this.mesh.position.set(this.pos.x, this.pos.y + 0.3 + Math.sin(this.age * 3) * 0.06, this.pos.z);
    this.mesh.rotation.y += dt * 2;
  }

  dispose() {
    this.claimed = true;
    this.world.engine.scene.remove(this.mesh);
  }
}

export default LootDrop;