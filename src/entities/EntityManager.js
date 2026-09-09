// Entity manager: spawns and updates mobs, enemies, NPCs, projectiles and
// loot drops. Handles entity hit-testing and explosions.

import { Mob } from './Mob.js';
import { Enemy } from './Enemy.js';
import { NPC } from './NPC.js';
import { MJ } from './MJ.js';
import { Projectile } from './Projectile.js';
import { LootDrop } from './LootDrop.js';
import { BIOMES } from '../world/TerrainGenerator.js';
import { hash2, dist2d } from '../core/MathUtils.js';
import { events } from '../core/Events.js';

const MOB_BY_BIOME = {
  [BIOMES.PLAINS]: ['herd', 'hare'],
  [BIOMES.FLOWER_MEADOW]: ['hare', 'owl'],
  [BIOMES.FOREST]: ['fox', 'owl'],
  [BIOMES.SWAMP]: ['owl'],
  [BIOMES.JUNGLE]: ['fox', 'owl'],
  [BIOMES.TUNDRA]: ['herd'],
  [BIOMES.BEACH]: ['hare'],
};

export class EntityManager {
  constructor(world, engine) {
    this.world = world;
    this.engine = engine;
    this.entities = new Map();   // id -> entity
    this.npcs = new Map();
    this.projectiles = new Set();
    this.loot = [];
    this._spawnTimer = 0;
    this._spawnCell = new Map();
    this.spawnRadius = 70;
    this.despawnRadius = 130;
    this.activeMobs = 0;
    this.maxMobs = 40;
  }

  register(entity) {
    this.entities.set(entity.id, entity);
    return entity;
  }

  spawnMob(type, x, y, z) {
    const m = new Mob(this.world, type, x, y, z);
    this.register(m);
    this.activeMobs++;
    return m;
  }

  spawnEnemy(type, x, y, z, opts = {}) {
    const e = new Enemy(this.world, type, x, y, z, opts);
    this.register(e);
    return e;
  }

  spawnNPC(type, x, y, z, opts = {}) {
    const n = new NPC(this.world, type, x, y, z, opts);
    this.register(n);
    this.npcs.set(n.id, n);
    return n;
  }

  spawnMJ(x, y, z, opts = {}) {
    const mj = new MJ(this.world, x, y, z, opts);
    this.register(mj);
    this.npcs.set(mj.id, mj);
    return mj;
  }

  spawnProjectile(opts) {
    const p = new Projectile(this.world, opts);
    this.projectiles.add(p);
    return p;
  }

  spawnLoot(x, y, z, itemId, count = 1) {
    if (this.loot.length > 120) this.loot[0]?.dispose?.(), this.loot.shift();
    const d = new LootDrop(this.world, x, y, z, itemId, count);
    this.loot.push(d);
    return d;
  }

  // Hit test against a point: returns nearest entity within radius (excluding `from`).
  hitEntities(x, y, z, radius, from) {
    let best = null, bestD = radius;
    for (const e of this.entities.values()) {
      if (e.dead) continue;
      if (e === from) continue;
      if (e.kind === 'npc') continue;
      const d = Math.hypot(e.pos.x - x, e.pos.y + e.height * 0.5 - y, e.pos.z - z);
      if (d < bestD) { bestD = d; best = e; }
    }
    // Also check local player
    const lp = this.world.localPlayer;
    if (lp && lp !== from && !lp.dead) {
      const d = Math.hypot(lp.pos.x - x, lp.pos.y + 1 - y, lp.pos.z - z);
      if (d < bestD && d < radius) { best = { entity: lp }; return best; }
    }
    return best ? { entity: best } : null;
  }

  explode(x, y, z, radius, damage, from) {
    this.engine.particles?.spawn(x, y, z, { count: 60, color: [1, 0.5, 0.2], speed: 9, life: 0.8 });
    this.engine.audio?.explosion();
    this.engine.camera?.addShake?.(0.4);
    // Damage entities
    for (const e of this.entities.values()) {
      if (e.dead || e === from) continue;
      const d = dist2d(e.pos.x, e.pos.z, x, z);
      if (d < radius) {
        const dmg = Math.round(damage * (1 - d / radius));
        e.damage(dmg, { source: from, type: 'explosion' });
      }
    }
    // Damage local player
    const lp = this.world.localPlayer;
    if (lp && lp !== from && !lp.dead) {
      const d = dist2d(lp.pos.x, lp.pos.z, x, z);
      if (d < radius) lp.applyDamage(Math.round(damage * (1 - d / radius)), { source: from, type: 'explosion' });
    }
    // Destroy blocks in radius
    const r = Math.floor(radius);
    for (let bx = -r; bx <= r; bx++) {
      for (let by = -r; by <= r; by++) {
        for (let bz = -r; bz <= r; bz++) {
          const gx = Math.floor(x) + bx, gy = Math.floor(y) + by, gz = Math.floor(z) + bz;
          if (bx * bx + by * by + bz * bz > r * r) continue;
          const id = this.world.getBlock(gx, gy, gz);
          if (id !== 0 && id !== 5 && id !== 15) {
            this.world.setBlockAndRemesh(gx, gy, gz, 0);
          }
        }
      }
    }
    events.emit('explosion', { x, y, z, radius });
  }

