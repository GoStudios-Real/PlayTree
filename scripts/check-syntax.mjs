// Syntax checker: parses every JS module in src/ as ES modules to catch
// syntax errors without running the game (browser-only imports are fine).
// Run:  node scripts/check-syntax.mjs

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, extname, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'src');

function walk(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (extname(p) === '.js') out.push(p);
  }
  return out;
}

const files = walk(root);
let failures = 0;

for (const file of files) {
  const src = readFileSync(file, 'utf8');
  const res = spawnSync(process.execPath, ['--input-type=module', '--check'], { input: src, encoding: 'utf8' });
  if (res.status !== 0) {
    failures++;
    console.error(`\n✗ ${file}\n${res.stderr || res.stdout}`);
  } else {
    process.stdout.write('.');
  }
}

// Validate that all static import specifiers resolve to real files
let importFailures = 0;
for (const file of files) {
  const src = readFileSync(file, 'utf8');
  const re = /(?:import\s+[^'"]*from\s*|import\s*|export\s+[^'"]*from\s*)['"]([^'"]+)['"]/g;
  let m;
  while ((m = re.exec(src)) !== null) {
    const spec = m[1];
    if (!spec.startsWith('.')) continue; // bare specifiers (three) skipped
    const target = resolve(dirname(file), spec);
    if (!statSync(target, { throwIfNoEntry: false })?.isFile()) {
      importFailures++;
      console.error(`\n✗ ${file} -> missing import "${spec}"`);
    }
  }
}

console.log(`\n\nChecked ${files.length} files. ${failures} syntax error(s), ${importFailures} missing import(s).`);
process.exit(failures + importFailures > 0 ? 1 : 0);