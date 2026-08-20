// Game: central orchestrator. Owns the active world, player, systems and mode.
// Modes plug in via the BaseMode contract.

import { events } from '../core/Events.js';
import { CONFIG } from '../core/Config.js';
import { World } from '../world/World.js';
import { Player } from '../player/Player.js';
import { ThirdPersonCamera } from '../player/ThirdPersonCamera.js';
import { EntityManager } from '../entities/EntityManager.js';
import { ParticleSystem } from '../systems/ParticleSystem.js';
import { BlockInteraction } from '../systems/BlockInteraction.js';
import { CombatSystem } from '../systems/CombatSystem.js';
import { CraftingSystem } from '../systems/CraftingSystem.js';
import { FarmingSystem } from '../systems/FarmingSystem.js';
import { QuestSystem } from '../systems/QuestSystem.js';
import { XPProgress } from '../systems/XPProgress.js';
import { AchievementSystem } from '../systems/AchievementSystem.js';
import { DayNightCycle } from '../systems/DayNightCycle.js';
import { WeatherSystem } from '../systems/WeatherSystem.js';
import { ChatSystem } from '../systems/ChatSystem.js';
import { SocialSystem } from '../systems/SocialSystem.js';
import { Moderation } from '../systems/ModerationSystem.js';
import { LeaderboardSystem } from '../systems/LeaderboardSystem.js';
import { ServerBrowser } from '../systems/ServerBrowser.js';
import { StoreSystem } from '../systems/StoreSystem.js';
import { Structures } from '../world/Structures.js';
import { getItem } from '../content/items.js';
import { getBlock } from '../content/blocks.js';

export class Game {
  constructor(engine) {
    this.engine = engine;
    this.state = 'menu';       // menu | playing | paused | loading
    this.mode = null;          // active mode instance
    this.world = null;
    this.player = null;
    this.camera = null;
    this.entities = null;
    this.otherPlayers = [];
    this.ui = null;            // set by UI manager
    this.bots = [];
    this.started = false;
    this.frameCount = 0;
    this.sensitivityMul = 1;

    // Systems that don't depend on a world
    this.xp = new XPProgress(this, null);
    this.chat = new ChatSystem(this);
    this.social = new SocialSystem(this);
    this.moderation = new Moderation(this);
    this.leaderboard = new LeaderboardSystem(this);
    this.serverBrowser = new ServerBrowser(this);
    this.store = new StoreSystem(this);
    this.social.login('Sprout', '1');
    this.store.addCoins(0);

    engine.addUpdater((dt, t) => this.update(dt, t), 10);
  }

  setUI(ui) { this.ui = ui; }

  setMode(name, opts = {}) {
    this.launchWorld(name, opts);
  }

