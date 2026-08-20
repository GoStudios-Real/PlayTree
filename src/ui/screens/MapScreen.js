// Full-screen map: rendered from biome samples of the world + landmarks + BR zone.

import { el, button, clearChildren } from '../../core/UI.js';

export class MapScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this._build();
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap', style: { maxWidth: '760px' } });
    wrap.append(el('h1', {}, 'World Map'));
    this.canvas = el('canvas', { width: 640, height: 640 });
    this.ctx = this.canvas.getContext('2d');
    wrap.append(this.canvas);
    const row = el('div', { class: 'row mt8', style: { justifyContent: 'space-between' } });
    row.append(button('Close', () => this.ui.toggleMap(), 'ghost'));
    row.append(el('div', { class: 'muted small' }, 'You are the white dot.'));
    wrap.append(row);
    r.append(wrap);
  }

  show() {
    const g = this.ui.game;
    if (!g?.world) return;
    const ctx = this.ctx;
    const S = 640;
    const view = 160; // half-world in blocks
    const px = g.player.pos.x, pz = g.player.pos.z;
    ctx.clearRect(0, 0, S, S);
    ctx.fillStyle = '#14240f';
    ctx.fillRect(0, 0, S, S);

    const colors = { 0: '#2e6fbf', 1: '#e6d9a8', 2: '#6fbf4f', 3: '#3f7f2f', 4: '#9fd86f', 5: '#e8d089', 6: '#dfeaf5', 7: '#8f9399', 8: '#5f8f4f', 9: '#2f9f4f' };
    const cell = 16;
    for (let gy = -S / 2; gy < S / 2; gy += cell) {
      for (let gx = -S / 2; gx < S / 2; gx += cell) {
        const wx = px + gx * (view * 2) / S;
        const wz = pz + gy * (view * 2) / S;
        const b = g.world.getBiome(wx, wz);
        ctx.fillStyle = colors[b] || '#6fbf4f';
        ctx.fillRect(gx + S / 2, gy + S / 2, cell, cell);
      }
    }

    // Water line / height shading
    for (let gy = -S / 2; gy < S / 2; gy += cell) {
      for (let gx = -S / 2; gx < S / 2; gx += cell) {
        const wx = px + gx * (view * 2) / S;
        const wz = pz + gy * (view * 2) / S;
        const h = g.world.getSurfaceHeight(wx, wz);
        if (h < 2) {
          ctx.fillStyle = 'rgba(46,111,191,0.55)';
          ctx.fillRect(gx + S / 2, gy + S / 2, cell, cell);
        }
      }
    }

    // Landmarks
    const story = g.story;
    if (story?.landmarks) {
      for (const lm of story.landmarks) {
        const sx = (lm.x - px) * S / (view * 2) + S / 2;
        const sz = (lm.z - pz) * S / (view * 2) + S / 2;
        if (sx > 0 && sx < S && sz > 0 && sz < S) {
          ctx.fillStyle = '#ffd75a';
          ctx.font = '10px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(lm.icon || '✦', sx, sz);
        }
      }
    }

    // BR zone
    if (g.mode?.zone) {
      const z = g.mode.zone;
      ctx.strokeStyle = '#a86bff';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc((z.center.x - px) * S / (view * 2) + S / 2, (z.center.z - pz) * S / (view * 2) + S / 2, z.radius * S / (view * 2), 0, Math.PI * 2);
      ctx.stroke();
    }

    // Player
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(S / 2, S / 2, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}

export default MapScreen;