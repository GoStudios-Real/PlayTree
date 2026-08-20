// Debug overlay (F4): live metrics, entity/block counts, memory.

import { el } from '../core/UI.js';

export class DebugOverlay {
  constructor(game) {
    this.game = game;
    this.open = false;
    this.root = el('div', { id: 'debug-overlay', class: 'hidden' });
    this.body = el('div', { class: 'dbg-body' });
    this.root.append(this.body);
    document.getElementById('app').append(this.root);
  }

  toggle() {
    this.open = !this.open;
    this.root.classList.toggle('hidden', !this.open);
  }

  update() {
    if (!this.open) return;
    const g = this.game;
    if (!g?.engine) return;
    const lines = [];
    const r = g.engine.renderer;
    if (r) {
      const info = r.info;
      lines.push(`FPS: ${g.engine.fps.toFixed(0)}`);
      lines.push(`Draw calls: ${info.render.calls}`);
      lines.push(`Triangles: ${(info.render.triangles / 1000).toFixed(0)}k`);
      lines.push(`Geometry: ${info.memory.geometries}`);
    }
    if (g.world) {
      lines.push(`Chunks loaded: ${g.world.chunks.size} / meshed ${g.world._meshedCount ?? '?'}`);
      lines.push(`Queued gens: ${g.world._queue?.length ?? 0}`);
    }
    if (g.entities) {
      const e = g.entities.list ?? [];
      lines.push(`Entities: ${e.length} (bots ${(g.bots || []).length})`);
    }
    lines.push(`Players: ${(g.otherPlayers || []).length}`);
    lines.push(`Particles: ${g.particles?.count ?? 0}`);
    if (g.player) {
      lines.push(`Pos: ${g.player.pos.x.toFixed(1)}, ${g.player.pos.y.toFixed(1)}, ${g.player.pos.z.toFixed(1)}`);
      lines.push(`Vel: ${g.player.vel.y.toFixed(1)} ${g.player.grounded ? '(grounded)' : ''}`);
      lines.push(`Mode: ${g.mode?.name} · Seed: ${g.world.seed}`);
    }
    if (g.net) lines.push(`Ping: ${g.net.ping ?? 0}ms · ${g.net.connected ? 'online' : 'offline'}`);
    this.body.textContent = lines.join('\n');
  }
}

export default DebugOverlay;