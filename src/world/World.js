// World: chunk management, streaming, meshing pipeline, physics queries,
// persistence of player edits and structure placement.

import * as THREE from '../../vendor/three.module.js';
import { CONFIG } from '../core/Config.js';
import { Storage } from '../core/Storage.js';
import { events } from '../core/Events.js';
import { Chunk, CHUNK_SIZE, CHUNK_HEIGHT } from './Chunk.js';
import { ChunkMesher } from './ChunkMesher.js';
import { TerrainGenerator } from './TerrainGenerator.js';
import { getBlock, isSolid } from '../content/blocks.js';

const SAVE_KEY = 'pt.world.v1.';

export class World {
  constructor(engine, opts = {}) {
    this.engine = engine;
    this.seed = opts.seed ?? (Date.now() >>> 0);
    this.generator = new TerrainGenerator(this.seed, opts);
    this.mesher = new ChunkMesher(this);
    this.chunks = new Map(); // "cx,cz" -> Chunk
    this.pending = [];       // chunks needing generation (phases)
    this._solidMaterial = new THREE.MeshLambertMaterial({ vertexColors: true });
    this._waterMaterial = new THREE.MeshLambertMaterial({ vertexColors: true, transparent: true, opacity: 0.66 });
    this._glassMaterial = new THREE.MeshLambertMaterial({ vertexColors: true, transparent: true, opacity: 0.5 });
    this.timeBudget = { gen: 5, light: 6, mesh: 5 };
    this._dirtySave = 0;
    this.loadedEdits = false;
    this.lastPlayerChunk = null;
    this.editable = true;
    this.biomeColors = {};
  }

  index(x, y, z) { return (y * CHUNK_SIZE + (z & (CHUNK_SIZE - 1))) * CHUNK_SIZE + (x & (CHUNK_SIZE - 1)); }

  chunkKey(cx, cz) { return cx + ',' + cz; }

  chunkAtCoord(gx, gz) {
    return this.chunks.get(this.chunkKey(Math.floor(gx / CHUNK_SIZE), Math.floor(gz / CHUNK_SIZE)));
  }

  getChunk(cx, cz) { return this.chunks.get(this.chunkKey(cx, cz)); }

