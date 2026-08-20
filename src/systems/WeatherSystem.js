// Weather system: clear / rain / storm with smooth transitions, rain visuals,
// fog, thunder + lightning during storms.

import * as THREE from '../../vendor/three.module.js';
import { events } from '../core/Events.js';

export class WeatherSystem {
  constructor(engine, world) {
    this.engine = engine;
    this.world = world;
    this.state = 'clear';       // clear | rain | storm
    this.rainIntensity = 0;     // 0..1 (smooth)
    this.targetRain = 0;
    this.stormFlash = 0;
    this._nextChange = 40 + Math.random() * 40;
    this._thunderTimer = 0;
    this._buildRain();
  }

  _buildRain() {
    const n = 800;
    this.positions = new Float32Array(n * 3);
    this.geo = new THREE.BufferGeometry();
    this.geo.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));
    this.rain = new THREE.Points(this.geo, new THREE.PointsMaterial({
      color: 0x9fb8cc, size: 0.12, transparent: true, opacity: 0, sizeAttenuation: true,
    }));
    this.rain.frustumCulled = false;
    this.engine.scene.add(this.rain);
    for (let i = 0; i < n; i++) this._randomize(i);
  }

  _randomize(i) {
    const x = (Math.random() - 0.5) * 120;
    const y = 30 + Math.random() * 50;
    const z = (Math.random() - 0.5) * 120;
    this.positions[i * 3] = x;
    this.positions[i * 3 + 1] = y;
    this.positions[i * 3 + 2] = z;
  }

  update(dt, playerPos) {
    // State machine
    this._nextChange -= dt;
    if (this._nextChange <= 0) {
      this._nextChange = 40 + Math.random() * 60;
      if (this.state === 'clear') {
        if (Math.random() < 0.5) this.setWeather('rain');
        else if (Math.random() < 0.3) this.setWeather('storm');
      } else {
        this.setWeather('clear');
      }
    }

    // Smooth rain
    this.rainIntensity += (this.targetRain - this.rainIntensity) * Math.min(1, dt * 0.7);
    if (this.rainIntensity < 0.01) this.rainIntensity = 0;

    // Rain particles follow player
    this.rain.position.set(playerPos.x, 0, playerPos.z);
    this.rain.material.opacity = this.rainIntensity * 0.8;
    if (this.rainIntensity > 0.01) {
      const arr = this.geo.attributes.position.array;
      for (let i = 0; i < 800; i++) {
        arr[i * 3 + 1] -= 45 * dt;
        if (arr[i * 3 + 1] < playerPos.y - 5) {
          this._randomize(i);
          arr[i * 3 + 1] = playerPos.y + 50;
          arr[i * 3] = playerPos.x + (Math.random() - 0.5) * 120;
          arr[i * 3 + 2] = playerPos.z + (Math.random() - 0.5) * 120;
        }
      }
      this.geo.attributes.position.needsUpdate = true;
    }

    // Storm lightning
    if (this.state === 'storm') {
      this._thunderTimer -= dt;
      if (this._thunderTimer <= 0) {
        this._thunderTimer = 3 + Math.random() * 8;
        this.stormFlash = 1;
        this.engine.audio?.thunder();
        events.emit('weather:lightning', { x: playerPos.x, z: playerPos.z });
      }
    }
    this.stormFlash = Math.max(0, this.stormFlash - dt * 2);

    // Apply to engine lights + fog
    const dim = this.rainIntensity;
    this.engine.scene.fog.near = 30 + dim * 8;
    if (this.stormFlash > 0) {
      const flash = this.stormFlash * 0.6;
      this.engine.ambient.intensity += flash;
      this.engine.sun.intensity += flash;
    }

    this.engine.audio?.setWeather?.(this.rainIntensity);
    events.emit('weather:changed', { state: this.state, rainIntensity: this.rainIntensity });
  }

  setWeather(state) {
    this.state = state;
    this.targetRain = state === 'clear' ? 0 : state === 'rain' ? 0.8 : 1;
    if (state === 'rain' || state === 'storm') this.engine.audio?.wind(3);
    events.emit('weather:set', { state });
  }

  dispose() {
    this.engine.scene.remove(this.rain);
    this.geo.dispose();
    this.engine.audio?.setWeather?.(0);
  }
}

export default WeatherSystem;