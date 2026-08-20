// Dev console (F3): evaluate expressions against the game, log messages.

import { el } from '../core/UI.js';

export class DevConsole {
  constructor(game) {
    this.game = game;
    this.open = false;
    this.root = el('div', { id: 'dev-console', class: 'hidden' });
    this.log = el('div', { class: 'dc-log' });
    this.input = el('input', { type: 'text', placeholder: 'Type a JS expression (game is `g`)...' });
    this.root.append(this.log, this.input);
    document.getElementById('app').append(this.root);
    this._bind();
  }

  _bind() {
    this.input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this._eval(this.input.value);
      if (e.key === 'Escape') this.toggle();
    });
  }

  _eval(code) {
    if (!code.trim()) return;
    this._print('> ' + code);
    this.input.value = '';
    try {
      // eslint-disable-next-line no-new-func
      const result = new Function('g', 'return (' + code + ');')(this.game);
      this._print(result === undefined ? 'undefined' : (typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)));
    } catch (err) {
      this._print('Error: ' + err.message);
    }
  }

  _print(text) {
    const line = el('div', {}, String(text));
    this.log.append(line);
    while (this.log.children.length > 200) this.log.removeChild(this.log.firstChild);
    this.log.scrollTop = this.log.scrollHeight;
  }

  logMsg(text) {
    if (this.open) this._print(text);
  }

  toggle() {
    this.open = !this.open;
    this.root.classList.toggle('hidden', !this.open);
    if (this.open) this.input.focus();
  }
}

export default DevConsole;