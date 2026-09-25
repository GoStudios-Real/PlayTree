import pygame
import math
import sys

IS_MOBILE = sys.platform in ("android", "ios") or hasattr(sys, "getandroidapilevel")


class VirtualJoystick:
    def __init__(self, x, y, radius=60):
        self.base_x = x
        self.base_y = y
        self.radius = radius
        self.knob_x = x
        self.knob_y = y
        self.active = False
        self.finger_id = None
        self.dx = 0.0
        self.dy = 0.0

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            fx = event.x * pygame.display.get_surface().get_width()
            fy = event.y * pygame.display.get_surface().get_height()
            dist = math.hypot(fx - self.base_x, fy - self.base_y)
            if dist < self.radius * 1.5:
                self.active = True
                self.finger_id = event.finger_id
                self._update(fx, fy)
                return True
        elif event.type == pygame.FINGERUP:
            if event.finger_id == self.finger_id:
                self.active = False
                self.finger_id = None
                self.knob_x = self.base_x
                self.knob_y = self.base_y
                self.dx = 0.0
                self.dy = 0.0
                return True
        elif event.type == pygame.FINGERMOTION:
            if event.finger_id == self.finger_id:
                fx = event.x * pygame.display.get_surface().get_width()
                fy = event.y * pygame.display.get_surface().get_height()
                self._update(fx, fy)
                return True
        return False

    def _update(self, fx, fy):
        dx = fx - self.base_x
        dy = fy - self.base_y
        dist = math.hypot(dx, dy)
        if dist > self.radius:
            dx = dx / dist * self.radius
            dy = dy / dist * self.radius
            dist = self.radius
        self.knob_x = self.base_x + dx
        self.knob_y = self.base_y + dy
        self.dx = dx / self.radius if self.radius > 0 else 0
        self.dy = dy / self.radius if self.radius > 0 else 0

    def draw(self, surface):
        alpha_surface = pygame.Surface((self.radius * 2 + 20, self.radius * 2 + 20), pygame.SRCALPHA)
        cx = self.radius + 10
        cy = self.radius + 10
        pygame.draw.circle(alpha_surface, (80, 255, 120, 40), (cx, cy), self.radius)
        pygame.draw.circle(alpha_surface, (80, 255, 120, 80), (cx, cy), self.radius, 2)
        knob_dx = self.knob_x - self.base_x
        knob_dy = self.knob_y - self.base_y
        pygame.draw.circle(alpha_surface, (80, 255, 120, 150), (int(cx + knob_dx), int(cy + knob_dy)), 22)
        pygame.draw.circle(alpha_surface, (80, 255, 120, 200), (int(cx + knob_dx), int(cy + knob_dy)), 22, 2)
        surface.blit(alpha_surface, (self.base_x - cx, self.base_y - cy))


class TouchButton:
    def __init__(self, x, y, radius, label, color=(80, 255, 120)):
        self.x = x
        self.y = y
        self.radius = radius
        self.label = label
        self.color = color
        self.pressed = False
        self.finger_id = None
        self.press_time = 0
        self._was_pressed = False
        self._cooldown = 0

    def handle_event(self, event):
        if event.type == pygame.FINGERDOWN:
            fx = event.x * pygame.display.get_surface().get_width()
            fy = event.y * pygame.display.get_surface().get_height()
            dist = math.hypot(fx - self.x, fy - self.y)
            if dist < self.radius * 1.3:
                self.pressed = True
                self.finger_id = event.finger_id
                self.press_time = pygame.time.get_ticks()
                return True
        elif event.type == pygame.FINGERUP:
            if event.finger_id == self.finger_id:
                self.pressed = False
                self.finger_id = None
                return True
        return False

    def just_pressed(self):
        now = self.pressed
        was = self._was_pressed
        self._was_pressed = now
        return now and not was

    def is_pressed(self):
        return self.pressed

    def draw(self, surface):
        alpha_surface = pygame.Surface((self.radius * 2 + 4, self.radius * 2 + 4), pygame.SRCALPHA)
        cx = self.radius + 2
        cy = self.radius + 2
        bg_alpha = 100 if self.pressed else 50
        border_alpha = 200 if self.pressed else 100
        bg_color = (*self.color[:3], bg_alpha)
        border_color = (*self.color[:3], border_alpha)
        pygame.draw.circle(alpha_surface, bg_color, (cx, cy), self.radius)
        pygame.draw.circle(alpha_surface, border_color, (cx, cy), self.radius, 2)
        font = pygame.font.Font(None, 24)
        txt = font.render(self.label, True, self.color)
        txt_rect = txt.get_rect(center=(cx, cy))
        alpha_surface.blit(txt, txt_rect)
        surface.blit(alpha_surface, (self.x - cx, self.y - cy))


