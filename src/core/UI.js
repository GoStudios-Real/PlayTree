// Lightweight DOM/UI helpers used by all screens. No framework, no deps.
// Provides element creation, panels, tabs, lists, tooltips, and a small
// reactive binding helper for building game UI quickly.

export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') node.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
    else if (k === 'html') node.innerHTML = v;
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
    else if (k === 'dataset') Object.assign(node.dataset, v);
    else node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c == null) continue;
    node.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return node;
}

export const h = (tag, attrs, ...children) => el(tag, attrs, ...children);

export function icon(name, size = 22) {
  return h('img', {
    src: `assets/icons/${name}.svg`, width: size, height: size, alt: '', class: 'item-icon',
    draggable: 'false',
  });
}

// A panel with head/body; returns { root, head, body }.
export function panel(title, sub = '', opts = {}) {
  const root = el('div', { class: `panel ${opts.class || ''}`, style: { ...(opts.style || {}) } });
  const head = el('div', { class: 'panel-head' });
  const headTitle = el('div');
  headTitle.append(h('h2', {}, title));
  if (sub) headTitle.append(h('div', { class: 'sub' }, sub));
  head.append(headTitle);
  if (opts.actions) head.append(opts.actions);
  const body = el('div', { class: 'panel-body' });
  root.append(head, body);
  if (opts.onClose) {
    const closeBtn = el('button', { class: 'btn icon small ghost', onclick: opts.onClose }, '✕');
    head.append(closeBtn);
  }
  return { root, head, body };
}

export function button(text, onClick, cls = '') {
  return el('button', { class: `btn ${cls}`, onclick: onClick }, text);
}

export function closeButton(onClick) {
  return el('button', { class: 'btn icon small ghost', onclick: onClick, 'aria-label': 'Close' }, '✕');
}

export function tabs(items, onSelect, initial = 0) {
  const wrap = el('div', { class: 'tabs' });
  const btns = items.map((t, i) => {
    const b = el('div', { class: `tab${i === initial ? ' active' : ''}`, onclick: () => {
      btns.forEach((x, j) => x.classList.toggle('active', j === i));
      onSelect(t, i);
    } }, t.label);
    return b;
  });
  wrap.append(...btns);
  return wrap;
}

export function list(items, render, cls = '') {
  const ul = el('div', { class: cls });
  for (const it of items) ul.append(render(it));
  return ul;
}

export function slider(labelText, min, max, step, value, onChange, opts = {}) {
  const row = el('div', { class: 'field' });
  const lab = el('label', {}, labelText);
  const val = el('span', { class: 'muted small', style: { marginLeft: '8px' } }, String(value));
  const input = el('input', {
    type: 'range', min, max, step, value,
    oninput: (e) => { val.textContent = opts.format ? opts.format(Number(e.target.value)) : e.target.value; onChange(Number(e.target.value)); },
  });
  const labelRow = el('div', { class: 'row' }, lab, val);
  row.append(labelRow, input);
  return row;
}

export function textField(labelText, value, onInput, opts = {}) {
  const row = el('div', { class: 'field' });
  if (labelText) row.append(el('label', {}, labelText));
  const input = el('input', {
    type: opts.type || 'text',
    placeholder: opts.placeholder || '',
    value,
    oninput: (e) => onInput(e.target.value),
  });
  row.append(input);
  return row;
}

export function toggle(labelText, checked, onChange) {
  const row = el('div', { class: 'field-row' });
  const cb = el('input', { type: 'checkbox', checked: checked ? 'checked' : null, onchange: (e) => onChange(e.target.checked) });
  const lab = el('label', { style: { marginBottom: 0, cursor: 'pointer' } }, labelText);
  row.append(cb, lab);
  return row;
}

export function dropdown(labelText, options, value, onChange) {
  const row = el('div', { class: 'field' });
  if (labelText) row.append(el('label', {}, labelText));
  const sel = el('select', {
    onchange: (e) => onChange(e.target.value),
  }, ...options.map(o => {
    const opt = el('option', { value: o.value }, o.label);
    if (o.value === value) opt.selected = true;
    return opt;
  }));
  row.append(sel);
  return row;
}

export function rarityClass(rarity) {
  return `rarity-${rarity || 'common'}`;
}

export function toast(root, msg, ms = 2600, cls = '') {
  if (!root) return;
  const t = el('div', { class: `toast ${cls}` }, msg);
  root.append(t);
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 320); }, ms);
}

export function confirmDialog(title, message, onConfirm, onCancel) {
  const shade = el('div', {
    class: 'shade',
    style: { position: 'fixed', inset: '0', background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 500 },
  });
  const p = panel(title, '', { style: { width: '400px', maxWidth: '92vw' }, onClose: () => shade.remove() });
  p.body.append(el('p', { class: 'muted' }, message));
  const row = el('div', { class: 'row mt8', style: { justifyContent: 'flex-end' } });
  row.append(
    button('Cancel', () => { shade.remove(); onCancel && onCancel(); }, 'ghost'),
    button('Confirm', () => { shade.remove(); onConfirm && onConfirm(); }, 'danger')
  );
  p.body.append(row);
  shade.append(p.root);
  document.body.append(shade);
  return shade;
}

export function showModal(modalEl) {
  const shade = el('div', {
    class: 'shade',
    style: { position: 'fixed', inset: '0', background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 500 },
  });
  shade.append(modalEl);
  document.body.append(shade);
  return shade;
}

export function clearChildren(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
}

export function formatNumber(n) {
  if (n >= 1e9) return (n / 1e9).toFixed(2) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(2) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return String(Math.floor(n));
}

export default { el, h, panel, button, tabs, list, slider, textField, toggle, dropdown, toast, icon, confirmDialog, showModal, clearChildren, rarityClass, formatNumber };