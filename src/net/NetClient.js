// NetClient: WebSocket client with reconnection, heartbeat, and message routing.
// Runs standalone — the game calls it when a real server is available. Falls
// back gracefully to offline (simulated) mode.

import { MSG, encode, decode } from './Protocol.js';
import { events } from '../core/Events.js';
import { CONFIG } from '../core/Config.js';

export class NetClient {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.connecting = false;
    this.playerId = null;
    this.url = null;
    this._reconnects = 0;
    this._pingTimer = null;
    this.ping = 0;
    this._lastPing = 0;
  }

  async connect(url) {
    this.url = url;
    if (this.connecting) return;
    this.connecting = true;
    events.emit('net:connecting', { url });
    try {
      this.socket = new WebSocket(url);
      this.socket.onopen = () => {
        this.connected = true;
        this.connecting = false;
        this._reconnects = 0;
        events.emit('net:connected', { url });
        this._send(MSG.HELLO, { version: '1.0.0', nickname: 'Sprout', token: null });
        this._startPing();
      };
      this.socket.onmessage = (ev) => this._onMessage(ev.data);
      this.socket.onclose = () => this._onClose();
      this.socket.onerror = (e) => events.emit('net:error', e);
    } catch (e) {
      this.connecting = false;
      events.emit('net:error', e);
      return false;
    }
    return true;
  }

  _startPing() {
    if (this._pingTimer) clearInterval(this._pingTimer);
    this._pingTimer = setInterval(() => {
      if (this.connected) {
        this._lastPing = Date.now();
        this._send(MSG.PING, { t: this._lastPing });
      }
    }, CONFIG.net.pingInterval * 1000);
  }

  _onClose() {
    const wasConnected = this.connected;
    this.connected = false;
    this.socket = null;
    if (this._pingTimer) { clearInterval(this._pingTimer); this._pingTimer = null; }
    events.emit('net:disconnected', { wasConnected });
    if (this.url && this._reconnects < CONFIG.net.maxReconnects) {
      this._reconnects++;
      setTimeout(() => this.connect(this.url), CONFIG.net.reconnectDelay * 1000);
    } else if (this.url) {
      events.emit('net:reconnect-failed', {});
    }
  }

  _onMessage(raw) {
    const msg = decode(raw);
    if (!msg) return;
    if (msg.m === MSG.PONG) {
      this.ping = Date.now() - (msg.d?.t || this._lastPing);
      events.emit('net:ping', this.ping);
      return;
    }
    if (msg.m === MSG.WELCOME) {
      this.playerId = msg.d.playerId;
      events.emit('net:welcome', msg.d);
    }
    events.emit('net:message', msg);
  }

  _send(msgId, data) {
    if (!this.connected || !this.socket) return false;
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(encode(msgId, data));
      return true;
    }
    return false;
  }

  // ---- game-facing API ----
  join(serverId, opts = {}) {
    this._send(MSG.JOIN, { serverId, mode: opts.mode, password: opts.password });
  }
  sendMove(state) {
    this._send(MSG.MOVE, {
      id: this.playerId,
      x: state.x, y: state.y, z: state.z,
      yaw: state.yaw, pitch: state.pitch,
      vx: state.vx, vy: state.vy, vz: state.vz,
      grounded: state.grounded,
    });
  }
  sendBlockSet(x, y, z, id) { this._send(MSG.BLOCK_SET, { x, y, z, id }); }
  sendBlockBreak(x, y, z) { this._send(MSG.BLOCK_BREAK, { x, y, z }); }
  sendChat(text) { this._send(MSG.CHAT, { sender: this.playerId, text, ts: Date.now() }); }
  sendEmote(emote) { this._send(MSG.EMOTE, { id: this.playerId, emote }); }
  sendReport(targetId, reason, text) { this._send(MSG.REPORT, { targetId, reason, text }); }

  close() {
    if (this._pingTimer) clearInterval(this._pingTimer);
    if (this.socket) this.socket.close();
    this.socket = null;
    this.connected = false;
  }
}

export default NetClient;