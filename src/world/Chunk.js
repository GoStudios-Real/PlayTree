// Chunk: voxel data container + edit tracking for a 32x96x32 region.

import { CONFIG } from '../core/Config.js';

export const CHUNK_SIZE = CONFIG.world.chunkSize;
export const CHUNK_HEIGHT = CONFIG.world.chunkHeight;

export class Chunk {
  constructor(cx, cz) {
    this.cx = cx;
    this.cz = cz;
    this.data = new Uint8Array(CHUNK_SIZE * CHUNK_HEIGHT * CHUNK_SIZE);
    this.modified = new Map();       // localIndex -> blockId (edits vs generated terrain)
    this.status = 'empty';           // empty | generating | ready
    this.mesh = null;                // { solid: Mesh|null, water: Mesh|null }
    this.generated = false;
    this.lastSeen = 0;
  }

  get size() { return CHUNK_SIZE; }

  idx(lx, y, lz) {
    if (lx < 0 || lx >= CHUNK_SIZE || lz < 0 || lz >= CHUNK_SIZE || y < 0 || y >= CHUNK_HEIGHT) return -1;
    return (y * CHUNK_SIZE + lz) * CHUNK_SIZE + lx;
  }

  getLocal(lx, y, lz) {
    const i = this.idx(lx, y, lz);
    return i < 0 ? 0 : this.data[i];
  }

  setLocal(lx, y, lz, id, track = true) {
    const i = this.idx(lx, y, lz);
    if (i < 0) return;
    if (this.data[i] === id) return;
    this.data[i] = id;
    if (track) this.modified.set(i, id);
  }

  // Fully rebuild from a generated data array.
  loadGenerated(data) {
    this.data.set(data);
    this.generated = true;
    this.status = 'ready';
  }

  // Serialize edits for persistence. Returns compact record.
  serializeEdits() {
    const out = new Uint8Array(this.modified.size * 3);
    let k = 0;
    for (const [i, id] of this.modified) {
      out[k++] = i & 255;
      out[k++] = (i >> 8) & 255;
      out[k++] = id;
    }
    return Array.from(out);
  }

  static deserializeEdits(chunk, arr) {
    chunk.modified.clear();
    for (let i = 0; i + 2 < arr.length; i += 3) {
      const idx = arr[i] | (arr[i + 1] << 8);
      chunk.modified.set(idx, arr[i + 2]);
    }
    for (const [i, id] of chunk.modified) chunk.data[i] = id;
  }
}

export default Chunk;