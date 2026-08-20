// Battle Royale zone ("The Storm"): a shrinking safe circle with damage outside.

import { events } from '../core/Events.js';
import { CONFIG } from '../core/Config.js';
import * as THREE from '../../vendor/three.module.js';

export class BRZone {
  constructor(game) {
    this.game = game;
    this.center = { x: 0, z: 0 };
    this.radius = CONFIG.br.zoneRadiusStart;
    this.targetCenter = { x: 0, z: 0 };
    this.targetRadius = CONFIG.br.zoneRadiusStart;
    this.state = 'waiting';   // waiting | shrinking | done
    this.phase = 0;
    this.phaseStart = 0;
    this.phaseDuration = CONFIG.br.zoneShrinkTime;
    this.delayTimer = CONFIG.br.zoneShrinkDelay;
    this._buildVisual();
    this._phases = [0.45, 0.3, 0.18, 0.08, 0.025].map(f => CONFIG.br.zoneRadiusStart * f);
  }

  _buildVisual() {
    const geo = new THREE.RingGeometry(this.radius, this.radius + 3, 48);
    this.mesh = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xa86bff, transparent: true, opacity: 0.45, side: THREE.DoubleSide, depthWrite: false }));
    this.mesh.rotation.x = -Math.PI / 2;
    this.mesh.position.y = 0.5;
    this.game.engine.scene.add(this.mesh);
    // Also a wall cylinder for edge
    this.wall = new THREE.Mesh(
      new THREE.CylinderGeometry(this.radius, this.radius, 200, 48, 1, true),
      new THREE.MeshBasicMaterial({ color: 0xa86bff, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false })
    );
    this.wall.position.y = 100;
    this.game.engine.scene.add(this.wall);
  }

  get zoneRadius() { return this.radius; }

  startMatch() {
    this.state = 'waiting';
    this.delayTimer = CONFIG.br.zoneShrinkDelay;
  }

  update(dt, playerPos) {
    if (this.state === 'done') return;

    if (this.state === 'waiting') {
      this.delayTimer -= dt;
      if (this.delayTimer <= 0) this._beginShrink();
      // Warn when shrink approaching
      if (this.delayTimer <= CONFIG.br.zoneWarnTime && this.delayTimer > 0 && Math.floor(this.delayTimer) !== Math.floor(this.delayTimer + dt)) {
        this.game.ui?.announce('The Storm is shrinking!', 'Move to the safe zone!', 2000);
        this.game.engine.audio?.zoneWarning();
      }
    } else if (this.state === 'shrinking') {
      const t = (performance.now() - this.phaseStart) / 1000;
      const k = Math.min(1, t / this.phaseDuration);
      const eased = k * k * (3 - 2 * k);
      this.radius = this.radius + (this.targetRadius - this.radius) * eased;
      this.center.x += (this.targetCenter.x - this.center.x) * eased;
      this.center.z += (this.targetCenter.z - this.center.z) * eased;
      if (k >= 1) {
        this.radius = this.targetRadius;
        this.state = 'waiting';
        this.delayTimer = CONFIG.br.zoneShrinkDelay;
        if (this.phase >= this._phases.length - 1) {
          this.state = 'done';
        } else {
          this.phase++;
          this._pickNextTarget();
        }
        events.emit('br:zone-settled', { center: this.center, radius: this.radius });
      }
    }

    // Damage outside zone
    const dx = (playerPos.x - this.center.x), dz = (playerPos.z - this.center.z);
    const dist = Math.hypot(dx, dz);
    if (dist > this.radius) {
      const dmg = (CONFIG.br.stormDamage + this.phase * CONFIG.br.stormDamageGrowth) * dt;
      if (this.game.player && !this.game.player.dead) {
        this.game.player.applyDamage(dmg, { source: { kind: 'zone' }, type: 'zone' });
      }
      this.game.ui?.zoneWarning(dist - this.radius);
    }

    // Update visuals
    this.mesh.scale.set(1, 1, 1);
    this._rebuildVisual();
    events.emit('br:zone', { center: this.center, radius: this.radius, phase: this.phase });
  }

  _rebuildVisual() {
    // cheap scale-based ring resizing
    const base = CONFIG.br.zoneRadiusStart;
    const s = this.radius / base;
    this.mesh.scale.set(s, s, 1);
    this.mesh.position.set(this.center.x, 0.5, this.center.z);
    const ws = this.radius / base;
    this.wall.scale.set(ws, 1, ws);
    this.wall.position.set(this.center.x, 100, this.center.z);
  }

  _beginShrink() {
    this.state = 'shrinking';
    this.phaseStart = performance.now();
    this.phaseDuration = CONFIG.br.zoneShrinkTime;
    this._pickNextTarget();
    events.emit('br:zone-shrinking', { targetCenter: this.targetCenter, targetRadius: this.targetRadius });
  }

  _pickNextTarget() {
    const frac = this._phases[this.phase] ?? 20;
    const ang = Math.random() * Math.PI * 2;
    const dist = this.radius * 0.3 * Math.random();
    this.targetRadius = frac;
    this.targetCenter = {
      x: this.center.x + Math.cos(ang) * dist,
      z: this.center.z + Math.sin(ang) * dist,
    };
  }

  inSafeZone(x, z) {
    return Math.hypot(x - this.center.x, z - this.center.z) <= this.radius;
  }

  dispose() {
    this.game.engine.scene.remove(this.mesh);
    this.game.engine.scene.remove(this.wall);
    this.mesh.geometry.dispose();
    this.wall.geometry.dispose();
  }
}

export default BRZone;