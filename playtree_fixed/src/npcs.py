import pygame
import math
import random
from config import *

NPC_TYPES = {
    "elder": {
        "name": "Elder Thorne", "color": (200, 180, 140), "hat_color": (80, 60, 40),
        "dialogue": [
            "Welcome, young one. The PlayTree once connected all lands...",
            "Corruption has shattered our world into floating islands.",
            "Gather Tree Energy from the forest to restore the roots.",
            "Only by restoring all five Tree Cores can we heal the world.",
            "The Root Titan guards the first Core. Be careful.",
        ],
        "quest_give": "Restore the Forest Core",
        "role": "quest_giver",
    },
    "blacksmith": {
        "name": "Forge", "color": (160, 120, 100), "hat_color": (100, 80, 60),
        "dialogue": [
            "Need a weapon? I can forge blades from Crystal Dust.",
            "Bring me materials and I'll make you something sharp.",
            "The crystal veins hold great power for enchanting.",
            "Every blade needs a soul. Ancient Seeds provide one.",
        ],
        "role": "shopkeeper",
    },
    "scout": {
        "name": "Veyra", "color": (100, 180, 140), "hat_color": (60, 120, 80),
        "dialogue": [
            "I've mapped the Skyroot Peaks. The air is thin up there.",
            "Watch for Crystal Monsters in the Hollow. They're fast.",
            "There's a hidden temple east of the ruins. Bring light.",
            "The desert hides ancient technology beneath the sand.",
            "Storms are getting worse. The corruption is spreading.",
        ],
        "role": "lore",
    },
    "healer": {
        "name": "Sage Mira", "color": (180, 200, 220), "hat_color": (100, 140, 200),
        "dialogue": [
            "Let me tend your wounds. The corruption leaves scars.",
            "Drink this tea. It will strengthen your spirit.",
            "Your pets need care too. Bring them by often.",
            "Light Fragments can heal even the deepest wounds.",
        ],
        "role": "healer",
    },
    "merchant": {
        "name": "Traveling Mira", "color": (200, 160, 100), "hat_color": (160, 120, 60),
        "dialogue": [
            "Rare goods from distant lands! Step right up!",
            "I've got eggs from creatures you've never seen.",
            "Golden Leaves open many doors, friend.",
            "Come back when you're richer. I'll have better stock.",
        ],
        "role": "shopkeeper",
    },
    "guard": {
        "name": "Captain Rook", "color": (120, 140, 160), "hat_color": (80, 100, 120),
        "dialogue": [
            "Halt! State your business in the village.",
            "The corruption beasts grow bolder each night.",
            "We need fighters. Will you stand with us?",
            "The Hollow King approaches. Prepare yourself.",
        ],
        "role": "guard",
    },
}


