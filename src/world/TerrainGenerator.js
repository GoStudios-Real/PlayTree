// Procedural terrain generation for PlayTree Chapter I: Season I.
// Produces heightmaps, biome masks, caves, ores and deterministic surface
// features. All deterministic from a world seed (chunk-independent so the
// world streams consistently). Supports incremental column generation for
// time-sliced chunk loading.

import { TerrainNoise, SimplexNoise, mulberry32, hash2 } from '../core/Noise.js';
import { CONFIG } from '../core/Config.js';
import { getBlock, isSolid } from '../content/blocks.js';

export const BIOMES = {
  OCEAN: 0,
  BEACH: 1,
  PLAINS: 2,
  FOREST: 3,
  FLOWER_MEADOW: 4,
  DESERT: 5,
  TUNDRA: 6,
  MOUNTAIN: 7,
  SWAMP: 8,
  JUNGLE: 9,
};

export const BIOME_INFO = {
  [BIOMES.OCEAN]: { name: 'Deep Waters', color: 0x2e6fbf, surface: 4, sub: 3 },
  [BIOMES.BEACH]: { name: 'Sandsprout Shore', color: 0xe6d9a8, surface: 4, sub: 45 },
  [BIOMES.PLAINS]: { name: 'Grove Plains', color: 0x6fbf4f, surface: 1, sub: 2 },
  [BIOMES.FOREST]: { name: 'Bloomwood Forest', color: 0x3f7f2f, surface: 1, sub: 2 },
  [BIOMES.FLOWER_MEADOW]: { name: 'Dewpetal Meadow', color: 0x9fd86f, surface: 1, sub: 2 },
  [BIOMES.DESERT]: { name: 'Sandsprout Wastes', color: 0xe8d089, surface: 4, sub: 45 },
  [BIOMES.TUNDRA]: { name: 'Snowdrift Peaks', color: 0xdfeaf5, surface: 17, sub: 3 },
  [BIOMES.MOUNTAIN]: { name: 'Cragspine Range', color: 0x8f9399, surface: 3, sub: 3 },
  [BIOMES.SWAMP]: { name: 'Fennwisp Swamp', color: 0x5f8f4f, surface: 2, sub: 2 },
  [BIOMES.JUNGLE]: { name: 'Sunvale Jungle', color: 0x2f9f4f, surface: 1, sub: 2 },
};

export class TerrainGenerator {
  constructor(seed, opts = {}) {
    this.seed = seed;
    this.terrain = new TerrainNoise(seed);
    this.simplex = new SimplexNoise(seed + 99);
    this.caveNoise = new SimplexNoise(seed + 7);
    this.oreNoise = new SimplexNoise(seed + 31);
    this.rand = mulberry32(seed);
    this.settings = {
      seaLevel: opts.seaLevel ?? CONFIG.world.seaLevel,
      heightAmplitude: opts.heightAmplitude ?? 20,
      baseHeight: opts.baseHeight ?? 46,
      caveThreshold: opts.caveThreshold ?? 0.02,
      ...opts,
    };
  }

  getHeightAt(x, z) {
    const continent = this.terrain.continent(x, z);
    const elev = this.terrain.elevation(x, z);
    const mountainous = this.simplex.noise2(x * 0.0009 + 400, z * 0.0009 - 800);
    const ridge = Math.abs(this.simplex.noise2(x * 0.0012, z * 0.0012));
    let h = this.settings.baseHeight + elev * this.settings.heightAmplitude;
    if (mountainous > 0.1) h += (mountainous - 0.1) * 26 * ridge;
    if (continent < -0.25) { const d = (continent + 0.25) / 0.25; h = this.settings.seaLevel - 8 + d * (h - this.settings.seaLevel); }
    if (h < 4) h = 4;
    return h;
  }

