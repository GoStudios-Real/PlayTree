// Populate www/ (Capacitor webDir) from the static site sources.
import { cpSync, rmSync, existsSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const www = join(root, "www");

if (existsSync(www)) rmSync(www, { recursive: true, force: true });
mkdirSync(www, { recursive: true });

// Static site + web game engine. Relative refs (assets/, src/) resolve inside www/.
cpSync(join(root, "index.html"), join(www, "index.html"));
cpSync(join(root, "assets"), join(www, "assets"), { recursive: true });
cpSync(join(root, "src"), join(www, "src"), { recursive: true });

console.log("www/ built");
