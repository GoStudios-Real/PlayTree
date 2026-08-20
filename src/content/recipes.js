// PlayTree crafting recipes (original designs).
// Recipe: { id, name, station: 'hand'|'table', ingredients: [[itemId, count],...], output: [itemId, count], category, unlockLevel }

export const RECIPES = [
  // ---- Hand crafting ----
  { id: 'r_planks', name: 'Planks', station: 'hand', ingredients: [[6, 1]], output: [8, 4], category: 'blocks' },
  { id: 'r_stick', name: 'Vine Rope', station: 'hand', ingredients: [[7, 2]], output: [400, 2], category: 'materials' },
  { id: 'r_fiber', name: 'Leaf Fiber', station: 'hand', ingredients: [[24, 2]], output: [401, 2], category: 'materials' },
  { id: 'r_craft_table', name: 'Assembly Table', station: 'hand', ingredients: [[8, 4]], output: [38, 1], category: 'blocks' },
  { id: 'r_crate', name: 'Sturdy Crate', station: 'hand', ingredients: [[8, 8]], output: [39, 1], category: 'blocks' },
  { id: 'r_torch', name: 'Torch', station: 'hand', ingredients: [[400, 1], [59, 1]], output: [22, 4], category: 'blocks' },
  { id: 'r_ladder', name: 'Ladder', station: 'hand', ingredients: [[8, 1]], output: [44, 3], category: 'blocks' },
  { id: 'r_pick_w', name: 'Wooden Pick', station: 'hand', ingredients: [[8, 3], [400, 2]], output: [101, 1], category: 'tools' },
  { id: 'r_axe_w', name: 'Wooden Axe', station: 'hand', ingredients: [[8, 3], [400, 2]], output: [111, 1], category: 'tools' },
  { id: 'r_shovel_w', name: 'Wooden Shovel', station: 'hand', ingredients: [[8, 1], [400, 2]], output: [121, 1], category: 'tools' },
  { id: 'r_pick_s', name: 'Stone Pick', station: 'hand', ingredients: [[9, 3], [400, 2]], output: [102, 1], category: 'tools' },
  { id: 'r_axe_s', name: 'Stone Axe', station: 'hand', ingredients: [[9, 3], [400, 2]], output: [112, 1], category: 'tools' },
  { id: 'r_shovel_s', name: 'Stone Shovel', station: 'hand', ingredients: [[9, 1], [400, 2]], output: [122, 1], category: 'tools' },
  { id: 'r_sword_w', name: 'Grove Sword', station: 'hand', ingredients: [[8, 2], [400, 1]], output: [131, 1], category: 'melee' },
  { id: 'r_sword_s', name: 'Stone Edge', station: 'hand', ingredients: [[9, 2], [400, 1]], output: [132, 1], category: 'melee' },
  { id: 'r_bow', name: 'Willow Bow', station: 'hand', ingredients: [[400, 3], [401, 3]], output: [207, 1], category: 'weapons' },
  { id: 'r_arrow', name: 'Arrow', station: 'hand', ingredients: [[400, 1], [402, 1]], output: [252, 4], category: 'ammo' },
  { id: 'r_berry_seed', name: 'Sprout Seed', station: 'hand', ingredients: [[300, 1]], output: [350, 2], category: 'farming' },
  { id: 'r_sunsteel_sword', name: 'Sunsteel Blade', station: 'table', ingredients: [[61, 2], [400, 1]], output: [133, 1], category: 'melee' },
  { id: 'r_pick_sunsteel', name: 'Sunsteel Pick', station: 'table', ingredients: [[61, 3], [400, 2]], output: [103, 1], category: 'tools' },
  { id: 'r_axe_sunsteel', name: 'Sunsteel Axe', station: 'table', ingredients: [[61, 3], [400, 2]], output: [113, 1], category: 'tools' },
  { id: 'r_shovel_sunsteel', name: 'Sunsteel Shovel', station: 'table', ingredients: [[61, 1], [400, 2]], output: [123, 1], category: 'tools' },
  { id: 'r_claymore', name: 'Shardlight Claymore', station: 'table', ingredients: [[62, 3], [61, 2], [400, 1]], output: [134, 1], category: 'melee' },
  { id: 'r_pick_shard', name: 'Shardlight Pick', station: 'table', ingredients: [[62, 3], [400, 2]], output: [104, 1], category: 'tools' },
  { id: 'r_glowstone', name: 'Glowstone', station: 'table', ingredients: [[36, 1], [62, 1]], output: [43, 1], category: 'blocks' },
  { id: 'r_glass', name: 'Crystal Glass', station: 'table', ingredients: [[4, 2], [59, 1]], output: [19, 4], category: 'blocks' },
  { id: 'r_shelf', name: 'Tome Shelf', station: 'table', ingredients: [[8, 6], [401, 3]], output: [37, 1], category: 'blocks' },
  { id: 'r_heal_vial', name: 'Healing Vial', station: 'table', ingredients: [[300, 3], [403, 1]], output: [302, 2], category: 'medicine' },
  { id: 'r_shield_flask', name: 'Shield Flask', station: 'table', ingredients: [[62, 1], [302, 1]], output: [303, 1], category: 'medicine' },
  { id: 'r_elixir', name: 'Everbloom Elixir', station: 'table', ingredients: [[63, 1], [62, 2], [302, 2]], output: [304, 1], category: 'medicine' },
  { id: 'r_heal_bandage', name: 'Roasted Sprout', station: 'hand', ingredients: [[26, 2], [59, 1]], output: [301, 1], category: 'food' },
  { id: 'r_iron_plate', name: 'Iron Plate', station: 'table', ingredients: [[60, 2]], output: [403, 1], category: 'materials' },
  { id: 'r_sunsteel_plate', name: 'Sunsteel Plate', station: 'table', ingredients: [[61, 2]], output: [404, 1], category: 'materials' },
  { id: 'r_barrel', name: 'Boom Barrel', station: 'table', ingredients: [[8, 2], [405, 1], [59, 2]], output: [47, 1], category: 'blocks' },
  { id: 'r_barrel_stave', name: 'Barrel Stave', station: 'table', ingredients: [[8, 2], [400, 1]], output: [405, 1], category: 'materials' },
  { id: 'r_pistol', name: 'Grove Pistol', station: 'table', ingredients: [[403, 2], [400, 1], [59, 1]], output: [200, 1], category: 'weapons', unlockLevel: 5 },
  { id: 'r_carbine', name: 'Longshot Carbine', station: 'table', ingredients: [[404, 2], [403, 1]], output: [203, 1], category: 'weapons', unlockLevel: 8 },
  { id: 'r_rounds', name: 'Bolt Rounds', station: 'table', ingredients: [[60, 1]], output: [250, 12], category: 'ammo' },
  { id: 'r_boom_launcher', name: 'Boom Barrel Launcher', station: 'table', ingredients: [[404, 3], [405, 2], [62, 1]], output: [206, 1], category: 'weapons', unlockLevel: 12 },
];

const byStation = { hand: [], table: [] };
for (const r of RECIPES) byStation[r.station].push(r);

export function recipesForStation(station) {
  return byStation[station] || [];
}

export function canCraft(recipe, inventory) {
  for (const [id, count] of recipe.ingredients) {
    if (inventory.countOf(id) < count) return false;
  }
  return true;
}

export function findRecipeForItem(itemId) {
  return RECIPES.find(r => r.output[0] === itemId) || null;
}

export default { RECIPES, recipesForStation, canCraft, findRecipeForItem };