class VirtualKeyboard:
    def __init__(self, screen_w=1280, screen_h=720):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.visible = False
        self.shift = False
        self._keys = []
        # bottom area
        kb_w, kb_h = 900, 190
        kb_x = (screen_w - kb_w)//2
        kb_y = screen_h - kb_h - 10
        rows = [
            list("1234567890"),
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
        ]
        self.rect = pygame.Rect(kb_x, kb_y, kb_w, kb_h)
        # build key rects
        y = kb_y + 8
        for r, row in enumerate(rows):
            n = len(row)
            w = 68 if r==0 else 62
            gap = 6
            total = n*w + (n-1)*gap
            x0 = kb_x + (kb_w - total)//2
            for i,ch in enumerate(row):
                rect = pygame.Rect(x0 + i*(w+gap), y, w, 32)
                self._keys.append((rect, ch))
            y += 38
        # bottom row: Shift, Space, Back, Enter
        self.shift_rect = pygame.Rect(kb_x+8, y, 90, 34)
        self.space_rect = pygame.Rect(kb_x+104, y, 580, 34)
        self.back_rect = pygame.Rect(kb_x+690, y, 90, 34)
        self.enter_rect = pygame.Rect(kb_x+788, y, 104, 34)

    def _post(self, char):
        # post KEYDOWN with unicode
        try:
            if char == "BACK":
                evt = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode="", mod=0)
            elif char == "ENTER":
                evt = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r", mod=0)
            elif char == " ":
                evt = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=" ", mod=0)
            else:
                key = ord(char.lower())
                evt = pygame.event.Event(pygame.KEYDOWN, key=key, unicode=char, mod=0)
            pygame.event.post(evt)
        except: pass

    def handle_event(self, event):
        if not self.visible:
            return False
        if event.type != pygame.FINGERDOWN:
            return False
        surf = pygame.display.get_surface()
        if not surf: return False
        fx = event.x * surf.get_width()
        fy = event.y * surf.get_height()
        # scale fx/fy to 1280x720 logical if display scaled? assume render_surface size
        # touch_controls uses display.get_surface() size, which is display size, but our rect is in 1280x720 logical — convert
        try:
            dw, dh = surf.get_size()
            fx = fx * 1280 / dw if dw!=1280 else fx
            fy = fy * 720 / dh if dh!=720 else fy
        except: pass
        for rect,ch in self._keys:
            if rect.collidepoint(fx,fy):
                c = ch if not self.shift else ch.lower() if ch.isalpha() else ch
                # for letters shift toggles lower/upper? we start upper, shift->lower
                if ch.isalpha():
                    c = ch.lower() if self.shift else ch
                self._post(c)
                return True
        if self.shift_rect.collidepoint(fx,fy):
            self.shift = not self.shift
            return True
        if self.space_rect.collidepoint(fx,fy):
            self._post(" ")
            return True
        if self.back_rect.collidepoint(fx,fy):
            self._post("BACK")
            return True
        if self.enter_rect.collidepoint(fx,fy):
            self._post("ENTER")
            return True
        # tap outside keyboard? don't consume
        return False

    def draw(self, surface):
        if not self.visible:
            return
        bg = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA).convert_alpha()
        bg.fill((20,20,30,210))
        pygame.draw.rect(bg, (80,255,120,70), bg.get_rect(), 2, border_radius=10)
        # keys
        for rect,ch in self._keys:
            lbl = ch.lower() if self.shift and ch.isalpha() else ch
            r = pygame.Rect(rect.x - self.rect.x, rect.y - self.rect.y, rect.w, rect.h)
            pygame.draw.rect(bg, (60,60,80,230), r, border_radius=6)
            pygame.draw.rect(bg, (80,255,120,90), r, 1, border_radius=6)
            f = pygame.font.Font(None, 20)
            txt = f.render(lbl, True, (230,255,230))
            tr = txt.get_rect(center=r.center)
            bg.blit(txt, tr)
        for rect,lbl in [(self.shift_rect,"Shift"),(self.space_rect,"Space"),(self.back_rect,"Back"),(self.enter_rect,"Enter")]:
            r = pygame.Rect(rect.x - self.rect.x, rect.y - self.rect.y, rect.w, rect.h)
            col = (80,255,120,50) if (lbl=="Shift" and self.shift) else (50,50,70,230)
            pygame.draw.rect(bg, col, r, border_radius=6)
            pygame.draw.rect(bg, (80,255,120,70), r, 1, border_radius=6)
            f = pygame.font.Font(None, 18)
            txt = f.render(lbl, True, (200,255,200))
            bg.blit(txt, txt.get_rect(center=r.center))
        surface.blit(bg, self.rect.topleft)


