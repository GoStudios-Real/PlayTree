// PlayTree test runner. Run:  node tests/run-tests.mjs
// Each test file exports a single async or sync function taking (assert, ctx).

import { readdirSync, statSync } from 'node:fs';
import { join, extname, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));

export function assert(cond, msg = 'assertion failed') {
  if (!cond) throw new Error('ASSERT FAILED: ' + msg);
}

export function approx(a, b, eps = 1e-6, msg = '') {
  if (Math.abs(a - b) > eps) throw new Error(`ASSERT FAILED: ${msg} ${a} !== ${b} (±${eps})`);
}

const files = readdirSync(here)
  .filter(f => f.endsWith('.test.mjs'))
  .sort();

let passed = 0;
const failures = [];

for (const f of files) {
  const mod = await import('./' + f);
  const test = mod.default || mod.run;
  if (typeof test !== 'function') continue;
  try {
    await test(assert, { approx });
    passed++;
    console.log(`✓ ${f}`);
  } catch (err) {
    failures.push({ file: f, error: err });
    console.log(`✗ ${f}: ${err.message}`);
  }
}

console.log(`\n${passed}/${files.length} test files passed.`);
if (failures.length) {
  process.exit(1);
}