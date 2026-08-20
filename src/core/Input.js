// Unified input: keyboard, mouse, gamepad, touch. Exposes semantic actions.
// Actions: forward/back/left/right, jump, sprint, crouch, attack, use, build,
// rotate (build rotation), inventory, map, quests, chat, pause, emote,
// hotbar1..9, flyUp/flyDown (creative), tab-menu.

import { events } from './Events.js';
import { Storage } from './Storage.js';
import { CONFIG } from './Config.js';

const BINDINGS_KEY = 'pt.bindings.v1';

export const DEFAULT_BINDINGS = {
  forward: ['KeyW', 'ArrowUp'],
  back: ['KeyS', 'ArrowDown'],
  left: ['KeyA', 'ArrowLeft'],
  right: ['KeyD', 'ArrowRight'],
  jump: ['Space', 'KeyZ'],
  sprint: ['ShiftLeft', 'ShiftRight'],
  crouch: ['ControlLeft', 'KeyC'],
  attack: ['Mouse0'],
  use: ['Mouse2'],
  build: ['KeyF'],
  rotate: ['KeyR'],
  inventory: ['KeyE', 'Tab'],
  map: ['KeyM'],
  quests: ['KeyL'],
  chat: ['Enter'],
  pause: ['Escape'],
  emote: ['KeyB'],
  flyUp: ['Space'],
  flyDown: ['ShiftLeft'],
  flyToggle: ['KeyV'],
  hotbar1: ['Digit1'], hotbar2: ['Digit2'], hotbar3: ['Digit3'],
  hotbar4: ['Digit4'], hotbar5: ['Digit5'], hotbar6: ['Digit6'],
  hotbar7: ['Digit7'], hotbar8: ['Digit8'], hotbar9: ['Digit9'],
  screenshot: ['F2'],
  devConsole: ['F3'],
  debug: ['F4'],
  drop: ['KeyQ'],
};

export const GAMEPAD_BUTTONS = {
  a: 0, b: 1, x: 2, y: 3,
  lb: 4, rb: 5, lt: 6, rt: 7,
  back: 8, start: 9, ls: 10, rs: 11,
  up: 12, down: 13, left: 14, right: 15,
  home: 16,
};

export const GAMEPAD_AXES = { lx: 0, ly: 1, rx: 2, ry: 3 };

export class Input {
  constructor(engine) {
    this.engine = engine;
    this.bindings = { ...DEFAULT_BINDINGS, ...(Storage.get(BINDINGS_KEY) || {}) };
    this.keys = new Map();
    this.mouse = { x: 0, y: 0, dx: 0, dy: 0, down: new Set() };
    this.gamepad = { index: -1, buttons: new Map(), axes: [0, 0, 0, 0] };
    this.touch = { move: null, look: null, lookActive: false, buttons: new Set() };
    this.pointerLocked = false;
    this._wheel = 0;
    this._pressed = new Set();
    this._released = new Set();
    this._attached = false;
    this._sensitivity = CONFIG.input.mouseSensitivity.medium;
    this._bind();
  }

  _bind() {
    if (this._attached) return;
    this._attached = true;
    window.addEventListener('keydown', (e) => this._keyDown(e), { passive: false });
    window.addEventListener('keyup', (e) => this._keyUp(e), { passive: false });
    window.addEventListener('mousemove', (e) => this._mouseMove(e), { passive: false });
    window.addEventListener('mousedown', (e) => this._mouseDown(e), { passive: false });
    window.addEventListener('mouseup', (e) => this._mouseUp(e), { passive: false });
    window.addEventListener('wheel', (e) => { this._wheel += e.deltaY; }, { passive: true });
    window.addEventListener('contextmenu', (e) => e.preventDefault());
    window.addEventListener('blur', () => this._releaseAll());
  }

  _keyDown(e) {
    if (!this.keys.has(e.code)) this._pressed.add(e.code);
    this.keys.set(e.code, true);
    if (e.code === 'Tab') e.preventDefault();
  }
  _keyUp(e) {
    this.keys.set(e.code, false);
    this._released.add(e.code);
  }
  _mouseMove(e) {
    const s = this._sensitivity;
    this.mouse.dx += (e.movementX || 0) * s;
    this.mouse.dy += (e.movementY || 0) * s;
    this.mouse.x = e.clientX;
    this.mouse.y = e.clientY;
  }
  _mouseDown(e) {
    this.mouse.down.add('Mouse' + e.button);
    this._pressed.add('Mouse' + e.button);
  }
  _mouseUp(e) {
    this.mouse.down.delete('Mouse' + e.button);
    this._released.add('Mouse' + e.button);
  }
  _releaseAll() {
    this.keys.clear();
    this.mouse.down.clear();
  }

  requestPointerLock(el) {
    if (this.pointerLocked) return;
    try { el.requestPointerLock(); } catch {}
  }
  exitPointerLock() {
    if (document.pointerLockElement) document.exitPointerLock();
  }

  onPointerLockChange = () => {
    this.pointerLocked = !!document.pointerLockElement;
    events.emit('input:lock', this.pointerLocked);
  };