  // ---------- World / mode lifecycle ----------
  launchWorld(modeName, opts = {}) {
    this.state = 'loading';
    this._teardownWorld();
    this.ui?.showLoading(`Planting the seed... ${modeName}`);

    // Build world
    const world = new World(this.engine, { seed: opts.seed ?? (Date.now() >>> 0) });
    this.world = world;
    world.game = this;
    world.localPlayer = null;
    world.loot = null;

    // Systems that need a world
    this.entities = new EntityManager(world, this.engine);
    world.loot = this.entities;
    world.entities = this.entities;
    this.particles = new ParticleSystem(this.engine);
    this.engine.particles = this.particles;
    world.particles = this.particles;
    world.spawnProjectile = (o) => this.entities.spawnProjectile(o);
    world.explode = (x, y, z, r, d, from) => this.entities.explode(x, y, z, r, d, from);
    world.hitEntities = (x, y, z, r, from) => this.entities.hitEntities(x, y, z, r, from);
    world.awardKill = (from, target) => this.awardKill(from, target);

    // Player
    for (let dx = -1; dx <= 1; dx++)
      for (let dz = -1; dz <= 1; dz++)
        world.buildChunkSync(dx, dz);
    const spawn = world.findSafeSpawn(0, 0);
    this.player = new Player(world, {
      x: spawn[0], y: spawn[1], z: spawn[2],
      nickname: this.social.profile?.nickname || 'Sprout',
      inventory: (opts.keepInventory && this.player) ? this.player.inventory : undefined,
    });
    world.localPlayer = this.player;
    this.player.world = world;
    this.player.game = this;

    this.camera = new ThirdPersonCamera(this.engine);
    this.camera.setTarget(this.player);
    this.engine.camera = this.camera.camera;
    this.engine.scene.add(this.player.entityGroup);

    // World systems
    this.blockInteraction = new BlockInteraction(this.engine, world, this.player);
    this.combat = new CombatSystem(this, this.player);
    this.crafting = new CraftingSystem(this);
    this.farming = new FarmingSystem(this);
    this.dayNight = new DayNightCycle(this.engine, world);
    this.weather = new WeatherSystem(this.engine, world);
    if (this.engine.settings.get('quality') !== 'low') {
      this.weather.setWeather('clear');
    }

    // Quest system (new per world so progress resets per session but persists saved state)
    this.quests = new QuestSystem(this);

    // BlockInteraction needs player.game
    this.player.game = this;
    this.blockInteraction.player = this.player;

    // Load edits
    world.loadEdits();

    // Apply avatar style
    this.applyAvatarStyle();

    // Start mode
    const ModeClass = MODES[modeName] || MODES.adventure;
    this.mode = new ModeClass(this, opts);
    this.mode.world = world;
    this.mode.onStart(opts);

    this.state = 'playing';
    events.emit('game:started', { mode: modeName, seed: world.seed });
    this.social.markPlayed(modeName, opts.serverName || this.world.getBiome(0, 0)?.name || 'The Grove');
    this.ui?.closeAll();
    this.ui?.hideLoading();
    this.ui?.showHUD();
    this._loadTime = performance.now();
  }

  applyAvatarStyle() {
    const style = this.store.styleForAvatar();
    if (this.player) {
      this.player.avatar.applyStyle({ ...this.player.avatar.style, ...style });
    }
  }

  _teardownWorld() {
    if (this.mode) { try { this.mode.onStop(); } catch {} this.mode = null; }
    if (this.quests) { this.quests.dispose(); this.quests = null; }
    if (this.farming) { this.farming.dispose(); this.farming = null; }
    if (this.weather) { this.weather.dispose(); this.weather = null; }
    if (this.entities) { this.entities.removeAll(); this.entities = null; }
    if (this.blockInteraction) { this.blockInteraction.destroy(); this.blockInteraction = null; }
    if (this.combat) this.combat = null;
    if (this.particles) { this.engine.scene.remove(this.particles.points); this.particles = null; this.engine.particles = null; }
    if (this.player?.entityGroup) this.engine.scene.remove(this.player.entityGroup);
    this.player = null;
    if (this.world) {
      for (const c of this.world.chunks.values()) this.world.unloadChunk(c);
      this.world = null;
    }
    this.otherPlayers = [];
    this.bots = [];
    this.engine.scene.traverse(o => {
      if (o.isMesh && o.name !== 'chunk-solid' && o.name !== 'chunk-water') {
        if (o.geometry) o.geometry.dispose();
        if (o.material) o.material.dispose();
      }
    });
  }

  returnToMenu() {
    this._teardownWorld();
    this.state = 'menu';
    this.ui?.showMainMenu();
    events.emit('game:ended');
  }

