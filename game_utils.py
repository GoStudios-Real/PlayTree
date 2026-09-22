"""Shared utilities for all PlayTree games — Controller support + Procedural SFX"""
import pygame
import math
import random
import struct
import io

pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

CONTROLLER_MAP = {
    "move_x": 0,   # left stick X
    "move_y": 1,   # left stick Y
    "aim_x": 3,    # right stick X (or 2 on some controllers)
    "aim_y": 4,    # right stick Y
    "btn_a": 0,    # A / Cross
    "btn_b": 1,    # B / Circle
    "btn_x": 2,    # X / Square
    "btn_y": 3,    # Y / Triangle
    "btn_lb": 4,   # Left Bumper
    "btn_rb": 5,   # Right Bumper
    "btn_lt": 6,   # Left Trigger
    "btn_rt": 7,   # Right Trigger
    "btn_back": 8, # Select / Share
    "btn_start": 9,# Start / Options
    "btn_ls": 10,  # Left Stick Click
    "btn_rs": 11,  # Right Stick Click
    "dpad_x": 5,   # D-pad horizontal
    "dpad_y": 6,   # D-pad vertical (added after axes)
}

DEADZONE = 0.15


class ControllerState:
    def __init__(self):
        self.joystick = None
        self.connected = False
        self.axes = [0.0] * 8
        self.buttons = [0] * 16
        self.hats = [(0, 0)]
        self.prev_buttons = [0] * 16

    def init(self):
        try:
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.connected = True
        except Exception:
            self.connected = False

    def update(self):
        if not self.connected:
            try:
                if pygame.joystick.get_count() > 0 and self.joystick is None:
                    self.joystick = pygame.joystick.Joystick(0)
                    self.joystick.init()
                    self.connected = True
            except Exception:
                self.connected = False
        if self.connected and self.joystick:
            try:
                self.prev_buttons = list(self.buttons)
                for i in range(min(self.joystick.get_numaxes(), len(self.axes))):
                    v = self.joystick.get_axis(i)
                    self.axes[i] = v if abs(v) > DEADZONE else 0.0
                for i in range(min(self.joystick.get_numbuttons(), len(self.buttons))):
                    self.buttons[i] = self.joystick.get_button(i)
                if self.joystick.get_numhats() > 0:
                    self.hats = [self.joystick.get_hat(0)]
            except Exception:
                self.connected = False

    def get_axis(self, name):
        idx = CONTROLLER_MAP.get(name, 0)
        if idx < len(self.axes):
            return self.axes[idx]
        return 0.0

    def get_button(self, name):
        idx = CONTROLLER_MAP.get(name, 0)
        if idx < len(self.buttons):
            return self.buttons[idx]
        return 0

    def just_pressed(self, name):
        idx = CONTROLLER_MAP.get(name, 0)
        if idx < len(self.buttons) and idx < len(self.prev_buttons):
            return self.buttons[idx] == 1 and self.prev_buttons[idx] == 0
        return False

    def get_dpad(self):
        if self.hats:
            return self.hats[0]
        return (0, 0)

    def move_x(self):
        v = self.get_axis("move_x")
        dx, dy = self.get_dpad()
        if dx != 0: return float(dx)
        return v

    def move_y(self):
        v = self.get_axis("move_y")
        dx, dy = self.get_dpad()
        if dy != 0: return float(-dy)
        return v

    def aim_angle(self, px, py):
        ax = self.get_axis("aim_x")
        ay = self.get_axis("aim_y")
        if abs(ax) > DEADZONE or abs(ay) > DEADZONE:
            return math.atan2(ay, ax)
        return None

    def trigger(self, name):
        v = self.get_axis(name)
        idx = CONTROLLER_MAP.get(name, 6)
        if idx < len(self.buttons):
            return max(v, float(self.buttons[idx]))
        return max(0.0, v)


controller = ControllerState()

# ===== PROCEDURAL SOUND EFFECTS =====

