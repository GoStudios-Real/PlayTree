// In-game HUD: bars, hotbar, crosshair, compass, quest tracker, kill feed,
// announcements, zone warning. Built into #hud.

import * as THREE from '../../vendor/three.module.js';
import { el, clearChildren, formatNumber } from '../core/UI.js';
import { events } from '../core/Events.js';
import { itemIconUrl } from './ItemIcon.js';

export class HUD {
  constructor(ui) {
    this.ui = ui;
    this.root = el('div', { id: 'hud', class: 'hidden' });
    document.getElementById('app').append(this.root);
    this._build();
    this._bind();
  }

  _build() {
    const r = this.root;
    this.hpFill = null;
    this.hpText = null;
    this.hudTopLeft = el('div', { class: 'hud-corner hud-top-left' });
    this.hudTopRight = el('div', { class: 'hud-corner hud-top-right' });
    this.hudBottomCenter = el('div', { class: 'hud-corner hud-bottom-center' });
    this.hudBottomRight = el('div', { class: 'hud-corner hud-bottom-right' });
    this.hudBottomLeft = el('div', { class: 'hud-corner hud-bottom-left' });
    r.append(this.hudTopLeft, this.hudTopRight, this.hudBottomCenter, this.hudBottomRight, this.hudBottomLeft);

    // HP / stamina / XP bars
    const bars = el('div', { class: 'hud-chip bar' });
    const hpLabel = el('div', { class: 'chip-label' }, [el('span', {}, 'HP'), el('span', { id: 'hud-hp-text' }, '100')]);
    this.hpFill = this._bar('bar-hp');
    const stamLabel = el('div', { class: 'chip-label' }, [el('span', {}, 'STAMINA'), el('span', {}, '100')]);
    this.stamFill = this._bar('bar-stamina');
    const xpLabel = el('div', { class: 'chip-label' }, [el('span', {}, 'LEVEL'), el('span', { id: 'hud-level' }, '1')]);
    this.xpFill = this._bar('bar-xp');
    this.shieldFill = null;
    const shieldLabel = el('div', { class: 'chip-label' }, [el('span', {}, 'SHIELD'), el('span', { id: 'hud-shield-text' }, '0')]);
    this.shieldFill = this._bar('bar-shield');
    bars.append(hpLabel, this.hpFill, stamLabel, this.stamFill, shieldLabel, this.shieldFill, xpLabel, this.xpFill);
    this.hudTopLeft.append(bars);

    // Clock + day
    this.clockChip = el('div', { class: 'hud-chip' });
    this.hudTopLeft.append(this.clockChip);

    // Ammo (BR/combat)
    this.ammoChip = el('div', { class: 'hud-chip', id: 'hud-ammo' });
    this.hudTopLeft.append(this.ammoChip);

    // Quest tracker
    this.questTracker = el('div', { class: 'quest-tracker hidden' });
    this.hudBottomLeft.append(this.questTracker);

    // Announcements
    this.announce = el('div', { class: 'announce' });
    this.hudTopRight.append(this.announce);

    // Minimap (canvas)
    this.minimap = el('canvas', { id: 'minimap', width: 150, height: 150 });
    this.mmCtx = this.minimap.getContext('2d');
    this.hudTopRight.append(this.minimap);
    this.minimap.addEventListener('click', () => this.ui.toggleMap());

    // BR player count + zone
    this.brChip = el('div', { class: 'hud-chip', id: 'hud-br' });
    this.hudTopRight.append(this.brChip);

    // Hotbar
    this.hotbar = el('div', { class: 'hotbar' });
    this.hotbarSlots = [];
    for (let i = 0; i < 9; i++) {
      const slot = el('div', { class: 'hotbar-slot' });
      slot.append(el('span', { class: 'keynum' }, String(i + 1)));
      slot.addEventListener('click', () => this.ui.game?.player?.inventory.select(i));
      this.hotbar.append(slot);
      this.hotbarSlots.push(slot);
    }
    this.hudBottomCenter.append(this.hotbar);

    // Crosshair
    this.crosshair = el('div', { id: 'crosshair' });
    this.root.append(this.crosshair);

    // Damage vignette
    this.vignette = el('div', { id: 'damage-vignette' });
    this.root.append(this.vignette);

    // Kill feed
    this.brFeed = el('div', { id: 'br-feed' });
    this.hudBottomRight.append(this.brFeed);

    // Chat
    this.chatBox = el('div', { id: 'chat' });
    this.chatInput = el('input', {
      id: 'chat-input', type: 'text', placeholder: 'Chat... (Enter to send)',
      maxlength: 200,
    });
    this.chatBox.append(this.chatInput);
    this.root.append(this.chatBox);

    // Toasts
    this.toasts = el('div', { id: 'toasts' });
    this.root.append(this.toasts);

    // Zone warning
    this.zoneWarn = el('div', { class: 'hud-chip hidden', style: { color: 'var(--pt-accent-3)', borderColor: 'var(--pt-accent-3)' } }, '⚠ STORM DANGER');
    this.hudTopRight.append(this.zoneWarn);
  }

