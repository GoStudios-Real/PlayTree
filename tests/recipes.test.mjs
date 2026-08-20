import { RECIPES, canCraft, recipesForStation, findRecipeForItem } from '../src/content/recipes.js';
import { getItem } from '../src/content/items.js';
import { Inventory } from '../src/player/Inventory.js';

export default function (assert) {
  assert(RECIPES.length > 30, 'recipe table populated');

  // Every recipe output and ingredient must reference a real item
  for (const r of RECIPES) {
    assert(getItem(r.output[0]), `recipe ${r.id} output ${r.output[0]} exists`);
    for (const [id, count] of r.ingredients) {
      assert(getItem(id), `recipe ${r.id} ingredient ${id} exists`);
      assert(count > 0, `recipe ${r.id} ingredient count positive`);
    }
    assert(r.station === 'hand' || r.station === 'table', `recipe ${r.id} has valid station`);
  }

  // canCraft true/false
  const inv = new Inventory();
  assert(!canCraft(RECIPES[0], inv), 'cannot craft with empty inventory');
  inv.add(6, 5); // log
  const planks = findRecipeForItem(8);
  assert(planks && canCraft(planks, inv), 'can craft planks from logs');

  // stations separated
  assert(recipesForStation('hand').length > 0, 'hand recipes exist');
  assert(recipesForStation('table').length > 0, 'table recipes exist');

  // All output ids map to block items or material items
  for (const r of recipesForStation('hand')) {
    const out = getItem(r.output[0]);
    assert(out && out.type, `output ${r.output[0]} has a type`);
  }
}