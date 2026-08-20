// Main menu: PlayTree title screen with mode, settings, servers, store,
// season, friends and profile shortcuts.

import { el, button, clearChildren, panel } from '../../core/UI.js';
import { events } from '../../core/Events.js';

export class MainMenuScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen menu-screen hidden' });
    this._build();
    this._bind();
  }

  _build() {
    const r = this.el;
    const bg = el('div', { class: 'menu-bg' });
    for (let i = 0; i < 40; i++) {
      const px = (Math.random() * 100).toFixed(1) + '%';
      const py = (Math.random() * 100).toFixed(1) + '%';
      const s = (2 + Math.random() * 6).toFixed(1);
      bg.append(el('div', { class: 'star', style: { left: px, top: py, width: s + 'px', height: s + 'px' } }));
    }
    r.append(bg);

    const logo = el('div', { class: 'menu-logo' });
    logo.append(
      el('div', { class: 'logo-title' }, 'PLAYTREE'),
      el('div', { class: 'logo-sub' }, 'Chapter I · Season I — "The Heartwood Grove"')
    );
    r.append(logo);

    const nav = el('div', { class: 'menu-nav' });
    const items = [
      ['▶ Play', () => this.ui.open('modeselect')],
      ['Servers', () => { this.ui.open('social'); this.ui.screens.social.showTab('servers'); }],
      ['Store', () => { this.ui.open('store'); this.ui.screens.store.showTab('store'); }],
      ['Season Pass', () => { this.ui.open('store'); this.ui.screens.store.showTab('season'); }],
      ['Friends', () => { this.ui.open('social'); this.ui.screens.social.showTab('friends'); }],
      ['Profile', () => { this.ui.open('social'); this.ui.screens.social.showTab('profile'); }],
      ['Settings', () => this.ui.open('settings')],
    ];
    for (const [label, fn] of items) nav.append(button(label, fn, 'menu-btn big'));
    r.append(nav);

    this.savesRow = el('div', { class: 'saves-row' });
    r.append(this.savesRow);

    this.footer = el('div', { class: 'menu-footer muted' }, 'PlayTree · original sandbox · offline-first');
    r.append(this.footer);
  }

  _bind() {
    events.on('saves:changed', () => this.refresh());
    events.on('world:entered', () => this.el.classList.add('hidden'));
  }

  show() { this.refresh(); }

  refresh() {
    const g = this.ui.game;
    clearChildren(this.savesRow);
    if (!g) return;
    const saves = g.storage?.listWorlds?.() || [];
    if (!saves.length) return;
    this.savesRow.append(el('div', { class: 'saves-title muted' }, 'Recent worlds:'));
    for (const s of saves.slice(0, 4)) {
      this.savesRow.append(button(`${s.name} (Day ${s.day || 1})`, () => {
        this.ui.open('modeselect');
        this.ui.screens.modeselect.continueWorld(s);
      }, 'save-chip'));
    }
  }
}

export default MainMenuScreen;