  _bar(cls) {
    const track = el('div', { class: 'bar-track' });
    const fill = el('div', { class: `bar-fill ${cls}` });
    fill.style.width = '100%';
    track.append(fill);
    return fill;
  }

  _bind() {
    events.on('inventory:changed', () => this._renderHotbar());
    events.on('inventory:select', () => this._renderHotbar());
    events.on('chat:message', (m) => this._onChat(m));
  }

  show() { this.root.classList.remove('hidden'); }
  hide() { this.root.classList.add('hidden'); }

  setVisible(v) { v ? this.show() : this.hide(); }

  update(dt) {
    const g = this.ui.game;
    if (!g?.player) return;
    const p = g.player;
    const xp = g.xp;
    this.hpFill.style.width = `${(p.health / p.maxHealth) * 100}%`;
    document.getElementById('hud-hp-text').textContent = Math.ceil(p.health);
    this.stamFill.style.width = `${(p.stamina / p.maxStamina) * 100}%`;
    this.xpFill.style.width = `${xp.xp / xp.xpToNext() * 100}%`;
    document.getElementById('hud-level').textContent = xp.level;
    this.shieldFill.style.width = `${(p.shield / p.maxShield) * 100}%`;
    document.getElementById('hud-shield-text').textContent = Math.ceil(p.shield);

    // Clock
    if (g.dayNight) {
      const tod = g.dayNight.timeOfDay;
      const icon = tod < 0.25 || tod > 0.75 ? '🌙' : '☀️';
      this.clockChip.innerHTML = '';
      this.clockChip.append(icon, ` Day ${g.dayNight.day} · ${g.dayNight.getClockText()}`);
    }

    // Ammo
    if (g.combat) {
      const a = g.combat.getHudAmmo();
      if (a) {
        this.ammoChip.innerHTML = '';
        this.ammoChip.append(`🔫 ${a.ammo}/${a.magSize}  (${a.inventory})${a.reloading ? ` reloading...` : ''}`);
        this.ammoChip.classList.remove('hidden');
      } else {
        this.ammoChip.classList.add('hidden');
      }
    }

    // Minimap
    this._drawMinimap();

    // BR info
    if (g.mode?.name === 'br' && g.mode.zone) {
      const z = g.mode.zone;
      this.brChip.innerHTML = '';
      this.brChip.append(`🎯 ${g.mode.aliveCount || 1} alive · Zone: ${z.radius.toFixed(0)}m`);
      this.brChip.classList.remove('hidden');
      this.zoneWarn.classList.remove('hidden');
    } else {
      this.brChip.classList.add('hidden');
      this.zoneWarn.classList.add('hidden');
    }

    // Crosshair hide when paused
    this.crosshair.style.display = g.state === 'playing' ? 'block' : 'none';
  }

