// PlayTree item database. Item ids keep block ids 0-58, resource items 59+,
// tools 100+, weapons 200+, consumables 300+, materials 400+.
// Each item: id, name, type, stack, rarity, category, description, and
// type-specific data (blockId for placeables, tool fields, weapon id, heal, etc.)

import { BLOCKS, ITEM_BLOCKS } from './blocks.js';

export const RARITY = {
  COMMON: 'common',
  UNCOMMON: 'uncommon',
  RARE: 'rare',
  EPIC: 'epic',
  LEGENDARY: 'legendary',
  MYTHIC: 'mythic',
};

// Auto-build block placeable items from the block list.
const blockItems = [];
for (const b of BLOCKS) {
  if (b.id === 0) continue;
  blockItems.push({
    id: b.id, name: b.name, type: 'block', stack: 64, rarity: RARITY.COMMON,
    category: 'blocks', blockId: b.id, placeable: true,
    description: b.id === 47 ? 'KABOOM. Handle with care.' : `A solid ${b.name.toLowerCase()} block.`,
  });
}

const ITEMS = [
  ...blockItems,

  // Resources
  { id: 59, name: 'Coal', type: 'material', stack: 64, rarity: RARITY.COMMON, category: 'resources', description: 'Dark, dusty, burns forever.' },
  { id: 60, name: 'Iron Ingot', type: 'material', stack: 64, rarity: RARITY.COMMON, category: 'resources', description: 'Melted grove iron.' },
  { id: 61, name: 'Sunsteel Ingot', type: 'material', stack: 64, rarity: RARITY.RARE, category: 'resources', description: 'Shines like the noon sun.' },
  { id: 62, name: 'Shardlight Gem', type: 'material', stack: 64, rarity: RARITY.EPIC, category: 'resources', description: 'Pulses with cold blue light.' },
  { id: 63, name: 'Verdant Gem', type: 'material', stack: 64, rarity: RARITY.RARE, category: 'resources', description: 'Thrums with growing life.' },

  // Tools
  { id: 101, name: 'Wooden Pick', type: 'tool', stack: 1, rarity: RARITY.COMMON, category: 'tools', tool: { kind: 'pickaxe', tier: 1, speed: 2.2, durability: 60 }, damage: 2, description: 'Better than a rock.' },
  { id: 102, name: 'Stone Pick', type: 'tool', stack: 1, rarity: RARITY.UNCOMMON, category: 'tools', tool: { kind: 'pickaxe', tier: 2, speed: 3.4, durability: 130 }, damage: 3, description: 'Reliable grove stone.' },
  { id: 103, name: 'Sunsteel Pick', type: 'tool', stack: 1, rarity: RARITY.RARE, category: 'tools', tool: { kind: 'pickaxe', tier: 3, speed: 5.2, durability: 260 }, damage: 4, description: 'Warm in your hands.' },
  { id: 104, name: 'Shardlight Pick', type: 'tool', stack: 1, rarity: RARITY.EPIC, category: 'tools', tool: { kind: 'pickaxe', tier: 4, speed: 7.4, durability: 900 }, damage: 5, description: 'Sings against stone.' },
  { id: 111, name: 'Wooden Axe', type: 'tool', stack: 1, rarity: RARITY.COMMON, category: 'tools', tool: { kind: 'axe', tier: 1, speed: 2.4, durability: 60 }, damage: 3, description: 'For stubborn trees.' },
  { id: 112, name: 'Stone Axe', type: 'tool', stack: 1, rarity: RARITY.UNCOMMON, category: 'tools', tool: { kind: 'axe', tier: 2, speed: 3.6, durability: 130 }, damage: 4, description: 'Thunk. Thunk. Thunk.' },
  { id: 113, name: 'Sunsteel Axe', type: 'tool', stack: 1, rarity: RARITY.RARE, category: 'tools', tool: { kind: 'axe', tier: 3, speed: 5.4, durability: 260 }, damage: 5, description: 'Cuts clean and quick.' },
  { id: 121, name: 'Wooden Shovel', type: 'tool', stack: 1, rarity: RARITY.COMMON, category: 'tools', tool: { kind: 'shovel', tier: 1, speed: 2.2, durability: 60 }, damage: 1, description: 'Digs grove dirt.' },
  { id: 122, name: 'Stone Shovel', type: 'tool', stack: 1, rarity: RARITY.UNCOMMON, category: 'tools', tool: { kind: 'shovel', tier: 2, speed: 3.2, durability: 130 }, damage: 2, description: 'Digs deeper.' },
  { id: 123, name: 'Sunsteel Shovel', type: 'tool', stack: 1, rarity: RARITY.RARE, category: 'tools', tool: { kind: 'shovel', tier: 3, speed: 4.8, durability: 260 }, damage: 3, description: 'Scoops like butter.' },

  // Melee
  { id: 131, name: 'Grove Sword', type: 'weapon', stack: 1, rarity: RARITY.UNCOMMON, category: 'melee', weapon: { kind: 'melee', damage: 8, speed: 0.6, range: 3.2 }, damage: 8, description: 'A fair wooden blade.' },
  { id: 132, name: 'Stone Edge', type: 'weapon', stack: 1, rarity: RARITY.RARE, category: 'melee', weapon: { kind: 'melee', damage: 14, speed: 0.55, range: 3.2 }, damage: 14, description: 'Crude, brutal, effective.' },
  { id: 133, name: 'Sunsteel Blade', type: 'weapon', stack: 1, rarity: RARITY.EPIC, category: 'melee', weapon: { kind: 'melee', damage: 22, speed: 0.5, range: 3.4 }, damage: 22, description: 'The sword of a grove-keeper.' },
  { id: 134, name: 'Shardlight Claymore', type: 'weapon', stack: 1, rarity: RARITY.LEGENDARY, category: 'melee', weapon: { kind: 'melee', damage: 34, speed: 0.62, range: 3.8, knockback: 1.5 }, damage: 34, description: 'Cold light, final judgement.' },

  // Ranged (Battle Royale + adventure)
  { id: 200, name: 'Grove Pistol', type: 'weapon', stack: 1, rarity: RARITY.COMMON, category: 'ranged', weapon: { kind: 'gun', damage: 22, fireRate: 3, magSize: 12, reload: 1.6, range: 90, spread: 0.04, projectileSpeed: 60, auto: false, bloom: 1.2 }, description: 'Reliable sidearm of the grove.' },
  { id: 201, name: 'Sprout Blaster', type: 'weapon', stack: 1, rarity: RARITY.UNCOMMON, category: 'ranged', weapon: { kind: 'gun', damage: 12, fireRate: 10, magSize: 30, reload: 2.2, range: 70, spread: 0.09, projectileSpeed: 55, auto: true, bloom: 2.4 }, description: 'Sprays seeds at high speed.' },
  { id: 202, name: 'Rootclaw Shotgun', type: 'weapon', stack: 1, rarity: RARITY.RARE, category: 'ranged', weapon: { kind: 'shotgun', damage: 10, pellets: 6, fireRate: 1.1, magSize: 6, reload: 2.8, range: 34, spread: 0.12, projectileSpeed: 55, auto: false, bloom: 2.8 }, description: 'Close-range root riot.' },
  { id: 203, name: 'Longshot Carbine', type: 'weapon', stack: 1, rarity: RARITY.RARE, category: 'ranged', weapon: { kind: 'gun', damage: 34, fireRate: 3.4, magSize: 16, reload: 2.0, range: 200, spread: 0.02, projectileSpeed: 90, auto: false, bloom: 1.0 }, description: 'Drops canopy-born flyers.' },
  { id: 204, name: 'Thorn Sniper', type: 'weapon', stack: 1, rarity: RARITY.EPIC, category: 'ranged', weapon: { kind: 'sniper', damage: 95, fireRate: 0.7, magSize: 5, reload: 3.2, range: 320, spread: 0, projectileSpeed: 140, auto: false, zoom: 1.8, bloom: 0 }, description: 'One thorn, one target.' },
  { id: 205, name: 'Verdant SMG', type: 'weapon', stack: 1, rarity: RARITY.EPIC, category: 'ranged', weapon: { kind: 'gun', damage: 16, fireRate: 12, magSize: 40, reload: 2.4, range: 80, spread: 0.07, projectileSpeed: 60, auto: true, bloom: 2.0 }, description: 'Grown for crowd control.' },
  { id: 206, name: 'Boom Barrel Launcher', type: 'weapon', stack: 1, rarity: RARITY.LEGENDARY, category: 'ranged', weapon: { kind: 'rocket', damage: 100, splash: 6, fireRate: 0.7, magSize: 1, reload: 3.4, range: 120, projectileSpeed: 40, auto: false }, description: 'Some barrels want to fly.' },
  { id: 207, name: 'Willow Bow', type: 'weapon', stack: 1, rarity: RARITY.UNCOMMON, category: 'ranged', weapon: { kind: 'bow', damage: 40, drawTime: 0.7, fireRate: 1.5, range: 120, projectileSpeed: 55, auto: false, ammo: 'arrow' }, description: 'Whispers when it releases.' },
  { id: 208, name: 'Emerald Rifle', type: 'weapon', stack: 1, rarity: RARITY.LEGENDARY, category: 'ranged', weapon: { kind: 'gun', damage: 44, fireRate: 4.5, magSize: 24, reload: 1.8, range: 240, spread: 0.015, projectileSpeed: 100, auto: true, bloom: 1.2 }, description: "Grove royalty's favorite." },
  { id: 209, name: 'Frostpalm Launcher', type: 'weapon', stack: 1, rarity: RARITY.EPIC, category: 'ranged', weapon: { kind: 'rocket', damage: 60, splash: 5, freeze: true, fireRate: 0.9, magSize: 2, reload: 3.0, range: 130, projectileSpeed: 45, auto: false }, description: 'Winter, delivered.' },

  // Ammo
  { id: 250, name: 'Bolt Rounds', type: 'ammo', stack: 120, rarity: RARITY.COMMON, category: 'ammo', description: 'Standard grove ammunition.' },
  { id: 251, name: 'Shells', type: 'ammo', stack: 60, rarity: RARITY.COMMON, category: 'ammo', description: 'For the Rootclaw.' },
  { id: 252, name: 'Arrow', type: 'ammo', stack: 60, rarity: RARITY.COMMON, category: 'ammo', description: 'Feathered, fletched, faithful.' },
  { id: 253, name: 'Barrel', type: 'ammo', stack: 12, rarity: RARITY.UNCOMMON, category: 'ammo', description: 'The Booms demand tribute.' },
  { id: 254, name: 'Heavy Cells', type: 'ammo', stack: 60, rarity: RARITY.RARE, category: 'ammo', description: 'Charged with sunlight.' },

  // Consumables
  { id: 300, name: 'Sunkiss Berry', type: 'consumable', stack: 20, rarity: RARITY.COMMON, category: 'food', heal: 10, useTime: 0.8, description: 'Sweet and energizing.' },
  { id: 301, name: 'Roasted Sprout', type: 'consumable', stack: 20, rarity: RARITY.COMMON, category: 'food', heal: 30, useTime: 1.2, description: 'Warm, filling, grove-good.' },
  { id: 302, name: 'Healing Vial', type: 'consumable', stack: 10, rarity: RARITY.UNCOMMON, category: 'medicine', heal: 50, useTime: 1.5, description: 'Bottled sunlight.' },
  { id: 303, name: 'Shield Flask', type: 'consumable', stack: 10, rarity: RARITY.RARE, category: 'medicine', shield: 30, useTime: 1.5, description: 'Makes you hard as bark.' },
  { id: 304, name: 'Everbloom Elixir', type: 'consumable', stack: 5, rarity: RARITY.LEGENDARY, category: 'medicine', heal: 100, shield: 50, useTime: 2, description: "The grove's own miracle." },

  // Farming seeds
  { id: 350, name: 'Sprout Seed', type: 'seed', stack: 64, rarity: RARITY.COMMON, category: 'farming', plant: 26, description: 'Plant on tilled soil.' },
  { id: 351, name: 'Pumpkin Seed', type: 'seed', stack: 64, rarity: RARITY.UNCOMMON, category: 'farming', plant: 27, description: 'Plant on tilled soil.' },
  { id: 352, name: 'Glowcap Spore', type: 'seed', stack: 64, rarity: RARITY.RARE, category: 'farming', plant: 31, description: 'Grows in dark caves.' },

  // Materials (crafting)
  { id: 400, name: 'Vine Rope', type: 'material', stack: 64, rarity: RARITY.COMMON, category: 'crafting', description: 'Surprisingly strong.' },
  { id: 401, name: 'Leaf Fiber', type: 'material', stack: 64, rarity: RARITY.COMMON, category: 'crafting', description: 'Soft, pliable.' },
  { id: 402, name: 'Pebble Chunk', type: 'material', stack: 64, rarity: RARITY.COMMON, category: 'crafting', description: 'Smooth and throwable.' },
  { id: 403, name: 'Iron Plate', type: 'material', stack: 64, rarity: RARITY.UNCOMMON, category: 'crafting', description: 'Hammered flat.' },
  { id: 404, name: 'Sunsteel Plate', type: 'material', stack: 64, rarity: RARITY.RARE, category: 'crafting', description: 'Glows faintly at dusk.' },
  { id: 405, name: 'Barrel Stave', type: 'material', stack: 64, rarity: RARITY.UNCOMMON, category: 'crafting', description: 'The Booms call.' },

  // Miscellaneous
  { id: 500, name: 'Grove Coin', type: 'currency', stack: 999, rarity: RARITY.RARE, category: 'currency', description: 'Standard grove coinage.' },
];

const itemById = new Map(ITEMS.map(i => [i.id, i]));
const itemByName = new Map(ITEMS.map(i => [i.name.toLowerCase(), i]));

export function getItem(id) { return itemById.get(id) || null; }
export function itemOfBlock(blockId) {
  const i = itemById.get(blockId);
  return i && i.type === 'block' ? i : null;
}
export function blockForItem(item) { return item.blockId; }

export default { ITEMS, getItem, itemOfBlock, RARITY };