class TouchControls:
    def __init__(self, screen_w=1280, screen_h=720):
        self.screen_w = screen_w
        self.screen_h = screen_h
        margin = 30
        btn_r = 28
        spacing = 70

        self.joystick = VirtualJoystick(margin + 70, screen_h - margin - 70, radius=55)

        attack_x = screen_w - margin - 50
        attack_y = screen_h - margin - 160
        self.attack_btn = TouchButton(attack_x, attack_y, btn_r, "ATK", (255, 80, 80))

        dodge_x = screen_w - margin - 50 - spacing
        dodge_y = screen_h - margin - 100
        self.dodge_btn = TouchButton(dodge_x, dodge_y, btn_r, "DGE", (80, 180, 255))

        special_x = screen_w - margin - 50
        special_y = screen_h - margin - 80
        self.special_btn = TouchButton(special_x, special_y, btn_r, "SPL", (255, 200, 50))

        interact_x = screen_w - margin - 50 - spacing
        interact_y = screen_h - margin - 170
        self.interact_btn = TouchButton(interact_x, interact_y, btn_r * 0.8, "ACT", (100, 255, 180))

        potion_x = screen_w - margin - 50 - spacing * 2
        potion_y = screen_h - margin - 130
        self.potion_btn = TouchButton(potion_x, potion_y, btn_r * 0.7, "POT", (60, 200, 60))

        inv_x = margin + 70
        inv_y = margin + 70
        self.inventory_btn = TouchButton(inv_x, inv_y, btn_r * 0.8, "INV", (200, 180, 100))

        craft_x = margin + 70 + spacing
        craft_y = margin + 70
        self.craft_btn = TouchButton(craft_x, craft_y, btn_r * 0.8, "CRF", (180, 140, 80))

        mount_x = margin + 70
        mount_y = margin + 70 + spacing
        self.mount_btn = TouchButton(mount_x, mount_y, btn_r * 0.7, "MNT", (150, 200, 255))

        storm_x = screen_w - margin - 50
        storm_y = screen_h - margin - 230
        self.storm_btn = TouchButton(storm_x, storm_y, btn_r * 0.85, "STRM", (200, 120, 255))

        tame_x = screen_w - margin - 50 - spacing
        tame_y = screen_h - margin - 230
        self.tame_btn = TouchButton(tame_x, tame_y, btn_r * 0.75, "TAME", (120, 255, 140))

        weapon_x = screen_w - margin - 50 - spacing * 2
        weapon_y = screen_h - margin - 200
        self.weapon_btn = TouchButton(weapon_x, weapon_y, btn_r * 0.75, "WPN", (255, 170, 60))

        shop_x = margin + 70
        shop_y = margin + 70 + spacing * 2
        self.shop_btn = TouchButton(shop_x, shop_y, btn_r * 0.75, "SHP", (255, 200, 80))

        build_x = margin + 70 + spacing
        build_y = margin + 70 + spacing * 2
        self.build_btn = TouchButton(build_x, build_y, btn_r * 0.75, "BLD", (140, 160, 220))

        bp_x = margin + 70
        bp_y = margin + 70 + spacing * 3
        self.battlepass_btn = TouchButton(bp_x, bp_y, btn_r * 0.75, "BP", (255, 120, 200))

        lobby_x = margin + 70 + spacing
        lobby_y = margin + 70 + spacing * 3
        self.lobby_btn = TouchButton(lobby_x, lobby_y, btn_r * 0.75, "LOB", (100, 200, 255))

        achv_x = margin + 70
        achv_y = margin + 70 + spacing * 4
        self.achv_btn = TouchButton(achv_x, achv_y, btn_r * 0.75, "ACH", (255, 230, 120))

        # WASD d-pad — right of the joystick, mirrors keyboard movement
        self.w_btn = TouchButton(270, 565, 24, "W", (235, 235, 235))
        self.a_btn = TouchButton(215, 620, 24, "A", (235, 235, 235))
        self.s_btn = TouchButton(270, 675, 24, "S", (235, 235, 235))
        self.d_btn = TouchButton(325, 620, 24, "D", (235, 235, 235))

        # Extra action buttons — left column rows 6-7
        self.save_btn = TouchButton(margin + 70, margin + 70 + spacing * 5, btn_r * 0.7, "SAV", (120, 255, 200))
        self.chat_btn = TouchButton(margin + 70 + spacing, margin + 70 + spacing * 5, btn_r * 0.7, "CHT", (200, 200, 255))
        self.shot_btn = TouchButton(margin + 70, margin + 70 + spacing * 6, btn_r * 0.7, "SNP", (255, 160, 160))
        self.lb_btn = TouchButton(margin + 70 + spacing, margin + 70 + spacing * 6, btn_r * 0.7, "LBD", (180, 160, 255))

        self.all_buttons = [self.attack_btn, self.dodge_btn, self.special_btn,
                            self.interact_btn, self.potion_btn, self.inventory_btn,
                            self.craft_btn, self.mount_btn, self.storm_btn,
                            self.tame_btn, self.weapon_btn, self.shop_btn,
                            self.build_btn, self.battlepass_btn, self.lobby_btn,
                            self.achv_btn, self.w_btn, self.a_btn, self.s_btn,
                            self.d_btn, self.save_btn, self.chat_btn,
                            self.shot_btn, self.lb_btn]

        self.menu_btn = TouchButton(screen_w // 2, margin + 30, btn_r * 0.7, "|||", (200, 200, 200))

        self.keyboard = VirtualKeyboard(screen_w, screen_h)

        # FIX: enable on mobile + auto-enable on any FINGER event (stops overlap toggle confusion)
        self.enabled = IS_MOBILE
        self._auto_enabled = False

    def handle_event(self, event):
        # auto-enable on first touch (Windows tablets)
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            if not self.enabled:
                self.enabled = True
                self._auto_enabled = True
        if not self.enabled:
            return False
        if self.keyboard.visible and self.keyboard.handle_event(event):
            return True
        # hide joystick when keyboard up to avoid overlap
        if not self.keyboard.visible and self.joystick.handle_event(event):
            return True
        if self.menu_btn.handle_event(event):
            return True
        # keyboard up -> only the keyboard and menu are interactive
        if self.keyboard.visible:
            return False
        for btn in self.all_buttons:
            if btn.handle_event(event):
                return True
        return False

    def draw(self, surface):
        if not self.enabled:
            return
        if self.keyboard.visible:
            self.keyboard.draw(surface)
            self.menu_btn.draw(surface)
            return
        self.joystick.draw(surface)
        self.menu_btn.draw(surface)
        for btn in self.all_buttons:
            btn.draw(surface)

    def draw_keyboard_only(self, surface):
        """On-screen keyboard for menus (login / character name) — no gameplay buttons."""
        if self.enabled and self.keyboard.visible:
            self.keyboard.draw(surface)

    def get_movement(self):
        dx = self.joystick.dx
        dy = self.joystick.dy
        # WASD d-pad (held buttons act like pressed movement keys)
        if self.w_btn.is_pressed():
            dy -= 1
        if self.s_btn.is_pressed():
            dy += 1
        if self.a_btn.is_pressed():
            dx -= 1
        if self.d_btn.is_pressed():
            dx += 1
        return max(-1.0, min(1.0, dx)), max(-1.0, min(1.0, dy))


def detect_mobile():
    if sys.platform in ("android", "ios"):
        return True
    if hasattr(sys, "getandroidapilevel"):
        return True
    try:
        import os
        if os.path.exists("/system/build.prop"):
            return True
    except Exception:
        pass
    return False
