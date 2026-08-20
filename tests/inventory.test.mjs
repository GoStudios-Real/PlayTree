import { Inventory } from '../src/player/Inventory.js';
import { getItem } from '../src/content/items.js';
import { BLOCKS } from '../src/content/blocks.js';

export default function (assert, { approx }) {
  const inv = new Inventory();
  assert(inv.size === 36, 'inventory has 36 slots');

  // add & stack
  const rem = inv.add(1, 10); // block id 1
  assert(rem === 0, 'all 10 added');
  const s0 = inv.slots[0];
  assert(s0 && s0.id === 1 && s0.count === 10, 'stack stored');
  inv.add(1, 64);
  assert(inv.countOf(1) === 74, 'stacks combine');

  // stacking respects item.stack cap
  inv.add(1, 100);
  assert(inv.slots.filter(s => s && s.id === 1).reduce((n, s) => n + s.count, 0) === 174, 'total conserved');

  // remove
  const leftover = inv.remove(1, 200);
  assert(leftover === 26, 'remove returns leftover');
  assert(inv.countOf(1) === 0, 'removed all');

  // tools don't stack in a single slot, but each slot holds one
  const t = inv.add(101, 2); // wooden pickaxe stack=1
  assert(t === 0, 'two tools fit in two slots (leftover 0)');
  assert(inv.slots.filter(s => s && s.id === 101).length === 2, 'tools in separate slots');

  // durability on tools
  const pick = inv.slots.find(s => s && s.id === 101);
  assert(pick.durability > 0, 'tool has durability');

  // select & damage
  inv.select(inv.slots.findIndex(s => s && s.id === 101));
  const before = inv.slots[inv.selected].durability;
  inv.damageSelected(10);
  assert(inv.slots[inv.selected].durability === before - 10, 'damage reduces durability');

  // move/merge
  inv.slots.fill(null);
  inv.slots[0] = { id: 5, count: 5 };
  inv.slots[1] = { id: 5, count: 10 };
  inv.move(0, 1);
  assert(inv.slots[1].count === 15, 'move merges stacks');
  assert(inv.slots[0] === null, 'move empties source');

  // serialization roundtrip
  inv.add(300, 3);
  const data = inv.toData();
  const inv2 = Inventory.fromData(data);
  assert(inv2.countOf(300) === 3, 'roundtrip preserves items');
  assert(inv2.selected === inv.selected, 'roundtrip preserves selection');

  // content integrity: every block has an item or is listed
  const items = [];
  for (let id = 1; id < BLOCKS.length; id++) {
    if (getItem(id)) items.push(id);
  }
  assert(items.length > 20, 'many blocks have items');
}