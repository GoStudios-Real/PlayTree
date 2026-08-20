// Block interaction: mining (hold-to-mine in survival, instant in creative)
// and placing. Handles the selection highlight, raycasting, tool tiers,
// durability, drops and sounds.

import * as THREE from '../../vendor/three.module.js';
import { raycastVoxels, clamp } from '../core/MathUtils.js';
import { events } from '../core/Events.js';
import { getBlock, isReplaceable, isSolid, maxBlockId } from '../content/blocks.js';
import { getItem, itemOfBlock } from '../content/items.js';

export class BlockInteraction {
  constructor(engine, world, player) {
    this.engine = engine;
    this.world = world;
    this.player = player;
    this.mode = 'survival'; // survival | creative
    this.highlight = null;
    this._highlightMesh = null;
    this._buildHighlight();
    this.mining = null; // { x,y,z, blockId, progress, hardness }
    this.lastBreak = 0;
    this.placeCooldown = 0;
  }

  setMode(mode) { this.mode = mode; }

  _buildHighlight() {
    const geo = new THREE.BoxGeometry(1.002, 1.002, 1.002);
    const edges = new THREE.EdgesGeometry(geo);
    this._highlightMesh = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 }));
    this._highlightMesh.visible = false;
    this.engine.scene.add(this._highlightMesh);
  }

  raycast(maxDist = null) {
    const eye = this.player.getEye();
    const dir = this.player.getAimDir();
    const dist = maxDist ?? this.player.reach;
    return raycastVoxels(eye.x, eye.y, eye.z, dir.x, dir.y, dir.z, dist, (x, y, z) => {
      const id = this.world.getBlock(x, y, z);
      return isSolid(getBlock(id));
    });
  }

  raycastEmpty(maxDist = null) {
    const eye = this.player.getEye();
    const dir = this.player.getAimDir();
    const dist = maxDist ?? this.player.reach;
    // find the first non-solid (air) block along the ray
    return raycastVoxels(eye.x, eye.y, eye.z, dir.x, dir.y, dir.z, dist, (x, y, z) => {
      const id = this.world.getBlock(x, y, z);
      return !isSolid(getBlock(id)) && getBlock(id).id !== 0;
    });
  }

  update(dt) {
    this.placeCooldown = Math.max(0, this.placeCooldown - dt);
    const hit = this.raycast();
    if (hit && hit.hit) {
      this._highlightMesh.visible = true;
      this._highlightMesh.position.set(hit.x + 0.5, hit.y + 0.5, hit.z + 0.5);
    } else {
      this._highlightMesh.visible = false;
    }
    this.hit = hit;

    // Mining progress
    if (this.mining) {
      const still = hit && hit.hit && hit.x === this.mining.x && hit.y === this.mining.y && hit.z === this.mining.z;
      if (!still) this.mining = null;
    }
  }

  // Returns damage dealt to block or true if broken.
  mine(dt) {
    const hit = this.raycast();
    if (!hit || !hit.hit) return false;
    const { x, y, z } = hit;
    const id = this.world.getBlock(x, y, z);
    const block = getBlock(id);
    if (!block.solid) return false;

    // Creative: instant
    if (this.mode === 'creative') {
      this._breakBlock(x, y, z, id);
      return true;
    }

    // Survival: hold-to-mine
    const tool = this._currentTool();
    const canMine = !block.tool || block.tool === 'any' || (tool && tool.kind === block.tool && tool.tier >= (block.tier || 1));
    if (!canMine) return false;

    const hardness = block.hardness;
    const speed = tool ? tool.speed * (tool.kind === block.tool ? 1 : 0.5) : 1;
    if (!this.mining) {
      this.mining = { x, y, z, id, progress: 0, hardness };
    }
    this.mining.progress += speed * dt;
    events.emit('block:mining', { x, y, z, progress: this.mining.progress / hardness, block });
    if (this.mining.progress >= hardness) {
      this._breakBlock(x, y, z, id);
      this.mining = null;
      return true;
    }
    return false;
  }

  _currentTool() {
    const s = this.player.inventory.selectedSlot;
    if (!s) return null;
    const item = getItem(s.id);
    if (item && item.tool) {
      const eff = item.tool.tier >= 3 ? 1.3 : item.tool.tier === 4 ? 1.6 : 1;
      return { ...item.tool, speed: item.tool.speed * eff };
    }
    return null;
  }

  _breakBlock(x, y, z, id) {
    const block = getBlock(id);
    // Drops
    const drops = this._rollDrops(block);
    const inv = this.player.inventory;
    let allCollected = true;
    for (const [did, count] of drops) {
      const rem = inv.add(did, count);
      if (rem > 0) allCollected = false;
    }
    // Durability
    const tool = getItem(this.player.inventory.selectedSlot?.id);
    if (tool && tool.tool) {
      this.player.inventory.damageSelected(1);
    }
    const ok = this.world.setBlockAndRemesh(x, y, z, 0);
    if (ok) {
      this.engine.audio?.breakBlock();
      const c = block.colors.all || block.colors.top || [0.6, 0.6, 0.6];
      this.engine.particles?.spawn(x + 0.5, y + 0.5, z + 0.5, { count: 14, color: c, speed: 4, life: 0.7 });
      events.emit('block:broken', { x, y, z, id, collected: allCollected });
    }
    this.lastBreak = performance.now();
  }

  _rollDrops(block) {
    const out = [];
    for (const d of block.drops) {
      if (Array.isArray(d)) {
        const [id, chance, qty] = d;
        if (Math.random() < (chance || 1)) out.push([id, qty || 1]);
      } else {
        out.push(d);
      }
    }
    return out;
  }

  place(selectedSlot = null) {
    if (this.placeCooldown > 0) return false;
    const slot = selectedSlot ?? this.player.inventory.selectedSlot;
    if (!slot) return false;
    const item = getItem(slot.id);
    if (!item || item.type !== 'block' || !item.blockId) return false;

    // Build position: the empty cell adjacent to the face we're looking at
    const eye = this.player.getEye();
    const dir = this.player.getAimDir();
    const dist = this.player.buildReach;
    // Use the "prev" empty cell from a solid raycast
    const hit = raycastVoxels(eye.x, eye.y, eye.z, dir.x, dir.y, dir.z, dist, (x, y, z) => {
      const id = this.world.getBlock(x, y, z);
      return isSolid(getBlock(id));
    });
    if (!hit.hit) return false;

    const bx = hit.prev.x, by = hit.prev.y, bz = hit.prev.z;
    const bid = this.world.getBlock(bx, by, bz);
    if (isSolid(getBlock(bid))) return false;
    // Can't place inside player
    const pbb = this.player.getAABB();
    if (pbb.intersects({ minX: bx, minY: by, minZ: bz, maxX: bx + 1, maxY: by + 1, maxZ: bz + 1 })) return false;
    if (by < 0 || by >= 96) return false;

    const blockId = item.blockId;
    const ok = this.world.setBlockAndRemesh(bx, by, bz, blockId);
    if (!ok) return false;

    // Consume
    if (this.mode !== 'creative') {
      this.player.inventory.removeFromSlot(this.player.inventory.selected, 1);
    }
    this.placeCooldown = 0.12;
    this.engine.audio?.place();
    const c = getBlock(blockId).colors.all || getBlock(blockId).colors.top || [0.6, 0.6, 0.6];
    this.engine.particles?.spawn(bx + 0.5, by + 0.5, bz + 0.5, { count: 6, color: c, speed: 2, life: 0.4 });
    events.emit('block:placed', { x: bx, y: by, z: bz, blockId });
    return true;
  }

  use(selectedSlot = null) {
    const slot = selectedSlot ?? this.player.inventory.selectedSlot;
    if (!slot) return;
    const item = getItem(slot.id);
    if (!item) return;
    if (item.type === 'block' && item.blockId) { this.place(slot); return; }
    events.emit('item:use', { player: this.player, item, slot });
  }

  destroy() {
    if (this._highlightMesh) {
      this.engine.scene.remove(this._highlightMesh);
      this._highlightMesh.geometry.dispose();
      this._highlightMesh.material.dispose();
    }
  }
}

export default BlockInteraction;