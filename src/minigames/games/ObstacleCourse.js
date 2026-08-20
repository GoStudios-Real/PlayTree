// Obstacle Course ("Canopy Dash"): race across floating platforms to the finish.

import { mulberry32 } from '../../core/MathUtils.js';
import { events } from '../../core/Events.js';

export class ObstacleCourse {
  constructor(game, opts = {}) {
    this.game = game;
    this.id = 'obstacle_course';
    this.name = 'Canopy Dash';
    this.icon = '🏃';
    this.description = 'Race across floating platforms to the finish line.';
    this.maxPlayers = 8;
    this.startTime = 0;
    this.finished = false;
    this.checkpoints = [];
    this.nextCheckpoint = 0;
    this.elapsed = 0;
  }

  onStart() {
    const g = this.game;
    g.blockInteraction.setMode('creative');
    g.player.setFlying(true);
    g.chat.system('Canopy Dash: reach all the checkpoints and cross the finish line!');

    // Build the course in the sky above the spawn
    const rng = mulberry32(g.world.seed + 777);
    const baseY = g.world.getSurfaceHeight(0, 0) + 20;
    const course = [];
    let x = 0, z = 0, y = baseY;
    for (let i = 0; i < 24; i++) {
      const step = 8 + rng() * 6;
      const dir = Math.floor(rng() * 4);
      if (dir === 0) x += step;
      else if (dir === 1) x -= step;
      else if (dir === 2) z += step;
      else z -= step;
      y += (rng() - 0.5) * 6;
      y = Math.max(baseY - 4, Math.min(baseY + 10, y));
      this._platform(x, y, z, i === 0 ? 6 : 3, i === 23);
      course.push({ x, y, z, index: i });
    }
    this.course = course;
    this.checkpoints = course;
    this.startTime = performance.now();

    g.player.teleport(course[0].x + 0.5, course[0].y + 2, course[0].z + 0.5);
    g.player.setFlying(false);

    this._interval = setInterval(() => this._check(), 500);
  }

  _platform(x, y, z, size, isFinish) {
    const g = this.game;
    const id = isFinish ? 43 : 8;
    for (let dx = -Math.floor(size / 2); dx <= Math.floor(size / 2); dx++) {
      for (let dz = -Math.floor(size / 2); dz <= Math.floor(size / 2); dz++) {
        g.world.setBlockAndRemesh(x + dx, y, z + dz, id);
      }
    }
    // checkpoint beacon
    if (isFinish) {
      g.world.setBlockAndRemesh(x, y + 1, z, 46);
    }
  }

  _check() {
    if (this.finished) return;
    const g = this.game;
    const p = g.player;
    const cp = this.checkpoints[this.nextCheckpoint];
    if (!cp) return;
    const d = Math.hypot(p.pos.x - cp.x, p.pos.z - cp.z, p.pos.y - cp.y);
    if (d < 4) {
      if (cp.index === this.checkpoints.length - 1) {
        this._finish();
      } else {
        this.nextCheckpoint++;
        g.ui?.toast(`Checkpoint ${this.nextCheckpoint}/${this.checkpoints.length - 1}`, 1500);
        g.engine.audio?.pickup();
      }
    }
    // Fall off the course?
    if (p.pos.y < 0) {
      p.teleport(this.checkpoints[Math.max(0, this.nextCheckpoint - 1)].x + 0.5, this.checkpoints[Math.max(0, this.nextCheckpoint - 1)].y + 2, this.checkpoints[Math.max(0, this.nextCheckpoint - 1)].z + 0.5);
      p.vel.y = 0;
    }
  }

  _finish() {
    this.finished = true;
    clearInterval(this._interval);
    this.elapsed = (performance.now() - this.startTime) / 1000;
    const score = Math.max(1, Math.round(10000 / Math.max(1, this.elapsed)));
    this.game.leaderboard.submit('obstacle_course', score, { time: this.elapsed });
    this.game.ui?.announce('FINISH!', `Time: ${this.elapsed.toFixed(1)}s`, 6000);
    this.game.engine.audio?.questComplete();
    events.emit('minigame:finished', { game: this.id, score, elapsed: this.elapsed });
    setTimeout(() => this.game.returnToMenu(), 6000);
  }

  update(dt) {
    if (this.finished) return;
  }

  onStop() {
    clearInterval(this._interval);
  }
}

export default ObstacleCourse;