// Player entity: physics, movement, health/stamina, and gameplay hooks.
// Uses voxel AABB collision from MathUtils.

import * as THREE from '../../vendor/three.module.js';
import { AABB, boxCollide, clamp, directionFromYaw } from '../core/MathUtils.js';
import { CONFIG } from '../core/Config.js';
import { events } from '../core/Events.js';
import { getBlock } from '../content/blocks.js';
import { Inventory, HOTBAR_SIZE } from './Inventory.js';
import { Avatar } from './Avatar.js';

export class Player {
  constructor(world, opts = {}) {
    this.world = world;
    this.id = opts.id || 'local';
    this.nickname = opts.nickname || 'Player';
    this.pos = { x: opts.x ?? 8.5, y: opts.y ?? 60, z: opts.z ?? 8.5 };
    this.vel = { x: 0, y: 0, z: 0 };
    this.yaw = opts.yaw ?? 0;
    this.pitch = opts.pitch ?? 0;
    this.width = 0.6;
    this.height = 1.8;
    this.eyeHeight = 1.62;
    this.onGround = false;
    this.inWater = false;
    this.isSwimming = false;
    this.crouching = false;
    this.sprinting = false;
    this.flying = false;
    this.speedRatio = 0;

    this.health = CONFIG.gameplay.defaultHealth;
    this.maxHealth = CONFIG.gameplay.defaultHealth;
    this.shield = 0;
    this.maxShield = 100;
    this.stamina = CONFIG.gameplay.defaultMaxStamina;
    this.maxStamina = CONFIG.gameplay.defaultMaxStamina;
    this.hunger = 100;
    this.armor = 0;
    this.dead = false;

    this.inventory = opts.inventory || new Inventory();
    this.avatar = new Avatar(opts.style);
    this.entityGroup = new THREE.Group();
    this.entityGroup.add(this.avatar.group);
    this.avatar.heldItem.visible = false;
    this.currentToolTier = 1;

    this.reach = CONFIG.gameplay.reach;
    this.buildReach = CONFIG.gameplay.buildReach;

    // Animation state
    this.attackAnim = 0;
    this.useAnim = 0;
    this._inBlock = false;
    this.spawned = false;
  }

  getEye() { return { x: this.pos.x, y: this.pos.y + this.eyeHeight, z: this.pos.z }; }

  getAimDir() {
    const cy = Math.cos(this.pitch), sy = Math.sin(this.pitch);
    const cx = Math.cos(this.yaw), sx = Math.sin(this.yaw);
    return { x: -sx * cy, y: sy, z: -cx * cy };
  }

  getAABB() {
    return AABB.fromPosSize(this.pos.x, this.pos.y, this.pos.z, this.width, this.height, this.width);
  }

  isCreative() { return this.flying || this.world.game?.mode === 'creative'; }

  setFlying(f) { this.flying = f; this.vel.y = 0; }

  teleport(x, y, z) {
    this.pos.x = x; this.pos.y = y; this.pos.z = z;
    this.vel.x = 0; this.vel.y = 0; this.vel.z = 0;
  }

  applyDamage(amount, source = {}) {
    if (this.dead) return 0;
    let dmg = amount;
    if (this.shield > 0) {
      const absorbed = Math.min(this.shield, dmg);
      this.shield -= absorbed;
      dmg -= absorbed;
    }
    dmg = Math.max(0, dmg - this.armor);
    this.health -= dmg;
    events.emit('player:damaged', { player: this, amount: dmg, source, health: this.health, shield: this.shield });
    if (this.health <= 0) {
      this.health = 0;
      this.die(source);
    }
    return dmg;
  }

  heal(amount) {
    this.health = Math.min(this.maxHealth, this.health + amount);
    events.emit('player:healed', { player: this, health: this.health });
  }

  addShield(amount) {
    this.shield = Math.min(this.maxShield, this.shield + amount);
    events.emit('player:shield', { player: this, shield: this.shield });
  }

  die(source) {
    this.dead = true;
    this.health = 0;
    events.emit('player:death', { player: this, source });
  }

  respawn(x, y, z) {
    this.dead = false;
    this.health = this.maxHealth;
    this.shield = 0;
    this.teleport(x, y, z);
    events.emit('player:respawn', { player: this });
  }