  // ---------- Input routing ----------
  handleInput(dt) {
    if (this.state !== 'playing') return;
    if (this.inputFrozen) return;
    const input = this.engine.input;

    // Look
    const look = input.takeLook();
    if (this.camera && (look.dx !== 0 || look.dy !== 0)) {
      this.camera.look(look.dx * this.sensitivityMul, look.dy * this.sensitivityMul, this.engine.settings.values);
    }

    // Hotbar scroll
    const wheel = input.takeWheel();
    if (wheel !== 0) {
      const dir = wheel > 0 ? 1 : -1;
      const next = (this.player.inventory.selected + dir + 9) % 9;
      this.player.inventory.select(next);
      this.combat?.onSlotChange?.();
    }

    // Hotbar number keys
    for (let i = 0; i < 9; i++) {
      if (input.pressed('hotbar' + (i + 1))) {
        this.player.inventory.select(i);
        this.combat?.onSlotChange?.();
      }
    }

    // Attack (mouse0)
    if (input.down('attack')) {
      const hitBlock = this.blockInteraction.raycast();
      const lookingAtBlock = hitBlock?.hit;
      if (this.mode?.blockInteractionPriority === 'break' || (lookingAtBlock && this.blockInteraction.mode === 'creative')) {
        this.blockInteraction.mine(dt);
      } else if (lookingAtBlock && this.blockInteraction.mode === 'survival') {
        // If holding a block item, left click breaks blocks; if weapon, attacks
        const sel = this.player.inventory.selectedSlot;
        const item = sel ? getItem(sel.id) : null;
        if (item && (item.type === 'weapon' || item.type === 'tool')) {
          this.blockInteraction.mine(dt);
          if (this.blockInteraction.mode === 'creative') { }
          this.combat.attack();
        } else {
          this.blockInteraction.mine(dt);
        }
      } else if (!lookingAtBlock) {
        this.combat.attack();
      }
    } else {
      this.blockInteraction.mining = null;
      this.blockInteraction.miningProgress = 0;
    }

    // Use / place (mouse1)
    if (input.pressed('use')) {
      const sel = this.player.inventory.selectedSlot;
      const item = sel ? getItem(sel.id) : null;
      if (item?.type === 'block') {
        this.blockInteraction.place(sel);
      } else if (item?.type === 'consumable') {
        this._useConsumable(item, sel);
      } else if (item?.type === 'seed') {
        this._plantSeed(item, sel);
      } else if (item?.type === 'weapon' && item.weapon.kind === 'gun') {
        this.combat.reload();
      } else {
        this.blockInteraction.use(sel);
      }
    }

    // Fly toggle (V)
    if (this.mode?.allowFly && input.pressed('flyToggle')) {
      this.player.setFlying(!this.player.flying);
      this.ui?.toast(this.player.flying ? 'Flight on' : 'Flight off', 1500);
    }

    // Reload (R)
    if (input.pressed('rotate')) {
      this.combat.reload();
    }

    // Item use (E while not opening inventory handled by UI)
    if (input.pressed('drop')) {
      this._dropSelected();
    }
  }

  _useConsumable(item, slot) {
    if (this.player.dead) return;
    if (item.heal && this.player.health < this.player.maxHealth) {
      this.player.heal(item.heal);
      this.player.inventory.removeFromSlot(this.player.inventory.selected, 1);
      this.engine.audio?.eat();
      events.emit('item:consumed', { itemId: item.id });
    } else if (item.shield) {
      this.player.addShield(item.shield);
      this.player.inventory.removeFromSlot(this.player.inventory.selected, 1);
      this.engine.audio?.eat();
    } else {
      this.ui?.toast('You are already at full health.', 1500);
    }
  }

  _plantSeed(item, slot) {
    const hit = this.blockInteraction.raycastEmpty();
    if (hit && hit.hit) {
      const { x, y, z } = hit;
      if (this.farming.plantSeed(this.player, x, y, z, item.id)) {
        this.player.inventory.removeFromSlot(this.player.inventory.selected, 1);
      }
    }
  }

  _dropSelected() {
    const slot = this.player.inventory.selectedSlot;
    if (!slot) return;
    this.entities.spawnLoot(this.player.pos.x, this.player.pos.y + 1.2, this.player.pos.z, slot.id, 1);
    this.player.inventory.removeFromSlot(this.player.inventory.selected, 1);
    this.engine.audio?.drop();
  }

