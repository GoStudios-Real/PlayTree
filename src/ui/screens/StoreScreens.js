// Store screens: shop, season pass, achievements, emotes.

import { el, button, tabs, clearChildren } from '../../core/UI.js';
import { COSMETICS, EMOTES } from '../../systems/StoreSystem.js';
import { ACHIEVEMENTS } from '../../content/achievements.js';
import { SEASON_TIERS, SEASON_REWARDS, SEASON_XP_PER_TIER } from '../../systems/XPProgress.js';
import { events } from '../../core/Events.js';

export class StoreScreens {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this.panes = {};
    this._build();
    this._bind();
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap', style: { maxWidth: '720px' } });
    wrap.append(el('h1', {}, 'PlayTree Store'));
    this.coinsChip = el('div', { class: 'coins-chip' });
    wrap.append(this.coinsChip);
    this.pane = el('div', { class: 'settings-pane' });
    const tabBar = el('div', { class: 'tabs' });
    const defs = [['store', 'Store'], ['season', 'Season Pass'], ['achievements', 'Achievements'], ['emotes', 'Emotes']];
    const btns = [];
    for (const [key, label] of defs) {
      const b = el('div', { class: 'tab', onclick: () => {
        btns.forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        this.showTab(key);
      } }, label);
      btns.push(b);
      tabBar.append(b);
    }
    wrap.append(tabBar, this.pane);
    wrap.append(el('div', { class: 'row mt8' }, button('Close', () => this.ui.closeAll(), 'ghost')));
    r.append(wrap);
    this._tabBtns = btns;
    this._bind();
  }

  _bind() {
    events.on('store:coins', () => this._updateCoins());
    events.on('store:purchased', () => { if (!this.el.classList.contains('hidden')) this.showTab('store'); });
    events.on('season:tier', () => { if (!this.el.classList.contains('hidden')) this.showTab('season'); });
  }

  _updateCoins() {
    this.coinsChip.textContent = `🪙 ${this.ui.game?.store?.getBalance?.() ?? 0} grove coins`;
  }

  show() {
    this._updateCoins();
    this._tabBtns[0].classList.add('active');
    this.showTab('store');
  }

  showTab(key) {
    this._updateCoins();
    this.panes[key] = this.panes[key] || this['_render' + key[0].toUpperCase() + key.slice(1)]();
    clearChildren(this.pane);
    this.pane.append(this.panes[key]);
  }

  _renderStore() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    box.append(el('div', { class: 'muted' }, `Balance: 🪙 ${g.store.getBalance()}`));
    const grid = el('div', { class: 'store-grid' });
    for (const c of COSMETICS) {
      const owned = g.store.owned.has(c.id);
      const card = el('div', { class: 'store-card' });
      card.append(el('div', { class: 'store-icon', style: { background: `#${c.color.toString(16).padStart(6, '0')}` } }, c.type === 'pet' ? '🐾' : c.type === 'glider' ? '🪂' : c.type === 'hat' ? '🎩' : '👕'));
      card.append(el('div', { class: 'store-name' }, c.name));
      card.append(el('div', { class: 'muted small' }, c.desc));
      if (owned) {
        card.append(el('div', { class: 'muted mt8' }, '✓ Owned'));
        card.append(button('Equip', () => g.store.setSelected(c.type, c.id), 'small primary'));
      } else {
        card.append(button(`Buy ${c.price} 🪙`, () => g.store.buy(c.id), 'small'));
      }
      grid.append(card);
    }
    box.append(grid);
    return box;
  }

  _renderSeason() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const xp = g.xp;
    box.append(el('div', { class: 'muted' }, `Season I · Tier ${xp.seasonTier}/${SEASON_TIERS} · ${xp.seasonXp}/${SEASON_XP_PER_TIER} XP`));
    const track = el('div', { class: 'season-track' });
    for (let i = 1; i <= SEASON_TIERS; i++) {
      const reward = SEASON_REWARDS[i - 1];
      const unlocked = i <= xp.seasonTier;
      const cell = el('div', { class: `season-cell${unlocked ? ' unlocked' : ''}` });
      cell.append(el('div', {}, unlocked ? '★' : '🔒'));
      cell.append(el('div', { class: 'muted small' }, `T${i}`));
      cell.append(el('div', { class: 'muted small' }, reward.cosmetic));
      track.append(cell);
    }
    box.append(track);
    box.append(el('div', { class: 'muted small' }, 'Earn Season XP from quests, kills, wins and crafting.'));
    return box;
  }

  _renderAchievements() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const grid = el('div', { class: 'ach-grid' });
    for (const a of ACHIEVEMENTS) {
      const unlocked = g.achievements.isUnlocked(a.id);
      const card = el('div', { class: `ach-card${unlocked ? ' unlocked' : ''}` });
      card.append(el('div', {}, unlocked ? '🏆' : '🔒'));
      card.append(el('div', { class: 'store-name' }, a.name));
      card.append(el('div', { class: 'muted small' }, a.desc));
      if (!unlocked) card.append(el('div', { class: 'muted small' }, `Goal: ${a.threshold} ${a.stat}`));
      grid.append(card);
    }
    box.append(grid);
    return box;
  }

  _renderEmotes() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const row = el('div', { class: 'emote-grid' });
    for (const e of EMOTES) {
      const owned = g.store.ownedEmotes.has(e.id);
      const cell = el('div', { class: `emote-cell${owned ? '' : ' locked'}` });
      cell.append(el('div', { class: 'emote-icon' }, e.icon));
      cell.append(el('div', { class: 'muted small' }, e.name));
      if (owned) {
        cell.addEventListener('click', () => g.player?.playEmote?.(e.id));
      } else {
        cell.append(button('Unlock', () => g.store.unlockEmote(e.id), 'small ghost'));
      }
      row.append(cell);
    }
    box.append(row);
    box.append(el('div', { class: 'muted small mt8' }, 'Press B in-game to open the emote wheel.'));
    return box;
  }
}

export default StoreScreens;