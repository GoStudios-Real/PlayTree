# PlayTree — Content

All content is data-driven and lives under `src/content/`. Entries are plain objects
exported from pure modules (importable under Node for tests).

## Blocks — `src/content/blocks.js`

`getBlock(id)` returns a block definition: `{ id, name, solid, transparent, opaque,
blocklight, tool, drop, category, ... }`. Terrain and structures reference these ids
directly. Notable special blocks used by mini-games:

- 8  wood planks (course platforms), 36 barrier block, 40 stone, 43/46 shrine/sprout
  beacon blocks, 47 boom barrel, 48/17 special flora.

## Items — `src/content/items.js`

`getItem(id)` returns an item definition `{ id, name, icon, type, stack, ... }`.
Item ids (200/300+) are distinct from block ids. Player inventories hold `{ id,
count }` slots.

## Recipes — `src/content/recipes.js`

Crafting recipes reference item ids and are driven by `CraftingSystem`.

## Enemies — `src/content/enemies.js`

Enemy definitions (grub, shade, brute, ...) with stats and XP/season-XP rewards,
consumed by `EntityManager` and `CombatSystem`.

## NPCs — `src/content/npcs.js`

Villager NPC definitions used by the village and quest-givers.

## Quests — `src/content/quests.js`

Main story quests, side quests, and seasonal events. Each quest has objectives and
rewards `{ xp, seasonXp, coins, items }`. Driven by `QuestSystem`; seasonal events
are listed in `SEASON_EVENTS`.

## Story — `src/content/story.js`

Chapter narrative beats ("Chapter I: Season I" / "The Heartwood Grove").

## Achievements — `src/content/achievements.js`

Stat-threshold achievements with XP rewards, checked by `AchievementSystem`.

## Content conventions

- Content is additive: to add a block/item/enemy/quest, add a definition and, for
  blocks, a render case in the mesher if needed.
- Keep ids stable across sessions — worlds and saves reference them.
- Content files must not import Three.js (Node tests import them).