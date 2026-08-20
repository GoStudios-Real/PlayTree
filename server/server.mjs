// PlayTree dev server: serves the game statically and hosts an optional
// WebSocket endpoint for the networking layer.
// Run:  npm.cmd start   (or)   node server/server.mjs

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const PORT = process.env.PORT || 8080;

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

function serveFile(req, res, pathname) {
  // Prevent path traversal
  const safePath = path.normalize(pathname).replace(/^(\.\.[/\\])+/, '');
  let filePath = path.join(ROOT, safePath);
  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html');
  }
  if (!fs.existsSync(filePath) || !filePath.startsWith(ROOT)) {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not found');
    return;
  }
  const ext = path.extname(filePath).toLowerCase();
  res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(res);
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const pathname = decodeURIComponent(url.pathname);
  if (req.method === 'GET') serveFile(req, res, pathname);
  else { res.writeHead(405); res.end('Method not allowed'); }
});

// ---- Optional WebSocket endpoint ----
// Uses the raw 'ws' protocol via a tiny fallback; if the 'ws' package is not
// installed the HTTP server still works fine (offline/simulated mode).
let wss = null;
try {
  const { WebSocketServer } = await import('ws');
  wss = new WebSocketServer({ server });
  wss.on('connection', (ws) => {
    ws.send(JSON.stringify({ m: 2, d: { playerId: 'srv_' + Math.random().toString(36).slice(2, 7), worldSeed: Date.now() >>> 0, worldName: 'The Grove', mode: 'adventure' } }));
    ws.on('message', (raw) => {
      // echo back PING/PONG and log joins
      try {
        const msg = JSON.parse(raw.toString());
        if (msg.m === 16) ws.send(JSON.stringify({ m: 17, d: { t: msg.d?.t } }));
        else if (msg.m === 1) ws.send(JSON.stringify({ m: 19, d: { ok: true, server: { id: 'srv_local', name: 'PlayTree Local', players: 1, max: 8 } } }));
      } catch {}
    });
  });
  console.log('[ws] WebSocket endpoint ready (ws://localhost:' + PORT + ')');
} catch (e) {
  console.log('[ws] ws package not installed — running HTTP only (offline mode).');
}

server.listen(PORT, () => {
  console.log('PlayTree dev server: http://localhost:' + PORT);
  console.log('Open that URL in a browser (Chrome/Edge/Firefox recommended).');
});