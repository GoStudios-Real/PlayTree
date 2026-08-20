// Chat system with safety controls + moderation filter.

import { events } from '../core/Events.js';
import { Moderation } from './ModerationSystem.js';

export class ChatSystem {
  constructor(game) {
    this.game = game;
    this.messages = []; // { sender, text, ts, type }
    this.muted = false;
    this.maxMessages = 60;
  }

  send(sender, text) {
    if (!text || !text.trim()) return;
    if (text.length > 200) text = text.slice(0, 200);
    if (this.muted) return;
    if (sender === this.game.player && this.game.moderation?.checkForbidden(text)) {
      this.game.ui?.toast('Your message was removed by the grove guardians.', 2500);
      events.emit('chat:blocked', { text });
      return;
    }
    const msg = { sender: sender === this.game.player ? this.game.player.nickname : sender, text, ts: Date.now(), type: 'player' };
    this.messages.push(msg);
    if (this.messages.length > this.maxMessages) this.messages.shift();
    events.emit('chat:message', msg);
  }

  system(text) {
    const msg = { sender: null, text, ts: Date.now(), type: 'system' };
    this.messages.push(msg);
    if (this.messages.length > this.maxMessages) this.messages.shift();
    events.emit('chat:message', msg);
  }

  report(chatMessage, reason) {
    if (!this.game.moderation) return;
    this.game.moderation.reportChat(chatMessage, this.game.player.nickname, reason);
    this.game.ui?.toast('Report submitted. Thank you, sprout.', 3000);
  }

  clear() { this.messages = []; }
}

export default ChatSystem;