// Social screens: friends, party, profile, avatar customizer, server browser.

import { el, button, tabs, slider, dropdown, clearChildren, toggle } from '../../core/UI.js';
import { events } from '../../core/Events.js';
import { listMiniGames } from '../../minigames/MiniGameRegistry.js';

export class SocialScreens {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this.panes = {};
    this._build();
    this._bind();
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap', style: { maxWidth: '720px' } });
    wrap.append(el('h1', {}, 'Community'));
    this.pane = el('div', { class: 'settings-pane' });
    const tabBar = el('div', { class: 'tabs' });
    const defs = [
      ['friends', 'Friends'],
      ['servers', 'Servers'],
      ['profile', 'Profile'],
      ['avatar', 'Avatar'],
    ];
    const btns = [];
    for (const [key, label] of defs) {
      const b = el('div', { class: 'tab', onclick: () => {
        btns.forEach(x => x.classList.remove('active'));
        b.classList.add('active');
        this.showTab(key);
      } }, label);
      btns.push(b);
      tabBar.append(b);
    }
    wrap.append(tabBar, this.pane);
    const row = el('div', { class: 'row mt8' });
    row.append(button('Close', () => this.ui.closeAll(), 'ghost'));
    wrap.append(row);
    r.append(wrap);
    this._tabBtns = btns;
  }

  _bind() {
    events.on('social:friends-changed', () => { if (!this.el.classList.contains('hidden')) this.showTab('friends'); });
  }

  show() {
    this._tabBtns[0].classList.add('active');
    this.showTab('friends');
  }

  showTab(key) {
    this.panes[key] = this.panes[key] || this['_render' + key[0].toUpperCase() + key.slice(1)]();
    clearChildren(this.pane);
    this.pane.append(this.panes[key]);
  }

  _renderFriends() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const row = el('div', { class: 'row' });
    const input = el('input', { type: 'text', placeholder: 'Add friend nickname', style: { flex: '1' } });
    row.append(input, button('Add', () => {
      const n = input.value.trim();
      if (n) { g.social.addFriend(n); input.value = ''; }
    }, 'primary'));
    box.append(row);
    const list = el('div', { class: 'friend-list' });
    box.append(list);
    const render = () => {
      clearChildren(list);
      const fs = g.social.friendState();
      for (const f of fs) {
        const item = el('div', { class: 'friend-item' });
        const status = f.status === 'online' ? '🟢' : f.status === 'in-menu' ? '🟡' : '⚪';
        item.append(el('span', { class: 'muted' }, `${status}`), el('span', {}, f.nickname));
        if (f.game) item.append(el('span', { class: 'muted small' }, ` · ${f.game}`));
        if (f.lastSeen) item.append(el('span', { class: 'muted small' }, ` · ${f.lastSeen}`));
        item.append(button('Join', () => { this.ui.toast(`Joining ${f.nickname}...`); g.social.createParty(); }, 'small ghost'));
        item.append(button('✕', () => g.social.removeFriend(f.id), 'small icon ghost'));
        list.append(item);
      }
      if (!fs.length) list.append(el('div', { class: 'muted' }, 'No friends yet. Add some to get started.'));
      // Party
      const party = g.social.party;
      list.append(el('div', { class: 'muted mt8' }, `Party (${party.members.length}/${party.maxSize}): ${party.members.join(', ') || 'none'}`));
      list.append(el('div', { class: 'row mt8' }, button('Create party', () => g.social.createParty(), 'small')));
    };
    render();
    events.on('social:friends-changed', () => render());
    events.on('party:changed', () => render());
    return box;
  }

  _renderServers() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const modeSel = dropdown('Mode', [{ value: '', label: 'All modes' }, { value: 'adventure', label: 'Adventure' }, { value: 'survival', label: 'Survival' }, { value: 'creative', label: 'Creative' }, { value: 'br', label: 'Battle Royale' }, { value: 'minigame', label: 'Mini-Games' }], '', () => {});
    const list = el('div', { class: 'server-list' });
    const render = () => {
      clearChildren(list);
      for (const s of g.serverBrowser.servers) {
        const item = el('div', { class: 'server-item' });
        item.append(
          el('span', { class: 'server-name' }, s.name),
          el('span', { class: 'muted small' }, `${s.gameName} · ${s.players}/${s.max} · ${s.region} · ${s.ping}ms`),
          button(s.status === 'open' ? 'Join' : 'Full', () => { if (s.status === 'open') g.serverBrowser.join(s); }, 'small primary')
        );
        list.append(item);
      }
    };
    const refreshRow = el('div', { class: 'row mt8' });
    refreshRow.append(button('Refresh', () => { g.serverBrowser.refresh(); render(); }, 'small'));
    box.append(modeSel, refreshRow, list);
    render();
    // Quick match
    const q = el('div', { class: 'row mt8' });
    q.append(button('Quick Match (BR)', () => g.matchmaker.queue('br'), 'primary'));
    q.append(button('Quick Match (Adventure)', () => g.matchmaker.queue('adventure'), 'ghost'));
    q.append(button('Create Private', () => { g.serverBrowser.createPrivate('creative', { name: 'My Grove' }); }, 'ghost'));
    box.append(q);
    // Mini-games section
    const mg = el('div', { class: 'col mt8' });
    mg.append(el('div', { class: 'muted' }, 'Mini-games:'));
    const mgRow = el('div', { class: 'row' });
    for (const def of listMiniGames()) {
      mgRow.append(button(`${def.icon} ${def.name}`, () => g.setMode('minigame', { minigame: def.id }), 'small'));
    }
    mg.append(mgRow);
    box.append(mg);
    return box;
  }

  _renderProfile() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const p = g.social.profile || { nickname: g.settings?.nickname || 'Sprout', tag: '0000', level: g.xp?.level || 1 };
    box.append(el('div', { class: 'profile-big' }, `${p.nickname}#${p.tag}`));
    box.append(el('div', { class: 'muted' }, `Level ${g.xp?.level || 1} · ${(g.xp?.playtime / 3600 || 0).toFixed(1)}h played`));
    const stats = g.xp?.stats || {};
    const grid = el('div', { class: 'stats-grid' });
    for (const [k, v] of Object.entries(stats)) grid.append(el('div', { class: 'stat-cell' }, [el('div', { class: 'stat-val' }, String(v)), el('div', { class: 'muted small' }, k)]));
    box.append(grid);
    const loginBtn = el('div', { class: 'row mt8' });
    if (!g.social.profile) loginBtn.append(button('Login', () => { g.social.login(p.nickname, p.tag); this.ui.toast('Logged in!'); }, 'primary'));
    box.append(loginBtn);
    return box;
  }

  _renderAvatar() {
    const g = this.ui.game;
    const box = el('div', { class: 'col' });
    const cur = g.playerStyle || {};
    const pickers = [
      ['Shirt color', 'shirt', ['#4aa8ff', '#ff6a6a', '#59c48f', '#ffd75a', '#a86bff', '#4a4a5a']],
      ['Pants color', 'pants', ['#3a4a66', '#6a4a3a', '#4a6a3a', '#3a3a4a', '#8a6a4a']],
      ['Hair color', 'hair', ['#4a3828', '#222', '#c89a5a', '#8a4a3a', '#3a3a6a']],
    ];
    const apply = () => {
      const style = { ...cur, ...this._style, shirtColor: this._style.shirt, pantsColor: this._style.pants, hairColor: this._style.hair };
      events.emit('avatar:changed', style);
      this.ui.toast('Avatar updated.');
    };
    this._style = { shirt: cur.shirtColor || '#4aa8ff', pants: cur.pantsColor || '#3a4a66', hair: cur.hairColor || '#4a3828' };
    for (const [label, key, colors] of pickers) {
      const rowEl = el('div', { class: 'field' });
      rowEl.append(el('label', {}, label));
      const sw = el('div', { class: 'swatches' });
      for (const c of colors) {
        const dot = el('div', { class: `swatch${this._style[key] === c ? ' sel' : ''}`, style: { background: c }, onclick: () => {
          this._style[key] = c;
          sw.querySelectorAll('.swatch').forEach(d => d.classList.remove('sel'));
          dot.classList.add('sel');
        } });
        sw.append(dot);
      }
      rowEl.append(sw);
      box.append(rowEl);
    }
    box.append(el('div', { class: 'row mt8' }, button('Apply', apply, 'primary')));
    return box;
  }
}

export default SocialScreens;