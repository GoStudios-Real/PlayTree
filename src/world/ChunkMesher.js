// Chunk mesher: builds a vertex-colored BufferGeometry for a chunk.
// - Culls faces against opaque neighbors
// - Directional shading per face + per-cell lighting (skylight BFS + emissive)
// - Biome tint for grass/leaves
// Produces one geometry for solid blocks and one for water.

import * as THREE from '../../vendor/three.module.js';
import { CHUNK_SIZE, CHUNK_HEIGHT } from './Chunk.js';
import { getBlock } from '../content/blocks.js';

const SHADE = { px: 0.78, nx: 0.78, py: 1.0, ny: 0.55, pz: 0.88, nz: 0.88 };

const FACES = [
  // dir, corners (v0,v1,v2,v3), normal, uv-ish
  { dir: 'px', n: [1, 0, 0], corner: (x, y, z) => [[x + 1, y, z + 1], [x + 1, y, z], [x + 1, y + 1, z], [x + 1, y + 1, z + 1]] },
  { dir: 'nx', n: [-1, 0, 0], corner: (x, y, z) => [[x, y, z], [x, y, z + 1], [x, y + 1, z + 1], [x, y + 1, z]] },
  { dir: 'py', n: [0, 1, 0], corner: (x, y, z) => [[x, y + 1, z], [x + 1, y + 1, z], [x + 1, y + 1, z + 1], [x, y + 1, z + 1]] },
  { dir: 'ny', n: [0, -1, 0], corner: (x, y, z) => [[x, y, z + 1], [x + 1, y, z + 1], [x + 1, y, z], [x, y, z]] },
  { dir: 'pz', n: [0, 0, 1], corner: (x, y, z) => [[x, y, z + 1], [x, y + 1, z + 1], [x + 1, y + 1, z + 1], [x + 1, y, z + 1]] },
  { dir: 'nz', n: [0, 0, -1], corner: (x, y, z) => [[x + 1, y, z], [x + 1, y + 1, z], [x, y + 1, z], [x, y, z]] },
];

export class ChunkMesher {
  constructor(world) {
    this.world = world;
  }

  // Compute a light buffer for the chunk (per-cell 0..15).
  // Local flood: skylight from column tops + emissive sources, BFS within chunk.
  computeLight(cx, cz, data) {
    const W = CHUNK_SIZE, H = CHUNK_HEIGHT;
    const light = new Uint8Array(W * H * W);
    const idx = (x, y, z) => (y * W + z) * W + x;
    const get = (x, y, z) => {
      const i = idx(x, y, z);
      return i >= 0 && i < light.length ? data[i] : 0;
    };
    const isOpaqueAt = (gx, gy, gz) => {
      const c = this.world.chunkAtCoord(gx, gz);
      if (!c || c.status !== 'ready') return gy < 0 || gy >= H;
      const lx = gx - c.cx * W, lz = gz - c.cz * W;
      if (lx < 0 || lx >= W || lz < 0 || lz >= W) return true;
      const bi = c.idx(lx, gy, lz);
      if (bi < 0) return gy < 0 || gy >= H;
      return getBlock(c.data[bi]).opaque;
    };

    const baseX = cx * W, baseZ = cz * W;
    const queue = [];

    // 1. Skylight: cells not under opaque get 15.
    for (let lx = 0; lx < W; lx++) {
      for (let lz = 0; lz < W; lz++) {
        for (let y = H - 1; y >= 0; y--) {
          if (getBlock(get(lx, y, lz)).opaque) break;
          light[idx(lx, y, lz)] = 15;
          queue.push([lx, y, lz, 15]);
        }
      }
    }

    // 2. Emissive sources (local)
    for (let lx = 0; lx < W; lx++) {
      for (let lz = 0; lz < W; lz++) {
        for (let y = 0; y < H; y++) {
          const bl = getBlock(get(lx, y, lz));
          if (bl.emitsLight && light[idx(lx, y, lz)] < bl.emitsLight) {
            light[idx(lx, y, lz)] = bl.emitsLight;
            queue.push([lx, y, lz, bl.emitsLight]);
          }
        }
      }
    }

    // 3. BFS flood (local)
    const visited = new Uint8Array(W * H * W);
    const dirs = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
    let head = 0;
    while (head < queue.length) {
      const [x, y, z, l] = queue[head++];
      if (l <= 1) continue;
      for (const [dx, dy, dz] of dirs) {
        const nx = x + dx, ny = y + dy, nz = z + dz;
        if (nx < 0 || nx >= W || nz < 0 || nz >= W || ny < 0 || ny >= H) continue;
        const ni = idx(nx, ny, nz);
        if (visited[ni]) continue;
        if (isOpaqueAt(baseX + nx, ny, baseZ + nz)) continue;
        const curBlock = getBlock(get(nx, ny, nz));
        if (curBlock.emitsLight && curBlock.emitsLight > l - 1) continue;
        visited[ni] = 1;
        const nl = l - 1;
        if (light[ni] < nl) light[ni] = nl;
        queue.push([nx, ny, nz, nl]);
      }
    }
    return light;
  }