  getBlock(x, y, z) {
    if (y < 0) return 15;
    if (y >= CHUNK_HEIGHT) return 0;
    const c = this.chunkAtCoord(x, z);
    if (!c || c.status === 'empty' || c.status === 'generating') return 0;
    const lx = x - c.cx * CHUNK_SIZE, lz = z - c.cz * CHUNK_SIZE;
    if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) return 0;
    const bi = c.idx(lx, y, lz);
    return bi < 0 ? 0 : c.data[bi];
  }

  setBlock(x, y, z, id, opts = {}) {
    x = Math.round(x); y = Math.round(y); z = Math.round(z);
    if (y < 0 || y >= CHUNK_HEIGHT) return false;
    const c = this.chunkAtCoord(x, z);
    if (!c) return false;
    const lx = x - c.cx * CHUNK_SIZE, lz = z - c.cz * CHUNK_SIZE;
    if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE) return false;
    if (opts.track === false) { c.data[c.idx(lx, y, lz)] = id; return true; }
    c.setLocal(lx, y, lz, id);
    if (id === 0 || c.data[c.idx(lx, y, lz)] !== undefined) this._markDirty();
    return true;
  }

  setBlockNoTrack(x, y, z, id) { return this.setBlock(x, y, z, id, { track: false }); }

  isSolidAt(x, y, z) {
    const id = this.getBlock(x, y, z);
    return isSolid(getBlock(id));
  }

  // ---------- Streaming ----------
  ensureChunk(cx, cz, priority = false) {
    const key = this.chunkKey(cx, cz);
    if (this.chunks.has(key)) {
      const c = this.chunks.get(key);
      if (priority && (c.status === 'empty' || this.pending.indexOf(c) === -1)) {
        if (c.status === 'empty') { c.status = 'generating'; this.pending.unshift(c); }
      }
      return this.chunks.get(key);
    }
    const chunk = new Chunk(cx, cz);
    this.chunks.set(key, chunk);
    chunk.status = 'generating';
    this.pending.push(chunk);
    return chunk;
  }

  remeshChunk(cx, cz) {
    const c = this.getChunk(cx, cz);
    if (c && c.status === 'ready') { c.status = 'meshing'; this.pending.push(c); }
  }

  setBlockAndRemesh(x, y, z, id) {
    x = Math.round(x); y = Math.round(y); z = Math.round(z);
    const cx = Math.floor(x / CHUNK_SIZE), cz = Math.floor(z / CHUNK_SIZE);
    const ok = this.setBlock(x, y, z, id);
    if (!ok) return false;
    // Remesh affected chunks (block may sit on a border)
    this.remeshChunk(cx, cz);
    const lx = x - cx * CHUNK_SIZE, lz = z - cz * CHUNK_SIZE;
    if (lx === 0) this.remeshChunk(cx - 1, cz);
    if (lx === CHUNK_SIZE - 1) this.remeshChunk(cx + 1, cz);
    if (lz === 0) this.remeshChunk(cx, cz - 1);
    if (lz === CHUNK_SIZE - 1) this.remeshChunk(cx, cz + 1);
    return true;
  }

  update(dt, px, pz) {
    const cx = Math.floor(px / CHUNK_SIZE), cz = Math.floor(pz / CHUNK_SIZE);
    const vd = this.engine.getViewDistance();

    // Ensure chunks in radius (far ones low priority)
    const base = [];
    for (let dx = -vd; dx <= vd; dx++) {
      for (let dz = -vd; dz <= vd; dz++) {
        const d2 = dx * dx + dz * dz;
        if (d2 > (vd + 0.5) * (vd + 0.5)) continue;
        base.push({ cx: cx + dx, cz: cz + dz, d2 });
      }
    }
    base.sort((a, b) => a.d2 - b.d2);
    // Prioritize 4 center + near chunks; rest appended to queue
    let i = 0;
    for (const b of base) {
      this.ensureChunk(b.cx, b.cz, i < 24);
      i++;
    }

    // Unload far chunks
    const unloadDist = vd + 2;
    for (const [key, c] of this.chunks) {
      if (Math.abs(c.cx - cx) > unloadDist || Math.abs(c.cz - cz) > unloadDist) {
        this.unloadChunk(c);
        this.chunks.delete(key);
      }
    }

    this._processQueues();
  }

  _processQueues() {
    let budget = { gen: this.timeBudget.gen, light: this.timeBudget.light, mesh: this.timeBudget.mesh };
    const start = performance.now();
    while (this.pending.length) {
      const chunk = this.pending[0];
      const t0 = performance.now();

      if (chunk.status === 'generating') {
        if (!chunk._gen) {
          chunk._gen = { col: 0, height: new Float32Array(CHUNK_SIZE * CHUNK_SIZE), biome: new Uint8Array(CHUNK_SIZE * CHUNK_SIZE) };
        }
        // Time-sliced columns
        const perFrame = 6;
        let done = true;
        for (let n = 0; n < perFrame; n++) {
          if (chunk._gen.col >= CHUNK_SIZE) { done = true; break; }
          const lx = chunk._gen.col;
          done = false;
          for (let lz = 0; lz < CHUNK_SIZE; lz++) {
            const gx = chunk.cx * CHUNK_SIZE + lx, gz = chunk.cz * CHUNK_SIZE + lz;
            const info = this.generator.getColumnInfo(gx, gz);
            chunk._gen.height[lx * CHUNK_SIZE + lz] = info.height;
            chunk._gen.biome[lx * CHUNK_SIZE + lz] = info.biome;
            this.generator.fillColumnChunk(chunk.data, CHUNK_SIZE, CHUNK_HEIGHT, CHUNK_SIZE, gx, gz, lx, lz, info.height, info.biome);
          }
          chunk._gen.col++;
        }
        if (chunk._gen.col >= CHUNK_SIZE) {
          chunk.loadGenerated(chunk.data);
          chunk._gen = null;
          // Apply saved edits + place surface features before meshing
          if (this.loadedEdits && chunk._edits) {
            Chunk.deserializeEdits(chunk, chunk._edits);
            chunk._edits = null;
          }
          this.generator.placeFeatures(chunk.cx, chunk.cz, this);
          chunk.status = 'lighting';
        }
      } else if (chunk.status === 'lighting') {
        chunk.light = this.mesher.computeLight(chunk.cx, chunk.cz, chunk.data);
        chunk.status = 'meshing';
      } else if (chunk.status === 'meshing') {
        const meshes = this.mesher.buildMesh(chunk.cx, chunk.cz, chunk.data, chunk.light || this.mesher.computeLight(chunk.cx, chunk.cz, chunk.data));
        this._applyMeshes(chunk, meshes);
        chunk.status = 'ready';
        chunk.light = null;
        this._onChunkReady(chunk);
      } else {
        this.pending.shift();
        continue;
      }

      const elapsed = performance.now() - t0;
      if (chunk.status === 'generating') budget.gen -= elapsed;
      else if (chunk.status === 'lighting') budget.light -= elapsed;
      else budget.mesh -= elapsed;

      if (chunk.status !== 'ready' && chunk.status !== 'generating') this.pending.shift();
      if (chunk.status === 'ready') this.pending.shift();

      if (performance.now() - start > 12) break;
      if (budget.gen <= 0 && chunk.status === 'generating') break;
      if (budget.light <= 0 && chunk.status === 'lighting') break;
      if (budget.mesh <= 0 && chunk.status === 'meshing') break;
    }
  }

  _applyMeshes(chunk, meshes) {
    const group = new THREE.Group();
    group.position.set(chunk.cx * CHUNK_SIZE, 0, chunk.cz * CHUNK_SIZE);
    const solidGeo = ChunkMesher.toGeometry(meshes.solid);
    const waterGeo = ChunkMesher.toGeometry(meshes.water);
    if (solidGeo) {
      const m = new THREE.Mesh(solidGeo, this._solidMaterial);
      m.name = 'chunk-solid';
      group.add(m);
    }
    if (waterGeo) {
      const m = new THREE.Mesh(waterGeo, this._waterMaterial);
      m.name = 'chunk-water';
      m.renderOrder = 1;
      group.add(m);
    }
    if (group.children.length === 0) {
      chunk.mesh = null;
      return;
    }
    this.engine.scene.add(group);
    chunk.mesh = group;
  }

  _onChunkReady(chunk) {
    events.emit('world:chunk-ready', chunk);
  }

  // Synchronously generate + light + mesh a chunk so its blocks are queryable
  // immediately (used for spawn area before the async queue has run).
  buildChunkSync(cx, cz) {
    const c = this.ensureChunk(cx, cz, true);
    if (c.status === 'ready') return c;
    const data = c.data;
    for (let lx = 0; lx < CHUNK_SIZE; lx++) {
      for (let lz = 0; lz < CHUNK_SIZE; lz++) {
        const gx = cx * CHUNK_SIZE + lx, gz = cz * CHUNK_SIZE + lz;
        const info = this.generator.getColumnInfo(gx, gz);
        this.generator.fillColumnChunk(data, CHUNK_SIZE, CHUNK_HEIGHT, CHUNK_SIZE, gx, gz, lx, lz, info.height, info.biome);
      }
    }
    c.loadGenerated(data);
    if (this.loadedEdits && c._edits) {
      Chunk.deserializeEdits(c, c._edits);
      c._edits = null;
    }
    this.generator.placeFeatures(cx, cz, this);
    c.light = this.mesher.computeLight(cx, cz, c.data);
    const meshes = this.mesher.buildMesh(cx, cz, c.data, c.light);
    this._applyMeshes(c, meshes);
    c.status = 'ready';
    c.light = null;
    this._onChunkReady(c);
    const idx = this.pending.indexOf(c);
    if (idx !== -1) this.pending.splice(idx, 1);
    return c;
  }

  unloadChunk(chunk) {
    if (chunk.mesh) {
      this.engine.scene.remove(chunk.mesh);
      chunk.mesh.traverse(o => {
        if (o.geometry) o.geometry.dispose();
      });
      chunk.mesh = null;
    }
    chunk.status = 'empty';
  }

  // ---------- Persistence ----------
  saveEdits() {
    const key = SAVE_KEY + this.seed;
    const saved = Storage.get(key, {});
    for (const [keyStr, c] of this.chunks) {
      if (c.modified.size === 0) continue;
      saved[keyStr] = c.serializeEdits();
    }
    Storage.set(key, saved);
    this._dirtySave = 0;
    events.emit('world:saved', Object.keys(saved).length);
  }

  loadEdits() {
    const saved = Storage.get(SAVE_KEY + this.seed, {});
    this.loadedEdits = true;
    for (const [keyStr, arr] of Object.entries(saved)) {
      const [cx, cz] = keyStr.split(',').map(Number);
      const c = this.getChunk(cx, cz);
      if (c) Chunk.deserializeEdits(c, arr);
    }
  }

  _markDirty() { this._dirtySave = performance.now(); }

  // ---------- Terrain helpers ----------
  getSurfaceHeight(x, z) {
    return Math.floor(this.generator.getHeightAt(x, z));
  }

  getBiome(x, z) { return this.generator.getBiomeAt(x, z); }

  findSafeSpawn(cx, cz) {
    const bx = cx * CHUNK_SIZE + 8, bz = cz * CHUNK_SIZE + 8;
    const gy = this.getSurfaceHeight(bx, bz);
    let y = Math.max(gy, 0);
    while (y > 0 && this.isSolidAt(bx, y + 1, bz)) y--;
    while (y < CHUNK_HEIGHT - 2 && this.isSolidAt(bx, y, bz)) y++;
    return [bx, y + 1.6, bz];
  }

  // Place a structure defined by a builder function or block array.
  // builder: (world, ox, oy, oz, rand) => void
  placeStructure(builder, origin, seed) {
    builder(this, origin[0], origin[1], origin[2], seed);
  }

  setFogDistance(dist) {
    if (this.engine.scene.fog) {
      this.engine.scene.fog.near = dist * 0.18;
      this.engine.scene.fog.far = dist * 0.85;
    }
  }

  getChunkCount() { return this.chunks.size; }
  getReadyChunkCount() {
    let n = 0;
    for (const c of this.chunks.values()) if (c.status === 'ready') n++;
    return n;
  }
}

export default World;