// Combat system: melee and ranged weapons, ammo, reload, and damage routing.

import { events } from '../core/Events.js';
import { dist3d, directionFromYaw } from '../core/MathUtils.js';
import { getItem } from '../content/items.js';

const WEAPON_AMMO = {
  200: 250, 201: 250, 203: 250, 204: 250, 205: 250, 208: 250, // Bolt Rounds
  202: 251,                                                  // Shells
  207: 252,                                                  // Arrows
  206: 253, 209: 253,                                        // Barrel
};

export class CombatSystem {
  constructor(game, player) {
    this.game = game;
    this.player = player;
    this.lastAttack = 0;
    this.reloading = false;
    this.reloadTimer = 0;
    this.magazines = new Map(); // weaponId -> { ammo, magSize }  (loaded rounds)
    this.recoil = 0;
    this.drawCharge = 0;
    this.meleeSwing = 0;
  }

  getWeapon() {
    const slot = this.player.inventory.selectedSlot;
    if (!slot) return null;
    const item = getItem(slot.id);
    if (item?.type !== 'weapon') return null;
    return item;
  }

  // Call when slot changes; resets charge.
  onSlotChange() {
    this.drawCharge = 0;
  }

  attack() {
    const weapon = this.getWeapon();
    if (!weapon) {
      // Bare hands: tiny damage
      this._melee(2, 2.6);
      return;
    }
    if (weapon.weapon.kind === 'melee') {
      this._melee(weapon.weapon.damage, weapon.weapon.range, weapon.weapon.knockback);
    } else if (weapon.weapon.kind === 'gun' || weapon.weapon.kind === 'shotgun' || weapon.weapon.kind === 'sniper') {
      this._fireGun(weapon);
    } else if (weapon.weapon.kind === 'rocket') {
      this._fireGun(weapon);
    } else if (weapon.weapon.kind === 'bow') {
      this._releaseBow(weapon);
    }
    this.player.attackAnim = 0.3;
  }

  // Hold for bow charge
  update(dt) {
    const weapon = this.getWeapon();
    this.recoil = Math.max(0, this.recoil - dt * 8);
    this.meleeSwing = Math.max(0, this.meleeSwing - dt * 4);

    if (weapon?.weapon.kind === 'bow' && this.player.world.game?.input?.down('attack')) {
      this.drawCharge = Math.min(1, this.drawCharge + dt * 1.4);
      if (this.drawCharge >= 1 && this._hasAmmo(weapon)) {
        this._releaseBow(weapon);
        this.drawCharge = 0;
      }
    }

    if (this.reloading) {
      this.reloadTimer -= dt;
      if (this.reloadTimer <= 0) {
        this.reloading = false;
        this._finishReload();
      }
    }
  }

  _hasAmmo(weapon) {
    const ammoId = WEAPON_AMMO[weapon.id];
    if (!ammoId) return true;
    return this.player.inventory.countOf(ammoId) > 0;
  }

  _consumeAmmo(weapon, n = 1) {
    const ammoId = WEAPON_AMMO[weapon.id];
    if (!ammoId) return;
    this.player.inventory.remove(ammoId, n);
  }

  _mag(weapon) {
    let m = this.magazines.get(weapon.id);
    if (!m) {
      m = { ammo: weapon.weapon.magSize || 0, magSize: weapon.weapon.magSize || 0 };
      this.magazines.set(weapon.id, m);
    }
    return m;
  }

  reload() {
    const weapon = this.getWeapon();
    if (!weapon || !WEAPON_AMMO[weapon.id]) return;
    if (this.reloading) return;
    const mag = this._mag(weapon);
    if (mag.ammo >= mag.magSize) return;
    if (!this._hasAmmo(weapon)) {
      this.game.ui?.toast('No ammo!', 1500);
      this.game.engine.audio?.error();
      return;
    }
    this.reloading = true;
    this.reloadTimer = weapon.weapon.reload || 2;
    this.game.engine.audio?.equip();
    events.emit('combat:reload', { weaponId: weapon.id, time: this.reloadTimer });
  }

  _finishReload() {
    const weapon = this.getWeapon();
    if (!weapon) return;
    const mag = this._mag(weapon);
    const need = mag.magSize - mag.ammo;
    const have = this.player.inventory.countOf(WEAPON_AMMO[weapon.id] || 0);
    const take = Math.min(need, have);
    if (take > 0) {
      this._consumeAmmo(weapon, take);
      mag.ammo += take;
    }
    events.emit('combat:reloaded', { weaponId: weapon.id, ammo: mag.ammo });
    this.game.engine.audio?.click();
  }

