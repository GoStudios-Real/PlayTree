import { BLOCKS, getBlock, blockById } from '../src/content/blocks.js';
import { getItem } from '../src/content/items.js';
import { RECIPES } from '../src/content/recipes.js';
import { ENEMIES } from '../src/content/enemies.js';
import { QUESTS } from '../src/content/quests.js';
import { ACHIEVEMENTS } from '../src/content/achievements.js';

export default function (assert) {
  // Block ids unique
  const ids = BLOCKS.map(b => b.id);
  assert(new Set(ids).size === ids.length, 'block ids unique');
  assert(getBlock(0).name === 'Air' || blockById.has(0), 'block 0 is air');

  // Item ids unique
  const items = [];
  for (let i = 0; i < 1000; i++) if (getItem(i)) items.push(i);
  assert(new Set(items).size === items.length, 'item ids unique');
  assert(items.length > 50, 'item catalog substantial');

  // Recipes outputs valid
  for (const r of RECIPES) {
    assert(getItem(r.output[0]), `recipe ${r.id} output exists`);
  }

  // Enemy defs well-formed
  for (const [k, v] of Object.entries(ENEMIES)) {
    assert(v.hp > 0 && v.speed > 0 && v.damage > 0, `enemy ${k} has positive stats`);
    assert(Array.isArray(v.loot), `enemy ${k} has loot array`);
  }

  // Quest defs well-formed
  for (const q of QUESTS) {
    assert(q.id && q.title, 'quest has id + title');
    assert(q.objectives.length > 0, `quest ${q.id} has objectives`);
    for (const o of q.objectives) assert(o.count > 0, `quest ${q.id} objective count`);
  }

  // Achievement thresholds positive
  for (const a of ACHIEVEMENTS) {
    assert(a.id && a.threshold > 0, `achievement ${a.id} valid`);
  }
}