  updateSensitivityFromSettings(s) {
    this._sensitivity = s;
  }

  pollGamepads() {
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    let gp = null;
    for (const p of pads) { if (p && p.connected) { gp = p; break; } }
    if (!gp) { this.gamepad.connected = false; return; }
    this.gamepad.connected = true;
    this.gamepad.buttons.clear();
    for (let i = 0; i < gp.buttons.length; i++) {
      this.gamepad.buttons.set(i, gp.buttons[i].pressed || gp.buttons[i].value > 0.5);
    }
    for (let i = 0; i < 4 && i < gp.axes.length; i++) {
      const v = Math.abs(gp.axes[i]) < 0.12 ? 0 : gp.axes[i];
      this.gamepad.axes[i] = v;
    }
  }

  // ---- Semantic queries ----
  axis(name) {
    let v = 0;
    const binds = this.bindings[name];
    for (const code of binds || []) {
      if (code === 'GamepadLeftStick') { v = this.gamepad.axes[GAMEPAD_AXES.ly]; }
      else if (this.keys.get(code)) { v = 1; }
    }
    // touch
    if (name === 'forward' && this.touch.move) v = Math.max(v, this.touch.move.y);
    if (name === 'back' && this.touch.move) v = Math.max(v, -this.touch.move.y);
    if (name === 'left' && this.touch.move) v = Math.max(v, -this.touch.move.x);
    if (name === 'right' && this.touch.move) v = Math.max(v, this.touch.move.x);
    return v;
  }

  axisX(name) {
    let v = 0;
    const binds = this.bindings[name];
    for (const code of binds || []) {
      if (code === 'GamepadLeftStick') v = this.gamepad.axes[GAMEPAD_AXES.lx];
      else if (code === 'GamepadRightStick') v = this.gamepad.axes[GAMEPAD_AXES.rx];
      else if (this.keys.get(code)) v = 1;
    }
    if (name === 'left' && this.touch.move) v = Math.max(v, -this.touch.move.x);
    if (name === 'right' && this.touch.move) v = Math.max(v, this.touch.move.x);
    return v;
  }

  axisZ(name) {
    let v = 0;
    const binds = this.bindings[name];
    for (const code of binds || []) {
      if (code === 'GamepadLeftStick') v = this.gamepad.axes[GAMEPAD_AXES.ly];
      else if (this.keys.get(code)) v = 1;
    }
    if (name === 'forward' && this.touch.move) v = Math.max(v, this.touch.move.y);
    if (name === 'back' && this.touch.move) v = Math.max(v, -this.touch.move.y);
    return v;
  }

  down(name) {
    const binds = this.bindings[name];
    for (const code of binds || []) {
      if (code.startsWith('Mouse')) { if (this.mouse.down.has(code)) return true; }
      else if (code.startsWith('Gamepad')) {
        const btn = GAMEPAD_BUTTONS[code.slice(8).toLowerCase()];
        if (btn !== undefined && this.gamepad.buttons.get(btn)) return true;
      }
      else if (this.keys.get(code)) return true;
    }
    if (this.touch.buttons.has(name)) return true;
    return false;
  }

  pressed(name) {
    const binds = this.bindings[name];
    for (const code of binds || []) {
      if (code.startsWith('Mouse')) { if (this._pressed.has(code)) return true; }
      else if (this._pressed.has(code)) return true;
      else if (code.startsWith('Gamepad')) {
        const btn = GAMEPAD_BUTTONS[code.slice(8).toLowerCase()];
        if (btn !== undefined && this.gamepad.buttons.get(btn)) return true;
      }
    }
    if (this.touch.buttons.has(name)) return true;
    return false;
  }

  takeLook() {
    const d = { dx: this.mouse.dx + (this.gamepad.axes[GAMEPAD_AXES.rx] * 40), dy: this.mouse.dy + (this.gamepad.axes[GAMEPAD_AXES.ry] * 40) };
    if (this.touch.look) {
      d.dx += this.touch.look.x * CONFIG.input.touchLookScale;
      d.dy += this.touch.look.y * CONFIG.input.touchLookScale;
    }
    this.mouse.dx = 0; this.mouse.dy = 0;
    if (this.touch.look) { this.touch.look.x = 0; this.touch.look.y = 0; }
    return d;
  }

  takeWheel() {
    const w = this._wheel;
    this._wheel = 0;
    return w;
  }

  // ---- Touch helpers (consumed by TouchControls UI) ----
  setTouchMove(x, y) {
    this.touch.move = (x || y) ? { x, y } : null;
  }

  setTouchButton(name, down) {
    if (down) this.touch.buttons.add(name);
    else this.touch.buttons.delete(name);
  }

  setTouchLook(dx, dy) {
    if (dx || dy) {
      this.touch.look = this.touch.look || { x: 0, y: 0 };
      this.touch.look.x += dx;
      this.touch.look.y += dy;
      this.touch.lookActive = true;
    } else {
      this.touch.look = null;
      this.touch.lookActive = false;
    }
  }

  endFrame() {
    this._pressed.clear();
    this._released.clear();
  }
}

export default Input;