def _make_samples(duration, freq_fn, amp_fn, sample_rate=44100):
    n = int(sample_rate * duration)
    buf = bytearray(n * 2)
    for i in range(n):
        t = i / sample_rate
        val = int(max(-32768, min(32767, amp_fn(t) * 32767 * freq_fn(t))))
        struct.pack_into('<h', buf, i * 2, val)
    return pygame.mixer.Sound(buffer=bytes(buf))

def sfx_shoot():
    def freq(t): return max(0, 1.0 - t * 8) * 800 + 200
    def amp(t): return max(0, 1.0 - t * 10)
    return _make_samples(0.1, freq, amp)

def sfx_explosion():
    def freq(t): return max(0.01, 1.0 - t * 3) * 200
    def amp(t): return max(0, 1.0 - t * 2.5) * (0.5 + 0.5 * math.sin(t * 60))
    return _make_samples(0.3, freq, amp)

def sfx_hit():
    def freq(t): return max(0, 1.0 - t * 15) * 400 + 100
    def amp(t): return max(0, 1.0 - t * 12)
    return _make_samples(0.08, freq, amp)

def sfx_collect():
    def freq(t): return 600 + t * 2000
    def amp(t): return max(0, 1.0 - t * 5)
    return _make_samples(0.15, freq, amp)

def sfx_levelup():
    def freq(t): return 400 + t * 800 + math.sin(t * 30) * 100
    def amp(t): return max(0, 1.0 - t * 2)
    return _make_samples(0.4, freq, amp)

def sfx_menu_click():
    def freq(t): return 800 + t * 1500
    def amp(t): return max(0, 1.0 - t * 20)
    return _make_samples(0.05, freq, amp)

def sfx_menu_hover():
    def freq(t): return 500 + t * 500
    def amp(t): return max(0, 1.0 - t * 25)
    return _make_samples(0.03, freq, amp)

def sfx_damage():
    def freq(t): return max(0.01, 1.0 - t * 5) * 300
    def amp(t): return max(0, 1.0 - t * 4) * (1 + 0.5 * math.sin(t * 80))
    return _make_samples(0.2, freq, amp)

def sfx_bubble():
    def freq(t): return 300 + t * 1200
    def amp(t): return max(0, 1.0 - t * 12) * 0.5
    return _make_samples(0.06, freq, amp)

def sfx_jump():
    def freq(t): return 200 + t * 600
    def amp(t): return max(0, 1.0 - t * 6)
    return _make_samples(0.15, freq, amp)

def sfx_coin():
    def freq(t): return 987 + t * 400 if t < 0.07 else 1319
    def amp(t): return max(0, 1.0 - t * 4)
    return _make_samples(0.2, freq, amp)

def sfx_powerup():
    def freq(t): return 300 + t * 1200 + math.sin(t * 40) * 200
    def amp(t): return max(0, 1.0 - t * 2.5)
    return _make_samples(0.3, freq, amp)

def sfx_game_over():
    def freq(t): return max(50, 400 - t * 300)
    def amp(t): return max(0, 1.0 - t * 1.5)
    return _make_samples(0.8, freq, amp)

def sfx_footstep():
    def freq(t): return 100 + random.random() * 50
    def amp(t): return max(0, 1.0 - t * 20) * 0.3
    return _make_samples(0.04, freq, amp)

def sfx_splash():
    def freq(t): return max(0.01, 1.0 - t * 3) * 500 * (1 + 0.3 * math.sin(t * 40))
    def amp(t): return max(0, 1.0 - t * 2.5) * 0.6
    return _make_samples(0.25, freq, amp)

def sfx_laser():
    def freq(t): return 1200 - t * 800
    def amp(t): return max(0, 1.0 - t * 5)
    return _make_samples(0.12, freq, amp)

class SFXManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.volume = 0.5

    def _load(self, name, gen_fn):
        if name not in self.sounds:
            try:
                self.sounds[name] = gen_fn()
            except Exception:
                pass

    def play(self, name, gen_fn=None):
        if not self.enabled:
            return
        if gen_fn:
            self._load(name, gen_fn)
        if name in self.sounds:
            try:
                ch = self.sounds[name].play()
                if ch:
                    ch.set_volume(self.volume)
            except Exception:
                pass

sfx = SFXManager()
