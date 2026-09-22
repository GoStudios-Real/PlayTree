"""Procedural background music generator for PlayTree Collection"""
import pygame
import math
import struct
import random

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

def generate_ambient_track(duration=30, style="calm"):
    sr = 44100
    n = sr * duration
    buf = bytearray(n * 4)

    notes_calm = [261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9, 523.3]
    notes_space = [130.8, 146.8, 164.8, 196.0, 220.0, 261.6]
    notes_deep = [65.4, 73.4, 82.4, 98.0, 110.0, 130.8]

    notes = {"calm": notes_calm, "space": notes_space, "deep": notes_deep}.get(style, notes_calm)

    def lfo(t, freq=0.2):
        return (math.sin(2 * math.pi * freq * t) + 1) / 2

    def pad(freq, t, dur=2.0):
        env = min(1.0, t * 3) * max(0, 1.0 - max(0, t - dur + 0.5) * 2)
        v = math.sin(2 * math.pi * freq * t)
        v += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
        v += 0.15 * math.sin(2 * math.pi * freq * 3 * t)
        v *= env * 0.15
        return v

    chord_pattern = [
        (0, 2, 4),
        (1, 3, 5),
        (0, 3, 5),
        (2, 4, 6),
        (0, 2, 5),
        (1, 4, 6),
        (0, 3, 4),
        (2, 5, 6),
    ]

    for i in range(n):
        t = i / sr
        val = 0

        chord_idx = int(t / 3.0) % len(chord_pattern)
        chord = chord_pattern[chord_idx]

        for ni in chord:
            freq = notes[ni % len(notes)]
            val += pad(freq, t % 3.0, 3.0)

        lfo_v = lfo(t, 0.1)
        val += 0.03 * math.sin(2 * math.pi * 50 * t) * lfo_v

        if random.random() < 0.0003:
            freq = random.choice(notes) * random.choice([1, 0.5, 2])
            for j in range(min(sr // 4, n - i)):
                tt = j / sr
                env = max(0, 1.0 - tt * 4)
                val += 0.08 * env * math.sin(2 * math.pi * freq * tt)

        val = max(-0.9, min(0.9, val))
        sample = int(val * 32767)
        struct.pack_into('<hh', buf, i * 4, sample, sample)

    sound = pygame.mixer.Sound(buffer=bytes(buf))
    return sound

class MusicPlayer:
    def __init__(self):
        self.track = None
        self.channel = None
        self.playing = False
        self.volume = 0.3
        self.enabled = True

    def play(self, style="calm"):
        if not self.enabled:
            return
        try:
            self.track = generate_ambient_track(30, style)
            self.channel = self.track.play(-1)
            if self.channel:
                self.channel.set_volume(self.volume)
            self.playing = True
        except Exception:
            self.playing = False

    def stop(self):
        if self.channel:
            self.channel.stop()
        self.playing = False

    def set_volume(self, v):
        self.volume = v
        if self.channel:
            self.channel.set_volume(v)

    def toggle(self):
        if self.playing:
            self.stop()
        else:
            self.play()

music = MusicPlayer()
