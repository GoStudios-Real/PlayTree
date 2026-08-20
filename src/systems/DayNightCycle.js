// Day/night cycle: advances in-game clock, drives sun/moon lighting, sky color,
// and emits time events. Also tracks calendar date.

import { CONFIG } from '../core/Config.js';
import { events } from '../core/Events.js';
import { fmtClock } from '../core/MathUtils.js';
import * as THREE from '../../vendor/three.module.js';

export class DayNightCycle {
  constructor(engine, world) {
    this.engine = engine;
    this.world = world;
    this.timeOfDay = CONFIG.world.startTimeOfDay;   // 0..1
    this.day = 1;
    this.dayLength = CONFIG.world.dayLengthSeconds;
    this.paused = false;
    this.speedMul = 1;
    this.stars = null;
    this._buildStars();
  }

  _buildStars() {
    const n = 500;
    const pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1) * 0.5 + Math.PI * 0.5;
      const r = 900;
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.cos(phi);
      pos[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.stars = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xffffff, size: 1.2, sizeAttenuation: false, transparent: true, opacity: 0 }));
    this.engine.scene.add(this.stars);
  }

  _sunColor(elev) {
    const day = new THREE.Color(0xfff4d6);
    const dusk = new THREE.Color(0xff8c42);
    const night = new THREE.Color(0x9fb4cc);
    if (elev > 0.15) return day.getHex();
    if (elev > -0.05) return dusk.clone().lerp(day, (elev + 0.05) / 0.2).getHex();
    return night.clone().lerp(dusk, Math.min(1, (-elev - 0.05) / 0.25)).getHex();
  }

  getHour() {
    return (this.timeOfDay * 24 + 6) % 24;
  }

  getClockText() {
    return fmtClock(this.getHour(), Math.floor((this.timeOfDay * 24 % 1) * 60));
  }

  update(dt, weather = null) {
    if (!this.paused) {
      this.timeOfDay += (dt / this.dayLength) * this.speedMul;
      if (this.timeOfDay >= 1) {
        this.timeOfDay -= 1;
        this.day++;
        events.emit('day:new', { day: this.day });
      }
    }

    const t = this.timeOfDay;
    // Solar elevation: sun peaks at noon (t=0.5)
    const angle = (t - 0.5) * Math.PI * 2;
    const sunElevation = Math.sin(angle);
    const sunIntensity = Math.max(0.15, sunElevation);
    const moonlight = 0.35 * (1 - Math.max(0, sunElevation));

    // Weather dimming
    let dim = 1;
    if (weather) dim = Math.max(0.35, 1 - (weather.rainIntensity || 0) * 0.45);

    const sun = this.engine.sun;
    const radius = 120;
    sun.position.set(
      Math.cos(angle) * radius,
      Math.max(-40, Math.sin(angle) * radius),
      Math.cos(angle) * 30
    );
    sun.target.position.set(0, 0, 0);
    sun.intensity = sunIntensity * dim * 1.4;
    sun.color.setHex(this._sunColor(sunElevation));

    this.engine.ambient.intensity = (0.38 + 0.42 * sunElevation) * dim;

    // Sky & fog
    const skyDay = new THREE.Color(0x87c5eb);
    const skyDusk = new THREE.Color(0xff9a5c);
    const skyNight = new THREE.Color(0x0a1230);
    let sky;
    if (sunElevation > 0.15) sky = skyDay;
    else if (sunElevation > -0.05) sky = skyDusk.lerp(skyDay, (sunElevation + 0.05) / 0.2);
    else sky = skyNight.clone().lerp(skyDusk, Math.min(1, (-sunElevation - 0.05) / 0.25));
    if (weather) {
      sky.lerp(new THREE.Color(0x7a8a92), Math.min(0.7, weather.rainIntensity || 0));
    }
    this.engine.scene.background = sky;
    if (this.engine.scene.fog) this.engine.scene.fog.color.copy(sky);

    // Stars
    if (this.stars) {
      const starVis = Math.max(0, Math.min(1, (-sunElevation - 0.1) * 6));
      this.stars.material.opacity = starVis * (weather ? Math.max(0, 1 - weather.rainIntensity) : 1);
    }

    this._t = t;
    events.emit('daynight:changed', { timeOfDay: t, hour: this.getHour(), day: this.day, sunElevation });
  }
}

export default DayNightCycle;