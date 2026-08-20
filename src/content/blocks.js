// PlayTree block content database (Chapter I: Season I).
// Every block is an original PlayTree design with a procedural color identity.
// Fields:
//   id, name, solid, opaque, hardness, tool, drops, colors {top, side, bottom, all},
//   emitsLight, lightColor, sound, craftable, placeable, tint (biome tint), breakTime.

export const BLOCKS = [
  { id: 0,  name: 'Air',                    solid: false, opaque: false, hardness: 0, tool: 'none', drops: [], colors: { all: [0, 0, 0] } },

  { id: 1,  name: 'Grove Grass',            solid: true, opaque: true, hardness: 0.6, tool: 'shovel', drops: [2, 1, 1], colors: { top: [0.42, 0.72, 0.32], side: [0.56, 0.42, 0.28], bottom: [0.52, 0.38, 0.24] }, tint: true, sound: 'grass' },
  { id: 2,  name: 'Loam',                   solid: true, opaque: true, hardness: 0.5, tool: 'shovel', drops: [2, 1, 1], colors: { all: [0.52, 0.38, 0.24] }, sound: 'dirt' },
  { id: 3,  name: 'Stone',                  solid: true, opaque: true, hardness: 1.8, tool: 'pickaxe', drops: [3, 1, 1], colors: { all: [0.45, 0.47, 0.5] }, sound: 'stone' },
  { id: 4,  name: 'Sandsprout',             solid: true, opaque: true, hardness: 0.5, tool: 'shovel', drops: [4, 1, 1], colors: { all: [0.91, 0.85, 0.66] }, sound: 'sand' },
  { id: 5,  name: 'Water',                  solid: false, opaque: false, hardness: 0, tool: 'none', drops: [], colors: { all: [0.2, 0.45, 0.75] }, liquid: true, sound: 'water' },
  { id: 6,  name: 'Bloomwood Log',          solid: true, opaque: true, hardness: 2.0, tool: 'axe', drops: [6, 1, 1], colors: { side: [0.52, 0.4, 0.24], top: [0.6, 0.5, 0.32], bottom: [0.6, 0.5, 0.32] }, sound: 'wood' },
  { id: 7,  name: 'Bloomwood Leaves',       solid: true, opaque: true, hardness: 0.25, tool: 'any', drops: [[7, 0.3], [7, 1, 0.05]], colors: { all: [0.33, 0.58, 0.25] }, tint: true, sound: 'grass' },
  { id: 8,  name: 'Planks',                 solid: true, opaque: true, hardness: 1.6, tool: 'axe', drops: [8, 1, 1], colors: { all: [0.72, 0.6, 0.38] }, sound: 'wood', craftable: true },
  { id: 9,  name: 'Cobblestone',            solid: true, opaque: true, hardness: 2.0, tool: 'pickaxe', drops: [9, 1, 1], colors: { all: [0.42, 0.43, 0.45] }, sound: 'stone', craftable: true },
  { id: 10, name: 'Coal Ore',               solid: true, opaque: true, hardness: 2.6, tool: 'pickaxe', drops: [59, 1, 1], colors: { all: [0.4, 0.42, 0.44] }, ore: true, sound: 'stone' },
  { id: 11, name: 'Iron Ore',               solid: true, opaque: true, hardness: 3.2, tool: 'pickaxe', drops: [60, 1, 1], colors: { all: [0.6, 0.55, 0.55] }, ore: true, sound: 'stone' },
  { id: 12, name: 'Sunsteel Ore',           solid: true, opaque: true, hardness: 3.6, tool: 'pickaxe', drops: [61, 1, 1], colors: { all: [0.6, 0.5, 0.35] }, ore: true, sound: 'stone' },
  { id: 13, name: 'Shardlight Ore',         solid: true, opaque: true, hardness: 4.5, tool: 'pickaxe', drops: [62, 1, 1], colors: { all: [0.42, 0.55, 0.6] }, ore: true, sound: 'stone' },
  { id: 14, name: 'Verdant Ore',            solid: true, opaque: true, hardness: 4.0, tool: 'pickaxe', drops: [63, 1, 1], colors: { all: [0.42, 0.5, 0.42] }, ore: true, sound: 'stone' },
  { id: 15, name: 'Rootstone',              solid: true, opaque: true, hardness: -1, tool: 'none', drops: [], colors: { all: [0.2, 0.2, 0.22] }, sound: 'stone' },
  { id: 16, name: 'Pebble',                 solid: true, opaque: true, hardness: 0.7, tool: 'shovel', drops: [16, 1, 1], colors: { all: [0.5, 0.5, 0.5] }, sound: 'gravel' },
  { id: 17, name: 'Snowdrift',              solid: true, opaque: true, hardness: 0.5, tool: 'shovel', drops: [17, 1, 1], colors: { all: [0.95, 0.97, 1.0] }, sound: 'snow' },
  { id: 18, name: 'Crystal Ice',            solid: true, opaque: true, hardness: 0.8, tool: 'pickaxe', drops: [18, 1, 1], colors: { all: [0.62, 0.82, 0.95] }, sound: 'ice' },
  { id: 19, name: 'Crystal Glass',          solid: true, opaque: false, hardness: 0.4, tool: 'any', drops: [19, 1, 1], colors: { all: [0.8, 0.92, 1.0] }, transparent: true, sound: 'glass', craftable: true },
  { id: 20, name: 'Brick',                  solid: true, opaque: true, hardness: 2.2, tool: 'pickaxe', drops: [20, 1, 1], colors: { all: [0.66, 0.4, 0.3] }, sound: 'stone', craftable: true },
  { id: 21, name: 'Stone Brick',            solid: true, opaque: true, hardness: 2.4, tool: 'pickaxe', drops: [21, 1, 1], colors: { all: [0.5, 0.52, 0.55] }, sound: 'stone', craftable: true },
  { id: 22, name: 'Torch',                  solid: false, opaque: false, hardness: 0.1, tool: 'any', drops: [22, 1, 1], colors: { all: [0.95, 0.8, 0.4] }, emitsLight: 12, sound: 'wood', craftable: true },
  { id: 23, name: 'Dewpetal',               solid: false, opaque: false, hardness: 0.05, tool: 'any', drops: [23, 1, 1], colors: { all: [0.96, 0.6, 0.7] }, sound: 'grass' },
  { id: 24, name: 'Fronds',                 solid: false, opaque: false, hardness: 0.05, tool: 'any', drops: [24, 1, 1], colors: { all: [0.5, 0.75, 0.35] }, sound: 'grass' },
  { id: 25, name: 'Sapling',                solid: false, opaque: false, hardness: 0.05, tool: 'any', drops: [25, 1, 1], colors: { all: [0.35, 0.6, 0.28] }, sound: 'grass', plant: 'sapling' },
  { id: 26, name: 'Sprout (crop)',          solid: false, opaque: false, hardness: 0.05, tool: 'any', drops: [], colors: { all: [0.4, 0.7, 0.3] }, sound: 'grass', plant: 'crop' },
  { id: 27, name: 'Pumpkin',                solid: true, opaque: true, hardness: 1.0, tool: 'axe', drops: [27, 1, 1], colors: { top: [0.85, 0.6, 0.2], side: [0.9, 0.65, 0.25], bottom: [0.85, 0.6, 0.2] }, sound: 'wood' },
  { id: 28, name: 'Thornbloom',             solid: true, opaque: true, hardness: 0.7, tool: 'any', drops: [28, 1, 1], colors: { all: [0.3, 0.62, 0.3] }, sound: 'grass' },
  { id: 29, name: 'Sandstone',              solid: true, opaque: true, hardness: 1.4, tool: 'pickaxe', drops: [29, 1, 1], colors: { all: [0.85, 0.78, 0.6] }, sound: 'stone', craftable: true },
  { id: 30, name: 'Clay',                   solid: true, opaque: true, hardness: 0.8, tool: 'shovel', drops: [30, 1, 1], colors: { all: [0.7, 0.68, 0.65] }, sound: 'dirt' },
  { id: 31, name: 'Glowcap',                solid: false, opaque: false, hardness: 0.1, tool: 'any', drops: [31, 1, 1], colors: { all: [0.85, 0.3, 0.3] }, emitsLight: 6, sound: 'grass' },
  { id: 32, name: 'Embercap',               solid: false, opaque: false, hardness: 0.1, tool: 'any', drops: [32, 1, 1], colors: { all: [0.7, 0.5, 0.3] }, emitsLight: 4, sound: 'grass' },
  { id: 33, name: 'Trailpath',              solid: true, opaque: true, hardness: 0.6, tool: 'shovel', drops: [2, 1, 1], colors: { all: [0.6, 0.48, 0.3] }, sound: 'dirt' },
  { id: 34, name: 'Tilled Soil',            solid: true, opaque: true, hardness: 0.5, tool: 'shovel', drops: [2, 1, 1], colors: { all: [0.38, 0.28, 0.18] }, sound: 'dirt' },
  { id: 35, name: 'Obsidian',               solid: true, opaque: true, hardness: 8.0, tool: 'pickaxe', drops: [35, 1, 1], colors: { all: [0.16, 0.14, 0.2] }, sound: 'stone' },
  { id: 36, name: 'Glowstone',              solid: true, opaque: true, hardness: 0.5, tool: 'any', drops: [36, 1, 1], colors: { all: [0.95, 0.8, 0.5] }, emitsLight: 14, sound: 'stone' },
  { id: 37, name: 'Tome Shelf',             solid: true, opaque: true, hardness: 1.8, tool: 'axe', drops: [37, 1, 1], colors: { side: [0.5, 0.4, 0.25], top: [0.65, 0.55, 0.4], bottom: [0.55, 0.45, 0.3] }, sound: 'wood', craftable: true },
  { id: 38, name: 'Assembly Table',         solid: true, opaque: true, hardness: 2.0, tool: 'axe', drops: [38, 1, 1], colors: { side: [0.55, 0.42, 0.26], top: [0.4, 0.55, 0.35], bottom: [0.45, 0.36, 0.24] }, sound: 'wood', craftable: true },
  { id: 39, name: 'Sturdy Crate',           solid: true, opaque: true, hardness: 2.0, tool: 'axe', drops: [39, 1, 1], colors: { all: [0.55, 0.42, 0.26] }, sound: 'wood', craftable: true },
  { id: 40, name: 'Hearted Stone',          solid: true, opaque: true, hardness: 3.0, tool: 'pickaxe', drops: [40, 1, 1], colors: { all: [0.4, 0.42, 0.5] }, sound: 'stone', craftable: true },
  { id: 41, name: 'Sunsteel Block',         solid: true, opaque: true, hardness: 4.0, tool: 'pickaxe', drops: [41, 1, 1], colors: { all: [0.95, 0.75, 0.35] }, sound: 'stone', craftable: true },
  { id: 42, name: 'Verdant Block',          solid: true, opaque: true, hardness: 4.5, tool: 'pickaxe', drops: [42, 1, 1], colors: { all: [0.4, 0.9, 0.5] }, sound: 'stone', craftable: true },
  { id: 43, name: 'Shardlight Block',       solid: true, opaque: true, hardness: 5.0, tool: 'pickaxe', drops: [43, 1, 1], colors: { all: [0.4, 0.8, 1.0] }, emitsLight: 8, sound: 'stone', craftable: true },
  { id: 44, name: 'Ladder',                 solid: false, opaque: false, hardness: 0.4, tool: 'axe', drops: [44, 1, 1], colors: { all: [0.68, 0.55, 0.34] }, sound: 'wood', craftable: true, climbable: true },
  { id: 45, name: 'Soft Sand',              solid: true, opaque: true, hardness: 0.4, tool: 'shovel', drops: [4, 1, 1], colors: { all: [0.85, 0.78, 0.55] }, sound: 'sand' },
  { id: 46, name: 'Aurora Crystal',         solid: true, opaque: false, hardness: 3.0, tool: 'pickaxe', drops: [46, 1, 1], colors: { all: [0.55, 0.9, 1.0] }, emitsLight: 10, transparent: true, sound: 'glass' },
  { id: 47, name: 'Boom Barrel',            solid: true, opaque: true, hardness: 0.4, tool: 'any', drops: [], colors: { all: [0.65, 0.2, 0.18] }, explodes: true, sound: 'wood' },
  { id: 48, name: 'Whisper Fern',           solid: false, opaque: false, hardness: 0.05, tool: 'any', drops: [48, 1, 1], colors: { all: [0.3, 0.7, 0.4] }, sound: 'grass' },
  { id: 49, name: 'Glowbloom',              solid: false, opaque: false, hardness: 0.05, tool: 'any', drops: [49, 1, 1], colors: { all: [0.6, 0.9, 1.0] }, emitsLight: 7, sound: 'grass' },
  { id: 50, name: 'Crystal Cluster',        solid: false, opaque: false, hardness: 1.2, tool: 'pickaxe', drops: [50, 1, 1], colors: { all: [0.6, 0.4, 1.0] }, emitsLight: 6, sound: 'glass' },
];

// Item-type blocks (non-placeable resources/items) continue IDs from 60+.
export const ITEM_BLOCKS = [
  { id: 59, name: 'Coal',    stack: 64 },
  { id: 60, name: 'Iron Ingot', stack: 64 },
  { id: 61, name: 'Sunsteel Ingot', stack: 64 },
  { id: 62, name: 'Shardlight Gem', stack: 64 },
  { id: 63, name: 'Verdant Gem', stack: 64 },
];

export const blockById = new Map(BLOCKS.map(b => [b.id, b]));
export const blockByName = new Map(BLOCKS.map(b => [b.name.toLowerCase(), b]));

export function getBlock(id) { return blockById.get(id) || blockById.get(0); }
export function isSolid(id) { const b = getBlock(id); return b.solid; }
export function isOpaque(id) { const b = getBlock(id); return b.opaque; }
export function isLiquid(id) { const b = getBlock(id); return b.liquid; }
export function isReplaceable(id) { const b = getBlock(id); return !b.solid; }
export function maxBlockId() { return BLOCKS.length; }

export default { BLOCKS, ITEM_BLOCKS, getBlock, isSolid, isOpaque, isLiquid, isReplaceable, blockById, blockByName };