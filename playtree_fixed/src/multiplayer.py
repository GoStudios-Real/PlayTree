import pygame
import math
import random
import json
import socket
import threading
import time
from config import *


class NetworkMessage:
    def __init__(self, msg_type, data=None):
        self.type = msg_type
        self.data = data or {}

    def serialize(self):
        return json.dumps({"type": self.type, "data": self.data}) + "\n"

    @staticmethod
    def deserialize(raw):
        try:
            obj = json.loads(raw.strip())
            return NetworkMessage(obj["type"], obj.get("data", {}))
        except Exception:
            return None


class GameServer:
    def __init__(self, host="0.0.0.0", port=7777):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.running = False
        self.thread = None
        self.player_states = {}
        self.game_state = {}
        self.lock = threading.Lock()
        self.local_messages = []

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(4)
            self.running = True
            self.thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.thread.start()
            return True
        except Exception as e:
            print(f"Server start failed: {e}")
            return False

    def stop(self):
        self.running = False
        try:
            self.server_socket.close()
        except Exception:
            pass
        for client_id in list(self.clients.keys()):
            self._disconnect_client(client_id)

    def _accept_loop(self):
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, addr = self.server_socket.accept()
                client_id = f"{addr[0]}:{addr[1]}"
                with self.lock:
                    self.clients[client_id] = {
                        "socket": client_socket,
                        "addr": addr,
                        "name": f"Player{len(self.clients) + 1}",
                    }
                    self.player_states[client_id] = {
                        "x": WORLD_W // 2, "y": WORLD_H // 2,
                        "hp": 100, "max_hp": 100,
                        "name": self.clients[client_id]["name"],
                        "class": "Guardian",
                        "weapon": None,
                    }
                thread = threading.Thread(target=self._client_loop, args=(client_id,), daemon=True)
                thread.start()
            except socket.timeout:
                continue
            except Exception:
                break

    def _client_loop(self, client_id):
        client = self.clients.get(client_id)
        if not client:
            return
        sock = client["socket"]
        try:
            welcome = NetworkMessage("welcome", {"id": client_id, "players": self._get_all_states()})
            sock.sendall(welcome.serialize().encode())
            while self.running:
                sock.settimeout(1.0)
                try:
                    data = sock.recv(4096).decode()
                    if not data:
                        break
                    for line in data.strip().split("\n"):
                        msg = NetworkMessage.deserialize(line)
                        if msg:
                            self._handle_message(client_id, msg)
                except socket.timeout:
                    continue
        except Exception:
            pass
        finally:
            self._disconnect_client(client_id)

    def _handle_message(self, client_id, msg):
        if msg.type == "player_update":
            with self.lock:
                self.player_states[client_id] = msg.data
            self._broadcast("state_update", self._get_all_states(), exclude=client_id)
        elif msg.type == "chat":
            self._broadcast("chat", {"from": self.clients[client_id]["name"], "text": msg.data.get("text", "")})
        elif msg.type == "attack":
            self._broadcast("attack", {"player": client_id, **msg.data})
        elif msg.type == "damage":
            self._broadcast("damage", msg.data)
        elif msg.type == "set_name":
            with self.lock:
                if client_id in self.clients:
                    self.clients[client_id]["name"] = msg.data.get("name", "Player")
                    if client_id in self.player_states:
                        self.player_states[client_id]["name"] = msg.data["name"]
        elif msg.type == "spawn_effect":
            self._broadcast("spawn_effect", msg.data, exclude=client_id)

    def _broadcast(self, msg_type, data, exclude=None):
        msg = NetworkMessage(msg_type, data)
        raw = msg.serialize().encode()
        with self.lock:
            for cid, client in self.clients.items():
                if cid != exclude:
                    try:
                        client["socket"].sendall(raw)
                    except Exception:
                        pass

    def _disconnect_client(self, client_id):
        with self.lock:
            if client_id in self.clients:
                try:
                    self.clients[client_id]["socket"].close()
                except Exception:
                    pass
                del self.clients[client_id]
            if client_id in self.player_states:
                del self.player_states[client_id]
        self._broadcast("player_left", {"id": client_id})

    def _get_all_states(self):
        with self.lock:
            return dict(self.player_states)

    def get_player_count(self):
        with self.lock:
            return len(self.clients)


class GameClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.player_id = None
        self.server_ip = ""
        self.server_port = 7777
        self.thread = None
        self.incoming = []
        self.outgoing = []
        self.lock = threading.Lock()
        self.other_players = {}
        self.chat_messages = []
        self.name = "Player"

    def connect(self, ip, port=7777, name="Player"):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((ip, port))
            self.server_ip = ip
            self.server_port = port
            self.name = name
            self.connected = True
            self.thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.thread.start()
            self.send(NetworkMessage("set_name", {"name": name}))
            return True
        except Exception as e:
            print(f"Connect failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        self.connected = False
        try:
            self.socket.close()
        except Exception:
            pass

    def _receive_loop(self):
        buffer = ""
        while self.connected:
            try:
                self.socket.settimeout(1.0)
                data = self.socket.recv(4096).decode()
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    msg = NetworkMessage.deserialize(line)
                    if msg:
                        self._process_message(msg)
            except socket.timeout:
                continue
            except Exception:
                break
        self.connected = False

    def _process_message(self, msg):
        if msg.type == "welcome":
            self.player_id = msg.data.get("id")
            states = msg.data.get("players", {})
            with self.lock:
                self.other_players = states
        elif msg.type == "state_update":
            with self.lock:
                self.other_players = msg.data
        elif msg.type == "chat":
            self.chat_messages.append({
                "from": msg.data.get("from", "?"),
                "text": msg.data.get("text", ""),
                "time": time.time(),
            })
        elif msg.type == "player_left":
            pid = msg.data.get("id")
            with self.lock:
                if pid in self.other_players:
                    del self.other_players[pid]
        elif msg.type == "attack":
            pass
        elif msg.type == "damage":
            pass
        elif msg.type == "spawn_effect":
            pass

    def send(self, msg):
        if not self.connected:
            return
        try:
            self.socket.sendall(msg.serialize().encode())
        except Exception:
            pass

    def send_player_state(self, player):
        state = {
            "x": player.x, "y": player.y,
            "hp": player.hp, "max_hp": player.max_hp,
            "name": getattr(player, "name", "Player"),
            "class": player.player_class.value,
            "weapon": player.weapon_id,
        }
        self.send(NetworkMessage("player_update", state))

    def send_chat(self, text):
        self.send(NetworkMessage("chat", {"text": text}))

    def send_attack(self, x, y, angle, damage):
        self.send(NetworkMessage("attack", {"x": x, "y": y, "angle": angle, "damage": damage}))

    def get其他玩家(self):
        with self.lock:
            return dict(self.other_players)

    def get_chat_messages(self):
        msgs = self.chat_messages[:]
        self.chat_messages.clear()
        return msgs


class MultiplayerManager:
    def __init__(self):
        self.is_host = False
        self.is_client = False
        self.server = None
        self.client = None
        self.connected = False
        self.show_menu = False
        self.menu_tab = "connect"
        self.ip_input = ""
        self.name_input = "Player"
        self.typing_ip = False
        self.typing_name = False
        self.status_message = ""
        self.status_timer = 0
        self.chat_input = ""
        self.typing_chat = False
        self.chat_visible = False

    def host_game(self, name="Player"):
        self.server = GameServer()
        if self.server.start():
            self.is_host = True
            self.client = GameClient()
            if self.client.connect("127.0.0.1", 7777, name):
                self.connected = True
                self.status_message = f"Hosting on port 7777!"
                return True
        self.status_message = "Failed to start server"
        return False

    def join_game(self, ip, name="Player"):
        self.client = GameClient()
        if self.client.connect(ip, 7777, name):
            self.is_client = True
            self.connected = True
            self.status_message = f"Connected to {ip}!"
            return True
        self.status_message = "Connection failed"
        return False

    def disconnect(self):
        if self.client:
            self.client.disconnect()
        if self.server:
            self.server.stop()
        self.connected = False
        self.is_host = False
        self.is_client = False
        self.status_message = "Disconnected"

    def update(self, dt, player=None):
        self.status_timer = max(0, self.status_timer - dt)
        if self.connected and self.client and player:
            self.client.send_player_state(player)

    def send_chat(self, text):
        if self.client:
            self.client.send_chat(text)
        if self.server:
            self.server.local_messages.append({"from": "You", "text": text})
            if len(self.server.local_messages) > 50:
                self.server.local_messages = self.server.local_messages[-50:]

    def draw(self, screen):
        if not self.show_menu:
            self._draw_hud(screen)
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))

        mx, my = 80, 60
        mw, mh = WIDTH - 160, HEIGHT - 120
        pygame.draw.rect(screen, (15, 20, 30), (mx, my, mw, mh), border_radius=12)
        pygame.draw.rect(screen, (*CYAN[:3], 60), (mx, my, mw, mh), border_radius=12, width=2)

        tf = pygame.font.Font(None, 44)
        ts = tf.render("MULTIPLAYER", True, CYAN)
        screen.blit(ts, (mx + 20, my + 10))

        tabs = ["connect", "lobby"]
        for i, tab in enumerate(tabs):
            tx = mx + 20 + i * 100
            ty = my + 60
            is_sel = tab == self.menu_tab
            color = GOLD if is_sel else (120, 120, 120)
            tab_f = pygame.font.Font(None, 24)
            tab_s = tab_f.render(tab.title(), True, color)
            screen.blit(tab_s, (tx, ty))

        if self.menu_tab == "connect":
            self._draw_connect_tab(screen, mx, my, mw, mh)
        elif self.menu_tab == "lobby":
            self._draw_lobby_tab(screen, mx, my, mw, mh)

        if self.status_message and self.status_timer > 0:
            sf = pygame.font.Font(None, 22)
            ss = sf.render(self.status_message, True, GREEN_GLOW)
            screen.blit(ss, (mx + 20, my + mh - 50))

        try:
            ctrl = pygame.joystick.get_count() > 0
        except Exception:
            ctrl = False
        if ctrl:
            from src.ui import xbox_icons
            xbox_icons.draw_menu_prompt(screen, [("B", "ESC", "Close")], my + mh - 25)
        else:
            hint = pygame.font.Font(None, 18).render("ESC to close", True, (80, 100, 80))
            screen.blit(hint, (mx + 20, my + mh - 25))

    def _draw_connect_tab(self, screen, mx, my, mw, mh):
        sf = pygame.font.Font(None, 26)
        sf_sm = pygame.font.Font(None, 20)

        iy = my + 100
        ns = sf.render("Name:", True, (180, 180, 180))
        screen.blit(ns, (mx + 20, iy))
        pygame.draw.rect(screen, (30, 30, 40), (mx + 120, iy - 2, 200, 26), border_radius=4)
        name_color = GOLD if self.name_input else (100, 100, 100)
        name_disp = self.name_input if self.name_input else "Player"
        nd = sf.render(name_disp, True, name_color)
        screen.blit(nd, (mx + 130, iy))
        if self.typing_name and int(time.time() * 2) % 2:
            pygame.draw.line(screen, GOLD, (mx + 130 + nd.get_width() + 2, iy),
                             (mx + 130 + nd.get_width() + 2, iy + 20), 2)

        iy += 50
        hs = sf.render("Host Game", True, GOLD)
        host_rect = pygame.Rect(mx + 20, iy, 200, 40)
        pygame.draw.rect(screen, (30, 40, 30), host_rect, border_radius=6)
        pygame.draw.rect(screen, (*GREEN_GLOW[:3], 60), host_rect, border_radius=6, width=1)
        screen.blit(hs, (mx + 60, iy + 8))

        iy += 60
        ip_label = sf.render("IP Address:", True, (180, 180, 180))
        screen.blit(ip_label, (mx + 20, iy))
        pygame.draw.rect(screen, (30, 30, 40), (mx + 160, iy - 2, 200, 26), border_radius=4)
        ip_color = GOLD if self.ip_input else (100, 100, 100)
        ip_disp = self.ip_input if self.ip_input else "127.0.0.1"
        ipd = sf.render(ip_disp, True, ip_color)
        screen.blit(ipd, (mx + 170, iy))
        if self.typing_ip and int(time.time() * 2) % 2:
            pygame.draw.line(screen, GOLD, (mx + 170 + ipd.get_width() + 2, iy),
                             (mx + 170 + ipd.get_width() + 2, iy + 20), 2)

        iy += 40
        js = sf.render("Join Game", True, CYAN)
        join_rect = pygame.Rect(mx + 20, iy, 200, 40)
        pygame.draw.rect(screen, (30, 30, 40), join_rect, border_radius=6)
        pygame.draw.rect(screen, (*CYAN[:3], 60), join_rect, border_radius=6, width=1)
        screen.blit(js, (mx + 60, iy + 8))

        iy += 60
        if self.connected:
            ds = sf.render("Disconnect", True, RED)
            disc_rect = pygame.Rect(mx + 20, iy, 200, 40)
            pygame.draw.rect(screen, (40, 20, 20), disc_rect, border_radius=6)
            pygame.draw.rect(screen, (*RED[:3], 60), disc_rect, border_radius=6, width=1)
            screen.blit(ds, (mx + 55, iy + 8))

            player_count = self.server.get_player_count() if self.server else 0
            pc = sf.render(f"Players connected: {player_count}", True, GREEN_GLOW)
            screen.blit(pc, (mx + 250, iy + 8))

    def _draw_lobby_tab(self, screen, mx, my, mw, mh):
        sf = pygame.font.Font(None, 24)
        sf_sm = pygame.font.Font(None, 18)

        iy = my + 100
        ls = sf.render("Connected Players:", True, GOLD)
        screen.blit(ls, (mx + 20, iy))
        iy += 30

        if self.client:
            players = self.client.get其他玩家()
            for pid, state in players.items():
                name = state.get("name", "Unknown")
                px = state.get("x", 0)
                py = state.get("y", 0)
                hp = state.get("hp", 100)
                ps = sf_sm.render(f"{name} - HP:{int(hp)} Pos:({int(px)},{int(py)})", True, (180, 200, 180))
                screen.blit(ps, (mx + 30, iy))
                iy += 22

        iy += 20
        cs = sf.render("Chat:", True, GOLD)
        screen.blit(cs, (mx + 20, iy))
        iy += 25

        chat_bg = pygame.Surface((mw - 40, 120), pygame.SRCALPHA)
        chat_bg.fill((10, 10, 20, 180))
        screen.blit(chat_bg, (mx + 20, iy))

        if self.client:
            for msg in self.client.chat_messages[-5:]:
                ms = sf_sm.render(f"{msg['from']}: {msg['text']}", True, (180, 180, 200))
                screen.blit(ms, (mx + 25, iy + 5))
                iy += 20

    def _draw_hud(self, screen):
        if not self.connected:
            return
        mf = pygame.font.Font(None, 20)
        status = "HOST" if self.is_host else "CLIENT"
        color = GREEN_GLOW if self.is_host else CYAN
        try:
            ctrl = pygame.joystick.get_count() > 0
        except Exception:
            ctrl = False
        if ctrl:
            ms = mf.render(f"[{status}]", True, color)
        else:
            ms = mf.render(f"[{status}] Press P for multiplayer", True, color)
        bg = pygame.Surface((ms.get_width() + 10, ms.get_height() + 4), pygame.SRCALPHA)
        bg.fill((10, 15, 25, 150))
        screen.blit(bg, (WIDTH - ms.get_width() - 15, HEIGHT - 25))
        screen.blit(ms, (WIDTH - ms.get_width() - 10, HEIGHT - 23))

        if self.client:
            players = self.client.get其他玩家()
            if players:
                count_s = mf.render(f"{len(players)} players nearby", True, (150, 180, 200))
                screen.blit(count_s, (WIDTH - count_s.get_width() - 15, HEIGHT - 48))

    def handle_key(self, event, player=None):
        if event.type == pygame.KEYDOWN:
            if self.typing_name:
                if event.key == pygame.K_RETURN:
                    self.typing_name = False
                elif event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.unicode.isprintable() and len(self.name_input) < 16:
                    self.name_input += event.unicode
                return True
            elif self.typing_ip:
                if event.key == pygame.K_RETURN:
                    self.typing_ip = False
                elif event.key == pygame.K_BACKSPACE:
                    self.ip_input = self.ip_input[:-1]
                elif event.unicode.isprintable() and len(self.ip_input) < 30:
                    self.ip_input += event.unicode
                return True
            elif self.typing_chat:
                if event.key == pygame.K_RETURN:
                    if self.chat_input.strip():
                        self.send_chat(self.chat_input.strip())
                    self.chat_input = ""
                    self.typing_chat = False
                elif event.key == pygame.K_BACKSPACE:
                    self.chat_input = self.chat_input[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.typing_chat = False
                    self.chat_input = ""
                elif event.unicode.isprintable() and len(self.chat_input) < 100:
                    self.chat_input += event.unicode
                return True

            if event.key == pygame.K_p:
                self.show_menu = not self.show_menu
                return True
            elif event.key == pygame.K_ESCAPE and self.show_menu:
                self.show_menu = False
                return True
            elif event.key == pygame.K_RETURN and self.show_menu:
                if self.menu_tab == "connect":
                    if not self.connected:
                        name = self.name_input if self.name_input else "Player"
                        self.host_game(name)
                    else:
                        name = self.name_input if self.name_input else "Player"
                        ip = self.ip_input if self.ip_input else "127.0.0.1"
                        self.join_game(ip, name)
                return True
        return False

    def handle_click(self, pos, player=None):
        mx, my = pos
        if not self.show_menu:
            return False

        connect_mx, connect_my = 80, 60
        iy = connect_my + 100
        if 120 <= mx <= 320 and iy - 2 <= my <= iy + 24:
            self.typing_name = True
            self.typing_ip = False
            return True

        iy += 50
        if connect_mx + 20 <= mx <= connect_mx + 220 and iy <= my <= iy + 40:
            if not self.connected:
                name = self.name_input if self.name_input else "Player"
                self.host_game(name)
            return True

        iy += 60
        if 160 <= mx <= 360 and iy - 2 <= my <= iy + 24:
            self.typing_ip = True
            self.typing_name = False
            return True

        iy += 40
        if connect_mx + 20 <= mx <= connect_mx + 220 and iy <= my <= iy + 40:
            name = self.name_input if self.name_input else "Player"
            ip = self.ip_input if self.ip_input else "127.0.0.1"
            self.join_game(ip, name)
            return True

        iy += 60
        if self.connected and connect_mx + 20 <= mx <= connect_mx + 220 and iy <= my <= iy + 40:
            self.disconnect()
            return True

        return False