  buildMesh(cx, cz, data, light) {
    const W = CHUNK_SIZE, H = CHUNK_HEIGHT;
    const baseX = cx * W, baseZ = cz * W;

    const isSolidAt = (gx, gy, gz) => {
      const c = this.world.chunkAtCoord(gx, gz);
      if (!c || c.status !== 'ready') return false;
      const lx = gx - c.cx * W, lz = gz - c.cz * W;
      if (lx < 0 || lx >= W || lz < 0 || lz >= W) return false;
      const bi = c.idx(lx, gy, lz);
      if (bi < 0) return false;
      return getBlock(c.data[bi]).solid;
    };

    const solid = { pos: [], col: [], nrm: [], idx: [] };
    const water = { pos: [], col: [], nrm: [], idx: [] };

    for (let lx = 0; lx < W; lx++) {
      for (let lz = 0; lz < W; lz++) {
        for (let y = 0; y < H; y++) {
          const i = (y * W + lz) * W + lx;
          const id = data[i];
          if (id === 0) continue;
          const block = getBlock(id);
          if (block.liquid) {
            // Water surface only (top faces)
            this._emitFace(cx, cz, baseX, baseZ, data, light, water, lx, y, lz, id, 'py');
            continue;
          }
          for (const face of FACES) {
            const nid = this._neighbor(cx, cz, baseX, baseZ, data, lx, y, lz, face.dir);
            const nb = getBlock(nid);
            if (nb.opaque) continue;
            // Skip faces between water and air below surface for perf (optional)
            this._emitFace(cx, cz, baseX, baseZ, data, light, solid, lx, y, lz, id, face.dir);
          }
        }
      }
    }
    return { solid, water };
  }

  _neighbor(cx, cz, baseX, baseZ, data, lx, y, lz, dir) {
    const W = CHUNK_SIZE;
    let nx = lx, ny = y, nz = lz;
    if (dir === 'px') nx += 1; else if (dir === 'nx') nx -= 1;
    else if (dir === 'py') ny += 1; else if (dir === 'ny') ny -= 1;
    else if (dir === 'pz') nz += 1; else nz -= 1;
    if (ny < 0 || ny >= CHUNK_HEIGHT) return 0;
    if (nx < 0 || nx >= W || nz < 0 || nz >= W) {
      const c = this.world.chunkAtCoord(baseX + nx, baseZ + nz);
      if (!c || c.status !== 'ready') return 0;
      const li = c.idx(nx < 0 ? W - 1 : nx >= W ? 0 : nx, ny, nz < 0 ? W - 1 : nz >= W ? 0 : nz);
      return c.data[li];
    }
    return data[(ny * W + nz) * W + nx];
  }

  _emitFace(cx, cz, baseX, baseZ, data, light, buf, lx, y, lz, id, dir) {
    const W = CHUNK_SIZE;
    const block = getBlock(id);
    const face = FACES.find(f => f.dir === dir);
    const corners = face.corner(lx, y, lz);
    const shade = SHADE[dir];

    // Determine color per face based on block color definition
    let base;
    if (dir === 'py' && block.colors.top) base = block.colors.top;
    else if (dir === 'ny' && block.colors.bottom) base = block.colors.bottom;
    else if (dir !== 'py' && dir !== 'ny' && block.colors.side) base = block.colors.side;
    else base = block.colors.all || block.colors.top || block.colors.side || [0.5, 0.5, 0.5];

    const gx = baseX + lx, gz = baseZ + lz;
    const lightVal = light[(y * W + lz) * W + lx] / 15;

    // Grass/leaves biome tint variation
    const r = base[0], g = base[1], b = base[2];
    const v = (lightVal * shade);
    let cr = r * v, cg = g * v, cb = b * v;

    // Simple directional tinting for depth
    if (block.tint) {
      const wob = 0.9 + 0.1 * Math.sin(gx * 0.5 + gz * 0.7 + y);
      cr *= wob; cg *= wob; cb *= wob;
    }

    const v0 = buf.pos.length / 3;
    for (const c of corners) buf.pos.push(c[0], c[1], c[2]);
    for (let i = 0; i < 4; i++) buf.col.push(cr, cg, cb);
    for (let i = 0; i < 4; i++) buf.nrm.push(face.n[0], face.n[1], face.n[2]);
    buf.idx.push(v0, v0 + 1, v0 + 2, v0, v0 + 2, v0 + 3);
  }

  static toGeometry(buf, transparent = false) {
    if (buf.pos.length === 0) return null;
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(buf.pos, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(buf.col, 3));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(buf.nrm, 3));
    geo.setIndex(buf.idx);
    geo.transparent = transparent;
    geo.computeBoundingSphere();
    return geo;
  }
}

export default ChunkMesher;