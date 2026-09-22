import pygame
import math
import random
import struct
import array
import os
import tempfile
from config import *

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 22050
        self.cache = {}
        self.enabled = True
        self.mixer_initialized = False
        self._init_mixer()

    def _init_mixer(self):
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.pre_init(self.sample_rate, -16, 1, 512)
            pygame.mixer.init()
            self.mixer_initialized = True
        except Exception:
            self.mixer_initialized = False
            self.enabled = False

    def _generate_wave(self, freq, duration, volume=0.3, wave_type="sine", fade_out=True):
        n_samples = int(self.sample_rate * duration)
        buf = []
        for i in range(n_samples):
            t = i / self.sample_rate
            if wave_type == "sine":
                val = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square":
                val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            elif wave_type == "sawtooth":
                val = 2.0 * (t * freq - math.floor(t * freq + 0.5))
            elif wave_type == "noise":
                val = random.uniform(-1, 1)
            elif wave_type == "triangle":
                val = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
            else:
                val = math.sin(2 * math.pi * freq * t)

            if fade_out and duration > 0.05:
                fade = 1.0 - (i / n_samples) * 0.5
                val *= fade

            val = max(-1.0, min(1.0, val * volume))
            buf.append(int(val * 32767))
        return buf

    def _generate_envelope(self, buf, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        n = len(buf)
        result = list(buf)
        attack_n = int(self.sample_rate * attack)
        decay_n = int(self.sample_rate * decay)
        release_n = int(self.sample_rate * release)

        for i in range(min(attack_n, n)):
            result[i] = int(result[i] * (i / max(1, attack_n)))
        for i in range(decay_n):
            idx = attack_n + i
            if idx < n:
                result[idx] = int(result[idx] * (1.0 - (i / max(1, decay_n)) * (1 - sustain)))
        release_start = n - release_n
        for i in range(release_n):
            idx = release_start + i
            if idx < n:
                result[idx] = int(result[idx] * (1.0 - i / max(1, release_n)))
        return result

    def _buf_to_sound(self, buf):
        try:
            audio_array = array.array('h', buf)
            data = audio_array.tobytes()
            sound = pygame.mixer.Sound(buffer=data)
            return sound
        except Exception:
            return None

    def _buf_to_wav_file(self, buf):
        try:
            audio_array = array.array('h', buf)
            tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            tmp_name = tmp.name
            tmp.close()
            with open(tmp_name, 'wb') as f:
                n = len(buf)
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + n * 2))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<IHHIIHH', 16, 1, 1, self.sample_rate, self.sample_rate * 2, 2, 16))
                f.write(b'data')
                f.write(struct.pack('<I', n * 2))
                f.write(audio_array.tobytes())
            return tmp_name
        except Exception:
            return None

    def generate_attack(self):
        buf = self._generate_wave(440, 0.08, 0.4, "sawtooth")
        buf2 = self._generate_wave(220, 0.12, 0.3, "square")
        combined = [buf[i] + buf2[min(i, len(buf2)-1)] for i in range(max(len(buf), len(buf2)))]
        combined = self._generate_envelope(combined, 0.005, 0.02, 0.5, 0.05)
        return self._buf_to_sound(combined)

    def generate_hit(self):
        buf = self._generate_wave(180, 0.1, 0.5, "noise")
        buf2 = self._generate_wave(90, 0.15, 0.3, "square")
        combined = [buf[i] + buf2[min(i, len(buf2)-1)] for i in range(max(len(buf), len(buf2)))]
        combined = self._generate_envelope(combined, 0.001, 0.03, 0.3, 0.08)
        return self._buf_to_sound(combined)

    def generate_collect(self):
        notes = [523, 659, 784, 1047]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.08, 0.35, "sine"))
        combined = self._generate_envelope(buf, 0.005, 0.02, 0.6, 0.05)
        return self._buf_to_sound(combined)

    def generate_heal(self):
        notes = [262, 330, 392, 523]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.12, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.02, 0.05, 0.7, 0.1)
        return self._buf_to_sound(combined)

    def generate_magic(self):
        buf = self._generate_wave(880, 0.15, 0.3, "sine")
        buf2 = self._generate_wave(1100, 0.2, 0.2, "triangle")
        combined = [buf[i] + buf2[min(i, len(buf2)-1)] for i in range(max(len(buf), len(buf2)))]
        combined = self._generate_envelope(combined, 0.01, 0.05, 0.6, 0.1)
        return self._buf_to_sound(combined)

    def generate_craft(self):
        notes = [392, 494, 587, 784]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.1, 0.3, "triangle"))
        combined = self._generate_envelope(buf, 0.01, 0.03, 0.5, 0.08)
        return self._buf_to_sound(combined)

    def generate_levelup(self):
        notes = [262, 330, 392, 523, 659, 784, 1047]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.12, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.01, 0.03, 0.7, 0.15)
        return self._buf_to_sound(combined)

    def generate_thunder(self):
        buf = self._generate_wave(40, 0.8, 0.5, "noise")
        buf2 = self._generate_wave(30, 1.0, 0.4, "square")
        combined = [buf[i] + buf2[min(i, len(buf2)-1)] for i in range(max(len(buf), len(buf2)))]
        combined = self._generate_envelope(combined, 0.001, 0.1, 0.4, 0.5)
        return self._buf_to_sound(combined)

    def generate_rain(self):
        buf = self._generate_wave(100, 0.5, 0.12, "noise")
        combined = self._generate_envelope(buf, 0.05, 0.1, 0.8, 0.2)
        return self._buf_to_sound(combined)

    def generate_menu_select(self):
        buf = self._generate_wave(660, 0.06, 0.3, "sine")
        buf2 = self._generate_wave(880, 0.06, 0.25, "sine")
        combined = buf + buf2
        combined = self._generate_envelope(combined, 0.005, 0.01, 0.6, 0.03)
        return self._buf_to_sound(combined)

    def generate_menu_confirm(self):
        notes = [440, 554, 659]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.08, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.005, 0.02, 0.6, 0.05)
        return self._buf_to_sound(combined)

    def generate_mount_summon(self):
        buf = self._generate_wave(200, 0.15, 0.3, "triangle")
        buf2 = self._generate_wave(400, 0.2, 0.2, "sine")
        buf3 = self._generate_wave(600, 0.25, 0.15, "sine")
        combined = buf + buf2 + buf3
        combined = self._generate_envelope(combined, 0.01, 0.05, 0.5, 0.15)
        return self._buf_to_sound(combined)

    def generate_boss_appear(self):
        notes = [110, 130, 146, 164, 174, 196]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.15, 0.35, "sawtooth"))
        combined = self._generate_envelope(buf, 0.005, 0.03, 0.6, 0.1)
        return self._buf_to_sound(combined)

    def generate_boss_defeat(self):
        notes = [392, 494, 587, 784, 988, 1175]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.15, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.01, 0.03, 0.7, 0.2)
        return self._buf_to_sound(combined)

    def generate_place(self):
        buf = self._generate_wave(300, 0.08, 0.35, "square")
        buf2 = self._generate_wave(200, 0.1, 0.3, "triangle")
        combined = buf + buf2
        combined = self._generate_envelope(combined, 0.005, 0.02, 0.5, 0.04)
        return self._buf_to_sound(combined)

    def generate_equip(self):
        notes = [523, 659, 784]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.1, 0.35, "sine"))
        combined = self._generate_envelope(buf, 0.005, 0.02, 0.6, 0.08)
        return self._buf_to_sound(combined)

    def generate_tab_switch(self):
        buf = self._generate_wave(800, 0.04, 0.25, "sine")
        buf2 = self._generate_wave(1000, 0.04, 0.15, "triangle")
        combined = buf + buf2
        combined = self._generate_envelope(combined, 0.002, 0.01, 0.5, 0.02)
        return self._buf_to_sound(combined)

    def generate_lobby_connect(self):
        notes = [330, 440, 554, 659]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.12, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.01, 0.03, 0.6, 0.1)
        return self._buf_to_sound(combined)

    def generate_lobby_disconnect(self):
        notes = [659, 554, 440, 330]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.12, 0.3, "triangle"))
        combined = self._generate_envelope(buf, 0.01, 0.03, 0.5, 0.1)
        return self._buf_to_sound(combined)

    def generate_controller_btn(self):
        buf = self._generate_wave(1200, 0.03, 0.25, "sine")
        combined = self._generate_envelope(buf, 0.001, 0.01, 0.4, 0.015)
        return self._buf_to_sound(combined)

    def generate_dodge(self):
        buf = self._generate_wave(600, 0.06, 0.3, "sine")
        buf2 = self._generate_wave(900, 0.08, 0.2, "triangle")
        combined = buf + buf2
        combined = self._generate_envelope(combined, 0.001, 0.01, 0.3, 0.03)
        return self._buf_to_sound(combined)

    def generate_level_up(self):
        notes = [392, 494, 587, 784, 988, 1175, 1568]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.15, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.005, 0.02, 0.7, 0.2)
        return self._buf_to_sound(combined)

    def generate_quest_complete(self):
        notes = [523, 659, 784, 1047, 784, 1047, 1319]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.12, 0.3, "sine"))
        combined = self._generate_envelope(buf, 0.005, 0.03, 0.7, 0.15)
        return self._buf_to_sound(combined)

    def generate_menu_hover(self):
        buf = self._generate_wave(880, 0.04, 0.25, "sine")
        combined = self._generate_envelope(buf, 0.001, 0.005, 0.5, 0.02)
        return self._buf_to_sound(combined)

    def generate_new_game_plus(self):
        notes = [220, 277, 330, 440, 554, 659, 880]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.2, 0.3, "triangle"))
        combined = self._generate_envelope(buf, 0.01, 0.05, 0.6, 0.3)
        return self._buf_to_sound(combined)

    def generate_screenshot(self):
        notes = [1200, 1600]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.04, 0.25, "sine"))
        combined = self._generate_envelope(buf, 0.001, 0.01, 0.3, 0.02)
        return self._buf_to_sound(combined)

    def generate_pet_ability(self):
        notes = [440, 554, 659]
        buf = []
        for note in notes:
            buf.extend(self._generate_wave(note, 0.08, 0.25, "triangle"))
        combined = self._generate_envelope(buf, 0.005, 0.02, 0.5, 0.08)
        return self._buf_to_sound(combined)

    def generate_place_sound(self):
        return self.generate_place()


