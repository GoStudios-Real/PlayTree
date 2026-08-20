import { mulberry32, hash2, hash3, clamp, lerp, AABB, raycastVoxels, moveWithCollision, directionFromYaw, smoothstep } from '../src/core/MathUtils.js';

export default function (assert, { approx }) {
  // Determinism
  const a = mulberry32(12345);
  const b = mulberry32(12345);
  const seq1 = Array.from({ length: 10 }, () => a());
  const seq2 = Array.from({ length: 10 }, () => b());
  assert(JSON.stringify(seq1) === JSON.stringify(seq2), 'mulberry32 deterministic');

  const c = mulberry32(999);
  for (let i = 0; i < 100; i++) {
    const v = c();
    assert(v >= 0 && v < 1, 'mulberry32 range');
  }

  // Different seeds differ
  assert(mulberry32(1)() !== mulberry32(2)(), 'different seeds differ');

  // hash2 deterministic
  assert(hash2(5, 7, 42) === hash2(5, 7, 42), 'hash2 deterministic');
  assert(hash3(1, 2, 3, 9) === hash3(1, 2, 3, 9), 'hash3 deterministic');

  // clamp / lerp
  assert(clamp(5, 0, 1) === 1 && clamp(-1, 0, 1) === 0 && clamp(0.5, 0, 1) === 0.5, 'clamp');
  approx(lerp(10, 20, 0.5), 15, 1e-9, 'lerp');
  approx(smoothstep(0, 1, 0.5), 0.5, 1e-9, 'smoothstep mid');

  // AABB
  const box = AABB.fromPosSize(0, 0, 0, 2, 2, 2);
  assert(box.minX === -1 && box.maxX === 1, 'AABB fromPosSize');
  assert(box.intersects(AABB.fromPosSize(0, 0, 0, 2, 2, 2)), 'AABB intersect overlap');
  assert(!box.intersects(AABB.fromPosSize(5, 5, 5, 1, 1, 1)), 'AABB intersect disjoint');
  assert(box.contains(0, 0.5, 0) && !box.contains(5, 5, 5), 'AABB contains');

  // Raycast: origin inside empty, wall at x=3
  const wall = (x, y, z) => x >= 3;
  const hit = raycastVoxels(0.5, 0.5, 0.5, 1, 0, 0, 20, wall);
  assert(hit.hit && hit.x === 3, 'raycast hits wall at x=3 (got ' + hit.x + ')');
  assert(hit.prev.x === 2, 'raycast previous voxel empty');

  const miss = raycastVoxels(0.5, 0.5, 0.5, 0, 1, 0, 3, () => false);
  assert(!miss.hit, 'raycast no hit');

  // moveWithCollision: small per-frame descent onto a floor stops and reverts
  const floor = (x, y, z) => y < 0;
  const bb = AABB.fromPosSize(0, 0.006, 0, 0.6, 1.8, 0.6);
  const vel = moveWithCollision(bb, { x: 0, y: -0.5, z: 0 }, 0.016, floor);
  assert(vel.y === 0, 'velocity zeroed on floor hit');
  assert(bb.minY >= 0 && bb.minY < 0.01, 'box rests on floor top (minY=' + bb.minY + ')');

  // Fast fall (penetration > horizontal overlap) must NOT tunnel or slide sideways.
  const bbFast = AABB.fromPosSize(0, 3, 0, 0.6, 1.8, 0.6);
  const velFast = { x: 0, y: -42, z: 0 };
  let landed = null;
  for (let f = 0; f < 10; f++) {
    moveWithCollision(bbFast, velFast, 0.016, floor);
    if (velFast.y === 0) { landed = f; break; }
  }
  assert(landed !== null, 'fast fall lands within a few frames');
  assert(bbFast.minY >= 0 && bbFast.minY < 0.01, 'fast fall rests on floor (minY=' + bbFast.minY + ')');
  assert(velFast.x === 0 && velFast.z === 0, 'fast fall keeps horizontal velocity');

  // Running into a wall at speed stops the player without vertical slide.
  const wallX = (x, y, z) => x >= 3;
  const bbWall = AABB.fromPosSize(1.5, 0.5, 0, 0.6, 1.8, 0.6);
  const velWall = { x: 20, y: 0, z: 0 };
  let wallStopped = false;
  for (let f = 0; f < 10; f++) {
    moveWithCollision(bbWall, velWall, 0.016, wallX);
    if (velWall.x === 0) { wallStopped = true; break; }
  }
  assert(wallStopped, 'wall stops horizontal velocity');
  assert(bbWall.maxX <= 3.001, 'box clamps against wall (maxX=' + bbWall.maxX + ')');
  assert(bbWall.minY === 0.5, 'wall hit does not move box vertically');

  // directionFromYaw
  const d0 = directionFromYaw(0);
  approx(d0.x, 0, 1e-9, 'yaw0 x'); approx(d0.z, -1, 1e-9, 'yaw0 z');
  const d90 = directionFromYaw(Math.PI / 2);
  approx(d90.x, -1, 1e-9, 'yaw90 x');
}