  update(dt, input, isLocal = true) {
    const cfg = CONFIG.gameplay;
    const bb = this.getAABB();

    // Water detection
    const headBlock = getBlock(this.world.getBlock(Math.floor(this.pos.x), Math.floor(this.pos.y + 1), Math.floor(this.pos.z)));
    const footBlock = getBlock(this.world.getBlock(Math.floor(this.pos.x), Math.floor(this.pos.y + 0.2), Math.floor(this.pos.z)));
    this.inWater = headBlock.liquid || footBlock.liquid;

    // Input
    let ix = 0, iz = 0;
    if (isLocal && input) {
      ix = input.axisX('right') - input.axisX('left');
      iz = input.axis('forward') - input.axis('back');
      this.sprinting = input.down('sprint') && iz > 0 && !this.inWater;
      this.crouching = input.down('crouch');
    }

    const len = Math.hypot(ix, iz);
    if (len > 1) { ix /= len; iz /= len; }

    // Aim direction in world space (yaw=0 faces -Z)
    const fwd = directionFromYaw(this.yaw);
    const cosY = Math.cos(this.yaw), sinY = Math.sin(this.yaw);
    const wishX = -sinY * iz + cosY * ix;
    const wishZ = -cosY * iz - sinY * ix;

    // Determine speed
    let speed = this.crouching ? cfg.walkSpeed * 0.5 : (this.sprinting ? cfg.sprintSpeed : cfg.walkSpeed);
    if (this.inWater) speed = cfg.swimSpeed;
    if (this.flying) speed = this.sprinting ? cfg.sprintSpeed * 1.8 : cfg.sprintSpeed * 1.2;
    this.speedRatio = Math.hypot(this.vel.x, this.vel.z) / cfg.walkSpeed;

    // Stamina
    if (this.sprinting && !this.inWater) {
      this.stamina = Math.max(0, this.stamina - cfg.sprintStaminaCost * dt);
      if (this.stamina <= 0) this.sprinting = false;
    } else if (!this.sprinting) {
      this.stamina = Math.min(this.maxStamina, this.stamina + cfg.staminaRegen * dt);
    }

    // Horizontal acceleration
    const accel = this.onGround ? 30 : 12;
    const targetVX = wishX * speed;
    const targetVZ = wishZ * speed;
    this.vel.x += (targetVX - this.vel.x) * Math.min(1, accel * dt);
    this.vel.z += (targetVZ - this.vel.z) * Math.min(1, accel * dt);

    // Jump
    if (isLocal && input && input.pressed('jump')) {
      if (this.flying) {
        this.vel.y = cfg.sprintSpeed * 0.9;
      } else if (this.onGround) {
        this.vel.y = cfg.jumpVelocity;
        this.onGround = false;
      } else if (this.inWater) {
        this.vel.y = Math.min(this.vel.y + cfg.jumpVelocity * 0.6 * dt, 4.5);
      }
    }
    // Fly up/down
    if (this.flying && isLocal && input) {
      if (input.down('flyUp')) this.vel.y = Math.min(this.vel.y + 30 * dt, 6);
      if (input.down('flyDown')) this.vel.y = Math.max(this.vel.y - 30 * dt, -6);
    }

    if (!this.flying) this.vel.y += CONFIG.world.gravity * dt;
    if (this.inWater) this.vel.y = Math.max(this.vel.y, -3.2);

    // Cap terminal velocity
    this.vel.y = Math.max(this.vel.y, -60);

    // Integrate with collision
    const blocks = (x, y, z) => {
      const id = this.world.getBlock(x, y, z);
      return getBlock(id).solid;
    };
    const prevOnGround = this.onGround;
    this.vel = boxCollide(bb, blocks, this.vel, dt);
    this.pos.x = bb.cx;
    this.pos.y = bb.minY;
    this.pos.z = bb.cz;
    this.onGround = Math.abs(this.vel.y) < 0.001 && this.vel.y >= 0;
    if (this.onGround && !prevOnGround && this.vel.y === 0 && bb.minY > 0) {
      events.emit('player:land', { player: this });
    }
    this.vel.y *= (this.onGround && !this.flying) ? 0 : 1;

    // Fall damage
    if (this.vel.y < -0.1 && this.onGround) { /* handled by landing velocity */ }

    // Animation
    this.attackAnim = Math.max(0, this.attackAnim - dt);
    this.useAnim = Math.max(0, this.useAnim - dt);
    this.avatar.update(dt, Math.hypot(this.vel.x, this.vel.z) > 0.5, this.speedRatio);

    // Sync entity group (avatar front faces -Z, same as aim at yaw=0)
    this.entityGroup.position.set(this.pos.x, this.pos.y, this.pos.z);
    this.entityGroup.rotation.y = this.yaw;
  }

  setHeldVisual(color, size) {
    this.avatar.setHeldItem(color, size);
    this.avatar.heldItem.visible = !!color;
  }
}

export default Player;