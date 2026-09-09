// Player avatar: a simple modular humanoid built from boxes.
// Supports customization colors and simple emotes (stored poses).

import * as THREE from '../../vendor/three.module.js';

const DEFAULT_STYLE = {
  skin: 0xf0c8a0,
  shirt: 0x59c48f,
  pants: 0x3a4a66,
  hair: 0x4a3828,
  hat: null,          // null | 'cap' | 'crown' | 'hood' | 'beret'
  face: 0x000000,
  backpack: 0x8a6a3a,
};

export class Avatar {
  constructor(style = {}) {
    this.group = new THREE.Group();
    this.style = { ...DEFAULT_STYLE, ...style };
    this.emote = null;
    this.emoteTime = 0;
    this._parts = {};
    this._build();
  }

  _box(w, h, d, color, x = 0, y = 0, z = 0) {
    const geo = new THREE.BoxGeometry(w, h, d);
    const mat = new THREE.MeshLambertMaterial({ color });
    const m = new THREE.Mesh(geo, mat);
    m.position.set(x, y, z);
    return m;
  }

  _build() {
    const s = this.style;
    const g = this.group;
    const torso = this._box(0.5, 0.6, 0.28, s.shirt, 0, 0.95, 0);
    const head = this._box(0.42, 0.42, 0.42, s.skin, 0, 1.42, 0);
    const hat = s.hat ? this._hat(s.hat) : this._box(0.46, 0.1, 0.46, s.hair, 0, 1.65, 0);
    const hair = this._box(0.44, 0.12, 0.44, s.hair, 0, 1.64, 0);
    hair.visible = false;
    const face = this._box(0.42, 0.42, 0.42, s.face, 0, 1.42, -0.215);
    const armL = this._box(0.16, 0.55, 0.16, s.shirt, -0.34, 0.95, 0);
    const armR = this._box(0.16, 0.55, 0.16, s.shirt, 0.34, 0.95, 0);
    const legL = this._box(0.2, 0.6, 0.2, s.pants, -0.12, 0.32, 0);
    const legR = this._box(0.2, 0.6, 0.2, s.pants, 0.12, 0.32, 0);
    const back = this._box(0.36, 0.4, 0.14, s.backpack, 0, 1.0, -0.22);

    for (const p of [torso, head, hat, face, armL, armR, legL, legR, back]) g.add(p);

    this._parts = { torso, head, hat, face, armL, armR, legL, legR, back, hair };

    // Held item group (in front of right hand)
    this.heldItem = new THREE.Group();
    this.heldItem.position.set(0.34, 0.95, 0);
    g.add(this.heldItem);
  }

  _hat(type) {
    const s = this.style;
    if (type === 'crown') {
      const crown = new THREE.Group();
      const base = this._box(0.46, 0.08, 0.46, 0xffcf5c, 0, 1.62, 0);
      const spike1 = this._box(0.06, 0.12, 0.06, 0xffcf5c, -0.12, 1.72, 0);
      const spike2 = this._box(0.06, 0.12, 0.06, 0xffcf5c, 0, 1.74, 0);
      const spike3 = this._box(0.06, 0.12, 0.06, 0xffcf5c, 0.12, 1.72, 0);
      crown.add(base, spike1, spike2, spike3);
      return crown;
    }
    if (type === 'beret') {
      const beret = new THREE.Group();
      beret.add(this._box(0.48, 0.1, 0.48, 0xff7a59, 0, 1.66, 0));
      beret.add(this._box(0.3, 0.06, 0.3, 0xff7a59, 0, 1.72, 0.02));
      return beret;
    }
    // default cap
    const cap = new THREE.Group();
    cap.add(this._box(0.46, 0.1, 0.46, s.hair, 0, 1.66, 0));
    cap.add(this._box(0.46, 0.05, 0.2, s.hair, 0, 1.62, -0.18));
    return cap;
  }

  applyStyle(style) {
    this.style = { ...DEFAULT_STYLE, ...style };
    this._build();
  }

  setHeldItem(color, size = 0.18) {
    while (this.heldItem.children.length) this.heldItem.remove(this.heldItem.children[0]);
    if (!color) return;
    const box = this._box(size, size, size * 1.2, color, 0, 0, 0);
    this.heldItem.add(box);
  }

  playEmote(emote) {
    this.emote = emote || null;
    this.emoteTime = 0;
    // Spawn particles from emote definition
    if (emote && this.group?.parent) {
      const EMOTES_MAP = { wave: [1,1,1], dance: [1,0.84,0], point: [0.6,0.8,1], jump: [1,0.6,0.2], sit: [0.5,0.8,0.5], flex: [1,0.4,0.4], moonwalk: [0.8,0.8,1], spin: [1,1,0.5], robot: [0.5,0.5,0.5], thriller: [0.8,0.2,0.2], lean: [1,0.9,0.7], kick: [0.9,0.9,0.9] };
      const col = EMOTES_MAP[emote] || [1,1,1];
      const pos = this.group.position;
      this.group.parent.parent?.particles?.spawn?.(pos.x, pos.y + 1.5, pos.z, { count: 12, color: col, speed: 3, life: 0.8 });
    }
  }

