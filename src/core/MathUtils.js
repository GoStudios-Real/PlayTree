// Math utilities: vectors, AABB, voxel raycasting. Framework agnostic (pure math).

export const clamp = (v, lo, hi) => v < lo ? lo : v > hi ? hi : v;
export const lerp = (a, b, t) => a + (b - a) * t;
export const smoothstep = (a, b, x) => {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
};
export const fract = (x) => x - Math.floor(x);
export const mix3 = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t];
export const dist2d = (ax, ay, bx, by) => Math.hypot(ax - bx, ay - by);
export const dist3d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

// Deterministic seeded PRNG (mulberry32)
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function hash2(x, y, seed = 0) {
  let h = seed + x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}

export function hash3(x, y, z, seed = 0) {
  let h = seed + x * 374761393 + y * 668265263 + z * 2147483647;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}

// ---- AABB ----
export class AABB {
  constructor(minX, minY, minZ, maxX, maxY, maxZ) {
    this.minX = minX; this.minY = minY; this.minZ = minZ;
    this.maxX = maxX; this.maxY = maxY; this.maxZ = maxZ;
  }
  static fromPosSize(cx, cy, cz, w, h, d) {
    return new AABB(cx - w / 2, cy, cz - d / 2, cx + w / 2, cy + h, cz + d / 2);
  }
  get cx() { return (this.minX + this.maxX) / 2; }
  get cz() { return (this.minZ + this.maxZ) / 2; }
  intersects(o) {
    return this.minX < o.maxX && this.maxX > o.minX &&
      this.minY < o.maxY && this.maxY > o.minY &&
      this.minZ < o.maxZ && this.maxZ > o.minZ;
  }
  contains(px, py, pz) {
    return px > this.minX && px < this.maxX && py > this.minY && py < this.maxY && pz > this.minZ && pz < this.maxZ;
  }
  // Push `this` out of `o` along the smallest overlap axis. Returns axis ['x'|'y'|'z'].
  collide(o) {
    const dx = Math.min(this.maxX, o.maxX) - Math.max(this.minX, o.minX);
    const dy = Math.min(this.maxY, o.maxY) - Math.max(this.minY, o.minY);
    const dz = Math.min(this.maxZ, o.maxZ) - Math.max(this.minZ, o.minZ);
    if (dx <= 0 || dy <= 0 || dz <= 0) return null;
    if (dx < dy && dx < dz) {
      if (this.cx < o.cx) { this.minX = o.minX - (this.maxX - this.minX); this.maxX = o.minX; }
      else { this.maxX = o.maxX + (this.maxX - this.minX); this.minX = o.maxX; }
      return 'x';
    } else if (dy < dz) {
      if (this.minY < o.minY) { this.maxY = o.minY; }
      else { this.minY = o.maxY; }
      return 'y';
    } else {
      if (this.cz < o.cz) { this.minZ = o.minZ - (this.maxZ - this.minZ); this.maxZ = o.minZ; }
      else { this.maxZ = o.maxZ + (this.maxZ - this.minZ); this.minZ = o.maxZ; }
      return 'z';
    }
  }
}

// ---- Voxel raycast (Amanatides & Woo style DDA over block grid) ----
// Returns { x, y, z } of first solid (or stopFn-true) block hit, plus the face normal
// of the entry point and the previous (empty) voxel for building.
export function raycastVoxels(ox, oy, oz, dx, dy, dz, maxDist, isSolidFn) {
  let x = Math.floor(ox), y = Math.floor(oy), z = Math.floor(oz);
  const stepX = dx > 0 ? 1 : -1, stepY = dy > 0 ? 1 : -1, stepZ = dz > 0 ? 1 : -1;
  const tDeltaX = Math.abs(1 / (dx || 1e-30));
  const tDeltaY = Math.abs(1 / (dy || 1e-30));
  const tDeltaZ = Math.abs(1 / (dz || 1e-30));
  let tMaxX = (dx > 0 ? (x + 1 - ox) : (ox - x)) * tDeltaX;
  let tMaxY = (dy > 0 ? (y + 1 - oy) : (oy - y)) * tDeltaY;
  let tMaxZ = (dz > 0 ? (z + 1 - oz) : (oz - z)) * tDeltaZ;
  let face = [0, 0, 0];
  let prev = { x, y, z };
  let t = 0;
  while (t <= maxDist) {
    if (isSolidFn(x, y, z)) {
      return { x, y, z, face, prev, t, hit: true };
    }
    prev.x = x; prev.y = y; prev.z = z;
    if (tMaxX < tMaxY && tMaxX < tMaxZ) {
      x += stepX; t = tMaxX; tMaxX += tDeltaX; face = [-stepX, 0, 0];
    } else if (tMaxY < tMaxZ) {
      y += stepY; t = tMaxY; tMaxY += tDeltaY; face = [0, -stepY, 0];
    } else {
      z += stepZ; t = tMaxZ; tMaxZ += tDeltaZ; face = [0, 0, -stepZ];
    }
  }
  return { x, y, z, face, prev, t, hit: false };
}

