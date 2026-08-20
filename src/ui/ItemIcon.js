// Procedural item icons: renders a small voxel cube (or symbol) per item on a
// canvas. No external image assets required — all icons are generated.

import { getItem } from '../content/items.js';
import { getBlock } from '../content/blocks.js';

const cache = new Map();

export function itemIconUrl(itemId, size = 64) {
  const key = itemId + '_' + size;
  if (cache.has(key)) return cache.get(key);
  const item = getItem(itemId);
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d');
  _drawItem(ctx, item, size);
  const url = canvas.toDataURL();
  cache.set(key, url);
  return url;
}

function _shade(hex, f) {
  const r = Math.min(255, Math.max(0, ((hex >> 16) & 255) * f));
  const g = Math.min(255, Math.max(0, ((hex >> 8) & 255) * f));
  const b = Math.min(255, Math.max(0, (hex & 255) * f));
  return `rgb(${r | 0},${g | 0},${b | 0})`;
}

function _colorTriple(c) {
  return (Math.round(c[0] * 255) << 16) | (Math.round(c[1] * 255) << 8) | Math.round(c[2] * 255);
}

function _drawItem(ctx, item, size) {
  if (!item) {
    ctx.fillStyle = '#333'; ctx.fillRect(0, 0, size, size);
    return;
  }
  const s = size;
  let top, side, front, symbol = null, symbolColor = '#fff';
  if (item.type === 'block' && item.blockId !== undefined) {
    const b = getBlock(item.blockId);
    const t = b.colors.top || b.colors.all || [0.6, 0.6, 0.6];
    const f = b.colors.side || b.colors.all || t;
    top = _colorTriple(t); side = _colorTriple(f); front = _colorTriple(f);
    if (item.blockId === 5) symbol = '💧';
    else if (item.blockId === 22) symbol = '🔥';
  } else if (item.type === 'weapon') {
    top = 0x9aa0aa; side = 0x6a707a; front = 0x7a808a;
    symbol = item.weapon.kind === 'melee' ? '⚔️' : item.weapon.kind === 'bow' ? '🏹' : item.weapon.kind === 'rocket' ? '🚀' : '🔫';
  } else if (item.type === 'tool') {
    top = 0x8a7a5a; side = 0x6a5a3a; front = 0x7a6a4a;
    symbol = item.tool.kind === 'pickaxe' ? '⛏️' : item.tool.kind === 'axe' ? '🪓' : '🧹';
  } else if (item.type === 'consumable') {
    top = 0xff6a6a; side = 0xcc4a4a; front = 0xe05a5a;
    symbol = item.heal ? '❤️' : '🛡️';
  } else if (item.type === 'seed') {
    top = 0x59c48f; side = 0x3a8a5a; front = 0x4a9a6a;
    symbol = '🌱';
  } else if (item.type === 'ammo') {
    top = 0xffcf5c; side = 0xcc9a3a; front = 0xddab4a;
    symbol = '📦';
  } else {
    top = 0x8a9a6a; side = 0x6a7a4a; front = 0x7a8a5a;
    symbol = item.type === 'material' ? '🧩' : item.type === 'currency' ? '🪙' : '❓';
  }

  // Draw isometric cube
  const cx = s / 2, cy = s / 2;
  const r = s * 0.34;
  const iso = (x, y, z) => {
    const px = cx + (x - z) * r * 0.72;
    const py = cy - (x + z) * r * 0.36 + y * r;
    return [px, py];
  };
  // top
  ctx.fillStyle = _shade(top, 1);
  ctx.beginPath();
  let [ax, ay] = iso(-0.7, 0.7, -0.7), [bx, by] = iso(0.7, 0.7, -0.7), [ex, ey] = iso(0.7, 0.7, 0.7), [fx, fy] = iso(-0.7, 0.7, 0.7);
  ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.lineTo(ex, ey); ctx.lineTo(fx, fy); ctx.closePath(); ctx.fill();
  // left (front-left)
  ctx.fillStyle = _shade(front, 0.8);
  let [gx, gy] = iso(-0.7, 0.7, 0.7), [hx, hy] = iso(-0.7, -0.7, 0.7), [ix, iy] = iso(-0.7, -0.7, -0.7), [jx, jy] = iso(-0.7, 0.7, -0.7);
  ctx.beginPath();
  ctx.moveTo(gx, gy); ctx.lineTo(hx, hy); ctx.lineTo(ix, iy); ctx.lineTo(jx, jy); ctx.closePath(); ctx.fill();
  // right
  ctx.fillStyle = _shade(side, 0.62);
  ctx.beginPath();
  ctx.moveTo(gx, gy); ctx.lineTo(ex, ey); ctx.lineTo(ex, ey - r * 1.4); ctx.lineTo(gx, gy - r * 1.4); ctx.closePath(); ctx.fill();
  ctx.beginPath();
  ctx.moveTo(ex, ey); ctx.lineTo(bx, by); ctx.lineTo(bx, by - r * 1.4); ctx.lineTo(ex, ey - r * 1.4); ctx.closePath(); ctx.fill();

  // symbol
  if (symbol) {
    ctx.font = `${s * 0.34}px sans-serif`;
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(symbol, cx, cy + s * 0.1);
  }
}

export default itemIconUrl;