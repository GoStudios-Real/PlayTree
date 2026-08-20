// User settings + quality management. Persisted via Storage.

import { Storage } from './Storage.js';
import { QUALITY_PRESETS } from './Config.js';
import { events } from './Events.js';

export const SETTINGS_KEY = 'settings.v1';

export const DEFAULT_SETTINGS = {
  quality: 'medium',
  renderDistance: 'auto',
  pixelRatio: 'auto',
  shadows: 'auto',
  vsync: true,
  maxFps: 0,
  fov: 75,
  sensitivity: 'medium',
  invertY: false,
  volume: 0.8,
  musicVolume: 0.6,
  sfxVolume: 0.8,
  language: 'en',
  showDamageNumbers: true,
  screenShake: true,
  showCompass: true,
  cameraBobbing: true,
  thirdPerson: true,
  accessibility: {
    reduceMotion: false,
    colorBlindMode: 'none',
    largeText: false,
  },
  controlHints: true,
};

export class Settings {
  constructor(engine) {
    this.engine = engine;
    this.values = { ...DEFAULT_SETTINGS, ...(Storage.get(SETTINGS_KEY) || {}) };
    this.qualityPreset = this.values.quality;
    this.applyQuality();
  }

  get(key) {
    return this.values[key];
  }

  set(key, value, persist = true) {
    this.values[key] = value;
    if (persist) this.save();
    events.emit('settings:changed', key, value, this);
    if (key === 'quality' || key === 'renderDistance' || key === 'shadows' || key === 'pixelRatio') {
      this.applyQuality();
    }
  }

  save() {
    Storage.set(SETTINGS_KEY, this.values);
  }

  reset() {
    this.values = { ...DEFAULT_SETTINGS };
    this.applyQuality();
    this.save();
  }

  applyQuality() {
    const preset = QUALITY_PRESETS[this.values.quality] || QUALITY_PRESETS.medium;
    this.effective = {
      ...preset,
      renderDistance: this.values.renderDistance !== 'auto' ? this.values.renderDistance : preset.renderDistance,
      shadows: this.values.shadows !== 'auto' ? this.values.shadows === 'on' : preset.shadows,
      pixelRatio: this.values.pixelRatio !== 'auto' ? Number(this.values.pixelRatio) : preset.pixelRatio,
    };
    events.emit('quality:changed', this.effective);
  }

  isLowEnd() {
    const cores = (navigator.hardwareConcurrency || 4);
    const mem = (navigator.deviceMemory || 4);
    return cores <= 4 && mem <= 4;
  }

  detectAuto() {
    if (this.isLowEnd()) return 'low';
    const gpu = document.createElement('canvas').getContext('webgl2') ? 'webgl2' : 'webgl';
    if (gpu !== 'webgl2') return 'low';
    return 'high';
  }
}

export default Settings;