  // ---------- Main update ----------
  update(dt, t) {
    this.frameCount++;
    if (this.state !== 'playing' || !this.world || !this.player) return;
    this.xp.player = this.player;

    this.handleInput(dt);

    // Player movement
    this.player.update(dt, this.engine.input, true);

    // World streaming
    this.world.update(dt, this.player.pos.x, this.player.pos.z);
    this.world.localPlayer = this.player;
    this.world.otherPlayers = this.otherPlayers;

    // Camera
    this.camera.update(dt, this.player);

    // Entities + bots
    this.entities.update(dt, this.player, this.dayNight.timeOfDay);
    this.updateBots(dt);

    // Block interaction + combat
    this.blockInteraction.update(dt);
    this.combat.update(dt);
    this.farming.update(dt, this.player);

    // Time + weather
    this.dayNight.update(dt, this.weather);
    this.weather.update(dt, this.player.pos);

    // Particles
    this.particles.update(dt);

    // Mode logic
    if (this.mode) this.mode.update(dt);

    // XP playtime + distance stats
    this.xp.addStat('playtime', dt);
    const move = Math.hypot(this.player.vel.x, this.player.vel.z) * dt;
    if (move > 0) {
      this.xp.addStat('distance', move);
      this.xp.stats.distance += 0; // no double count
    }

    // Save world edits periodically
    if (this.frameCount % 300 === 0) this.world.saveEdits();

    // Damage vignette decay
    this.ui?.updateVignette?.(dt);
  }

  updateBots(dt) {
    for (const bot of this.bots) {
      if (bot.update) bot.update(dt);
    }
  }

  awardKill(from, target) {
    if (!from || !target) return;
    const isPlayerKill = from === this.player || from?.id === this.player?.id;
    const enemyType = target.type;
    const isBoss = target.boss;
    if (isPlayerKill && enemyType) {
      this.xp.recordKill(enemyType, target.def?.xp || 10, target.def?.exp || 20);
      if (isBoss) {
        this.xp.addStat('bossesKilled');
        this.ui?.announce(`${target.name} has been defeated!`, 'The grove breathes easier.');
        if (this.mode?.onBossDefeated) this.mode.onBossDefeated(target);
      } else {
        this.ui?.announce(`${target.name} defeated`, null, 2500);
      }
    }
    if (this.mode?.onKill) this.mode.onKill(from, target);
  }

  setModeState(state) { this.state = state; }

  pause() {
    if (this.state !== 'playing') return;
    this.state = 'paused';
    this.engine.input.exitPointerLock();
    events.emit('game:paused');
  }

  resume() {
    if (this.state !== 'paused') return;
    this.state = 'playing';
    this.engine.input.requestPointerLock(this.engine.canvas);
    events.emit('game:resumed');
  }

  // Interact with NPC / chest
  interact() {
    if (this.state !== 'playing' || !this.player) return;
    const hit = this.blockInteraction.raycast(3.4);
    if (hit?.hit) {
      const id = this.world.getBlock(hit.x, hit.y, hit.z);
      if (id === 39) { // crate
        this.ui?.openCrate(this._crateLoot());
        return;
      }
      if (id === 38) { // assembly table
        this.ui?.openCrafting('table');
        return;
      }
    }
    // Nearby NPC?
    const npcs = this.entities?.npcs || new Map();
    for (const npc of npcs.values()) {
      const d = Math.hypot(npc.pos.x - this.player.pos.x, npc.pos.z - this.player.pos.z);
      if (d < npc.interactDistance) {
        npc.interact(this.player);
        return;
      }
    }
  }

  toggleInventory() { this.ui?.toggleInventory(); }
  toggleMap() { this.ui?.toggleMap(); }
  toggleQuests() { this.ui?.toggleQuests(); }

  // Rolls a small pile of loot for opened crates.
  _crateLoot() {
    const rolls = [];
    const table = [5, 6, 8, 9, 20, 26, 39, 46, 55, 300, 301, 302, 303];
    const n = 2 + Math.floor(Math.random() * 3);
    for (let i = 0; i < n; i++) {
      const id = table[Math.floor(Math.random() * table.length)];
      const count = 1 + Math.floor(Math.random() * 4);
      const existing = rolls.find(r => r.id === id);
      if (existing) existing.count += count;
      else rolls.push({ id, count });
    }
    return rolls;
  }

  get FPS() { return this.engine.fps; }
}

// Mode registry
export const MODES = {};
export function registerMode(name, cls) { MODES[name] = cls; }

export default Game;