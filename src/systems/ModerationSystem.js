// Moderation: chat filter, reporting, anti-cheat hooks (client-side checks that
// a real server would enforce authoritatively).

import { Storage } from '../core/Storage.js';
import { events } from '../core/Events.js';

const FORBIDDEN = [
  'hack', 'cheat', 'exploit', 'glitch', 'mod', 'admin abuse', 'scam',
  // slurs removed from dataset intentionally — filter relies on blocklist + heuristics
];

export class Moderation {
  constructor(game) {
    this.game = game;
    this.reports = Storage.get('pt.moderation.reports', []);
    this.bans = Storage.get('pt.moderation.bans', []);
    this.filterLevel = 'standard'; // off | light | standard | strict
    this._setupFilter();
  }

  _setupFilter() {
    // Basic heuristic: repeated capitals, long strings, phone numbers
  }

  checkForbidden(text) {
    const lower = text.toLowerCase();
    if (this.filterLevel === 'off') return false;
    for (const w of FORBIDDEN) {
      if (lower.includes(w)) return true;
    }
    if (this.filterLevel === 'strict') {
      // Flag very long all-caps
      if (text.length > 40 && text === text.toUpperCase()) return true;
      // Flag excess punctuation
      if ((text.match(/[!?]/g) || []).length > 8) return true;
    }
    return false;
  }

  reportChat(chatMessage, reporter, reason) {
    this.reports.push({
      id: Math.random().toString(36).slice(2),
      reporter,
      sender: chatMessage.sender,
      text: chatMessage.text,
      reason,
      ts: Date.now(),
      resolved: false,
    });
    Storage.set('pt.moderation.reports', this.reports.slice(-100));
    events.emit('moderation:report', this.reports[this.reports.length - 1]);
  }

  resolveReport(id) {
    const r = this.reports.find(x => x.id === id);
    if (r) r.resolved = true;
    Storage.set('pt.moderation.reports', this.reports);
  }

  banUser(nickname, reason) {
    this.bans.push({ nickname, reason, ts: Date.now() });
    Storage.set('pt.moderation.bans', this.bans);
  }

  isBanned(nickname) {
    return this.bans.some(b => b.nickname === nickname);
  }

  // ---- Anti-cheat hooks (client-side validation; authoritative in real server) ----
  validateBlockEdit(player, x, y, z) {
    // Basic sanity: within reach and height bounds
    const d = Math.hypot(player.pos.x - x, player.pos.y + 1 - y, player.pos.z - z);
    if (d > 12) return false;
    if (y < 0 || y >= 128) return false;
    return true;
  }

  validatePlayerState(player) {
    // Velocity sanity (server would clamp)
    if (Math.abs(player.vel.y) > 80) return false;
    if (Math.abs(player.vel.x) > 30 || Math.abs(player.vel.z) > 30) return false;
    return true;
  }
}

export default Moderation;