// Entity-vs-voxel physics sweep for a moving AABB. `blocks` is a function
// (x,y,z)=>bool returning true if that integer voxel is solid.
// Resolves each axis explicitly (clamps the penetrated face) so fast falls
// never tunnel through terrain, even when penetration > horizontal overlap.
export function moveWithCollision(bb, vel, dt, blocks) {
  const w = bb.maxX - bb.minX, h = bb.maxY - bb.minY, d = bb.maxZ - bb.minZ;

  const solidVoxels = () => {
    const hits = [];
    const bx0 = Math.floor(bb.minX), by0 = Math.floor(bb.minY), bz0 = Math.floor(bb.minZ);
    const bx1 = Math.floor(bb.maxX), by1 = Math.floor(bb.maxY), bz1 = Math.floor(bb.maxZ);
    for (let x = bx0; x <= bx1; x++)
      for (let y = by0; y <= by1; y++)
        for (let z = bz0; z <= bz1; z++) {
          if (blocks(x, y, z)) hits.push({ x, y, z });
        }
    return hits;
  };

  // X
  bb.minX += vel.x * dt; bb.maxX += vel.x * dt;
  for (const v of solidVoxels()) {
    if (vel.x > 0) { bb.maxX = v.x; bb.minX = bb.maxX - w; vel.x = 0; }
    else if (vel.x < 0) { bb.minX = v.x + 1; bb.maxX = bb.minX + w; vel.x = 0; }
  }
  // Y (resolve vertically: land on top of blocks below, bump head into blocks above)
  bb.minY += vel.y * dt; bb.maxY += vel.y * dt;
  for (const v of solidVoxels()) {
    if (vel.y < 0) { bb.minY = v.y + 1; bb.maxY = bb.minY + h; vel.y = 0; }
    else if (vel.y > 0) { bb.maxY = v.y; bb.minY = bb.maxY - h; vel.y = 0; }
  }
  // Z
  bb.minZ += vel.z * dt; bb.maxZ += vel.z * dt;
  for (const v of solidVoxels()) {
    if (vel.z > 0) { bb.maxZ = v.z; bb.minZ = bb.maxZ - d; vel.z = 0; }
    else if (vel.z < 0) { bb.minZ = v.z + 1; bb.maxZ = bb.minZ + d; vel.z = 0; }
  }
  return vel;
}

// Axis-aligned box corner collider (used for simpler entity physics).
export function boxCollide(bb, blocks, vel, dt) {
  return moveWithCollision(bb, vel, dt, blocks);
}

export function directionFromYaw(yaw) {
  return {
    x: -Math.sin(yaw),
    y: 0,
    z: -Math.cos(yaw),
  };
}

export function fmtTime(sec) {
  const s = Math.floor(sec);
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}`;
}

export function fmtClock(gameHour, gameMinute) {
  let h = gameHour % 24;
  const suffix = h < 12 ? 'AM' : 'PM';
  h = h % 12 || 12;
  return `${h}:${String(gameMinute).padStart(2, '0')} ${suffix}`;
}

export default {
  clamp, lerp, smoothstep, fract, mix3, dist2d, dist3d,
  mulberry32, hash2, hash3, AABB, raycastVoxels, moveWithCollision,
  boxCollide, directionFromYaw, fmtTime, fmtClock,
};