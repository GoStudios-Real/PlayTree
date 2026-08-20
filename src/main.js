// PlayTree entry point: boots the engine, builds the UI, wires systems,
// registers all modes, and shows the main menu.

import { Engine } from './core/Engine.js';
import { Game, registerMode } from './game/Game.js';
import { UIManager } from './ui/UIManager.js';
import { DevConsole } from './devtools/DevConsole.js';
import { DebugOverlay } from './devtools/DebugOverlay.js';
import { SpawnTool } from './devtools/SpawnTool.js';
import { MapEditor } from './devtools/MapEditor.js';
import { EmoteWheel } from './ui/EmoteWheel.js';
import { TouchControls } from './ui/TouchControls.js';
import { NetClient } from './net/NetClient.js';
import { Matchmaker } from './net/Matchmaker.js';
import { NetSimulation } from './net/NetSimulation.js';
import { events } from './core/Events.js';

import { AdventureMode } from './game/modes/AdventureMode.js';
import { SurvivalMode } from './game/modes/SurvivalMode.js';
import { CreativeMode } from './game/modes/CreativeMode.js';
import { BattleRoyaleMode } from './br/BattleRoyaleMode.js';
import { MiniGameMode } from './game/modes/MiniGameMode.js';

// ---- Register modes ----
registerMode('adventure', AdventureMode);
registerMode('survival', SurvivalMode);
registerMode('creative', CreativeMode);
registerMode('br', BattleRoyaleMode);
registerMode('minigame', MiniGameMode);

function boot() {
  const engine = new Engine();
  engine.init();

  const game = new Game(engine);
  window.g = game;
  const ui = new UIManager(game);
  game.setUI(ui);

  // Dev tools
  const devConsole = new DevConsole(game);
  const debug = new DebugOverlay(game);
  const spawnTool = new SpawnTool(game);
  const mapEditor = new MapEditor(game);

  // Emote wheel + touch
  const emoteWheel = new EmoteWheel(ui);
  const touch = new TouchControls(ui);

  // Network layer
  const net = new NetClient();
  game.net = net;
  const matchmaker = new Matchmaker(game);
  game.matchmaker = matchmaker;
  const simulation = new NetSimulation(game, 3);
  game.simulation = simulation;

  const input = engine.input;
  const chatInput = ui.hud.chatInput;
  let chatOpen = false;

  function setChat(open) {
    chatOpen = open;
    game.inputFrozen = open;
    chatInput.classList.toggle('visible', open);
    if (open) {
      engine.input.exitPointerLock();
      chatInput.focus();
    } else {
      chatInput.blur();
      if (game.state === 'playing') engine.input.requestPointerLock(engine.canvas);
    }
  }

  // Keyboard shortcuts that need to run even when paused/menu (dev + system)
  window.addEventListener('keydown', (e) => {
    const code = e.code;

    if (code === 'Enter') {
      if (chatOpen) {
        const text = chatInput.value.trim();
        if (text) {
          game.chat.send(game.social.profile?.nickname || 'You', text);
          net.sendChat(text);
        }
        chatInput.value = '';
        setChat(false);
        e.preventDefault();
        return;
      }
      if (game.state === 'playing') {
        setChat(true);
        e.preventDefault();
        return;
      }
    }

    if (code === 'Escape') {
      if (chatOpen) { setChat(false); return; }
      if (emoteWheel.isOpen()) { emoteWheel.close(); return; }
      if (game.state === 'playing') { game.pause(); ui.open('pause'); }
      else if (game.state === 'paused') { ui.closeAll(); game.resume(); }
      return;
    }
  });

  // Per-frame global updates
  engine.addUpdater((dt) => {
    if (input.pressed('devConsole')) devConsole.toggle();
    if (input.pressed('debug')) debug.toggle();
    if (input.pressed('emote') && game.state === 'playing') {
      if (!emoteWheel.isOpen()) emoteWheel.open(); else emoteWheel.close();
    }

    if (game.state === 'playing' && !chatOpen && !emoteWheel.isOpen()) {
      if (input.pressed('inventory')) game.toggleInventory();
      if (input.pressed('map')) game.toggleMap();
      if (input.pressed('quests')) game.toggleQuests();
      if (input.pressed('interact') || input.pressed('build')) game.interact();
    }

    debug.update();
    if (touch.active) touch.update();
    if (game.state === 'playing') simulation.update(dt);
  }, 5);

  // Hide loader, show menu
  const loader = document.getElementById('loader');
  loader.classList.add('hidden');
  setTimeout(() => loader.remove(), 700);

  ui.open('mainmenu');
  events.emit('boot:done', { game });

  // touch devices
  if (('ontouchstart' in window) || navigator.maxTouchPoints > 0) {
    touch.enable();
  }

  engine.start();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', boot);
} else {
  boot();
}