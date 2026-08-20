// Procedural audio engine (WebAudio). All sounds are synthesized at runtime,
// so there are no copyrighted audio assets. Includes a simple ambient music
// system driven by a soft generative pad.

import { events } from './Events.js';

const padNotes = [55, 82.41, 110, 164.81, 220]; // A2, E3, A3, E4, A4

export class AudioEngine {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.sfxGain = null;
    this.musicGain = null;
    this.enabled = false;
    this._padNodes = [];
    this._musicTimer = null;
    this._weatherNodes = [];
  }

  init() {
    if (this.enabled) return;
    try {
      const AC = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AC();
      this.master = this.ctx.createGain();
      this.master.gain.value = 0.8;
      this.master.connect(this.ctx.destination);
      this.sfxGain = this.ctx.createGain();
      this.sfxGain.connect(this.master);
      this.musicGain = this.ctx.createGain();
      this.musicGain.connect(this.master);
      this.enabled = true;
      this.startAmbient();
    } catch (e) {
      console.warn('Audio unavailable', e);
    }
  }

  setVolumes(vol, sfx, music) {
    if (!this.enabled) return;
    this.master.gain.value = vol;
    this.sfxGain.gain.value = sfx;
    this.musicGain.gain.value = music;
  }

  _env(dur) {
    const g = this.ctx.createGain();
    const t = this.ctx.currentTime;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(1, t + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    g.connect(this.sfxGain);
    return g;
  }

  _noiseBuffer(dur = 0.5) {
    const rate = this.ctx.sampleRate;
    const len = Math.max(1, Math.floor(rate * dur));
    const buf = this.ctx.createBuffer(1, len, rate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    return buf;
  }

  _playNoise(dur, filterType, freq, q, gain = 0.5, detune = 0) {
    if (!this.enabled) return;
    const src = this.ctx.createBufferSource();
    src.buffer = this._noiseBuffer(dur);
    const filter = this.ctx.createBiquadFilter();
    filter.type = filterType; filter.frequency.value = freq; filter.Q.value = q;
    const g = this._env(dur);
    g.gain.value = gain;
    src.connect(filter).connect(g);
    src.detune.value = detune;
    src.start();
  }

  _playTone(freq, dur, type = 'triangle', gain = 0.3, slideTo = null) {
    if (!this.enabled) return;
    const osc = this.ctx.createOscillator();
    osc.type = type; osc.frequency.value = freq;
    if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, this.ctx.currentTime + dur);
    const g = this._env(dur);
    g.gain.value = gain;
    osc.connect(g);
    osc.start();
    osc.stop(this.ctx.currentTime + dur + 0.05);
  }

  // ---------- public sfx ----------
  click() { this._playTone(660, 0.06, 'sine', 0.12); }
  hover() { this._playTone(440, 0.04, 'sine', 0.06); }
  step(groundType = 'grass') {
    const freq = groundType === 'stone' ? 120 : 90;
    this._playNoise(0.08, 'lowpass', freq, 1, 0.12, Math.random() * 30);
  }
  dig(material = 'stone') {
    const f = material === 'stone' ? 300 : material === 'wood' ? 500 : 400;
    this._playNoise(0.18, 'bandpass', f, 2, 0.35, (Math.random() - 0.5) * 60);
    this._playTone(120 + Math.random() * 40, 0.12, 'square', 0.08, 80);
  }
  place() { this._playNoise(0.12, 'lowpass', 250, 1, 0.3); }
  breakBlock() {
    this._playNoise(0.16, 'bandpass', 200, 1.5, 0.5, 40);
    this._playTone(140, 0.14, 'triangle', 0.15, 60);
  }
  pickup() { this._playTone(880, 0.07, 'sine', 0.15, 1180); this._playTone(1320, 0.05, 'sine', 0.08); }
  equip() { this._playTone(520, 0.08, 'sine', 0.14, 700); }
  jump() { this._playTone(320, 0.09, 'sine', 0.1, 480); }
  land() { this._playNoise(0.09, 'lowpass', 160, 1, 0.2); }
  hurt() { this._playTone(180, 0.18, 'sawtooth', 0.2, 70); this._playNoise(0.12, 'lowpass', 400, 1, 0.25); }
  die() { this._playTone(300, 0.5, 'sawtooth', 0.25, 60); }
  shoot() {
    this._playNoise(0.09, 'bandpass', 1400, 1.5, 0.4, 300);
    this._playTone(220, 0.08, 'square', 0.12, 90);
  }
  bow() { this._playNoise(0.08, 'highpass', 1800, 1, 0.3); }
  arrow() { this._playNoise(0.2, 'bandpass', 900, 2, 0.2, 500); }
  hitmarker() { this._playTone(900, 0.05, 'sine', 0.18, 1200); }
  explosion() {
    this._playNoise(0.6, 'lowpass', 300, 1, 0.8);
    this._playTone(80, 0.5, 'sine', 0.5, 30);
  }
  zoneWarning() { this._playTone(440, 0.25, 'sine', 0.2); this._playTone(660, 0.25, 'sine', 0.2); }
  drop() { this._playNoise(0.4, 'lowpass', 200, 1, 0.3); this._playTone(90, 0.4, 'sine', 0.25, 50); }
  wind(duration = 2) { this._playNoise(duration, 'lowpass', 400, 0.5, 0.06); }
  thunder() {
    this._playNoise(1.2, 'lowpass', 140, 1, 0.6);
    this._playNoise(0.5, 'bandpass', 300, 2, 0.4);
  }
  questComplete() {
    this._playTone(523, 0.12, 'triangle', 0.2);
    setTimeout(() => this._playTone(659, 0.12, 'triangle', 0.2), 120);
    setTimeout(() => this._playTone(784, 0.2, 'triangle', 0.22), 240);
  }
  achievement() {
    this._playTone(784, 0.1, 'sine', 0.2);
    setTimeout(() => this._playTone(1046, 0.16, 'sine', 0.2), 100);
  }
  levelUp() {
    this._playTone(440, 0.1, 'triangle', 0.2);
    setTimeout(() => this._playTone(554, 0.1, 'triangle', 0.2), 90);
    setTimeout(() => this._playTone(659, 0.22, 'triangle', 0.24), 180);
  }
  error() { this._playTone(200, 0.12, 'sawtooth', 0.12); }
  splash() { this._playNoise(0.2, 'bandpass', 700, 1, 0.3); }
  swim() { this._playNoise(0.12, 'bandpass', 500, 2, 0.15); }
  eat() { this._playNoise(0.1, 'lowpass', 300, 1, 0.2); }
  craft() { this._playTone(400, 0.1, 'sine', 0.15, 600); this._playTone(600, 0.1, 'sine', 0.12, 800); }
  buy() { this._playTone(880, 0.08, 'sine', 0.15); this._playTone(1175, 0.14, 'sine', 0.15); }
  notify() { this._playTone(1000, 0.06, 'sine', 0.12); }

  // ---------- Ambient generative music ----------
  startAmbient() {
    if (!this.enabled || this._musicTimer) return;
    const playPad = () => {
      if (!this.enabled) return;
      for (const f of padNotes) {
        const osc = this.ctx.createOscillator();
        osc.type = 'sine';
        const r = Math.random();
        osc.frequency.value = f * (r < 0.15 ? 0.5 : 1) * (r > 0.85 ? 1.5 : 1);
        const g = this.ctx.createGain();
        g.gain.setValueAtTime(0.0001, this.ctx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.04 + Math.random() * 0.04, this.ctx.currentTime + 1.2);
        g.gain.exponentialRampToValueAtTime(0.0001, this.ctx.currentTime + 4.5);
        osc.connect(g).connect(this.musicGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 5);
        this._padNodes.push(osc);
      }
      this._padNodes = this._padNodes.filter(n => n.onended !== undefined);
    };
    playPad();
    this._musicTimer = setInterval(playPad, 5200);
  }

  stopAmbient() {
    if (this._musicTimer) { clearInterval(this._musicTimer); this._musicTimer = null; }
    for (const n of this._padNodes) { try { n.stop(); } catch {} }
    this._padNodes = [];
  }

  setWeather(rainIntensity) {
    for (const n of this._weatherNodes) { try { n.stop(); } catch {} }
    this._weatherNodes = [];
    if (rainIntensity <= 0 || !this.enabled) return;
    const src = this.ctx.createBufferSource();
    src.buffer = this._noiseBuffer(3);
    src.loop = true;
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'bandpass'; filter.frequency.value = 900; filter.Q.value = 0.4;
    const g = this.ctx.createGain();
    g.gain.value = 0.04 * rainIntensity;
    src.connect(filter).connect(g).connect(this.sfxGain);
    src.start();
    this._weatherNodes.push(src);
  }
}

export default AudioEngine;