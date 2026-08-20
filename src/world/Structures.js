// Structure builders: place original village buildings and landmarks using
// block patterns. Each builder(world, ox, oy, oz, rng) places blocks via
// world.setBlockAndRemesh (idempotent, saved with the world).

import { mulberry32 } from '../core/MathUtils.js';

function B(world, x, y, z, id) { world.setBlockAndRemesh(x, y, z, id); }

export const Structures = {
  // Small villager house (5 wide x 4 tall x 6 deep)
  house(world, ox, oy, oz, rng = Math.random) {
    const W = 6, H = 4, D = 5;
    // Floor
    for (let x = 0; x < W; x++) for (let z = 0; z < D; z++) B(world, ox + x, oy, oz + z, 8);
    // Walls
    for (let y = 1; y <= H; y++) {
      for (let x = 0; x < W; x++) {
        for (let z = 0; z < D; z++) {
          const edge = x === 0 || x === W - 1 || z === 0 || z === D - 1;
          if (!edge) continue;
          // door on front wall
          if (z === 0 && x === Math.floor(W / 2) && (y === 1 || y === 2)) continue;
          // windows
          if ((x === 0 || x === W - 1) && y === 2 && (z === 1 || z === D - 2)) { B(world, ox + x, oy + y, oz + z, 19); continue; }
          B(world, ox + x, oy + y, oz + z, 8);
        }
      }
    }
    // Ceiling
    for (let x = 0; x < W; x++) for (let z = 0; z < D; z++) B(world, ox + x, oy + H + 1, oz + z, 8);
    // Roof
    for (let r = 0; r < 2; r++) {
      for (let x = -r - 1; x < W + r + 1; x++) {
        for (let z = -r - 1; z < D + r + 1; z++) {
          B(world, ox + x, oy + H + 2 + r, oz + z, 21);
        }
      }
    }
    // Lantern inside
    B(world, ox + Math.floor(W / 2), oy + 2, oz + Math.floor(D / 2), 22);
    // Crafting table
    B(world, ox + 1, oy + 1, oz + 1, 38);
  },

  // Watchtower 3x3
  watchtower(world, ox, oy, oz, rng) {
    for (let y = 0; y < 6; y++) {
      for (let x = 0; x < 3; x++) for (let z = 0; z < 3; z++) {
        if (x === 1 && z === 1) continue;
        B(world, ox + x, oy + y, oz + z, y === 0 ? 9 : 8);
      }
    }
    // Top platform
    for (let x = -1; x < 4; x++) for (let z = -1; z < 4; z++) B(world, ox + x, oy + 6, oz + z, 8);
    // Railing
    for (let x = -1; x < 4; x++) { B(world, ox + x, oy + 7, oz - 1, 44); B(world, ox + x, oy + 7, oz + 3, 44); }
    for (let z = 0; z < 3; z++) { B(world, ox - 1, oy + 7, oz + z, 44); B(world, ox + 3, oy + 7, oz + z, 44); }
    // Ladder
    for (let y = 1; y <= 6; y++) B(world, ox + 1, oy + y, oz, 44);
  },

  // Well
  well(world, ox, oy, oz, rng) {
    for (let x = 0; x < 3; x++) for (let z = 0; z < 3; z++) {
      if (x === 1 && z === 1) continue;
      for (let y = 0; y < 3; y++) B(world, ox + x, oy + y, oz + z, 9);
      B(world, ox + x, oy + 3, oz + z, 9);
    }
    for (let x = -1; x < 4; x++) { B(world, ox + x, oy + 3, oz - 1, 8); B(world, ox + x, oy + 3, oz + 3, 8); }
    for (let z = 0; z < 3; z++) { B(world, ox - 1, oy + 3, oz + z, 8); B(world, ox + 3, oy + 3, oz + z, 8); }
    for (let x = 0; x < 3; x++) for (let z = 0; z < 3; z++) {
      if (x !== 1 && z !== 1) B(world, ox + x, oy - 1, oz + z, 5);
    }
  },

  // Market stall
  stall(world, ox, oy, oz, rng) {
    for (let x = 0; x < 4; x++) for (let z = 0; z < 2; z++) B(world, ox + x, oy, oz + z, 8);
    B(world, ox, oy + 1, oz, 8); B(world, ox + 3, oy + 1, oz, 8);
    B(world, ox, oy + 2, oz, 8); B(world, ox + 3, oy + 2, oz, 8);
    for (let x = 0; x < 4; x++) B(world, ox + x, oy + 2, oz, 19);
    // Goods
    B(world, ox + 1, oy + 1, oz + 1, 27);
    B(world, ox + 2, oy + 1, oz + 1, 39);
  },

  // Heartstone Shrine
  shrine(world, ox, oy, oz, rng) {
    for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++) {
      B(world, ox + x, oy, oz + z, 40);
    }
    for (let x = -2; x <= 2; x++) for (let z = -2; z <= 2; z++) {
      if (Math.abs(x) === 2 || Math.abs(z) === 2) B(world, ox + x, oy + 1, oz + z, 40);
    }
    // Center pedestal + crystal
    B(world, ox, oy + 1, oz, 43);
    B(world, ox, oy + 2, oz, 43);
    B(world, ox, oy + 3, oz, 43);
    B(world, ox, oy + 4, oz, 46);
    // Glowcaps around
    B(world, ox - 1, oy + 1, oz - 1, 31);
    B(world, ox + 1, oy + 1, oz + 1, 31);
  },

  // Village wall segment
  wallSegment(world, ox, oy, oz, length, rng) {
    for (let i = 0; i < length; i++) {
      for (let y = 0; y < 3; y++) B(world, ox + i, oy + y, oz, 9);
    }
    for (let i = 1; i < length - 1; i += 3) B(world, ox + i, oy + 3, oz, 22);
  },

  // Secret cave entrance (covered with a breakable rock face)
  caveEntrance(world, ox, oy, oz, rng) {
    for (let x = -1; x <= 1; x++) for (let z = -1; z <= 1; z++) {
      B(world, ox + x, oy, oz + z, 9);
    }
    for (let y = 1; y <= 2; y++) {
      B(world, ox - 1, oy + y, oz, 9); B(world, ox + 1, oy + y, oz, 9);
    }
    B(world, ox, oy + 1, oz, 9); B(world, ox, oy + 2, oz, 9);
  },

  // Boss arena pedestal
  arena(world, ox, oy, oz, radius = 4, rng) {
    for (let x = -radius; x <= radius; x++) for (let z = -radius; z <= radius; z++) {
      if (x * x + z * z > radius * radius) continue;
      B(world, ox + x, oy, oz + z, 40);
    }
    for (let x = -radius; x <= radius; x++) {
      B(world, ox + x, oy + 1, oz - radius, 36);
      B(world, ox + x, oy + 1, oz + radius, 36);
      B(world, ox - radius, oy + 1, oz + x, 36);
      B(world, ox + radius, oy + 1, oz + x, 36);
    }
  },
};

export function buildVillage(world, cx, cz, rng) {
  const oy = world.getSurfaceHeight(cx, cz);
  // flatten area roughly
  const flat = (x, z, w, h) => {
    for (let dx = -w; dx <= w; dx++) for (let dz = -h; dz <= h; dz++) {
      const hh = world.getSurfaceHeight(cx + dx, cz + dz);
      for (let y = oy; y <= hh; y++) world.setBlockAndRemesh(cx + dx, y, cz + dz, y === hh ? 33 : 2);
    }
  };
  flat(0, 0, 14, 12);
  Structures.house(world, cx - 8, oy, cz - 6, rng);
  Structures.house(world, cx + 6, oy, cz - 5, rng);
  Structures.house(world, cx - 5, oy, cz + 6, rng);
  Structures.house(world, cx + 8, oy, cz + 5, rng);
  Structures.watchtower(world, cx + 12, oy, cz - 10, rng);
  Structures.well(world, cx, oy, cz + 2, rng);
  Structures.stall(world, cx - 2, oy, cz - 8, rng);
  Structures.stall(world, cx + 3, oy, cz + 9, rng);
  Structures.shrine(world, cx, oy, cz - 14, rng);
  return { oy };
}

export default Structures;