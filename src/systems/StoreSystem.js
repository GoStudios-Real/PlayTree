// Store + cosmetics + emotes: unlockable original cosmetic items.

import { events } from '../core/Events.js';
import { Storage } from '../core/Storage.js';

export const COSMETICS = [
  { id: 'shirt_dusk', type: 'shirt', name: 'Dusk Weave Shirt', desc: 'A shirt dyed the color of a grove sunset.', price: 120, color: 0x8a5ac8 },
  { id: 'shirt_verdant', type: 'shirt', name: 'Verdant Tunic', desc: 'Woven from living leaves.', price: 160, color: 0x3fa86a },
  { id: 'shirt_ember', type: 'shirt', name: 'Ember Threads', desc: 'Warm to the touch.', price: 200, color: 0xff6a3a },
  { id: 'hat_beret', type: 'hat', name: 'Artist Beret', desc: 'For the creative sprout.', price: 90, color: 0xff7a59 },
  { id: 'hat_crown', type: 'hat', name: 'Grove Crown', desc: 'Only the heartiest may wear it.', price: 300, color: 0xffcf5c },
  { id: 'hat_hood', type: 'hat', name: 'Nightwisp Hood', desc: 'Blends into the shadows.', price: 180, color: 0x4a4a6a },
  { id: 'glider_groveleaf', type: 'glider', name: 'Grove Leaf Glider', desc: 'Glide on a giant leaf.', price: 400, color: 0x59c48f },
  { id: 'pet_mossling', type: 'pet', name: 'Mossling Pet', desc: 'A tiny moss ball that follows you.', price: 350, color: 0x6a9a5a },
];

export const EMOTES = [
  { id: 'wave', name: 'Wave', icon: '👋', particles: [1, 1, 1] },
  { id: 'dance', name: 'Dance', icon: '🕺', particles: [1, 0.84, 0] },
  { id: 'point', name: 'Point', icon: '👉', particles: [0.6, 0.8, 1] },
  { id: 'jump', name: 'Cheer', icon: '🙌', particles: [1, 0.6, 0.2] },
  { id: 'sit', name: 'Sit', icon: '🧘', particles: [0.5, 0.8, 0.5] },
  { id: 'flex', name: 'Flex', icon: '💪', particles: [1, 0.4, 0.4] },
  { id: 'moonwalk', name: 'Moonwalk', icon: '🌙', particles: [0.8, 0.8, 1] },
  { id: 'spin', name: 'Spin', icon: '💫', particles: [1, 1, 0.5] },
  { id: 'robot', name: 'Robot', icon: '🤖', particles: [0.5, 0.5, 0.5] },
  { id: 'thriller', name: 'Thriller', icon: '🧟', particles: [0.8, 0.2, 0.2] },
  { id: 'lean', name: 'Lean', icon: '🦩', particles: [1, 0.9, 0.7] },
  { id: 'kick', name: 'Kick', icon: '🦶', particles: [0.9, 0.9, 0.9] },
];

export class StoreSystem {
  constructor(game) {
    this.game = game;
    this.owned = new Set(Storage.get('pt.store.owned', []));
    this.ownedEmotes = new Set(Storage.get('pt.store.emotes', ['wave', 'dance', 'point', 'jump', 'moonwalk', 'spin']));
    this.currency = Storage.get('pt.store.coins', 250);
    this.selected = {
      shirt: Storage.get('pt.store.sel.shirt', 'shirt_verdant'),
      hat: Storage.get('pt.store.sel.hat', null),
    };
  }

  getBalance() { return this.currency; }
  addCoins(n) { this.currency += n; Storage.set('pt.store.coins', this.currency); events.emit('store:coins', this.currency); }

  buy(id) {
    const item = COSMETICS.find(c => c.id === id);
    if (!item || this.owned.has(id)) return false;
    if (this.currency < item.price) {
      this.game.ui?.toast('Not enough grove coins.', 2500);
      return false;
    }
    this.currency -= item.price;
    this.owned.add(id);
    Storage.set('pt.store.coins', this.currency);
    Storage.set('pt.store.owned', Array.from(this.owned));
    this.game.engine.audio?.buy();
    this.game.ui?.toast(`Purchased: ${item.name}`, 3000);
    events.emit('store:purchased', item);
    return true;
  }

  unlockEmote(id) {
    if (this.ownedEmotes.has(id)) return;
    this.ownedEmotes.add(id);
    Storage.set('pt.store.emotes', Array.from(this.ownedEmotes));
  }

  setSelected(type, id) {
    this.selected[type] = id || null;
    Storage.set(`pt.store.sel.${type}`, this.selected[type]);
    events.emit('avatar:restyle', this.styleForAvatar());
  }

  styleForAvatar() {
    const style = {};
    const shirt = COSMETICS.find(c => c.id === this.selected.shirt);
    const hat = COSMETICS.find(c => c.id === this.selected.hat);
    if (shirt) style.shirt = shirt.color;
    if (hat) style.hat = hat.type === 'hat' ? (hat.id.includes('crown') ? 'crown' : hat.id.includes('beret') ? 'beret' : 'cap') : null;
    return style;
  }
}

export default StoreSystem;