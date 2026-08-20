// Emote wheel: radial picker bound to key B.

import { el, clearChildren } from '../core/UI.js';
import { EMOTES } from '../systems/StoreSystem.js';

export class EmoteWheel {
  constructor(ui) {
    this.ui = ui;
    this.root = el('div', { id: 'emote-wheel' });
    this.wrap = el('div', { class: 'ew-wrap' });
    this.root.append(this.wrap);
    document.getElementById('app').append(this.root);
  }

  open() {
    const g = this.ui.game;
    const owned = g.store.ownedEmotes || new Set(['wave', 'dance']);
    clearChildren(this.wrap);
    for (const e of EMOTES) {
      const has = owned.has(e.id);
      const cell = el('div', { class: `ew-cell${has ? '' : ' locked'}`, onclick: () => {
        if (has) {
          g.player?.playEmote?.(e.id);
          g.net?.sendEmote?.(e.id);
          this.close();
        }
      } });
      cell.append(el('div', { class: 'ew-icon' }, e.icon));
      cell.append(el('div', { class: 'muted small' }, e.name));
      this.wrap.append(cell);
    }
    this.root.classList.remove('hidden');
    g.setPaused(true);
  }

  close() {
    this.root.classList.add('hidden');
    if (this.ui.current === null) this.ui.game?.setPaused(false);
  }

  isOpen() { return !this.root.classList.contains('hidden'); }
}

export default EmoteWheel;