  getBiomeAt(x, z) {
    const continent = this.terrain.continent(x, z);
    const elev = this.terrain.elevation(x, z);
    const moisture = this.terrain.moisture(x, z);
    const h = this.getHeightAt(x, z);
    if (h <= this.settings.seaLevel + 1) return BIOMES.OCEAN;
    if (h <= this.settings.seaLevel + 3) return BIOMES.BEACH;
    const mountainous = this.simplex.noise2(x * 0.0009 + 400, z * 0.0009 - 800);
    if (mountainous > 0.12 || h > this.settings.baseHeight + 12) return BIOMES.MOUNTAIN;
    if (h > this.settings.baseHeight + 5) return BIOMES.TUNDRA;
    if (continent < -0.05) {
      if (moisture < -0.2) return BIOMES.DESERT;
      return BIOMES.SWAMP;
    }
    if (moisture > 0.35) return BIOMES.JUNGLE;
    if (moisture > 0.1) return BIOMES.FOREST;
    if (moisture > -0.1) return BIOMES.FLOWER_MEADOW;
    if (moisture < -0.35) return BIOMES.DESERT;
    return BIOMES.PLAINS;
  }

  getColumnInfo(gx, gz) {
    return { height: Math.floor(this.getHeightAt(gx, gz)), biome: this.getBiomeAt(gx, gz) };
  }

  // Fill a single column (x,z local) into `data`. Also applies cave + ore for that column.
  fillColumnChunk(data, W, H, D, gx, gz, lx, lz, height, biome) {
    const sea = this.settings.seaLevel;
    const idx = (y) => (y * D + lz) * W + lx;
    const h = height;
    const b = biome;
    const info = BIOME_INFO[b];
    const surface = info.surface;
    const sub = info.sub;
    for (let y = 0; y < H; y++) {
      let id = 0;
      if (y === 0) id = 15;
      else if (y < h - 4) id = 3;
      else if (y < h - 1) id = sub;
      else if (y <= h) id = y === h ? surface : sub;
      data[idx(y)] = id;
    }
    if (h < sea) {
      for (let y = h + 1; y <= sea; y++) data[idx(y)] = 5;
    }
    // Caves
    for (let y = 2; y < H - 4; y++) {
      const i = idx(y);
      const cur = data[i];
      if (!isSolid(getBlock(cur)) || cur === 15) continue;
      const c = this.caveNoise.noise3(gx * 0.02, y * 0.028, gz * 0.02);
      if (c > this.settings.caveThreshold) data[i] = 0;
    }
    // Ores
    for (let y = 2; y < H - 3; y++) {
      const i = idx(y);
      if (data[i] !== 3) continue;
      const n = this.oreNoise.noise3(gx * 0.06, y * 0.06, gz * 0.06);
      const hsh = hash2(gx, y + gz * 31, this.seed);
      if (n > 0.62 && y < 42) data[i] = 10;
      else if (n > 0.6 && y < 32 && hsh > 0.5) data[i] = 11;
      else if (n > 0.72 && y < 24 && hsh > 0.6) data[i] = 12;
      else if (n > 0.82 && y < 16 && hsh > 0.7) data[i] = 13;
      else if (n > 0.78 && y < 28 && hsh > 0.3) data[i] = 14;
    }
  }

  // Sync full generation (used for tests + offline maps).
  generateChunkData(cx, cz) {
    const { chunkSize: W, chunkHeight: H } = CONFIG.world;
    const D = W;
    const data = new Uint8Array(W * H * D);
    const baseX = cx * W, baseZ = cz * W;
    for (let lx = 0; lx < W; lx++) {
      for (let lz = 0; lz < W; lz++) {
        const info = this.getColumnInfo(baseX + lx, baseZ + lz);
        this.fillColumnChunk(data, W, H, D, baseX + lx, baseZ + lz, lx, lz, info.height, info.biome);
      }
    }
    return data;
  }

