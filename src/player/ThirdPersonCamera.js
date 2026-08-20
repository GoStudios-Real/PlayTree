// Third-person orbit camera with smooth follow and wall occlusion.

import * as THREE from '../../vendor/three.module.js';
import { lerp, raycastVoxels } from '../core/MathUtils.js';
import { CONFIG } from '../core/Config.js';
import { getBlock } from '../content/blocks.js';

const DEFAULT_DIST = 4.6;
const MIN_DIST = 1.2;
const MAX_DIST = 8;

export class ThirdPersonCamera {
  constructor(engine) {
    this.engine = engine;
    this.camera = engine.camera;
    this.distance = DEFAULT_DIST;
    this.target = null;
    this.smoothing = 8;
    this.pitch = 0.35;
    this.offsetY = 1.55;
    this.shake = 0;
    this.zoom = 1;
    this._cur = { x: 0, y: 0, z: 0 };
    this._pos = new THREE.Vector3();
    this._dir = new THREE.Vector3();
  }

  setTarget(player) {
    this.target = player;
    this.pitch = player.pitch;
    this._cur.x = player.pos.x;
    this._cur.y = player.pos.y;
    this._cur.z = player.pos.z;
  }

  look(dx, dy, settings) {
    const sens = CONFIG.input.mouseSensitivity[settings?.sensitivity || 'medium'] || 2.0;
    const invY = settings?.invertY ? 1 : -1;
    this.target.yaw -= dx * sens * 0.012;
    this.target.pitch += dy * sens * 0.012 * invY;
    const lim = Math.PI / 2 - 0.01;
    this.target.pitch = Math.max(-lim, Math.min(lim, this.target.pitch));
  }

  update(dt, player) {
    const t = player;
    const eyeY = t.pos.y + 1.35;
    const cy = Math.cos(t.pitch), sy = Math.sin(t.pitch);
    const cx = Math.cos(t.yaw), sx = Math.sin(t.yaw);

    // Desired camera position behind player
    let dx = sx * cy, dy = -sy, dz = cx * cy;
    let dist = this.distance * (this.zoom || 1);

    // Wall occlusion: raycast from player eye toward camera
    if (player.world) {
      const hit = raycastVoxels(t.pos.x, eyeY, t.pos.z, dx, dy, dz, dist, (x, y, z) => {
        const id = player.world.getBlock(x, y, z);
        return getBlock(id).solid;
      });
      if (hit.hit) dist = Math.max(MIN_DIST, hit.t - 0.25);
    }

    const desired = {
      x: t.pos.x + dx * dist,
      y: eyeY + dy * dist,
      z: t.pos.z + dz * dist,
    };

    // Smooth follow
    const k = Math.min(1, this.smoothing * dt);
    this._cur.x = lerp(this._cur.x, desired.x, k);
    this._cur.y = lerp(this._cur.y, desired.y, k);
    this._cur.z = lerp(this._cur.z, desired.z, k);

    // Camera shake
    let sxOff = 0, syOff = 0;
    if (this.shake > 0) {
      const s = this.shake * 0.08;
      sxOff = (Math.random() - 0.5) * s;
      syOff = (Math.random() - 0.5) * s;
      this.shake = Math.max(0, this.shake - dt * 3);
    }

    this.camera.position.set(this._cur.x + sxOff, this._cur.y + syOff, this._cur.z);
    this.camera.lookAt(t.pos.x, t.pos.y + t.eyeHeight * 0.85, t.pos.z);
  }

  zoomIn() { this.zoom = Math.max(0.6, this.zoom - 0.15); }
  zoomOut() { this.zoom = Math.min(1.6, this.zoom + 0.15); }
  addShake(amount) { this.shake = Math.min(1, this.shake + amount); }
}

export default ThirdPersonCamera;