  _drawMinimap() {
    const g = this.ui.game;
    if (!g?.player) return;
    const ctx = this.mmCtx;
    const S = 150;
    ctx.clearRect(0, 0, S, S);
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.fillRect(0, 0, S, S);
    const scale = 4;
    const cx = S / 2, cy = S / 2;
    const px = g.player.pos.x, pz = g.player.pos.z;
    // Grid samples
    ctx.fillStyle = '#5a8a4a';
    for (let i = 0; i < 60; i++) {
      const sx = px + (Math.random() - 0.5) * 150;
      const sz = pz + (Math.random() - 0.5) * 150;
      const b = g.world.getBiome(sx, sz);
      const colors = { 0: '#2e6fbf', 1: '#e6d9a8', 2: '#6fbf4f', 3: '#3f7f2f', 4: '#9fd86f', 5: '#e8d089', 6: '#dfeaf5', 7: '#8f9399', 8: '#5f8f4f', 9: '#2f9f4f' };
      ctx.fillStyle = colors[b] || '#6fbf4f';
      const dx = (sx - px) * scale + cx, dy = (sz - pz) * scale + cy;
      ctx.fillRect(dx, dy, 3, 3);
    }
    // BR zone
    if (g.mode?.zone) {
      const z = g.mode.zone;
      ctx.strokeStyle = '#a86bff';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx + (z.center.x - px) * scale, cy + (z.center.z - pz) * scale, z.radius * scale, 0, Math.PI * 2);
      ctx.stroke();
    }
    // Player
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fill();
  }

  _renderHotbar() {
    const g = this.ui.game;
    if (!g?.player) return;
    const inv = g.player.inventory;
    for (let i = 0; i < 9; i++) {
      const slot = this.hotbarSlots[i];
      clearChildren(slot);
      slot.append(el('span', { class: 'keynum' }, String(i + 1)));
      const s = inv.slots[i];
      if (s) {
        const img = el('img', { src: itemIconUrl(s.id), width: 34, height: 34, draggable: 'false' });
        slot.append(img);
        if (s.count > 1) slot.append(el('span', { class: 'count' }, formatNumber(s.count)));
        if (i === inv.selected) slot.classList.add('selected');
        else slot.classList.remove('selected');
      } else {
        slot.classList.remove('selected');
        if (i === inv.selected) slot.classList.add('selected');
      }
    }
  }

  setQuestTracker(tracked) {
    if (!tracked) { this.questTracker.classList.add('hidden'); return; }
    this.questTracker.classList.remove('hidden');
    clearChildren(this.questTracker);
    this.questTracker.append(
      el('div', { class: 'qt-title' }, tracked.title),
      el('div', { class: 'qt-desc' }, tracked.desc),
    );
    for (const obj of tracked.objectives) {
      this.questTracker.append(el('div', { class: 'qt-goal' }, `• ${obj.desc || ''} (${obj.current}/${obj.count})`));
    }
  }

  announce(title, sub = null, ms = 4000) {
    clearChildren(this.announce);
    this.announce.append(el('div', {}, title));
    if (sub) this.announce.append(el('div', { class: 'sub' }, sub));
    clearTimeout(this._announceTimer);
    this._announceTimer = setTimeout(() => clearChildren(this.announce), ms);
  }

  feed(text) {
    const item = el('div', { class: 'feed-item' }, text);
    this.brFeed.append(item);
    setTimeout(() => item.remove(), 4000);
  }

  _onChat(m) {
    const line = el('div', { class: `chat-msg${m.type === 'system' ? ' system' : ''}` });
    if (m.sender) line.append(el('span', { class: 'sender' }, m.sender + ': '));
    line.append(el('span', {}, m.text));
    this.chatBox.insertBefore(line, this.chatInput);
    while (this.chatBox.children.length > 8) this.chatBox.removeChild(this.chatBox.firstChild);
    setTimeout(() => line.remove(), 8000);
  }

  toast(msg, ms = 2600) {
    const t = el('div', { class: 'toast' }, msg);
    this.toasts.append(t);
    setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 320); }, ms);
  }

  updateVignette(dt) {
    // handled by game calling with intensity fade
  }

  flashVignette() {
    this.vignette.classList.add('hit');
    setTimeout(() => this.vignette.classList.remove('hit'), 150);
  }

  zoneWarning(distToZone) {
    if (distToZone < 0) return;
    this.zoneWarn.textContent = `⚠ STORM ${distToZone.toFixed(0)}m away`;
  }

  setBRMode(mode) {
    this.brMode = mode;
  }
}

export default HUD;