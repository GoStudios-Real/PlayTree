// Touch controls: virtual joystick + action buttons + look drag for phones.
// Buttons emit semantic input names (attack/use/jump) so Game.handleInput
// works exactly like desktop mouse/keyboard.

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
    this.attackBtn = el('button', { class: 'tc-btn tc-mine' }, '⚔');
    this.useBtn = el('button', { class: 'tc-btn tc-place' }, '▣');
    this.menuBtn = el('button', { class: 'tc-btn tc-menu' }, '☰');
    this.invBtn = el('button', { class: 'tc-btn tc-inv' }, '🎒');
    this.root.append(this.joystick, this.jumpBtn, this.attackBtn, this.useBtn, this.menuBtn, this.invBtn);
    document.getElementById('app').append(this.root);
    this._bind();
  }

  enable() {
    this.active = true;
    this.root.classList.remove('hidden');
    this.root.classList.add('visible');
  }

  disable() {
    this.active = false;
    this.root.classList.remove('visible');
    this.root.classList.add('hidden');
    const input = this._input();
    if (input) { input.setTouchMove(0, 0); input.setTouchLook(0, 0); }
  }

  _input() {
    return this.ui?.game?.engine?.input || null;
  }

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

    // Action buttons → semantic input names.
    const press = (name) => (e) => { e.preventDefault(); this._act(name, true); };
    const release = (name) => (e) => { e.preventDefault(); this._act(name, false); };
    this.jumpBtn.addEventListener('touchstart', press('jump'));
    this.jumpBtn.addEventListener('touchend', release('jump'));
    this.attackBtn.addEventListener('touchstart', press('attack'));
    this.attackBtn.addEventListener('touchend', release('attack'));
    this.useBtn.addEventListener('touchstart', press('use'));
    this.useBtn.addEventListener('touchend', release('use'));

    // Pause + inventory shortcuts (no keyboard on phones).
    this.menuBtn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const g = this.ui.game;
      if (!g) return;
      if (g.state === 'playing') { g.pause(); this.ui.open('pause'); }
      else if (g.state === 'paused') { this.ui.closeAll(); g.resume(); }
    });
    this.invBtn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const g = this.ui.game;
      if (!g || g.state !== 'playing') return;
      g.toggleInventory();
    });

    // Look drag: anywhere on the game area except the touch UI itself.
    const app = document.getElementById('app');
    const isUiTarget = (t) =>
      this.root.contains(t) || t.closest?.('#chat-input, input, textarea, .screen, .settings-pane');
    let look = null;
    app.addEventListener('touchstart', (e) => {
      if (this.ui.game?.state !== 'playing') return;
      const t = e.changedTouches[0];
      if (!t || isUiTarget(t.target)) return;
      look = { id: t.identifier, x: t.clientX, y: t.clientY };
    }, { passive: true });
    app.addEventListener('touchmove', (e) => {
      if (!look || this.ui.game?.state !== 'playing') return;
      const t = Array.from(e.changedTouches).find(x => x.identifier === look.id);
      if (!t) return;
      const dx = t.clientX - look.x;
      const dy = t.clientY - look.y;
      look.x = t.clientX;
      look.y = t.clientY;
      this._input()?.setTouchLook(dx, dy);
      e.preventDefault();
    }, { passive: false });
    const lookEnd = (e) => {
      if (!look) return;
      if (Array.from(e.changedTouches).some(x => x.identifier === look.id)) {
        look = null;
        this._input()?.setTouchLook(0, 0);
      }
    };
    app.addEventListener('touchend', lookEnd);
    app.addEventListener('touchcancel', lookEnd);
  }

  _act(name, down) {
    this._input()?.setTouchButton(name, down);
  }

  update() {
    const input = this._input();
    if (!input) return;
    const mag = this.joy.active ? Math.hypot(this.joy.x, this.joy.y) : 0;
    // Auto-sprint when the stick is pushed nearly all the way.
    input.setTouchButton('sprint', mag > 0.85);
    input.setTouchMove(this.joy.active ? this.joy.x : 0, this.joy.active ? -this.joy.y : 0);
  }
}

export default TouchControls;
