// PlayTree Electron shell: boots the static game server in-process and loads it
// in a Chromium window. The game stays a plain web app served over localhost.
const { app, BrowserWindow } = require('electron');
const path = require('node:path');
const { pathToFileURL, fileURLToPath } = require('node:url');

// Optional CDP port for debugging/automated verification (set PT_DEBUG_PORT=<port>).
if (process.env.PT_DEBUG_PORT) {
  app.commandLine.appendSwitch('remote-debugging-port', String(process.env.PT_DEBUG_PORT));
}

const PORT = process.env.PORT || 8080;
let server = null;
let win = null;

async function bootServer() {
  const entry = path.join(__dirname, '..', 'server', 'server.mjs');
  const mod = await import(pathToFileURL(entry).href);
  server = await mod.startServer(PORT);
}

function createWindow() {
  win = new BrowserWindow({
    width: 1280,
    height: 720,
    minWidth: 800,
    minHeight: 600,
    backgroundColor: '#0e1626',
    title: 'PlayTree — Chapter I: Season I',
    show: false,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  win.loadURL('http://localhost:' + PORT);
  win.once('ready-to-show', () => win.show());
  win.on('closed', () => { win = null; });
  return win;
}

app.whenReady().then(async () => {
  try {
    await bootServer();
    createWindow();
  } catch (e) {
    console.error('Failed to start PlayTree:', e);
    app.quit();
  }
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

function shutdown() {
  try { if (server) server.close(); } catch (_) {}
}
app.on('before-quit', shutdown);
