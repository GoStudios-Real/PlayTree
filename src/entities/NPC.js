// Interactive NPCs: dialog, quest assignment, trading.

import { Avatar } from '../player/Avatar.js';
import { events } from '../core/Events.js';
import { NPCS } from '../content/npcs.js';
import { getItem } from '../content/items.js';
import * as THREE from '../../vendor/three.module.js';

export class NPC {
  constructor(world, type, x, y, z, opts = {}) {
    const def = NPCS[type] || NPCS.villager;
    this.world = world;
    this.id = opts.id || ('npc_' + type + '_' + Math.floor(x) + '_' + Math.floor(z));
    this.type = type;
    this.def = def;
    this.pos = { x, y, z };
    this.role = opts.role || def.role || 'Villager';
    this.group = null;
    this.avatar = new Avatar(opts.style || def.avatar);
    this.avatar.group.position.set(0, 0, 0);
    this.interactable = true;
    this.interactDistance = 3.2;
    this.quests = opts.quests || [];
    this.trades = opts.trades || this._defaultTrades();
    this.rotationY = opts.rotation || 0;
    this._marker = null;
    this._build();
  }

  _defaultTrades() {
    const base = [
      { give: 300, take: 1, price: 10 },   // buy berry for 10 coins? inverse: sell
    ];
    return base;
  }

  _build() {
    this.group = this.avatar.group;
    this.group.position.set(this.pos.x, this.pos.y, this.pos.z);
    this.group.rotation.y = this.rotationY;
    this.world.engine.scene.add(this.group);
    this._marker = this._makeMarker();
  }

  _makeMarker() {
    // Floating name tag
    const canvas = document.createElement('canvas');
    canvas.width = 256; canvas.height = 48;
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 24px sans-serif';
    ctx.fillStyle = 'rgba(0,0,0,0.5)';
    ctx.fillRect(0, 0, 256, 48);
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.fillText(this.def.name, 128, 30);
    const tex = new THREE.CanvasTexture(canvas);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false }));
    sprite.position.y = 2.1;
    sprite.scale.set(2.2, 0.45, 1);
    this.group.add(sprite);
    return sprite;
  }

  interact(player) {
    events.emit('npc:interact', { npc: this, player, type: this.type, def: this.def });
    this.facePlayer(player);
  }

  facePlayer(player) {
    const ang = Math.atan2(this.pos.x - player.pos.x, this.pos.z - player.pos.z);
    this.group.rotation.y = ang;
  }

  update(dt) {
    if (this.avatar) {
      this.avatar.update(dt, false, 0);
    }
  }

  dispose() {
    this.world.engine.scene.remove(this.group);
  }
}

export default NPC;