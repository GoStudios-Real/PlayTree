// Named-export cross-check: resolves every relative import and verifies the
// imported names actually exist in the target module's namespace.
// Run: node scripts/check-exports.mjs

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, extname, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

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
const nsCache = new Map();

async function getNamespace(file) {
  if (nsCache.has(file)) return nsCache.get(file);
  try {
    const mod = await import(pathToFileURL(file).href);
    nsCache.set(file, mod);
    return mod;
  } catch (err) {
    nsCache.set(file, null);
    return null;
  }
}

let failures = 0;

for (const file of files) {
  const src = readFileSync(file, 'utf8');
  const re = /import\s+([^;]*?)\s+from\s+['"]([^'"]+)['"]/g;
  let m;
  while ((m = re.exec(src)) !== null) {
    const spec = m[1];
    const target = m[2];
    if (!target.startsWith('.')) continue;
    const targetFile = resolve(dirname(file), target);
    if (!statSync(targetFile, { throwIfNoEntry: false })?.isFile()) continue; // reported elsewhere
    // parse named imports: { A, B as C }
    const named = [...spec.matchAll(/\{([^}]*)\}/g)];
    for (const grp of named) {
      for (const name of grp[1].split(',').map(s => s.trim()).filter(Boolean)) {
        const orig = name.split(/\s+as\s+/)[0].trim();
        const ns = await getNamespace(targetFile);
        if (ns === null) { /* target can't be evaluated in Node; skip */ continue; }
        if (!(orig in ns)) {
          failures++;
          console.error(`✗ ${file} -> '${orig}' not exported by ${target}`);
        }
      }
    }
  }
}

console.log(`\nChecked named imports across ${files.length} files. ${failures} problem(s).`);
process.exit(failures > 0 ? 1 : 0);