// Pause screen: resume, settings, save & exit, quit to menu.

import { el, button } from '../../core/UI.js';

export class PauseScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this._build();
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap' });
    wrap.append(el('h1', {}, 'Paused'));
    const col = el('div', { class: 'menu-nav' });
    col.append(
      button('Resume', () => this.ui.game?.setPaused(false), 'menu-btn big'),
      button('Settings', () => { this.ui.open('settings'); }, 'menu-btn big'),
      button('Save & Exit to Menu', () => { this.ui.game?.saveWorld(); this.ui.game?.returnToMenu(); }, 'menu-btn big'),
      button('Quit to Main Menu', () => this.ui.game?.returnToMenu(), 'menu-btn danger big')
    );
    wrap.append(col);
    r.append(wrap);
  }
}

export default PauseScreen;