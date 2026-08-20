// Engine: owns the Three.js renderer, scene graph, game loop, resize handling
// and applies quality settings. Systems register update callbacks.

import * as THREE from '../../vendor/three.module.js';
import { events } from './Events.js';
import { Input } from './Input.js';
import { AudioEngine } from './Audio.js';
import Settings from './Settings.js';
import { CONFIG } from './Config.js';

export class Engine {
  constructor() {
    this.canvas = null;
    this.renderer = null;
    this.scene = null;
    this.camera = null;
    this.clock = null;
    this.running = false;
    this.frames = 0;
    this.fps = 0;
    this.frameTime = 0;
    this.stats = { fps: 0, frameMs: 0, draws: 0, chunks: 0, tris: 0, players: 0, entities: 0, memoryMB: 0 };
    this._updaters = [];
    this._fpsAccum = 0;
    this._fpsCount = 0;
    this._raf = null;
    this.sceneReady = false;
  }

  init() {
    const app = document.getElementById('app');
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'webgl';
    app.appendChild(this.canvas);
    this.renderer = new THREE.WebGLRenderer({ canvas: this.canvas, antialias: true, powerPreference: 'high-performance' });
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x87c5eb);
    this.scene.fog = new THREE.Fog(0x87c5eb, 60, 300);
    this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1600);
    this.camera.position.set(0, 60, 0);
    this.clock = new THREE.Clock();

    this.settings = new Settings(this);
    this.input = new Input(this);
    this.audio = new AudioEngine();
    this.input.updateSensitivityFromSettings(CONFIG.input.mouseSensitivity[this.settings.get('sensitivity')] || 2.0);

    document.addEventListener('pointerlockchange', this.input.onPointerLockChange);
    window.addEventListener('resize', () => this.resize());

    // Helpers
    this.ambient = new THREE.HemisphereLight(0xcfe8ff, 0x6b7d4f, 0.9);
    this.scene.add(this.ambient);
    this.sun = new THREE.DirectionalLight(0xfff2d8, 1.3);
    this.sun.castShadow = true;
    this.sun.shadow.mapSize.set(2048, 2048);
    const d = 60;
    this.sun.shadow.camera.left = -d; this.sun.shadow.camera.right = d;
    this.sun.shadow.camera.top = d; this.sun.shadow.camera.bottom = -d;
    this.sun.shadow.camera.near = 1; this.sun.shadow.camera.far = 400;
    this.sun.shadow.bias = -0.0004;
    this.scene.add(this.sun);
    this.scene.add(this.sun.target);
    this.sceneReady = true;
    this.applyQuality();
    events.emit('engine:ready', this);
    return this;
  }

  applyQuality() {
    const eff = this.settings.effective || {};
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, eff.pixelRatio || 1));
    this.renderer.shadowMap.enabled = !!eff.shadows;
    if (this.sun) this.sun.castShadow = !!eff.shadows;
    if (this.scene.fog) {
      const dist = (eff.renderDistance || 5) * CONFIG.world.chunkSize;
      this.scene.fog.near = dist * 0.18;
      this.scene.fog.far = dist * 0.85;
    }
  }

  resize() {
    const w = window.innerWidth, h = window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h, false);
  }

  addUpdater(fn, priority = 0) {
    this._updaters.push({ fn, priority });
    this._updaters.sort((a, b) => a.priority - b.priority);
  }

  start() {
    if (this.running) return;
    this.running = true;
    this.clock.start();
    this._loop();
  }

  _loop = () => {
    if (!this.running) return;
    this._raf = requestAnimationFrame(this._loop);
    const dt = Math.min(this.clock.getDelta(), 0.05);
    const t = this.clock.elapsedTime;
    this.frameTime = dt;
    this.frames++;
    this._fpsCount++;
    this._fpsAccum += dt;
    if (this._fpsAccum >= 0.5) {
      this.fps = Math.round(this._fpsCount / this._fpsAccum);
      this.stats.fps = this.fps;
      this._fpsAccum = 0;
      this._fpsCount = 0;
    }
    this.input.pollGamepads();
    for (const { fn } of this._updaters) {
      try { fn(dt, t); } catch (e) { console.error('updater error', e); }
    }
    this.renderer.render(this.scene, this.camera);
    this.stats.frameMs = Math.round(this.frameTime * 1000);
    this.input.endFrame();
    events.emit('tick:end', dt, t);
  };

  getViewDistance() {
    return this.settings.effective?.renderDistance || 5;
  }

  requestLock() {
    this.input.requestPointerLock(this.canvas);
  }

  setBackgroundColor(hex) {
    this.scene.background = new THREE.Color(hex);
  }

  dispose() {
    this.running = false;
    if (this._raf) cancelAnimationFrame(this._raf);
    this.renderer.dispose();
  }
}

export default Engine;