// Player inventory: hotbar (9) + backpack (27) with item stacks.
// Pure data/logic — UI-agnostic so it can be unit tested.

import { getItem } from '../content/items.js';
import { events } from '../core/Events.js';

export const HOTBAR_SIZE = 9;
export const BACKPACK_ROWS = 3;
export const BACKPACK_COLS = 9;
export const BACKPACK_SIZE = BACKPACK_ROWS * BACKPACK_COLS;

export class Inventory {
  constructor(size = HOTBAR_SIZE + BACKPACK_SIZE) {
    this.size = size;
    this.slots = new Array(size).fill(null); // null or { id, count, durability }
    this.selected = 0;
  }

  clone() {
    const inv = new Inventory(this.size);
    inv.slots = this.slots.map(s => s ? { ...s } : null);
    inv.selected = this.selected;
    return inv;
  }

  get selectedSlot() { return this.slots[this.selected]; }

  // Add up to `count` of item id. Returns amount NOT added.
  add(id, count, durability) {
    const item = getItem(id);
    if (!item) return count;
    let remaining = count;
    for (let i = 0; i < this.size && remaining > 0; i++) {
      const s = this.slots[i];
      if (s && s.id === id && s.count < item.stack) {
        const can = item.stack - s.count;
        const take = Math.min(can, remaining);
        s.count += take;
        remaining -= take;
        if (durability !== undefined) s.durability = durability;
      }
    }
    for (let i = 0; i < this.size && remaining > 0; i++) {
      if (!this.slots[i]) {
        this.slots[i] = { id, count: Math.min(item.stack, remaining), durability: durability !== undefined ? durability : (item.tool ? item.tool.durability : undefined) };
        remaining -= this.slots[i].count;
      }
    }
    if (count !== remaining) events.emit('inventory:changed', this);
    return remaining;
  }

  countOf(id) {
    let n = 0;
    for (const s of this.slots) if (s && s.id === id) n += s.count;
    return n;
  }

  remove(id, count) {
    let remaining = count;
    for (let i = 0; i < this.size && remaining > 0; i++) {
      const s = this.slots[i];
      if (s && s.id === id) {
        const take = Math.min(s.count, remaining);
        s.count -= take;
        remaining -= take;
        if (s.count <= 0) this.slots[i] = null;
      }
    }
    events.emit('inventory:changed', this);
    return remaining; // not-removed amount
  }

  hasAny(items) {
    for (const [id, count] of items) if (this.countOf(id) < count) return false;
    return true;
  }

  consume(items) {
    for (const [id, count] of items) this.remove(id, count);
  }

  setSlot(i, slot) { this.slots[i] = slot; events.emit('inventory:changed', this); }

  select(i) {
    if (i >= 0 && i < HOTBAR_SIZE) {
      this.selected = i;
      events.emit('inventory:select', i, this.slots[i]);
    }
  }

  // Try merge/swap slots a & b (drag & drop). Returns new state.
  move(a, b) {
    if (a === b) return;
    const sa = this.slots[a], sb = this.slots[b];
    if (sa && sb && sa.id === sb.id && !getItem(sa.id).tool && !getItem(sa.id).weapon) {
      const item = getItem(sa.id);
      const room = item.stack - sb.count;
      if (room > 0) {
        const take = Math.min(room, sa.count);
        sb.count += take;
        sa.count -= take;
        if (sa.count <= 0) this.slots[a] = null;
        events.emit('inventory:changed', this);
        return;
      }
    }
    this.slots[a] = sb;
    this.slots[b] = sa;
    events.emit('inventory:changed', this);
  }

  damageSelected(amount = 1) {
    const s = this.slots[this.selected];
    if (!s) return;
    const item = getItem(s.id);
    if (!item.tool) return;
    s.durability = (s.durability ?? item.tool.durability) - amount;
    if (s.durability <= 0) {
      this.slots[this.selected] = null;
      events.emit('inventory:break', this.selected);
    }
    events.emit('inventory:changed', this);
  }

  removeFromSlot(i, count) {
    const s = this.slots[i];
    if (!s) return;
    s.count -= count;
    if (s.count <= 0) this.slots[i] = null;
    events.emit('inventory:changed', this);
  }

  toData() {
    return { slots: this.slots.map(s => s ? { id: s.id, count: s.count, durability: s.durability } : null), selected: this.selected };
  }

  static fromData(data) {
    const inv = new Inventory();
    if (data) {
      inv.slots = data.slots.map(s => s ? { ...s } : null);
      inv.selected = data.selected || 0;
    }
    return inv;
  }
}

export default Inventory;