// Social system: profile, friends, parties, presences, recently played.

import { events } from '../core/Events.js';
import { Storage } from '../core/Storage.js';

const FRIENDS_SAVE = 'pt.social.friends.v1';
const RECENT_SAVE = 'pt.social.recent.v1';

export class SocialSystem {
  constructor(game) {
    this.game = game;
    this.profile = null;           // set after login
    this.friends = Storage.get(FRIENDS_SAVE, []);   // [{ id, nickname, status, online, lastPlayed, mutual }]
    this.requests = [];            // incoming friend requests
    this.party = { members: [], leader: null, maxSize: 4 };
    this.recentlyPlayed = Storage.get(RECENT_SAVE, []);
    this.favorites = Storage.get('pt.social.favorites', []);
    this._mockPlayers = this._mockFriends();
  }

  _mockFriends() {
    // Simulated online players so the social surface is alive pre-server.
    return [
      { id: 'u_leaf', nickname: 'LeafRider', status: 'online', game: 'Creative' },
      { id: 'u_bloom', nickname: 'BloomFox', status: 'online', game: 'Battle Royale' },
      { id: 'u_root', nickname: 'RootMaster99', status: 'offline', lastSeen: '2h ago' },
      { id: 'u_sprout', nickname: 'SproutPip', status: 'in-menu' },
      { id: 'u_sun', nickname: 'SunKnight', status: 'online', game: 'Adventure' },
    ];
  }

  login(nickname, tag) {
    this.profile = {
      nickname,
      tag: tag || (1000 + Math.floor(Math.random() * 9000)),
      level: this.game.xp?.level || 1,
      created: Date.now(),
      verified: false,
    };
    events.emit('social:login', this.profile);
  }

  addFriend(id) {
    if (this.friends.some(f => f.id === id)) return;
    const mock = this._mockPlayers.find(m => m.id === id);
    this.friends.push({
      id, nickname: mock?.nickname || 'Friend', status: 'pending', added: Date.now(),
    });
    this._saveFriends();
    events.emit('social:friends-changed', this.friends);
  }

  removeFriend(id) {
    this.friends = this.friends.filter(f => f.id !== id);
    this._saveFriends();
    events.emit('social:friends-changed', this.friends);
  }

  friendState() {
    return this.friends.map(f => {
      const mock = this._mockPlayers.find(m => m.id === f.id);
      return {
        ...f,
        status: mock?.status || f.status,
        game: mock?.game || null,
        lastSeen: mock?.lastSeen,
      };
    });
  }

  _saveFriends() { Storage.set(FRIENDS_SAVE, this.friends); }

  createParty() {
    this.party = { members: [this.profile?.nickname || 'You'], leader: this.profile?.nickname || 'You', maxSize: 4 };
    events.emit('party:changed', this.party);
    return this.party;
  }

  invite(nickname) {
    if (this.party.members.length >= this.party.maxSize) return false;
    if (!this.party.members.includes(nickname)) {
      this.party.members.push(nickname);
      events.emit('party:changed', this.party);
    }
    return true;
  }

  leaveParty() {
    this.party = { members: [], leader: null, maxSize: 4 };
    events.emit('party:changed', this.party);
  }

  markPlayed(gameMode, worldName) {
    this.recentlyPlayed.unshift({ gameMode, worldName, ts: Date.now() });
    this.recentlyPlayed = this.recentlyPlayed.slice(0, 12);
    Storage.set(RECENT_SAVE, this.recentlyPlayed);
  }

  addFavorite(worldId, name) {
    if (!this.favorites.some(f => f.worldId === worldId)) {
      this.favorites.push({ worldId, name, ts: Date.now() });
      Storage.set('pt.social.favorites', this.favorites);
    }
  }

  removeFavorite(worldId) {
    this.favorites = this.favorites.filter(f => f.worldId !== worldId);
    Storage.set('pt.social.favorites', this.favorites);
  }

  discoverWorlds() {
    // Simulated game discovery feed
    return [
      { worldId: 'w_adventure', name: 'Chapter I: The Grove', mode: 'adventure', players: 142, rating: 4.8, genre: 'Story' },
      { worldId: 'w_survival', name: 'Grove Survival', mode: 'survival', players: 86, rating: 4.6, genre: 'Survival' },
      { worldId: 'w_creative', name: 'Sprout Workshop', mode: 'creative', players: 214, rating: 4.9, genre: 'Creative' },
      { worldId: 'w_br', name: 'Storm Grove Arena', mode: 'br', players: 96, rating: 4.7, genre: 'Battle Royale' },
      { worldId: 'w_ctf', name: 'Capture the Sprout', mode: 'minigame', players: 33, rating: 4.5, genre: 'Mini-game' },
      { worldId: 'w_obstacle', name: 'Canopy Dash', mode: 'minigame', players: 58, rating: 4.4, genre: 'Mini-game' },
      { worldId: 'w_tnt', name: 'BoomBarrel Brawl', mode: 'minigame', players: 71, rating: 4.6, genre: 'Mini-game' },
      { worldId: 'w_player1', name: 'Jungle Escape by BloomFox', mode: 'custom', players: 12, rating: 4.2, genre: 'Player-made' },
    ];
  }
}

export default SocialSystem;