class MusicGenerator:
    def __init__(self):
        self.sample_rate = 22050

    SCALES = {
        "major":       [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24],
        "minor":       [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24],
        "dorian":      [0, 2, 3, 5, 7, 9, 10, 12, 14, 15, 17, 19, 21, 22, 24],
        "pentatonic":  [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28, 31, 33],
        "blues":       [0, 3, 5, 6, 7, 10, 12, 15, 17, 18, 19, 22, 24, 27, 29],
        "harmonic_m":  [0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17, 19, 20, 23, 24],
    }

    def _generate_bass_line(self, tempo, duration, key, scale_notes, wave_type="sawtooth"):
        base_freq = 110 * (2 ** (key / 12))
        beat_dur = 60.0 / tempo
        n_beats = int(duration / beat_dur)
        buf = []
        bass_pattern = [0, 0, 7, 5, 0, 0, 3, 7]
        for i in range(n_beats):
            note_offset = bass_pattern[i % len(bass_pattern)]
            freq = base_freq * (2 ** (note_offset / 12))
            volume = 0.08 + 0.02 * math.sin(i * 0.5)
            n_samples = int(self.sample_rate * beat_dur * 0.6)
            note_buf = []
            for s in range(n_samples):
                st = s / self.sample_rate
                val = math.sin(2 * math.pi * freq * st)
                val *= 0.8 + 0.2 * math.sin(2 * math.pi * (freq * 0.5) * st)
                env = 1.0 - (s / max(1, n_samples)) * 0.4
                note_buf.append(int(max(-1, min(1, val * volume * env)) * 32767))
            buf.extend(note_buf)
        return buf

    def _generate_harmony(self, tempo, duration, key, scale_notes):
        base_freq = 220 * (2 ** (key / 12))
        beat_dur = 60.0 / tempo
        n_beats = int(duration / beat_dur)
        buf = []
        chord_prog = [[0, 4, 7], [5, 9, 12], [7, 11, 14], [0, 4, 7]]
        for i in range(n_beats):
            chord = chord_prog[i % len(chord_prog)]
            n_samples = int(self.sample_rate * beat_dur * 0.5)
            note_buf = []
            for s in range(n_samples):
                st = s / self.sample_rate
                val = 0
                for interval in chord:
                    freq = base_freq * (2 ** (interval / 12))
                    val += math.sin(2 * math.pi * freq * st) * 0.15
                env = 1.0 - (s / max(1, n_samples)) * 0.3
                note_buf.append(int(max(-1, min(1, val * env)) * 32767))
            buf.extend(note_buf)
        return buf

    def _generate_melody(self, tempo=120, duration=15, key=0, scale_name=None):
        if scale_name is None:
            scale_name = random.choice(list(self.SCALES.keys()))
        scale = self.SCALES[scale_name]
        base_freq = 220 * (2 ** (key / 12))
        beat_dur = 60.0 / tempo
        n_beats = int(duration / beat_dur)
        buf = []
        prev_idx = random.randint(0, min(6, len(scale) - 1))

        for i in range(n_beats):
            intervals = [-2, -1, 0, 1, 2, 3]
            weights = [0.1, 0.2, 0.25, 0.2, 0.15, 0.1]
            chosen_interval = random.choices(intervals, weights)[0]
            note_idx = max(0, min(len(scale) - 1, prev_idx + chosen_interval))
            prev_idx = note_idx
            freq = base_freq * (2 ** (scale[note_idx] / 12))
            volume = 0.10 + 0.04 * math.sin(i * 0.3) + 0.02 * math.sin(i * 0.7)
            note_len = beat_dur * random.choice([0.5, 0.75, 1.0])
            n_samples = int(self.sample_rate * note_len)
            note_buf = []
            for s in range(n_samples):
                st = s / self.sample_rate
                val = math.sin(2 * math.pi * freq * st)
                val *= 0.7 + 0.3 * math.sin(2 * math.pi * (freq * 0.5) * st)
                if s > n_samples * 0.7:
                    val *= 1.0 - (s - n_samples * 0.7) / (n_samples * 0.3) * 0.5
                note_buf.append(int(max(-1, min(1, val * volume)) * 32767))
            pad_len = int(self.sample_rate * beat_dur) - len(note_buf)
            note_buf.extend([0] * max(0, pad_len))
            buf.extend(note_buf)
        return buf

    def _mix_buffers(self, *buffers, weights=None):
        if weights is None:
            weights = [1.0] * len(buffers)
        max_len = max(len(b) for b in buffers)
        result = []
        for i in range(max_len):
            val = 0
            for buf, w in zip(buffers, weights):
                val += buf[min(i, len(buf) - 1)] * w
            result.append(int(max(-32767, min(32767, val))))
        return result

    def _save_as_wav(self, buf, filepath):
        try:
            n = len(buf)
            audio_array = array.array('h', buf)
            with open(filepath, 'wb') as f:
                f.write(b'RIFF')
                f.write(struct.pack('<I', 36 + n * 2))
                f.write(b'WAVE')
                f.write(b'fmt ')
                f.write(struct.pack('<IHHIIHH', 16, 1, 1, self.sample_rate, self.sample_rate * 2, 2, 16))
                f.write(b'data')
                f.write(struct.pack('<I', n * 2))
                f.write(audio_array.tobytes())
            return True
        except Exception:
            return False

    def generate_ambient_music(self):
        key = random.choice([0, 3, 5, 7, 9])
        scale_name = random.choice(["major", "pentatonic", "dorian", "minor"])
        melody = self._generate_melody(75, 20, key, scale_name)
        harmony = self._generate_harmony(75, 20, key, self.SCALES[scale_name])
        bass = self._generate_bass_line(75, 20, key, self.SCALES[scale_name])
        mixed = self._mix_buffers(melody, harmony, bass, weights=[0.6, 0.25, 0.35])
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        path = tmp.name
        tmp.close()
        if self._save_as_wav(mixed, path):
            return path
        return None

    def generate_combat_music(self):
        key = random.choice([0, 5, 7])
        scale_name = random.choice(["minor", "blues", "harmonic_m"])
        melody = self._generate_melody(140, 15, key, scale_name)
        harmony = self._generate_harmony(140, 15, key, self.SCALES[scale_name])
        bass = self._generate_bass_line(140, 15, key, self.SCALES[scale_name])
        mixed = self._mix_buffers(melody, harmony, bass, weights=[0.55, 0.2, 0.45])
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        path = tmp.name
        tmp.close()
        if self._save_as_wav(mixed, path):
            return path
        return None

    def generate_boss_music(self):
        key = 0
        scale_name = random.choice(["harmonic_m", "minor", "blues"])
        melody = self._generate_melody(165, 20, key, scale_name)
        harmony = self._generate_harmony(165, 20, key, self.SCALES[scale_name])
        bass = self._generate_bass_line(165, 20, key, self.SCALES[scale_name])
        mixed = self._mix_buffers(melody, harmony, bass, weights=[0.5, 0.2, 0.5])
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        path = tmp.name
        tmp.close()
        if self._save_as_wav(mixed, path):
            return path
        return None

    def generate_menu_music(self):
        key = random.choice([0, 5, 7])
        scale_name = "pentatonic"
        melody = self._generate_melody(70, 22, key, scale_name)
        harmony = self._generate_harmony(70, 22, key, self.SCALES[scale_name])
        mixed = self._mix_buffers(melody, harmony, weights=[0.7, 0.3])
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        path = tmp.name
        tmp.close()
        if self._save_as_wav(mixed, path):
            return path
        return None


