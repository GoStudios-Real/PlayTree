// Seeded noise library (no external deps).
// Implements 2D/3D value noise with fractal octaves, and a simplex noise variant.

import { mulberry32, lerp, smoothstep, clamp } from './MathUtils.js';

const GRAD2 = [
  [1, 0], [-1, 0], [0, 1], [0, -1],
  [0.7071, 0.7071], [-0.7071, 0.7071], [0.7071, -0.7071], [-0.7071, -0.7071]
];

// ---- Value noise with smoothed hashing ----
export class ValueNoise {
  constructor(seed = 0) {
    this.seed = seed;
  }
  // 2D value noise in [0,1]
  noise2(x, y) {
    const xi = Math.floor(x), yi = Math.floor(y);
    const xf = x - xi, yf = y - yi;
    const u = smoothstep(0, 1, xf), v = smoothstep(0, 1, yf);
    const a = hash2(xi, yi, this.seed);
    const b = hash2(xi + 1, yi, this.seed);
    const c = hash2(xi, yi + 1, this.seed);
    const d = hash2(xi + 1, yi + 1, this.seed);
    return lerp(lerp(a, b, u), lerp(c, d, u), v);
  }
  // 3D value noise in [0,1]
  noise3(x, y, z) {
    const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
    const xf = x - xi, yf = y - yi, zf = z - zi;
    const u = smoothstep(0, 1, xf), v = smoothstep(0, 1, yf), w = smoothstep(0, 1, zf);
    let acc = 0, n = 0;
    for (let dz = 0; dz <= 1; dz++)
      for (let dy = 0; dy <= 1; dy++)
        for (let dx = 0; dx <= 1; dx++) {
          const k = hash3(xi + dx, yi + dy, zi + dz, this.seed);
          acc += lerp(
            lerp(lerp(k, hash3(xi + dx + 1, yi + dy, zi + dz, this.seed), u),
              lerp(hash3(xi + dx, yi + dy + 1, zi + dz, this.seed), hash3(xi + dx + 1, yi + dy + 1, zi + dz, this.seed), u), v),
            lerp(lerp(hash3(xi + dx, yi + dy, zi + dz + 1, this.seed), hash3(xi + dx + 1, yi + dy, zi + dz + 1, this.seed), u),
              lerp(hash3(xi + dx, yi + dy + 1, zi + dz + 1, this.seed), hash3(xi + dx + 1, yi + dy + 1, zi + dz + 1, this.seed), u), v),
            w);
          n++;
        }
    return acc / n;
  }
  // Fractal (fBm) 2D
  fbm2(x, y, octaves = 4, lacunarity = 2, gain = 0.5) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < octaves; i++) {
      sum += amp * this.noise2(x * freq, y * freq);
      norm += amp;
      amp *= gain; freq *= lacunarity;
    }
    return sum / norm;
  }
  // Fractal 3D
  fbm3(x, y, z, octaves = 3, lacunarity = 2, gain = 0.5) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < octaves; i++) {
      sum += amp * this.noise3(x * freq, y * freq, z * freq);
      norm += amp;
      amp *= gain; freq *= lacunarity;
    }
    return sum / norm;
  }
}

export function hash2(x, y, seed) {
  let h = seed + x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}
export function hash3(x, y, z, seed) {
  let h = seed + x * 374761393 + y * 668265263 + z * 2147483647;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) >>> 0) / 4294967296;
}

// ---- Simplex noise (2D/3D) ----
const F2 = 0.5 * (Math.sqrt(3) - 1);
const G2 = (3 - Math.sqrt(3)) / 6;
const F3 = 1 / 3;
const G3 = 1 / 6;

