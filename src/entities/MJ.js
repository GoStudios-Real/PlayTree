// MJ entity: Michael Jackson – dance stage performer with signature moves.

import { events } from '../core/Events.js';
import { dist2d } from '../core/MathUtils.js';
import * as THREE from '../../vendor/three.module.js';

const MJ_COLOR   = 0x1a1a1a; // black jacket
const MJ_PANTS   = 0x111111; // black pants
const MJ_SOCK     = 0xffffff; // white socks
const MJ_SHOE     = 0x222222; // black shoes
const MJ_GLOVE    = 0xffffff; // single white glove
const MJ_HAT      = 0x111111; // black fedora
const MJ_SKIN     = 0xc68642; // skin tone
const MJ_SASH     = 0xffd700; // gold sash on jacket

export class MJ {
  constructor(world, x, y, z, opts = {}) {
    this.world = world;
    this.id = opts.id || ('mj_' + Math.floor(x) + '_' + Math.floor(z));
    this.kind = 'mj';
    this.type = 'mj';
    this.name = opts.name || 'MJ';
    this.pos = { x, y: y + 0.1, z };
    this.vel = { x: 0, y: 0, z: 0 };
    this.health = Infinity;
    this.dead = false;
    this.width = 0.7;
    this.height = 1.8;
    this.yaw = 0;
    this.group = new THREE.Group();
    this.interactable = true;
    this.interactDistance = 4;
    this._danceTimer = 0;
    this._danceMove = 0;
    this._dancing = false;
    this._particles = null;

    this._build();
    this.group.position.set(this.pos.x, this.pos.y, this.pos.z);
    this.world.engine.scene.add(this.group);
  }

  _build() {
    const g = new THREE.Group();

    // Torso (jacket)
    const torso = this._box(0.55, 0.65, 0.3, MJ_COLOR, 0, 0.95, 0);
    // Gold sash
    const sash = this._box(0.08, 0.65, 0.32, MJ_SASH, -0.15, 0.95, 0);
    // Head
    const head = this._box(0.42, 0.42, 0.42, MJ_SKIN, 0, 1.42, 0);
    // Eyes
    const eyeL = this._box(0.08, 0.06, 0.05, 0x222222, -0.1, 1.48, -0.22);
    const eyeR = this._box(0.08, 0.06, 0.05, 0x222222, 0.1, 1.48, -0.22);

    // Fedora hat
    const brim = this._box(0.56, 0.06, 0.56, MJ_HAT, 0, 1.7, 0);
    const crown = this._box(0.38, 0.22, 0.38, MJ_HAT, 0, 1.83, 0);
    const band = this._box(0.39, 0.04, 0.39, MJ_SASH, 0, 1.74, 0);

    // Left arm (normal)
    const armL = this._box(0.16, 0.55, 0.16, MJ_COLOR, -0.38, 0.95, 0);
    // Right arm (white glove)
    const armR = this._box(0.16, 0.55, 0.16, MJ_COLOR, 0.38, 0.95, 0);
    const gloveR = this._box(0.14, 0.14, 0.14, MJ_GLOVE, 0.38, 0.62, 0);

    // Legs (black pants)
    const legL = this._box(0.2, 0.5, 0.2, MJ_PANTS, -0.12, 0.38, 0);
    const legR = this._box(0.2, 0.5, 0.2, MJ_PANTS, 0.12, 0.38, 0);
    // White socks
    const sockL = this._box(0.18, 0.08, 0.18, MJ_SOCK, -0.12, 0.1, 0);
    const sockR = this._box(0.18, 0.08, 0.18, MJ_SOCK, 0.12, 0.1, 0);
    // Black shoes
    const shoeL = this._box(0.22, 0.1, 0.28, MJ_SHOE, -0.12, 0.03, -0.03);
    const shoeR = this._box(0.22, 0.1, 0.28, MJ_SHOE, 0.12, 0.03, -0.03);

    g.add(torso, sash, head, eyeL, eyeR,
      brim, crown, band,
      armL, armR, gloveR,
      legL, legR, sockL, sockR, shoeL, shoeR);

    this.group.add(g);
    this._limbs = { armL, armR, legL, legR, gloveR, torso, head };
    this._nameTag();
  }