  // Deterministic spawn of mobs/enemies around the player based on cell hashes.
  update(dt, player, timeOfDay) {
    if (!player) return;

    // Spawn mobs in nearby cells
    this._spawnTimer += dt;
    const cellSize = 24;
    const pcx = Math.floor(player.pos.x / cellSize), pcz = Math.floor(player.pos.z / cellSize);
    const range = Math.ceil(this.spawnRadius / cellSize);
    for (let dx = -range; dx <= range; dx++) {
      for (let dz = -range; dz <= range; dz++) {
        const cx = pcx + dx, cz = pcz + dz;
        const key = cx + ',' + cz;
        if (this._spawnCell.has(key)) continue;
        const h = hash2(cx, cz, this.world.seed);
        if (h > 0.35) continue; // not every cell gets a spawn
        const gx = cx * cellSize + (hash2(cx, cz + 99) * cellSize);
        const gz = cz * cellSize + (hash2(cx + 99, cz) * cellSize);
        const dist = dist2d(player.pos.x, player.pos.z, gx, gz);
        if (dist > this.spawnRadius || dist < 14) continue;
        const gy = this.world.getSurfaceHeight(gx, gz);
        if (gy > 40) continue;
        const biome = this.world.getBiome(gx, gz);
        this._spawnCell.set(key, true);

        // Night = more enemies
        const isNight = timeOfDay < 0.28 || timeOfDay > 0.72;
        const roll = hash2(cx * 3, cz * 5, this.world.seed + 7);
        if (isNight && roll < 0.5) {
          const types = ['grub', 'shade', 'brute'];
          const t = types[Math.floor(roll * types.length * 2) % types.length];
          this.spawnEnemy(t, gx, gy + 0.2, gz);
        } else if (roll > 0.62 && this.activeMobs < this.maxMobs) {
          const mobs = MOB_BY_BIOME[biome] || ['hare'];
          const t = mobs[Math.floor(hash2(cx, cz, 33) * mobs.length) % mobs.length];
          this.spawnMob(t, gx, gy + 0.2, gz);
        }
      }
    }
    // Cleanup cells behind player
    for (const key of this._spawnCell.keys()) {
      const [cx, cz] = key.split(',').map(Number);
      if (Math.abs(cx - pcx) > range + 1 || Math.abs(cz - pcz) > range + 1) this._spawnCell.delete(key);
    }

    // Despawn far entities
    for (const e of this.entities.values()) {
      if (e.kind === 'npc') continue;
      const d = dist2d(e.pos.x, e.pos.z, player.pos.x, player.pos.z);
      if (d > this.despawnRadius && !e.boss) {
        this.removeEntity(e);
      }
    }

    // Update all
    const players = [player, ...(this.world.otherPlayers || [])].filter(Boolean);
    for (const e of this.entities.values()) {
      if (e.kind === 'mob') e.update(dt, players.filter(p => p.kind === 'player'));
      else if (e.kind === 'enemy') e.update(dt, this.world, players);
      else if (e.kind === 'npc') e.update(dt);
    }
    for (const p of this.projectiles) {
      p.update(dt);
      if (p.dead) this.projectiles.delete(p);
    }
    for (const l of this.loot) l.update(dt, players);
    this.loot = this.loot.filter(l => !l.claimed);
  }

  removeEntity(e) {
    this.entities.delete(e.id);
    if (e.kind === 'npc') this.npcs.delete(e.id);
    if (e.kind === 'mob') this.activeMobs--;
    e.dispose();
  }

  removeAll() {
    for (const e of this.entities.values()) e.dispose();
    for (const p of this.projectiles) p.dispose();
    for (const l of this.loot) l.dispose();
    this.entities.clear();
    this.npcs.clear();
    this.projectiles.clear();
    this.loot = [];
    this._spawnCell.clear();
  }
}

export default EntityManager;