class NPC:
    def __init__(self, x, y, npc_type="elder"):
        data = NPC_TYPES.get(npc_type, NPC_TYPES["elder"])
        self.x = x
        self.y = y
        self.npc_type = npc_type
        self.name = data["name"]
        self.color = data["color"]
        self.hat_color = data["hat_color"]
        self.dialogue = list(data["dialogue"])
        self.role = data.get("role", "npc")
        self.dialogue_index = 0
        self.interact_range = 50
        self.size = 14
        self.anim_time = random.uniform(0, 6.28)
        self.state = "idle"
        self.state_timer = 0
        self.walk_target = None
        self.speed = 0.8

    def update(self, dt):
        self.anim_time += dt
        self.state_timer = max(0, self.state_timer - dt)

        if self.state_timer <= 0:
            if random.random() < 0.01:
                self.state = "wander"
                self.state_timer = random.uniform(2, 5)
                angle = random.uniform(0, 6.28)
                dist = random.randint(30, 80)
                self.walk_target = (self.x + math.cos(angle) * dist, self.y + math.sin(angle) * dist)
            else:
                self.state = "idle"
                self.state_timer = random.uniform(1, 4)

        if self.state == "wander" and self.walk_target:
            dx = self.walk_target[0] - self.x
            dy = self.walk_target[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 3:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            else:
                self.state = "idle"
                self.walk_target = None

    def is_in_range(self, player_x, player_y):
        dx = self.x - player_x
        dy = self.y - player_y
        return math.sqrt(dx * dx + dy * dy) < self.interact_range

    def get_dialogue(self):
        if not self.dialogue:
            return None
        text = self.dialogue[self.dialogue_index % len(self.dialogue)]
        self.dialogue_index += 1
        return text

    def draw(self, screen, camera_x, camera_y, time=0):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if sx < -50 or sx > WIDTH + 50 or sy < -50 or sy > HEIGHT + 50:
            return

        pygame.draw.ellipse(screen, (0, 0, 0, 50), (sx - 10, sy + 8, 20, 7))

        bob = math.sin(self.anim_time * 2) * 1.5

        body_y = int(sy + bob)
        pygame.draw.circle(screen, self.color, (sx, body_y), self.size)
        pygame.draw.circle(screen, (*self.color[:3], 60), (sx, body_y), self.size + 3, 2)

        hat_w = 18
        pygame.draw.ellipse(screen, self.hat_color, (sx - hat_w // 2, body_y - self.size - 5, hat_w, 8))
        pygame.draw.rect(screen, self.hat_color, (sx - 4, body_y - self.size - 12, 8, 10))

        for ex in [-3, 3]:
            pygame.draw.circle(screen, (40, 40, 50), (sx + ex, body_y - 2), 2)
            pygame.draw.circle(screen, WHITE, (sx + ex, body_y - 2), 1)

        mouth_y = body_y + 3
        pygame.draw.arc(screen, (60, 40, 40), (sx - 2, mouth_y - 1, 4, 3), 3.14, 6.28, 1)

        name_f = pygame.font.Font(None, 14)
        name_s = name_f.render(self.name, True, (200, 200, 200))
        screen.blit(name_s, (sx - name_s.get_width() // 2, body_y - self.size - 20))

        if self.role == "quest_giver":
            indicator_y = body_y - self.size - 30 + math.sin(time * 3) * 3
            pygame.draw.polygon(screen, GOLD, [(sx, indicator_y), (sx - 4, indicator_y - 8), (sx + 4, indicator_y - 8)])
        elif self.role == "healer":
            pygame.draw.circle(screen, (100, 255, 100), (sx + self.size + 2, body_y - 5), 3)

    def draw_interaction(self, screen, player_x, player_y, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        if self.is_in_range(player_x, player_y):
            try:
                ctrl = pygame.joystick.get_count() > 0
            except Exception:
                ctrl = False
            if ctrl:
                from src.ui import xbox_icons
                xbox_icons.draw_dual_prompt(screen, sx - 20, sy - self.size - 35, "X", "E", "Talk", 14)
            else:
                prompt_f = pygame.font.Font(None, 22)
                ps = prompt_f.render("Press E to talk", True, GOLD)
                bg = pygame.Surface((ps.get_width() + 10, ps.get_height() + 4), pygame.SRCALPHA)
                bg.fill((10, 15, 10, 180))
                screen.blit(bg, (sx - bg.get_width() // 2, sy - self.size - 42))
                screen.blit(ps, (sx - ps.get_width() // 2, sy - self.size - 40))


class DialogueBox:
    def __init__(self):
        self.active = False
        self.npc_name = ""
        self.text = ""
        self.char_index = 0
        self.timer = 0
        self.speed = 0.03
        self.done = False

    def start(self, npc_name, text):
        self.active = True
        self.npc_name = npc_name
        self.text = text
        self.char_index = 0
        self.timer = 0
        self.done = False

    def update(self, dt):
        if not self.active:
            return
        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0
            self.char_index += 1
            if self.char_index >= len(self.text):
                self.char_index = len(self.text)
                self.done = True

    def advance(self):
        if not self.done:
            self.char_index = len(self.text)
            self.done = True
        else:
            self.active = False

    def draw(self, screen):
        if not self.active:
            return
        box_h = 100
        box_y = HEIGHT - box_h - 20
        box_x = 60
        box_w = WIDTH - 120

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((10, 15, 10, 220))
        pygame.draw.rect(bg, (*GREEN_GLOW[:3], 60), bg.get_rect(), border_radius=8, width=2)
        screen.blit(bg, (box_x, box_y))

        nf = pygame.font.Font(None, 26)
        name_s = nf.render(self.npc_name, True, GOLD)
        screen.blit(name_s, (box_x + 15, box_y + 10))

        tf = pygame.font.Font(None, 22)
        visible = self.text[:self.char_index]
        words = visible.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + " " + word if current_line else word
            if tf.size(test)[0] < box_w - 40:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines[-3:]):
            ls = tf.render(line, True, (200, 220, 200))
            screen.blit(ls, (box_x + 15, box_y + 35 + i * 20))

        if self.done:
            try:
                ctrl = pygame.joystick.get_count() > 0
            except Exception:
                ctrl = False
            if ctrl:
                from src.ui import xbox_icons
                xbox_icons.draw_dual_prompt(screen, box_x + box_w - 40, box_y +
                                            box_h - 18, "A", "E/Click", "Continue", 12)
            else:
                hint_f = pygame.font.Font(None, 18)
                hint = hint_f.render("Click or press E to continue", True, (100, 140, 100))
                screen.blit(hint, (box_x + box_w - hint.get_width() - 15, box_y + box_h - 20))
