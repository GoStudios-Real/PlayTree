// Crafting system: validates and performs recipes against the player inventory.

import { RECIPES, canCraft } from '../content/recipes.js';
import { getItem } from '../content/items.js';
import { events } from '../core/Events.js';

export class CraftingSystem {
  constructor(game) {
    this.game = game;
  }

  availableRecipes(station = 'hand') {
    const playerLevel = this.game.xp?.level || 1;
    return RECIPES.filter(r =>
      r.station === station && (!r.unlockLevel || playerLevel >= r.unlockLevel)
    );
  }

  canCraft(recipeId) {
    const r = RECIPES.find(x => x.id === recipeId);
    if (!r) return false;
    return canCraft(r, this.game.player.inventory);
  }

  craft(recipeId, opts = {}) {
    const r = RECIPES.find(x => x.id === recipeId);
    if (!r) return false;
    const inv = this.game.player.inventory;
    if (opts.station && r.station !== opts.station) return false;
    const levelOk = !r.unlockLevel || (this.game.xp?.level || 1) >= r.unlockLevel;
    if (!levelOk) return false;
    if (!canCraft(r, inv)) {
      this.game.ui?.toast('Missing ingredients', 2000);
      this.game.engine.audio?.error();
      return false;
    }
    inv.consume(r.ingredients);
    const [outId, outCount] = r.output;
    const rem = inv.add(outId, outCount);
    this.game.xp?.addStat?.('itemsCrafted', outCount);
    this.game.xp?.addXp?.(5);
    events.emit('item:crafted', { itemId: outId, count: outCount, recipe: r });
    this.game.ui?.toast(`Crafted: ${getItem(outId).name}`, 2500);
    this.game.engine.audio?.craft();
    return true;
  }
}

export default CraftingSystem;