  // Place surface features into the world. Called after chunk is registered.
  placeFeatures(cx, cz, world) {
    const { chunkSize: W } = CONFIG.world;
    const D = W;
    const baseX = cx * W, baseZ = cz * W;
    const sea = this.settings.seaLevel;
    const cell = 6;
    for (let dx = 0; dx < W; dx++) {
      for (let dz = 0; dz < D; dz++) {
        const wx = baseX + dx, wz = baseZ + dz;
        const h = Math.floor(this.getHeightAt(wx, wz));
        if (h <= sea + 1) continue;
        const b = this.getBiomeAt(wx, wz);
        const hsh = hash2(wx, wz, this.seed * 7 + 1);
        const cellX = Math.floor(wx / cell), cellZ = Math.floor(wz / cell);
        const r = mulberry32(hash2(cellX, cellZ, this.seed + 5) * 4294967296);
        const ox = Math.floor(r() * cell), oz = Math.floor(r() * cell);
        const isTreeCell = wx - cellX * cell === ox && wz - cellZ * cell === oz;

        if ((b === BIOMES.FOREST || b === BIOMES.JUNGLE) && isTreeCell) {
          this._tree(world, wx, h, wz, b === BIOMES.JUNGLE ? 'jungle' : 'oak', r);
        } else if (b === BIOMES.DESERT) {
          if (hsh > 0.985 && world.getBlock(wx, h + 1, wz) === 0) {
            const hgt = 2 + Math.floor(r() * 3);
            for (let i = 1; i <= hgt; i++) world.setBlock(wx, h + i, wz, 28);
          }
        } else if (b === BIOMES.PLAINS || b === BIOMES.FLOWER_MEADOW) {
          if (hsh > 0.93 && hsh < 0.95 && world.getBlock(wx, h + 1, wz) === 0) {
            world.setBlock(wx, h + 1, wz, b === BIOMES.FLOWER_MEADOW ? 23 : 24);
          } else if (hsh > 0.96 && world.getBlock(wx, h + 1, wz) === 0) {
            world.setBlock(wx, h + 1, wz, 24);
          } else if (b === BIOMES.PLAINS && hsh > 0.988) {
            world.setBlock(wx, h + 1, wz, 27);
          }
        } else if (b === BIOMES.TUNDRA) {
          if (hsh > 0.97 && world.getBlock(wx, h + 1, wz) === 0) world.setBlock(wx, h + 1, wz, 48);
        } else if (b === BIOMES.SWAMP) {
          if (hsh > 0.9 && world.getBlock(wx, h + 1, wz) === 0) world.setBlock(wx, h + 1, wz, 48);
          if (hsh > 0.985 && isTreeCell) this._tree(world, wx, h, wz, 'swamp', r);
        } else if (b === BIOMES.MOUNTAIN) {
          if (hsh > 0.995 && world.getBlock(wx, h + 1, wz) === 0) world.setBlock(wx, h + 1, wz, 17);
        }
      }
    }
  }

  _tree(world, x, groundY, z, type, r) {
    const baseH = type === 'jungle' ? 7 : 4 + Math.floor(r() * 2);
    for (let i = 1; i <= baseH; i++) world.setBlock(x, groundY + i, z, 6);
    const leafY = groundY + baseH;
    const spread = type === 'jungle' ? 2 : 1;
    for (let dy = -2; dy <= 1; dy++) {
      const rad = dy >= 0 ? spread : 0;
      for (let dx = -rad; dx <= rad; dx++) {
        for (let dz = -rad; dz <= rad; dz++) {
          if (dx === 0 && dz === 0 && dy <= 0) continue;
          if (Math.abs(dx) === rad && Math.abs(dz) === rad && r() > 0.4) continue;
          const y = leafY + dy;
          if (world.getBlock(x + dx, y, z + dz) === 0) world.setBlock(x + dx, y, z + dz, 7);
        }
      }
    }
    if (r() > 0.5) world.setBlock(x, leafY + 1, z, 7);
  }
}

export default TerrainGenerator;