class ProceduralAudio:
    def __init__(self, sfx_vol=0.5, music_vol=0.3):
        self.sounds = {}
        self.music_gen = MusicGenerator()
        self.sfx_vol = sfx_vol
        self.music_vol = music_vol
        self.enabled = True
        self.music_playing = False
        self.current_music_type = None
        self.current_music_path = None
        self.music_temp_files = []
        self._generate_all()

    def _generate_all(self):
        gen = SoundGenerator()
        if not gen.enabled or not gen.mixer_initialized:
            self.enabled = False
            return
        try:
            self.sounds["attack"] = gen.generate_attack()
            self.sounds["hit"] = gen.generate_hit()
            self.sounds["collect"] = gen.generate_collect()
            self.sounds["heal"] = gen.generate_heal()
            self.sounds["magic"] = gen.generate_magic()
            self.sounds["craft"] = gen.generate_craft()
            self.sounds["levelup"] = gen.generate_levelup()
            self.sounds["thunder"] = gen.generate_thunder()
            self.sounds["rain"] = gen.generate_rain()
            self.sounds["menu_select"] = gen.generate_menu_select()
            self.sounds["menu_confirm"] = gen.generate_menu_confirm()
            self.sounds["mount"] = gen.generate_mount_summon()
            self.sounds["boss_appear"] = gen.generate_boss_appear()
            self.sounds["boss_defeat"] = gen.generate_boss_defeat()
            self.sounds["place"] = gen.generate_place()
            self.sounds["equip"] = gen.generate_equip()
            self.sounds["tab_switch"] = gen.generate_tab_switch()
            self.sounds["lobby_connect"] = gen.generate_lobby_connect()
            self.sounds["lobby_disconnect"] = gen.generate_lobby_disconnect()
            self.sounds["controller_btn"] = gen.generate_controller_btn()
            self.sounds["dodge"] = gen.generate_dodge()
            self.sounds["quest_complete"] = gen.generate_quest_complete()
            self.sounds["menu_hover"] = gen.generate_menu_hover()
            self.sounds["new_game_plus"] = gen.generate_new_game_plus()
            self.sounds["screenshot"] = gen.generate_screenshot()
            self.sounds["pet_ability"] = gen.generate_pet_ability()
        except Exception:
            self.enabled = False

    def play(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.set_volume(self.sfx_vol)
                sound.play()
            except Exception:
                pass

    def play_music(self, music_type="ambient"):
        if not self.enabled:
            return
        if self.current_music_type == music_type and self.music_playing:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

        try:
            if music_type == "ambient":
                path = self.music_gen.generate_ambient_music()
            elif music_type == "combat":
                path = self.music_gen.generate_combat_music()
            elif music_type == "boss":
                path = self.music_gen.generate_boss_music()
            elif music_type == "menu":
                path = self.music_gen.generate_menu_music()
            else:
                path = self.music_gen.generate_ambient_music()

            if path and os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.music_vol)
                pygame.mixer.music.play(-1)
                self.music_playing = True
                self.current_music_type = music_type
                self.current_music_path = path
                self.music_temp_files.append(path)
                if len(self.music_temp_files) > 10:
                    old = self.music_temp_files.pop(0)
                    try:
                        os.remove(old)
                    except Exception:
                        pass
        except Exception:
            self.music_playing = False

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
            self.current_music_type = None
        except Exception:
            pass

    def set_sfx_volume(self, vol):
        self.sfx_vol = vol

    def set_music_volume(self, vol):
        self.music_vol = vol
        try:
            pygame.mixer.music.set_volume(vol)
        except Exception:
            pass