  update(dt, moving, speedRatio) {
    const t = this.emoteTime += dt;
    const p = this._parts;
    const bob = moving ? Math.sin(t * 10) * 0.06 * speedRatio : 0;
    const lean = moving ? speedRatio * 0.12 : 0;

    // Legs swing
    p.legL.rotation.x = moving ? Math.sin(t * 10) * 0.6 * speedRatio : 0;
    p.legR.rotation.x = moving ? -Math.sin(t * 10) * 0.6 * speedRatio : 0;
    // Arms swing opposite
    p.armL.rotation.x = moving ? -Math.sin(t * 10) * 0.5 * speedRatio : 0;
    p.armR.rotation.x = moving ? Math.sin(t * 10) * 0.5 * speedRatio : 0;
    p.torso.position.y = 0.95 + Math.abs(bob);
    p.head.position.y = 1.42 + Math.abs(bob);

    if (this.emote === 'wave') {
      p.armR.rotation.x = -Math.sin(t * 4) * 1.2;
    } else if (this.emote === 'dance') {
      p.torso.rotation.y = Math.sin(t * 3) * 0.3;
      p.head.rotation.y = -Math.sin(t * 3) * 0.3;
      p.armL.rotation.z = Math.sin(t * 3) * 0.4;
      p.armR.rotation.z = -Math.sin(t * 3) * 0.4;
    } else if (this.emote === 'point') {
      p.armR.rotation.x = -1.4;
      p.armL.rotation.x = -0.3;
    } else if (this.emote === 'jump') {
      p.armL.rotation.x = -2.2;
      p.armR.rotation.x = -2.2;
      p.legL.rotation.x = -0.3;
      p.legR.rotation.x = 0.3;
    } else if (this.emote === 'moonwalk') {
      // Moonwalk: alternating leg slides, arm swings
      const s = Math.sin(t * 6);
      p.legL.position.z = s * 0.12;
      p.legR.position.z = -s * 0.12;
      p.legL.rotation.x = s * 0.5;
      p.legR.rotation.x = -s * 0.5;
      p.armL.rotation.x = -s * 0.7;
      p.armR.rotation.x = s * 0.7;
    } else if (this.emote === 'spin') {
      // Spin: arms out, rotate body
      p.armL.position.x = -0.4;
      p.armR.position.x = 0.4;
      p.armL.rotation.z = -0.8;
      p.armR.rotation.z = 0.8;
      p.torso.rotation.y += dt * 10;
    } else if (this.emote === 'robot') {
      // Robot: stiff angular movements
      const snap = Math.floor(t * 4) % 4;
      p.armL.rotation.x = snap === 0 ? -1.2 : snap === 1 ? 0 : snap === 2 ? -0.6 : 0;
      p.armR.rotation.x = snap === 0 ? 0 : snap === 1 ? -1.2 : snap === 2 ? 0 : -0.6;
      p.head.rotation.y = (snap % 2) * 0.4 - 0.2;
    } else if (this.emote === 'thriller') {
      // Thriller: zombie arms, stiff walk
      p.armL.rotation.x = -1.8;
      p.armR.rotation.x = -1.8;
      p.armL.position.z = Math.sin(t * 2) * 0.1;
      p.armR.position.z = -Math.sin(t * 2) * 0.1;
      p.legL.rotation.x = Math.sin(t * 3) * 0.4;
      p.legR.rotation.x = -Math.sin(t * 3) * 0.4;
    } else if (this.emote === 'lean') {
      // Anti-gravity lean
      p.torso.rotation.z = Math.sin(t * 2) * 0.2;
      p.armL.rotation.x = Math.sin(t * 3) * 0.5;
      p.armR.rotation.x = -Math.sin(t * 3) * 0.5;
    } else if (this.emote === 'kick') {
      // Alternating kicks
      const s = Math.sin(t * 5);
      p.legL.rotation.x = Math.max(0, s) * 1.4;
      p.legR.rotation.x = Math.max(0, -s) * 1.4;
      p.armL.rotation.x = -0.6;
      p.armR.rotation.x = -0.6;
    }
    // reset base rotations after emote
    if (!this.emote) {
      p.torso.rotation.y = 0;
      p.torso.rotation.z = 0;
      p.head.rotation.y = 0;
      p.head.rotation.z = 0;
      p.armL.rotation.z = 0;
      p.armR.rotation.z = 0;
      p.armL.position.x = -0.34;
      p.armR.position.x = 0.34;
      p.armL.position.z = 0;
      p.armR.position.z = 0;
      p.legL.position.z = 0;
      p.legR.position.z = 0;
    }
  }

  setVisible(v) { this.group.visible = v; }
}

export default Avatar;