import pygame
from config import WIDTH, HEIGHT, GOLD, GREEN_GLOW, BLUE

TUTORIAL_STEPS = [
    {"msg": "Welcome to PLAYTREE!", "sub": "Move with WASD", "key": "wasd", "timeout": 5},
    {"msg": "Attack enemies", "sub": "Left Click or SPACE + A", "key": "attack", "timeout": 0},
    {"msg": "Dodge incoming damage", "sub": "Press SPACE to dodge roll", "key": "dodge", "timeout": 0},
    {"msg": "Use your special ability", "sub": "Press Q or Left Shift", "key": "special", "timeout": 0},
    {"msg": "Collect resources", "sub": "Walk over glowing items", "key": "collect", "timeout": 0},
    {"msg": "Open Inventory", "sub": "Press I", "key": "inventory", "timeout": 0},
    {"msg": "Craft items", "sub": "Press C to craft", "key": "craft", "timeout": 0},
    {"msg": "Interact with the world", "sub": "Press E to interact", "key": "interact", "timeout": 0},
    {"msg": "Tame creatures", "sub": "Press TAB near a creature", "key": "tame", "timeout": 0},
    {"msg": "Build your base", "sub": "Press V for build mode", "key": "build", "timeout": 0},
    {"msg": "You're ready!", "sub": "Explore and complete rounds!", "key": "done", "timeout": 4},
]


class Tutorial:
    def __init__(self, player, audio=None):
        self.player = player
        self.audio = audio
        self.steps = list(TUTORIAL_STEPS)
        self.current_step = 0
        self.completed = []
        self.visible = False
        self.timer = 0
        self.step_timer = 0
        self.done = False
        self.alpha = 0
        self.fading_in = True

    def start(self):
        self.visible = True
        self.current_step = 0
        self.done = False
        self.timer = 0
        self.step_timer = 0
        self.fading_in = True
        self.alpha = 0

    def skip(self):
        self.done = True
        self.visible = False

    def update(self, dt, keys_pressed, action_triggers):
        if self.done or not self.visible:
            return

        if self.fading_in:
            self.alpha = min(255, self.alpha + dt * 300)
            if self.alpha >= 255:
                self.fading_in = False

        self.step_timer += dt
        step = self.steps[self.current_step]
        timeout = step.get("timeout", 0)
        key = step.get("key", "")

        if key == "done":
            self.done = True
            self.visible = False
            return

        if timeout > 0:
            if self.step_timer >= timeout:
                self._next_step()
                return

        if self.current_step >= 0:
            if self.steps[self.current_step].get("key") == "wasd":
                any_movement = (keys_pressed.get(pygame.K_w) or keys_pressed.get(pygame.K_a) or
                                keys_pressed.get(pygame.K_s) or keys_pressed.get(pygame.K_d) or
                                keys_pressed.get(pygame.K_UP) or keys_pressed.get(pygame.K_DOWN) or
                                keys_pressed.get(pygame.K_LEFT) or keys_pressed.get(pygame.K_RIGHT))
                if any_movement:
                    self._next_step()

        if action_triggers and key in action_triggers:
            if action_triggers[key]:
                self._next_step()

    def _next_step(self):
        self.completed.append(self.current_step)
        self.current_step += 1
        self.step_timer = 0
        self.fading_in = True
        self.alpha = 0
        if self.audio:
            self.audio.play("menu_hover")
        if self.current_step >= len(self.steps):
            self.done = True
            self.visible = False

    def draw(self, surface, font, small_font):
        if self.done or not self.visible:
            return

        step = self.steps[self.current_step]
        alpha = min(255, self.alpha)

        # Bottom-center box
        bw, bh = 500, 80
        bx = WIDTH // 2 - bw // 2
        by = HEIGHT - 110

        overlay = pygame.Surface((bw, bh), pygame.SRCALPHA)
        overlay.fill((8, 12, 8, int(180 * alpha / 255)))
        pygame.draw.rect(overlay, (*GREEN_GLOW[:3], int(100 * alpha / 255)), (0, 0, bw, bh), 2, border_radius=8)
        surface.blit(overlay, (bx, by))

        title = font.render(step["msg"], True, (*GREEN_GLOW[:3], alpha))
        surface.blit(title, (bx + 20, by + 12))

        sub = small_font.render(step["sub"], True, (180, 200, 180, alpha))
        surface.blit(sub, (bx + 20, by + 44))

        # Progress dots
        total = len(self.steps)
        dot_y = by + bh + 12
        for i in range(total):
            cx = WIDTH // 2 + (i - total // 2) * 20
            if i <= self.current_step:
                color = GREEN_GLOW
            else:
                color = (40, 60, 40)
            pygame.draw.circle(surface, color, (cx, dot_y), 5)

        hint = small_font.render("Press ESC to skip tutorial", True, (60, 80, 60, alpha))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, dot_y + 14))