  _melee(damage, range, knockback = 0.5) {
    const now = performance.now();
    if (now - this.lastAttack < 350) return;
    this.lastAttack = now;
    this.meleeSwing = 1;
    const eye = this.player.getEye();
    const dir = this.player.getAimDir();
    const entities = [...this.game.entities.entities.values(), this.player];
    let hit = false;
    for (const e of entities) {
      if (e === this.player || e.dead) continue;
      if (e.kind === 'npc') continue;
      const targetCenter = { x: e.pos.x, y: e.pos.y + e.height * 0.5, z: e.pos.z };
      const d = dist3d(eye, targetCenter);
      if (d > range) continue;
      const toTarget = { x: targetCenter.x - eye.x, y: targetCenter.y - eye.y, z: targetCenter.z - eye.z };
      const len = Math.hypot(toTarget.x, toTarget.y, toTarget.z) || 1;
      const dot = (toTarget.x * dir.x + toTarget.y * dir.y + toTarget.z * dir.z) / len;
      if (dot < 0.5) continue;
      const dmg = e.applyDamage(damage, { source: this.player, type: 'melee' });
      hit = true;
      events.emit('combat:hit', { attacker: this.player, target: e, damage: dmg });
      this.game.ui?.hitmarker();
      this.game.engine.audio?.hitmarker();
      if (e.dead) this.game.awardKill(this.player, e);
    }
    this.game.engine.audio?.dig(this.game.player._currentTool ? 'wood' : 'stone');
  }

  _fireGun(weapon) {
    const now = performance.now();
    const cooldown = 1000 / (weapon.weapon.fireRate || 2);
    if (now - this.lastAttack < cooldown) return;
    const mag = this._mag(weapon);
    if (mag.ammo <= 0) {
      this.reload();
      return;
    }
    this.lastAttack = now;
    mag.ammo--;
    this.recoil = 1;
    this._consumeAmmo(weapon, 1);

    const eye = this.player.getEye();
    let dir = this.player.getAimDir();
    // Spread
    const spread = (weapon.weapon.spread || 0) * (this.player.sprinting ? 2 : 1);
    const spx = (Math.random() - 0.5) * spread;
    const spy = (Math.random() - 0.5) * spread;
    dir = {
      x: dir.x + spx * Math.cos(this.player.yaw),
      y: dir.y + spy,
      z: dir.z + spx * Math.sin(this.player.yaw),
    };
    const len = Math.hypot(dir.x, dir.y, dir.z);
    dir = { x: dir.x / len, y: dir.y / len, z: dir.z / len };

    const speed = weapon.weapon.projectileSpeed || 60;
    const pellets = weapon.weapon.pellets || 1;
    for (let i = 0; i < pellets; i++) {
      let d = dir;
      if (pellets > 1) {
        const a1 = (Math.random() - 0.5) * weapon.weapon.spread;
        const a2 = (Math.random() - 0.5) * weapon.weapon.spread;
        d = { x: dir.x + a1, y: dir.y + a2, z: dir.z + a1 };
      }
      this.game.entities.spawnProjectile({
        from: this.player, x: eye.x, y: eye.y, z: eye.z,
        vx: d.x * speed, vy: d.y * speed, vz: d.z * speed,
        damage: weapon.weapon.damage,
        life: weapon.weapon.range / speed,
        explosive: weapon.weapon.kind === 'rocket',
        explosionRadius: weapon.weapon.splash || 5,
        color: weapon.weapon.kind === 'rocket' ? 0xff8a3a : 0xffe080,
      });
    }
    this.game.engine.audio?.shoot();
    events.emit('combat:shot', { weaponId: weapon.id, ammo: mag.ammo, magSize: mag.magSize });
    if (mag.ammo === 0) this.reload();
  }

  _releaseBow(weapon) {
    const now = performance.now();
    if (now - this.lastAttack < 500) return;
    const charge = Math.max(this.drawCharge, 0.2);
    if (!this._hasAmmo(weapon)) return;
    this.lastAttack = now;
    this._consumeAmmo(weapon, 1);
    const eye = this.player.getEye();
    const dir = this.player.getAimDir();
    const speed = weapon.weapon.projectileSpeed * charge;
    this.game.entities.spawnProjectile({
      from: this.player, x: eye.x, y: eye.y, z: eye.z,
      vx: dir.x * speed, vy: dir.y * speed, vz: dir.z * speed,
      damage: Math.round(weapon.weapon.damage * charge),
      life: weapon.weapon.range / speed, gravity: 8, arc: true,
      color: 0xd8c090,
    });
    this.game.engine.audio?.bow();
    this.drawCharge = 0;
  }

  getHudAmmo() {
    const weapon = this.getWeapon();
    if (!weapon || !WEAPON_AMMO[weapon.id]) return null;
    const mag = this._mag(weapon);
    return {
      ammo: mag.ammo,
      magSize: mag.magSize,
      inventory: this.player.inventory.countOf(WEAPON_AMMO[weapon.id]),
      reloading: this.reloading,
      reloadTimer: Math.max(0, this.reloadTimer),
      kind: weapon.weapon.kind,
    };
  }
}

export default CombatSystem;