export class SimplexNoise {
  constructor(seed = 0) {
    this.rand = mulberry32(seed);
    this.perm = new Uint8Array(512);
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    for (let i = 255; i > 0; i--) {
      const j = Math.floor(this.rand() * (i + 1));
      const t = p[i]; p[i] = p[j]; p[j] = t;
    }
    for (let i = 0; i < 512; i++) this.perm[i] = p[i & 255];
  }
  _grad2(ix, iy) {
    return GRAD2[this.perm[ix + this.perm[iy]] & 7];
  }
  noise2(xin, yin) {
    const s = (xin + yin) * F2;
    const i = Math.floor(xin + s), j = Math.floor(yin + s);
    const t = (i + j) * G2;
    const x0 = xin - (i - t), y0 = yin - (j - t);
    let i1, j1;
    if (x0 > y0) { i1 = 1; j1 = 0; } else { i1 = 0; j1 = 1; }
    const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2;
    const x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2;
    const ii = i & 255, jj = j & 255;
    let sum = 0;
    let t0 = 0.5 - x0 * x0 - y0 * y0;
    if (t0 >= 0) {
      const g = this._grad2(ii, jj);
      t0 *= t0; t0 *= t0;
      sum += t0 * (g[0] * x0 + g[1] * y0);
    }
    let t1 = 0.5 - x1 * x1 - y1 * y1;
    if (t1 >= 0) {
      const g = this._grad2(ii + i1, jj + j1);
      t1 *= t1; t1 *= t1;
      sum += t1 * (g[0] * x1 + g[1] * y1);
    }
    let t2 = 0.5 - x2 * x2 - y2 * y2;
    if (t2 >= 0) {
      const g = this._grad2(ii + 1, jj + 1);
      t2 *= t2; t2 *= t2;
      sum += t2 * (g[0] * x2 + g[1] * y2);
    }
    return 70 * sum;
  }
  noise3(xin, yin, zin) {
    const s = (xin + yin + zin) * F3;
    const i = Math.floor(xin + s), j = Math.floor(yin + s), k = Math.floor(zin + s);
    const t = (i + j + k) * G3;
    const x0 = xin - (i - t), y0 = yin - (j - t), z0 = zin - (k - t);
    let i1, j1, k1, i2, j2, k2;
    if (x0 >= y0) {
      if (y0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
      else if (x0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 0; k2 = 1; }
      else { i1 = 0; j1 = 0; k1 = 1; i2 = 1; j2 = 0; k2 = 1; }
    } else {
      if (y0 < z0) { i1 = 0; j1 = 0; k1 = 1; i2 = 0; j2 = 1; k2 = 1; }
      else if (x0 < z0) { i1 = 0; j1 = 1; k1 = 0; i2 = 0; j2 = 1; k2 = 1; }
      else { i1 = 0; j1 = 1; k1 = 0; i2 = 1; j2 = 1; k2 = 0; }
    }
    const x1 = x0 - i1 + G3, y1 = y0 - j1 + G3, z1 = z0 - k1 + G3;
    const x2 = x0 - i2 + 2 * G3, y2 = y0 - j2 + 2 * G3, z2 = z0 - k2 + 2 * G3;
    const x3 = x0 - 1 + 3 * G3, y3 = y0 - 1 + 3 * G3, z3 = z0 - 1 + 3 * G3;
    const ii = i & 255, jj = j & 255, kk = k & 255;
    let sum = 0;
    let t0 = 0.6 - x0 * x0 - y0 * y0 - z0 * z0;
    if (t0 >= 0) { t0 *= t0; sum += t0 * t0 * this._dot3(ii, jj, kk, x0, y0, z0); }
    let t1 = 0.6 - x1 * x1 - y1 * y1 - z1 * z1;
    if (t1 >= 0) { t1 *= t1; sum += t1 * t1 * this._dot3(ii + i1, jj + j1, kk + k1, x1, y1, z1); }
    let t2 = 0.6 - x2 * x2 - y2 * y2 - z2 * z2;
    if (t2 >= 0) { t2 *= t2; sum += t2 * t2 * this._dot3(ii + i2, jj + j2, kk + k2, x2, y2, z2); }
    let t3 = 0.6 - x3 * x3 - y3 * y3 - z3 * z3;
    if (t3 >= 0) { t3 *= t3; sum += t3 * t3 * this._dot3(ii + 1, jj + 1, kk + 1, x3, y3, z3); }
    return 32 * sum;
  }
  _dot3(ix, iy, iz, x, y, z) {
    const g = this._grad3(ix, iy, iz);
    return g[0] * x + g[1] * y + g[2] * z;
  }
  _grad3(ix, iy, iz) {
    const h = this.perm[ix + this.perm[iy + this.perm[iz]]] & 15;
    return GRAD3[h];
  }
  fbm2(x, y, octaves = 4, lac = 2, gain = 0.5) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < octaves; i++) { sum += amp * this.noise2(x * freq, y * freq); norm += amp; amp *= gain; freq *= lac; }
    return sum / norm;
  }
  fbm3(x, y, z, octaves = 3, lac = 2, gain = 0.5) {
    let amp = 1, freq = 1, sum = 0, norm = 0;
    for (let i = 0; i < octaves; i++) { sum += amp * this.noise3(x * freq, y * freq, z * freq); norm += amp; amp *= gain; freq *= lac; }
    return sum / norm;
  }
}

const GRAD3 = [
  [1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0],
  [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1],
  [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1],
  [1, 1, 0], [0, -1, 1], [-1, 1, 0], [0, -1, -1]
];

// Domain-warped noise for terrain (combines value + simplex).
export class TerrainNoise {
  constructor(seed = 0) {
    this.simplex = new SimplexNoise(seed);
    this.value = new ValueNoise(seed * 7919 + 13);
  }
  // Returns elevation roughly in [-1,1]
  elevation(x, z, scale = 0.0016) {
    const wx = x * scale, wz = z * scale;
    const warp = 3.0 * this.simplex.noise2(wx * 0.5 + 100, wz * 0.5 - 300);
    const n = this.simplex.fbm2(wx + warp, wz - warp, 4, 2, 0.5);
    return n;
  }
  // Continental + detail mix
  continent(x, z) {
    return this.simplex.noise2(x * 0.00035, z * 0.00035);
  }
  moisture(x, z) {
    return this.simplex.fbm2(x * 0.0005 + 55, z * 0.0005 - 77, 3);
  }
  // Cave density in [-1,1]
  cave(x, y, z) {
    const s = 0.008;
    const a = this.simplex.noise3(x * s, y * s, z * s);
    const b = this.simplex.noise3(x * s * 2 + 500, y * s * 2, z * s * 2 - 900);
    return a + 0.5 * b;
  }
  // Ore blob density
  ore(x, y, z, scale = 0.09) {
    return this.simplex.noise3(x * scale, y * scale, z * scale);
  }
}

export function pickNoise(seed) {
  return { value: new ValueNoise(seed), simplex: new SimplexNoise(seed), terrain: new TerrainNoise(seed) };
}

// Re-exported for content modules that use these directly.
export { mulberry32 };

export default { ValueNoise, SimplexNoise, TerrainNoise, pickNoise };