  _box(w, h, d, color, x = 0, y = 0, z = 0) {
    const m = new THREE.Mesh(
      new THREE.BoxGeometry(w, h, d),
      new THREE.MeshLambertMaterial({ color })
    );
    m.position.set(x, y, z);
    return m;
  }

  _nameTag() {
    const canvas = document.createElement('canvas');
    canvas.width = 256; canvas.height = 48;
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 24px sans-serif';
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(0, 0, 256, 48);
    ctx.fillStyle = '#ffd700';
    ctx.textAlign = 'center';
    ctx.fillText(this.name, 128, 30);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(canvas), depthTest: false
    }));
    sprite.position.y = 2.3;
    sprite.scale.set(2.4, 0.5, 1);
    this.group.add(sprite);
  }

  interact(player) {
    events.emit('npc:interact', { npc: this, player, type: 'mj', def: { name: this.name } });
    this._startDance();
    this.facePlayer(player);
  }

  facePlayer(player) {
    this.yaw = Math.atan2(this.pos.x - player.pos.x, this.pos.z - player.pos.z);
    this.group.rotation.y = this.yaw;
  }

  _startDance() {
    this._dancing = true;
    this._danceTimer = 0;
    this._danceMove = 0;
    events.emit('mj:dance', { mj: this });
  }

  update(dt) {
    if (!this._dancing) return;
    this._danceTimer += dt;
    const t = this._danceTimer;
    const L = this._limbs;
    if (!L) return;

    // MJ signature moves cycle every ~3 seconds
    const phase = Math.floor(t / 3) % 4;

    if (phase === 0) {
      // Moonwalk: slide legs alternately, arms swing
      const s = Math.sin(t * 8);
      L.legL.position.z = s * 0.15;
      L.legR.position.z = -s * 0.15;
      L.legL.rotation.x = s * 0.4;
      L.legR.rotation.x = -s * 0.4;
      L.armL.rotation.x = -s * 0.6;
      L.armR.rotation.x = s * 0.6;
      L.gloveR.position.y = 0.62 + Math.abs(Math.sin(t * 4)) * 0.15;
    } else if (phase === 1) {
      // Spin: rotate body, arms out
      this.group.rotation.y += dt * 12;
      L.armL.position.x = -0.5;
      L.armR.position.x = 0.5;
      L.armL.rotation.z = -0.8;
      L.armR.rotation.z = 0.8;
      L.legL.rotation.x = Math.sin(t * 6) * 0.3;
      L.legR.rotation.x = -Math.sin(t * 6) * 0.3;
    } else if (phase === 2) {
      // Kick: alternating leg kicks
      const s = Math.sin(t * 6);
      L.legL.rotation.x = Math.max(0, s) * 1.2;
      L.legR.rotation.x = Math.max(0, -s) * 1.2;
      L.armL.rotation.x = -0.5;
      L.armR.rotation.x = -0.5;
      L.gloveR.position.y = 0.62 + Math.abs(s) * 0.2;
    } else {
      // Lean: anti-gravity lean
      L.torso.rotation.z = Math.sin(t * 2) * 0.15;
      L.armL.rotation.x = Math.sin(t * 3) * 0.4;
      L.armR.rotation.x = -Math.sin(t * 3) * 0.4;
      L.legL.rotation.x = 0;
      L.legR.rotation.x = 0;
    }

    // Spawn sparkles while dancing
    if (Math.random() < 0.15) {
      this.world.engine.particles?.spawn(
        this.pos.x + (Math.random() - 0.5) * 1.5,
        this.pos.y + 1.2 + Math.random() * 0.8,
        this.pos.z + (Math.random() - 0.5) * 1.5,
        { count: 3, color: [1, 0.84, 0], speed: 2, life: 0.6 }
      );
    }
  }

  dispose() {
    this.world.engine.scene.remove(this.group);
    this.group.traverse(o => { if (o.geometry) o.geometry.dispose(); });
  }
}

export default MJ;
