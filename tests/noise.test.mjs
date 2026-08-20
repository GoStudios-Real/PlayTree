import { ValueNoise, SimplexNoise, TerrainNoise } from '../src/core/Noise.js';

export default function (assert, { approx }) {
  const vn = new ValueNoise(123);
  const vn2 = new ValueNoise(123);
  assert(vn.noise2(10.5, 20.5) === vn2.noise2(10.5, 20.5), 'value noise deterministic');
  for (let i = 0; i < 200; i++) {
    const v = vn.noise2(Math.random() * 100, Math.random() * 100);
    assert(v >= 0 && v <= 1, 'value noise in [0,1]');
  }
  // continuity: close points are close
  const a = vn.noise2(5, 5), b = vn.noise2(5.01, 5.01);
  assert(Math.abs(a - b) < 0.2, 'value noise continuous');

  const sn = new SimplexNoise(77);
  const sn2 = new SimplexNoise(77);
  assert(sn.noise2(1.5, 2.5) === sn2.noise2(1.5, 2.5), 'simplex deterministic');
  const samples = Array.from({ length: 400 }, () => sn.noise2(Math.random() * 80, Math.random() * 80));
  const mean = samples.reduce((s, v) => s + v, 0) / samples.length;
  assert(Math.abs(mean) < 0.2, 'simplex roughly zero-mean (got ' + mean.toFixed(3) + ')');

  const tn = new TerrainNoise(999);
  assert(tn.elevation(10, 20) === tn.elevation(10, 20), 'terrain deterministic');
  approx(tn.elevation(0, 0), tn.elevation(0, 0), 1e-9, 'elevation stable');
}