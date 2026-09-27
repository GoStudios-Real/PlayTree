// Settings screen: graphics, controls, audio, gameplay + profile rename.
// Backed by engine.settings (Settings store) with live re-application.

import { el, button, panel, slider, toggle, dropdown, textField, clearChildren } from '../../core/UI.js';
import { CONFIG } from '../../core/Config.js';

export class SettingsScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this._build();
    this._load();
  }

  _settings() {
    return this.ui.game?.engine?.settings || null;
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
    const s = this._settings();
    if (!s) return;
    const g = this.ui.game;
    const engine = g?.engine;
    clearChildren(this.pane);

    if (name === 'graphics') {
      const q = s.get('quality');
      this.pane.append(
        dropdown('Quality', [
          { value: 'low', label: 'Low' },
          { value: 'medium', label: 'Medium' },
          { value: 'high', label: 'High' },
          { value: 'ultra', label: 'Ultra' },
        ], q, v => { s.set('quality', v); this.ui.toast(`Quality: ${v}`); }),
        slider('Render distance (chunks)', 2, 10, 1, s.effective.renderDistance, v => { s.set('renderDistance', v); }, { format: v => v + ' chunks' }),
        slider('Field of view', 55, 110, 1, s.get('fov'), v => {
          s.set('fov', v);
          const cam = g?.camera?.camera || engine?.camera;
          if (cam) { cam.fov = v; cam.updateProjectionMatrix(); }
        }, { format: v => v + '°' }),
        toggle('Particles', g?.particles ? g.particles.enabled !== false : true, v => { g?.particles?.setEnabled?.(v); }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'controls') {
      const binds = engine?.input?.bindings || {};
      this.pane.append(el('div', { class: 'muted', style: { marginBottom: '12px' } }, 'Keyboard bindings:'));
      const grid = el('div', { class: 'binds-grid' });
      for (const [action, key] of Object.entries(binds)) {
        grid.append(
          el('div', { class: 'bind-row' }, [
            el('span', {}, action),
            el('span', { class: 'key' }, Array.isArray(key) ? key.join(', ') : String(key)),
          ])
        );
      }
      this.pane.append(grid);
      this.pane.append(
        dropdown('Mouse sensitivity', [
          { value: 'low', label: 'Low' },
          { value: 'medium', label: 'Medium' },
          { value: 'high', label: 'High' },
        ], s.get('sensitivity'), v => {
          s.set('sensitivity', v);
          engine?.input?.updateSensitivityFromSettings?.(CONFIG.input.mouseSensitivity[v] || 2.0);
        }),
        toggle('Invert Y', !!s.get('invertY'), v => { s.set('invertY', v); }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'audio') {
      this.pane.append(
        slider('Master volume', 0, 100, 1, Math.round(s.get('volume') * 100), v => {
          s.set('volume', v / 100);
          engine?.audio?.setVolumes(v / 100, s.get('sfxVolume'), s.get('musicVolume'));
        }, { format: v => v + '%' }),
        slider('Music volume', 0, 100, 1, Math.round(s.get('musicVolume') * 100), v => {
          s.set('musicVolume', v / 100);
          engine?.audio?.setVolumes(s.get('volume'), s.get('sfxVolume'), v / 100);
        }, { format: v => v + '%' }),
        slider('SFX volume', 0, 100, 1, Math.round(s.get('sfxVolume') * 100), v => {
          s.set('sfxVolume', v / 100);
          engine?.audio?.setVolumes(s.get('volume'), v / 100, s.get('musicVolume'));
        }, { format: v => v + '%' }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'gameplay') {
      this.pane.append(
        toggle('Show damage numbers', !!s.get('showDamageNumbers'), v => { s.set('showDamageNumbers', v); }),
        toggle('Screen shake', !!s.get('screenShake'), v => { s.set('screenShake', v); }),
        toggle('Show compass', !!s.get('showCompass'), v => { s.set('showCompass', v); }),
        toggle('Control hints', !!s.get('controlHints'), v => { s.set('controlHints', v); }),
        toggle('Camera bobbing', !!s.get('cameraBobbing'), v => { s.set('cameraBobbing', v); }),
        button('Save', () => this._save(), 'primary')
      );
    } else if (name === 'profile') {
      const g2 = this.ui.game;
      const pname = g2?.social?.profile?.nickname || 'Sprout';
      const field = textField('Nickname', pname, v => { this._name = v; });
      const row = el('div', { class: 'row mt8' });
      row.append(button('Save', () => {
        if (this._name && g2?.social?.profile) {
          g2.social.profile.nickname = this._name;
          if (g2.player) g2.player.nickname = this._name;
        }
        this._save();
        this.ui.toast('Nickname saved.');
      }, 'primary'));
      this.pane.append(field, row);
    }
  }

  _load() {
    if (!this._settings()) return;
    this._showPane('graphics');
    const t = this.el.querySelector('.tab');
    if (t) t.classList.add('active');
  }

  _save() {
    this._settings()?.save();
    this.ui.toast('Settings saved.');
  }

  show() { this._load(); }
}

export default SettingsScreen;
