// Inventory screen: item grid + hotbar, crafting recipes, and loot-crate view.

import { el, button, tabs, clearChildren } from '../../core/UI.js';
import { itemIconUrl } from '../ItemIcon.js';
import { getItem } from '../../content/items.js';
import { HOTBAR_SIZE } from '../../player/Inventory.js';
import { events } from '../../core/Events.js';

export class InventoryScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this.crateContents = null;
    this._build();
    this._bind();
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap', style: { maxWidth: '720px' } });
    wrap.append(el('h1', {}, 'Inventory'));
    this.body = el('div', { class: 'inv-wrap' });
    this.grid = el('div', { class: 'inv-grid' });
    this.craftArea = el('div', { class: 'craft-area hidden' });
    this.body.append(this.grid, this.craftArea);
    wrap.append(this.body);
    const row = el('div', { class: 'row mt8', style: { justifyContent: 'space-between' } });
    row.append(
      button('Close', () => this.ui.toggleInventory(), 'ghost'),
      button('Crafting', () => this.showTab('crafting'), 'ghost')
    );
    wrap.append(row);
    r.append(wrap);
  }

  _bind() {
    events.on('inventory:changed', () => { if (!this.el.classList.contains('hidden')) this.refresh(); });
    events.on('item:crafted', () => { if (!this.el.classList.contains('hidden')) this.refresh(); });
  }

  show() { this.refresh(); }

  showTab(tab) {
    if (tab === 'crafting') {
      this.grid.classList.add('hidden');
      this.craftArea.classList.remove('hidden');
      this._renderCrafting();
    } else {
      this.grid.classList.remove('hidden');
      this.craftArea.classList.add('hidden');
    }
  }

  showCrate(contents) {
    this.crateContents = contents || [];
    this.grid.classList.remove('hidden');
    this.craftArea.classList.add('hidden');
    this.refresh();
  }

  refresh() {
    const g = this.ui.game;
    if (!g?.player) return;
    const inv = g.player.inventory;
    clearChildren(this.grid);

    // Hotbar row
    const hotRow = el('div', { class: 'inv-hotbar' });
    for (let i = 0; i < HOTBAR_SIZE; i++) this._slot(hotRow, inv, i);
    this.grid.append(el('div', { class: 'inv-label muted' }, 'Hotbar'), hotRow);

    // Backpack
    const pack = el('div', { class: 'inv-backpack' });
    for (let i = HOTBAR_SIZE; i < inv.size; i++) this._slot(pack, inv, i);
    this.grid.append(el('div', { class: 'inv-label muted' }, 'Backpack'), pack);

    // Crate loot if any
    if (this.crateContents && this.crateContents.length) {
      const crate = el('div', { class: 'inv-backpack' });
      for (const it of this.crateContents) this._crateSlot(crate, it);
      this.grid.append(el('div', { class: 'inv-label muted' }, 'Crate loot (click to take)'), crate);
    }
  }

  _slot(parent, inv, i) {
    const s = inv.slots[i];
    const cell = el('div', { class: 'inv-cell' });
    if (s) {
      const item = getItem(s.id);
      cell.append(el('img', { src: itemIconUrl(s.id), width: 36, height: 36, draggable: 'false' }));
      cell.append(el('span', { class: 'count' }, s.count > 1 ? s.count : ''));
      if (s.durability !== undefined && item?.tool) {
        cell.append(el('span', { class: 'dur', style: { width: `${(s.durability / item.tool.durability) * 100}%` } }));
      }
      if (item?.rarity) cell.classList.add(`rarity-${item.rarity}`);
      cell.title = `${item?.name || s.id}${s.count > 1 ? ' ×' + s.count : ''}`;
      cell.addEventListener('click', () => {
        if (i < HOTBAR_SIZE) inv.select(i);
      });
    }
    parent.append(cell);
  }

  _crateSlot(parent, it) {
    const cell = el('div', { class: 'inv-cell crate' });
    const item = getItem(it.id);
    cell.append(el('img', { src: itemIconUrl(it.id), width: 36, height: 36, draggable: 'false' }));
    cell.append(el('span', { class: 'count' }, it.count > 1 ? it.count : ''));
    cell.title = `${item?.name || it.id} — click to take`;
    cell.addEventListener('click', () => {
      const g = this.ui.game;
      g.player.inventory.add(it.id, it.count);
      g.engine.audio?.pickup();
      const idx = this.crateContents.indexOf(it);
      if (idx >= 0) this.crateContents.splice(idx, 1);
      this.refresh();
      if (!this.crateContents.length) this.crateContents = null;
    });
    parent.append(cell);
  }

  _renderCrafting() {
    const g = this.ui.game;
    clearChildren(this.craftArea);
    if (!g?.crafting) return;
    const recipes = g.crafting.availableRecipes('hand');
    this.craftArea.append(el('div', { class: 'inv-label muted' }, `Crafting (${recipes.length} recipes)`));
    const grid = el('div', { class: 'craft-grid' });
    for (const r of recipes) {
      const [outId, outCount] = r.output;
      const out = getItem(outId);
      const ok = g.crafting.canCraft(r.id);
      const card = el('div', { class: `craft-card${ok ? '' : ' locked'}` });
      const top = el('div', { class: 'craft-out' });
      top.append(el('img', { src: itemIconUrl(outId), width: 40, height: 40, draggable: 'false' }));
      top.append(el('span', { class: 'count' }, outCount > 1 ? '×' + outCount : ''));
      card.append(top, el('div', { class: 'craft-name' }, out?.name || outId));
      const ings = el('div', { class: 'craft-ings' });
      for (const [ingId, cnt] of r.ingredients) {
        const ing = getItem(ingId);
        const have = g.player.inventory.countOf(ingId);
        ings.append(el('span', { class: `ing${have >= cnt ? '' : ' missing'}` }, `${ing?.name || ingId} ${have}/${cnt}`));
      }
      card.append(ings);
      card.append(button(ok ? 'Craft' : 'Missing', () => g.crafting.craft(r.id), ok ? 'small primary' : 'small ghost'));
      grid.append(card);
    }
    this.craftArea.append(grid);
  }
}

export default InventoryScreen;