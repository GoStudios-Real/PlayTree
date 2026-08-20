// Persistence layer. Wraps localStorage with an in-memory fallback
// (e.g. file:// contexts or privacy modes). Namespaced + versioned.

const MEM = new Map();
const PREFIX = 'playtree.';

export const Storage = {
  available: (() => {
    try { const k = '__pt_test__'; window.localStorage.setItem(k, '1'); window.localStorage.removeItem(k); return true; }
    catch { return false; }
  })(),

  get(key, fallback = null) {
    const full = PREFIX + key;
    try {
      if (this.available) {
        const raw = window.localStorage.getItem(full);
        if (raw == null) return fallback;
        return JSON.parse(raw);
      }
    } catch {}
    if (MEM.has(full)) return MEM.get(full);
    return fallback;
  },

  set(key, value) {
    const full = PREFIX + key;
    try {
      if (this.available) {
        window.localStorage.setItem(full, JSON.stringify(value));
        return;
      }
    } catch {}
    MEM.set(full, value);
  },

  remove(key) {
    const full = PREFIX + key;
    try { if (this.available) window.localStorage.removeItem(full); } catch {}
    MEM.delete(full);
  },

  has(key) {
    return this.get(key, undefined) !== undefined;
  },
};

export default Storage;