import { BRZone } from '../src/br/BRZone.js';
import { CONFIG } from '../src/core/Config.js';

function stubGame() {
  const meshes = [];
  return {
    ui: { announce() {}, zoneWarning() {} },
    engine: {
      scene: { add(m) { meshes.push(m); } },
      audio: { zoneWarning() {} },
    },
    player: { applyDamage() {}, dead: false },
  };
}

export default function (assert) {
  const g = stubGame();
  const zone = new BRZone(g);
  assert(zone.radius === CONFIG.br.zoneRadiusStart, 'starts at max radius');
  assert(zone.inSafeZone(0, 0), 'center is safe');

  // Outside zone takes damage
  let dmg = 0;
  g.player.applyDamage = (d) => { dmg += d; };
  zone.update(0.1, { x: zone.radius + 50, z: 0 });
  assert(dmg > 0, 'outside zone takes damage');

  // Safe inside
  dmg = 0;
  zone.update(0.1, { x: 0, z: 0 });
  assert(dmg === 0, 'inside zone safe');

  // Zone eventually shrinks (fast-forward through delay)
  zone.state = 'waiting';
  zone.delayTimer = 0.01;
  // stub performance for deterministic shrinking
  const realPerf = globalThis.performance;
  globalThis.performance = {
    now: () => zone._simT || 0,
  };
  try {
    zone.update(0.05, { x: 0, z: 0 });
    assert(zone.state === 'shrinking', 'zone enters shrinking after delay');
  } finally {
    globalThis.performance = realPerf;
  }
}