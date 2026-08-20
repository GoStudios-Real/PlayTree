// Touch controls: virtual joystick + action buttons for mobile/tablet play.

import { el } from '../core/UI.js';

export class TouchControls {
  constructor(ui) {
    this.ui = ui;
    this.active = false;
    this.root = el('div', { id: 'touch-controls', class: 'hidden' });
    this.joystick = el('div', { class: 'tc-joystick' });
    this.joystickKnob = el('div', { class: 'tc-knob' });
    this.joystick.append(this.joystickKnob);
    this.jumpBtn = el('button', { class: 'tc-btn tc-jump' }, '⤒');
    this.mineBtn = el('button', { class: 'tc-btn tc-mine' }, '⛏');
    this.placeBtn = el('button', { class: 'tc-btn tc-place' }, '▣');
    this.root.append(this.joystick, this.jumpBtn, this.mineBtn, this.placeBtn);
    document.getElementById('app').append(this.root);
    this._bind();
  }

  enable() { this.active = true; this.root.classList.remove('hidden'); }
  disable() { this.active = false; this.root.classList.add('hidden'); }

  _bind() {
    this.joy = { x: 0, y: 0, active: false, id: null };
    this.joystick.addEventListener('touchstart', (e) => {
      const t = e.changedTouches[0];
      this.joy.active = true;
      this.joy.id = t.identifier;
      this.joy.cx = t.clientX; this.joy.cy = t.clientY;
      this.joystick.style.left = (t.clientX - 55) + 'px';
      this.joystick.style.top = (t.clientY - 55) + 'px';
      this.joystick.style.transform = 'none';
      e.preventDefault();
    });
    const move = (e) => {
      if (!this.joy.active) return;
      const t = Array.from(e.changedTouches).find(x => x.identifier === this.joy.id);
      if (!t) return;
      let dx = t.clientX - this.joy.cx;
      let dy = t.clientY - this.joy.cy;
      const m = Math.hypot(dx, dy);
      const max = 45;
      if (m > max) { dx = dx / m * max; dy = dy / m * max; }
      this.joy.x = dx / max;
      this.joy.y = dy / max;
      this.joystickKnob.style.transform = `translate(${dx}px, ${dy}px)`;
    };
    const end = (e) => {
      if (!this.joy.active) return;
      const had = Array.from(e.changedTouches).some(x => x.identifier === this.joy.id);
      if (had) {
        this.joy.active = false;
        this.joy.x = 0; this.joy.y = 0;
        this.joystickKnob.style.transform = 'translate(0,0)';
      }
    };
    this.joystick.addEventListener('touchmove', move, { passive: false });
    this.joystick.addEventListener('touchend', end);
    this.joystick.addEventListener('touchcancel', end);
    document.addEventListener('touchmove', (e) => {
      if (this.joy.active) { e.preventDefault(); move(e); }
    }, { passive: false });

    this.jumpBtn.addEventListener('touchstart', (e) => { e.preventDefault(); this._act('jump', true); });
    this.jumpBtn.addEventListener('touchend', (e) => { e.preventDefault(); this._act('jump', false); });
    this.mineBtn.addEventListener('touchstart', (e) => { e.preventDefault(); this._act('mine', true); });
    this.mineBtn.addEventListener('touchend', (e) => { e.preventDefault(); this._act('mine', false); });
    this.placeBtn.addEventListener('touchstart', (e) => { e.preventDefault(); this._act('place', true); });
    this.placeBtn.addEventListener('touchend', (e) => { e.preventDefault(); this._act('place', false); });
  }

  _act(name, down) {
    const g = this.ui.game;
    if (!g?.input) return;
    g.input.setTouchButton(name, down);
  }

  update() {
    const g = this.ui.game;
    if (!g?.input) return;
    g.input.setTouchMove(this.joy.active ? { x: this.joy.x, y: -this.joy.y } : null);
  }
}

export default TouchControls;