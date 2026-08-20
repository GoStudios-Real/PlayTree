// Simple GPU-free particle system using THREE.Points for performance.
// Emitters are cheap bursts; particles fade and fall.

import * as THREE from '../../vendor/three.module.js';

const MAX_PARTICLES = 6000;

export class ParticleSystem {
  constructor(engine) {
    this.engine = engine;
    this.pool = [];
    this.active = [];
    this.count = 0;
    this.geo = new THREE.BufferGeometry();
    this.positions = new Float32Array(MAX_PARTICLES * 3);
    this.colors = new Float32Array(MAX_PARTICLES * 3);
    this.vels = new Float32Array(MAX_PARTICLES * 3);
    this.life = new Float32Array(MAX_PARTICLES);
    this.maxLife = new Float32Array(MAX_PARTICLES);
    this.sizes = new Float32Array(MAX_PARTICLES);
    this.geo.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.geo.setAttribute('color', new THREE.BufferAttribute(this.colors, 3));
    const mat = new THREE.PointsMaterial({
      size: 0.14, vertexColors: true, transparent: true, opacity: 0.9,
      sizeAttenuation: true, depthWrite: false,
    });
    this.points = new THREE.Points(this.geo, mat);
    this.points.frustumCulled = false;
    this.points.renderOrder = 5;
    engine.scene.add(this.points);
    this.enabled = true;
  }

  spawn(x, y, z, opts = {}) {
    if (!this.enabled) return;
    const n = opts.count ?? 8;
    for (let i = 0; i < n; i++) {
      if (this.count >= MAX_PARTICLES) break;
      const idx = this.count++;
      this.positions[idx * 3] = x;
      this.positions[idx * 3 + 1] = y;
      this.positions[idx * 3 + 2] = z;
      const c = opts.color || [1, 1, 1];
      this.colors[idx * 3] = c[0];
      this.colors[idx * 3 + 1] = c[1];
      this.colors[idx * 3 + 2] = c[2];
      const spd = opts.speed ?? 3;
      const dir = opts.dir || [0, 1, 0];
      this.vels[idx * 3] = dir[0] * spd + (Math.random() - 0.5) * spd * 0.6;
      this.vels[idx * 3 + 1] = dir[1] * spd + (Math.random() - 0.5) * spd * 0.6;
      this.vels[idx * 3 + 2] = dir[2] * spd + (Math.random() - 0.5) * spd * 0.6;
      const life = opts.life ?? 0.5 + Math.random() * 0.4;
      this.life[idx] = life;
      this.maxLife[idx] = life;
      this.sizes[idx] = opts.size ?? (0.08 + Math.random() * 0.1);
    }
    this._markDirty();
  }

  _markDirty() {
    this.geo.setDrawRange(0, this.count);
    this.geo.attributes.position.needsUpdate = true;
    this.geo.attributes.color.needsUpdate = true;
  }

  update(dt) {
    let alive = 0;
    const last = this.count;
    this.count = 0;
    for (let i = 0; i < last; i++) {
      if (this.life[i] <= 0) continue;
      this.life[i] -= dt;
      if (this.life[i] <= 0) continue;
      const i3 = i * 3;
      this.vels[i3 + 1] -= 9.8 * dt * 0.6;
      this.positions[i3] += this.vels[i3] * dt;
      this.positions[i3 + 1] += this.vels[i3 + 1] * dt;
      this.positions[i3 + 2] += this.vels[i3 + 2] * dt;
      const src = i, dst = alive;
      if (src !== dst) {
        this.positions[dst * 3] = this.positions[src * 3];
        this.positions[dst * 3 + 1] = this.positions[src * 3 + 1];
        this.positions[dst * 3 + 2] = this.positions[src * 3 + 2];
        this.colors[dst * 3] = this.colors[src * 3];
        this.colors[dst * 3 + 1] = this.colors[src * 3 + 1];
        this.colors[dst * 3 + 2] = this.colors[src * 3 + 2];
        this.vels[dst * 3] = this.vels[src * 3];
        this.vels[dst * 3 + 1] = this.vels[src * 3 + 1];
        this.vels[dst * 3 + 2] = this.vels[src * 3 + 2];
        this.life[dst] = this.life[src];
        this.maxLife[dst] = this.maxLife[src];
      }
      alive++;
    }
    this.count = alive;
    this.geo.setDrawRange(0, this.count);
    this.geo.attributes.position.needsUpdate = true;
    this.geo.attributes.color.needsUpdate = true;
  }

  setEnabled(v) {
    this.enabled = v;
    this.points.visible = v;
  }
}

export default ParticleSystem;