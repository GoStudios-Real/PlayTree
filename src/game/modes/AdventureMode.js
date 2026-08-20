// Adventure Mode: Chapter I story — villages, NPCs, quests, bosses, secrets.

import { BaseMode } from './BaseMode.js';
import { buildVillage } from '../../world/Structures.js';
import { structuresPositions } from '../../content/story.js';
import { events } from '../../core/Events.js';
import { mulberry32 } from '../../core/MathUtils.js';

export class AdventureMode extends BaseMode {
  constructor(game, opts = {}) {
    super(game, opts);
    this.name = 'adventure';
    this.displayName = 'Adventure';
    this.description = 'Explore the grove, follow the Chapter I story, and face the Withering.';
    this.icon = '🗺️';
    this._villageBuilt = false;
    this._spawnNPCs = false;
    this.deathCount = 0;
  }

  onStart(opts = {}) {
    const g = this.game;
    g.blockInteraction.setMode('survival');
    g.chat.system('Welcome to Chapter I: Season I — "The Sprouting".');
    g.chat.system('Speak to Mayor Bramble at the Grove Town to begin your quests.');

    // Start the first story quest
    setTimeout(() => { g.quests?.startQuest('q_awakening'); }, 1200);

    // Player starts with a few basic supplies
    const inv = g.player.inventory;
    if (inv.countOf(101) === 0) inv.add(101, 1);   // wooden pick
    if (inv.countOf(300) === 0) inv.add(300, 8);   // berries
    if (inv.countOf(400) === 0) inv.add(400, 4);   // rope
    if (inv.countOf(8) === 0) inv.add(8, 16);      // planks

    // Spawn NPCs once village is built (chunks ready)
    this._on('player:death', () => this._onDeath());
    this._on('boss:defeated', (d) => this._onBossDefeated(d));
  }

  update(dt) {
    const g = this.game;
    // Build village + NPCs after the spawn chunks are generated
    if (!this._villageBuilt) {
      const c = g.world.getChunk(0, 0);
      if (c && c.status === 'ready' && g.world.getChunk(1, 0)?.status === 'ready') {
        this._villageBuilt = true;
        const rng = mulberry32(g.world.seed);
        buildVillage(g.world, 0, 0, rng);
        // Rebuild meshes around village for the flattened area
        for (let dx = -2; dx <= 2; dx++) for (let dz = -2; dz <= 2; dz++) {
          g.world.remeshChunk(dx, dz);
        }
        this._spawnStoryNPCs();
        this._placeSecretLocations();
        g.ui?.toast('Welcome to Grove Town, sprout!', 3000);
      }
    }
    // Quest tracker highlight
  }

  _spawnStoryNPCs() {
    const g = this.game;
    const spots = [
      { type: 'mayor', x: 0, z: -14 },        // near shrine
      { type: 'osmund', x: -8, z: -6 },
      { type: 'flora', x: 6, z: -5 },
      { type: 'sage', x: 8, z: 5 },
      { type: 'merchant', x: -2, z: -8 },
      { type: 'blacksmith', x: 12, z: -10 },
      { type: 'guard', x: -5, z: 6 },
      { type: 'kid', x: 3, z: 9 },
      { type: 'shrine', x: 0, z: -14 },
    ];
    for (const s of spots) {
      const y = g.world.getSurfaceHeight(s.x, s.z);
      g.entities.spawnNPC(s.type, s.x + 0.5, y + 1, s.z + 0.5);
    }
  }

  _placeSecretLocations() {
    const g = this.game;
    // Heartstone cave entrance (west of town, under a cliff)
    const cave = structuresPositions.heartstoneCave;
    const cy = g.world.getSurfaceHeight(cave.x, cave.z);
    // clear a cave mouth down into stone
    g.world.setBlockAndRemesh(cave.x, cy, cave.z, 0);
    g.world.setBlockAndRemesh(cave.x, cy + 1, cave.z, 0);
    for (let i = 1; i <= 4; i++) g.world.setBlockAndRemesh(cave.x, cy - i, cave.z, 0);
    g.world.setBlockAndRemesh(cave.x + 1, cy - 2, cave.z, 36);
    g.world.setBlockAndRemesh(cave.x - 1, cy - 2, cave.z, 36);
    g.world.remeshChunk(Math.floor(cave.x / 32), Math.floor(cave.z / 32));
    // Boss arena (deep under the cave)
    const arena = structuresPositions.titanArena;
    this._arenaPos = { ...arena };
  }

  _onDeath() {
    const g = this.game;
    this.deathCount++;
    g.chat.system('The grove calls you back. You wake in Grove Town.');
    g.xp.addXp(-Math.round(g.xp.xp * 0.05));
    g.player.respawn(4.5, g.world.getSurfaceHeight(4, 4) + 2, 4.5);
    g.ui?.toast('You were defeated. Respawned at Grove Town.', 3000);
  }

  _onBossDefeated(d) {
    const g = this.game;
    if (d.boss?.type === 'boss_titan') {
      g.ui?.announce('The Root Titan has fallen!', 'The Heartstone stirs...');
      // Spawn the finale quest
      g.quests?.startQuest('q_finale');
    }
    if (d.boss?.type === 'boss_queen') {
      g.ui?.announce('The Ember Queen is extinguished!', 'The desert sighs in relief.');
    }
  }

  onKill(from, target) {
    if (from === this.game.player && target?.type) {
      this.game.xp.addStat('kills');
    }
  }
}

export default AdventureMode;