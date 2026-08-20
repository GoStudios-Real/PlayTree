// Server browser + matchmaking simulation (offline). Designed to plug into the
// real networking layer when a server is present.

import { CONFIG } from '../core/Config.js';
import { events } from '../core/Events.js';

const WORLD_DEFS = {
  adventure: { name: 'Chapter I: The Grove', mode: 'adventure' },
  survival: { name: 'Grove Survival', mode: 'survival' },
  creative: { name: 'Sprout Workshop', mode: 'creative' },
  br: { name: 'Storm Grove Arena', mode: 'br' },
  minigame: { name: 'Canopy Games', mode: 'minigame' },
};

export class ServerBrowser {
  constructor(game) {
    this.game = game;
    this.servers = [];
    this.regions = ['US-East', 'US-West', 'EU-West', 'Asia-East'];
    this._populate();
  }

  _populate() {
    const names = ['Sprout Grove #1', 'Meadow Blossom', 'Cragspine Patrol', 'Sunvale Lounge', 'Dune Oasis', 'Bloomwood Retreat', 'Heartstone Guard', 'Canopy Nights'];
    this.servers = [];
    for (let i = 0; i < names.length; i++) {
      const mode = ['adventure', 'survival', 'creative', 'br', 'minigame'][i % 5];
      const def = WORLD_DEFS[mode];
      const max = CONFIG.maxPlayersPerServer;
      this.servers.push({
        id: 'srv_' + i,
        name: names[i],
        mode,
        gameName: def.name,
        players: Math.floor(Math.random() * max * 0.6) + (i % 3),
        max,
        ping: 20 + Math.floor(Math.random() * 80),
        region: this.regions[i % 4],
        status: 'open',
        seed: 1000 + i * 7,
        password: false,
      });
    }
  }

  refresh() {
    this._populate();
    events.emit('servers:changed', this.servers);
    return this.servers;
  }

  filter({ mode, region, search }) {
    return this.servers.filter(s =>
      (!mode || s.mode === mode) &&
      (!region || s.region === region) &&
      (!search || s.name.toLowerCase().includes(search.toLowerCase()) || s.gameName.toLowerCase().includes(search.toLowerCase()))
    );
  }

  join(server) {
    events.emit('server:joining', server);
    this.game.launchWorld(server.mode, { seed: server.seed, serverId: server.id, serverName: server.name });
  }

  createPrivate(mode, opts = {}) {
    const server = {
      id: 'srv_private_' + Date.now(),
      name: opts.name || 'Private Grove',
      mode,
      gameName: WORLD_DEFS[mode]?.name || mode,
      players: 1, max: opts.max || 4,
      ping: 10, region: 'Local', status: 'open',
      seed: opts.seed ?? (Date.now() >>> 0),
      password: !!opts.password,
      private: true,
    };
    events.emit('server:joining', server);
    this.game.launchWorld(mode, { seed: server.seed, serverId: server.id, serverName: server.name, isPrivate: true });
    return server;
  }
}

export default ServerBrowser;