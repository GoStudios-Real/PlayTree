// Mode select: pick Adventure, Survival, Creative, Battle Royale, Mini-Games,
// or join an existing world.

import { el, button, clearChildren } from '../../core/UI.js';
import { events } from '../../core/Events.js';

export class ModeSelectScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this._build();
    this.pendingWorld = null;
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap' });
    wrap.append(el('h1', {}, 'Choose a mode'));
    const grid = el('div', { class: 'mode-grid' });
    const modes = [
      { id: 'adventure', icon: '🏞️', name: 'Adventure', desc: 'The story of the Heartwood Grove. Build a village, save the grove.', color: '#59c48f' },
      { id: 'survival', icon: '⛺', name: 'Survival', desc: 'Gather, build, fight and thrive. Lose items on death.', color: '#f0b84f' },
      { id: 'creative', icon: '🎨', name: 'Creative', desc: 'Unlimited flight and blocks. Build anything.', color: '#7aa8ff' },
      { id: 'br', icon: '🏆', name: 'Battle Royale', desc: 'Drop into the storm. Last one standing wins.', color: '#a86bff' },
      { id: 'minigame', icon: '🎮', name: 'Mini-Games', desc: 'Canopy Dash, BoomBarrel Brawl, Capture the Sprout.', color: '#ff7a59' },
    ];
    for (const m of modes) {
      const card = el('div', { class: 'mode-card', onclick: () => this._start(m.id) });
      card.append(
        el('div', { class: 'mode-icon', style: { background: m.color } }, m.icon),
        el('div', { class: 'mode-name' }, m.name),
        el('div', { class: 'mode-desc muted' }, m.desc)
      );
      grid.append(card);
    }
    wrap.append(grid);
    const backRow = el('div', { class: 'row mt8', style: { justifyContent: 'space-between' } });
    backRow.append(button('← Back', () => this.ui.open('mainmenu'), 'ghost'));
    backRow.append(button('Join a World', () => this.ui.open('social'), 'ghost'));
    wrap.append(backRow);
    r.append(wrap);
  }

  _start(mode) {
    const g = this.ui.game;
    const worldName = this.pendingWorld ? null : `Grove ${g.storage?.newWorldName?.() || 'Home'}`;
    const opts = { name: worldName };
    if (this.pendingWorld) {
      opts.load = this.pendingWorld;
      this.pendingWorld = null;
    }
    events.emit('mode:selected', { mode, opts });
    g.setMode(mode, opts);
  }

  continueWorld(save) {
    this.pendingWorld = save.name;
    this.ui.open('modeselect');
  }
}

export default ModeSelectScreen;