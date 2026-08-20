// Settings screen: graphics, controls, audio, gameplay + profile rename.

import { el, button, panel, slider, toggle, dropdown, textField, clearChildren } from '../../core/UI.js';

export class SettingsScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this._build();
    this._load();
  }

  _build() {
    const r = this.el;
    const p = panel('Settings', 'Tweak PlayTree to your liking', {
      style: { width: '640px', maxWidth: '94vw', margin: '40px auto' },
      onClose: () => this.ui.open('mainmenu'),
    });
    this.body = p.body;

    const tabBar = el('div', { class: 'tabs' });
    const tabs = { graphics: null, controls: null, audio: null, gameplay: null, profile: null };
    const makeTab = (label, fn) => {
      const b = el('div', { class: 'tab', onclick: () => {
        Object.values(tabs).forEach(x => x && x.classList.remove('active'));
        b.classList.add('active');
        this._showPane(fn);
      } }, label);
      tabBar.append(b);
      return b;
    };
    tabs.graphics = makeTab('Graphics', 'graphics');
    tabs.controls = makeTab('Controls', 'controls');
    tabs.audio = makeTab('Audio', 'audio');
    tabs.gameplay = makeTab('Gameplay', 'gameplay');
    tabs.profile = makeTab('Profile', 'profile');
    p.head.insertBefore(tabBar, p.head.firstChild);

    this.pane = el('div', { class: 'settings-pane' });
    p.body.append(this.pane);

    r.append(p.root);
  }

  _showPane(name) {
    const g = this.ui.game;
    clearChildren(this.pane);
    const s = g?.settings;
    if (!s) return;

    if (name === 'graphics') {
      this.pane.append(
        slider('Render distance (chunks)', 2, 8, 1, s.renderDistance, v => { s.renderDistance = v; g?.setRenderDistance?.(v); }, { format: v => v + ' chunks' }),
        slider('Field of view', 55, 110, 1, s.fov, v => { s.fov = v; g?.setFov?.(v); }, { format: v => v + '°' }),
        toggle('Particles', s.particles, v => { s.particles = v; g?.particles?.setEnabled?.(v); }),
        toggle('Ambient occlusion', s.ao, v => { s.ao = v; g?.world?.remeshAll?.(); }),
        toggle('VSync', s.vsync, v => { s.vsync = v; g?.engine?.setVsync?.(v); }),
        dropdown('Texture quality', [{ value: 'low', label: 'Low' }, { value: 'medium', label: 'Medium' }, { value: 'high', label: 'High' }], s.textureQuality, v => { s.textureQuality = v; }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'controls') {
      const binds = g?.input?.bindings || {};
      this.pane.append(el('div', { class: 'muted', style: { marginBottom: '12px' } }, 'Keyboard bindings:'));
      const grid = el('div', { class: 'binds-grid' });
      for (const [action, key] of Object.entries(binds)) {
        grid.append(
          el('div', { class: 'bind-row' }, [
            el('span', {}, action),
            el('span', { class: 'key' }, String(key)),
          ])
        );
      }
      this.pane.append(grid);
      this.pane.append(
        slider('Mouse sensitivity', 0.1, 2, 0.05, s.sensitivity, v => { s.sensitivity = v; g?.setSensitivity?.(v); }, { format: v => v.toFixed(2) }),
        toggle('Invert Y', s.invertY, v => { s.invertY = v; g?.input?.setInvertY?.(v); }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'audio') {
      this.pane.append(
        slider('Master volume', 0, 100, 1, s.masterVolume * 100, v => { s.masterVolume = v / 100; g?.audio?.setMaster?.(v / 100); }, { format: v => v + '%' }),
        slider('Music volume', 0, 100, 1, s.musicVolume * 100, v => { s.musicVolume = v / 100; g?.audio?.setMusic?.(v / 100); }, { format: v => v + '%' }),
        slider('SFX volume', 0, 100, 1, s.sfxVolume * 100, v => { s.sfxVolume = v / 100; g?.audio?.setSfx?.(v / 100); }, { format: v => v + '%' }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'gameplay') {
      this.pane.append(
        toggle('Show coordinates', s.showCoords, v => { s.showCoords = v; }),
        toggle('Auto-jump', s.autoJump, v => { s.autoJump = v; }),
        toggle('Tooltips', s.tooltips, v => { s.tooltips = v; }),
        toggle('Damage numbers', s.damageNumbers, v => { s.damageNumbers = v; }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'profile') {
      const pname = s.nickname || 'Sprout';
      const field = textField('Nickname', pname, v => { this._name = v; });
      const row = el('div', { class: 'row mt8' });
      row.append(button('Save', () => {
        s.nickname = this._name || s.nickname;
        this._save();
        this.ui.toast('Nickname saved.');
      }, 'primary'));
      this.pane.append(field, row);
    }
  }

  _load() {
    const g = this.ui.game;
    if (!g?.settings) return;
    this._name = g.settings.nickname || 'Sprout';
    this._showPane('graphics');
    // mark first tab active
    const t = this.el.querySelector('.tab');
    if (t) t.classList.add('active');
  }

  _save() {
    const g = this.ui.game;
    if (g?.settings) g.settings.save();
    this.ui.toast('Settings saved.');
  }

  show() { this._load(); }
}

export default SettingsScreen;