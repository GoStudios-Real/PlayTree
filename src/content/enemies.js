// PlayTree hostile creatures + boss definitions (original designs).

export const ENEMIES = {
  grub: {
    name: 'Murk Grub', color: 0x6b5a3a, sub: 0x8a7a55, hp: 20, speed: 2.6,
    width: 0.7, height: 0.6, damage: 6, attackRange: 1.6, attackCooldown: 1.1,
    xp: 10, exp: 20, loot: [[300, 0.5]], kind: 'melee',
  },
  shade: {
    name: 'Nightshade', color: 0x3a3550, sub: 0x574f6e, hp: 35, speed: 3.6,
    width: 0.7, height: 1.5, damage: 10, attackRange: 1.8, attackCooldown: 1.0,
    xp: 20, exp: 40, loot: [[59, 0.3], [401, 0.6]], kind: 'melee',
  },
  brute: {
    name: 'Bark Brute', color: 0x5a4a35, sub: 0x7a664a, hp: 70, speed: 2.4,
    width: 0.9, height: 1.7, damage: 16, attackRange: 2.2, attackCooldown: 1.3,
    xp: 40, exp: 80, loot: [[6, 0.8], [400, 0.7]], kind: 'melee',
  },
  spitter: {
    name: 'Puff Spitter', color: 0x6a8a4a, sub: 0x8fae68, hp: 30, speed: 2.2,
    width: 0.8, height: 1.0, damage: 8, attackRange: 14, attackCooldown: 2.0,
    ranged: true, projectile: 'acid', xp: 25, exp: 50, loot: [[26, 0.4]], kind: 'ranged',
  },
  wraith: {
    name: 'Cave Wraith', color: 0x2a2a44, sub: 0x4a4a6e, hp: 55, speed: 4.4,
    width: 0.7, height: 1.8, damage: 14, attackRange: 2.0, attackCooldown: 0.9,
    xp: 35, exp: 70, loot: [[50, 0.5], [62, 0.1]], kind: 'melee',
  },
  boss_titan: {
    name: 'The Root Titan', color: 0x4a3a2a, sub: 0x6e5a3e, hp: 900, speed: 2.0,
    width: 2.2, height: 4.2, damage: 30, attackRange: 3.5, attackCooldown: 1.6,
    boss: true, xp: 500, exp: 1000, loot: [[63, 3], [62, 4], [61, 8]], kind: 'melee',
  },
  boss_queen: {
    name: 'The Ember Queen', color: 0xb04020, sub: 0xe06030, hp: 650, speed: 3.0,
    width: 1.4, height: 2.6, damage: 22, attackRange: 3.0, attackCooldown: 1.2,
    boss: true, ranged: true, projectile: 'fireball', xp: 400, exp: 800, loot: [[61, 6], [63, 2]], kind: 'mixed',
  },
};

export default ENEMIES;