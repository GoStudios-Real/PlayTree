// Tiny event bus. All systems communicate through typed events.

export class Emitter {
  constructor() {
    this._map = new Map();
  }
  on(type, fn, ctx) {
    if (!this._map.has(type)) this._map.set(type, []);
    this._map.get(type).push({ fn, ctx });
    return () => this.off(type, fn);
  }
  once(type, fn, ctx) {
    const off = this.on(type, (...a) => { off(); fn.apply(ctx, a); }, ctx);
    return off;
  }
  off(type, fn) {
    const arr = this._map.get(type);
    if (!arr) return;
    const i = arr.findIndex(e => e.fn === fn);
    if (i >= 0) arr.splice(i, 1);
  }
  emit(type, ...args) {
    const arr = this._map.get(type);
    if (!arr) return;
    for (const { fn, ctx } of arr.slice()) {
      try { fn.apply(ctx, args); }
      catch (e) { console.error(`[event:${type}]`, e); }
    }
  }
  clear() { this._map.clear(); }
}

export const events = new Emitter();

export default Emitter;