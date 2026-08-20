// Central configuration + build metadata for PlayTree Chapter I: Season I.

export const VERSION = {
  game: '1.0.0',
  chapter: 'I',
  season: 'I',
  seasonName: 'The Sprouting',
  build: 1,
};

export const CONFIG = {
  name: 'PlayTree',
  title: 'Chapter I: Season I',
  maxPlayersPerServer: 24,

  world: {
    chunkSize: 32,
    chunkHeight: 96,
    worldRadius: 96,             // chunks loaded in radius around player
    viewDistance: { low: 3, medium: 5, high: 7, ultra: 9 },
    seaLevel: 30,
    baseHeight: 48,
    dayLengthSeconds: 480,       // real seconds per in-game day
    startTimeOfDay: 0.3,         // morning
    gravity: -28,
    maxBuildHeight: 128,
  },

  gameplay: {
    defaultHealth: 100,
    defaultMaxStamina: 100,
    sprintStaminaCost: 14,
    staminaRegen: 22,
    sprintSpeed: 8.6,
    walkSpeed: 5.2,
    jumpVelocity: 9.2,
    swimSpeed: 3.2,
    reach: 6,
    buildReach: 9,
    xpToLevelBase: 100,
    xpToLevelGrowth: 1.35,
    maxLevel: 100,
  },

  br: {
    zoneRadiusStart: 400,
    zoneShrinkDelay: 15,         // seconds before first shrink
    zoneShrinkTime: 40,          // seconds per shrink
    zoneWarnTime: 8,
    stormDamage: 4,              // per second
    stormDamageGrowth: 0.25,
    matchLengthMinutes: 18,
    lootCrates: 140,
    supplyDrops: 5,
    startHeight: 180,
    dropTime: 6,
    teams: { solo: 1, duo: 2, squad: 4 },
  },

  net: {
    tickRate: 20,
    wsPort: 8765,
    reconnectDelay: 2,
    maxReconnects: 6,
    pingInterval: 3,
  },

  storage: {
    versionKey: 'pt.ch1s1.storageVersion',
    saveVersion: 3,
  },

  input: {
    mouseSensitivity: { low: 1.2, medium: 2.0, high: 3.2 },
    gamepadLookScale: 3.2,
    touchLookScale: 0.28,
  },
};

export const QUALITY_PRESETS = {
  low:    { renderDistance: 3, pixelRatio: 0.6, shadows: false, particles: 0.4, clouds: false, ao: false, grassDetail: 0.5, waterReflections: false, foliageDensity: 0.7 },
  medium: { renderDistance: 5, pixelRatio: 1.0, shadows: true,  particles: 0.7, clouds: true,  ao: true,  grassDetail: 1.0, waterReflections: false, foliageDensity: 1.0 },
  high:   { renderDistance: 7, pixelRatio: 1.25, shadows: true, particles: 1.0, clouds: true, ao: true, grassDetail: 1.5, waterReflections: true, foliageDensity: 1.0 },
  ultra:  { renderDistance: 9, pixelRatio: 1.5, shadows: true,  particles: 1.2, clouds: true, ao: true, grassDetail: 2.0, waterReflections: true, foliageDensity: 1.0 },
};

export default CONFIG;