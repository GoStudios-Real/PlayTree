// UIManager: owns the HUD and all full-screen/menu screens, plus app-wide
// helpers (toasts, announcements, feed, matchmaking overlay).

import { el, clearChildren } from '../core/UI.js';
import { events } from '../core/Events.js';
import { HUD } from './HUD.js';
import { MainMenuScreen } from './screens/MainMenuScreen.js';
import { ModeSelectScreen } from './screens/ModeSelectScreen.js';
import { SettingsScreen } from './screens/SettingsScreen.js';
import { PauseScreen } from './screens/PauseScreen.js';
import { InventoryScreen } from './screens/InventoryScreen.js';
import { MapScreen } from './screens/MapScreen.js';
import { QuestScreen } from './screens/QuestScreen.js';
import { SocialScreens } from './screens/SocialScreens.js';
import { StoreScreens } from './screens/StoreScreens.js';

export class UIManager {
  constructor(game) {
    this.game = game;
    this.app = document.getElementById('app');
    this.screens = {};
    this.hud = new HUD(this);
    this._registerScreens();
    this._buildMatchmaking();
    this._bind();
  }

  _registerScreens() {
    this.register('mainmenu', new MainMenuScreen(this));
    this.register('modeselect', new ModeSelectScreen(this));
    this.register('settings', new SettingsScreen(this));
    this.register('pause', new PauseScreen(this));
    this.register('inventory', new InventoryScreen(this));
    this.register('map', new MapScreen(this));
    this.register('quests', new QuestScreen(this));
    this.register('social', new SocialScreens(this));
    this.register('store', new StoreScreens(this));
  }

  register(name, screen) {
    this.screens[name] = screen;
    this.app.append(screen.el);
  }

  _bind() {
    events.on('inventory:changed', () => this.refreshScreens());
  }

  _buildMatchmaking() {
    this.mm = el('div', { id: 'matchmaking', class: 'hidden' });
    this.mmTrack = el('div', { class: 'mm-track' });
    this.mmFill = el('div', { class: 'mm-fill' });
    this.mmTrack.append(this.mmFill);
    this.mmLabel = el('div', { class: 'mm-label' });
    this.mm.append(el('div', { class: 'mm-title' }, 'Finding match...'), this.mmLabel, this.mmTrack);
    this.app.append(this.mm);

    this.loadingOverlay = el('div', { id: 'loading-overlay', class: 'hidden' });
    this.loadingOverlay.append(
      el('div', { class: 'spinner' }),
      el('div', { class: 'lbl', id: 'loading-lbl' }, 'Loading...')
    );
    this.app.append(this.loadingOverlay);
  }

  showLoading(text) {
    const lbl = this.loadingOverlay.querySelector('#loading-lbl');
    if (lbl) lbl.textContent = text || 'Loading...';
    this.loadingOverlay.classList.remove('hidden');
  }

  hideLoading() { this.loadingOverlay.classList.add('hidden'); }

  showMainMenu() { this.open('mainmenu'); }

  setGame(game) { this.game = game; }

  // ---- screen management ----
  open(name) {
    const s = this.screens[name];
    if (!s) return;
    for (const k in this.screens) this.screens[k].el.classList.add('hidden');
    s.show?.();
    s.el.classList.remove('hidden');
    this.current = name;
  }

  closeAll() {
    for (const k in this.screens) this.screens[k].el.classList.add('hidden');
    this.current = null;
  }

  refreshScreens() {
    for (const k in this.screens) {
      const s = this.screens[k];
      if (!s.el.classList.contains('hidden') && s.refresh) s.refresh();
    }
  }

  // ---- HUD passthroughs ----
  toast(msg, ms) { this.hud.toast(msg, ms); }
  announce(title, sub, ms) { this.hud.announce(title, sub, ms); }
  feed(text) { this.hud.feed(text); }
  flashVignette() { this.hud.flashVignette(); }
  setQuestTracker(t) { this.hud.setQuestTracker(t); }
  showHUD() { this.hud.show(); }
  hideHUD() { this.hud.hide(); }
  updateHUD(dt) { this.hud.update(dt); }
  setBRMode(mode) { this.hud.setBRMode(mode); }

  toggleInventory() {
    if (this.current === 'inventory') { this.closeAll(); this.game.setPaused(false); }
    else { this.open('inventory'); this.game.setPaused(true); }
  }
  toggleMap() {
    if (this.current === 'map') { this.closeAll(); this.game.setPaused(false); }
    else { this.open('map'); this.game.setPaused(true); }
  }
  toggleQuests() {
    if (this.current === 'quests') { this.closeAll(); this.game.setPaused(false); }
    else { this.open('quests'); this.game.setPaused(true); }
  }

  openCrafting() { this.open('inventory'); this.screens.inventory.showTab('crafting'); this.game.setPaused(true); }
  openCrate(contents) {
    this.open('inventory');
    this.screens.inventory.showCrate(contents);
    this.game.setPaused(true);
  }

  // ---- matchmaking ----
  showMatchmaking(mode, estimate) {
    this.mmLabel.textContent = `Queue: ${mode} · ETA ~${estimate}s`;
    this.mm.classList.remove('hidden');
    this.mmFill.style.width = '0%';
  }
  updateMatchmaking(progress) { this.mmFill.style.width = `${progress * 100}%`; }
  hideMatchmaking() { this.mm.classList.add('hidden'); }

  openSettings() { this.open('settings'); this.game.setPaused(true); }
}

export default UIManager;