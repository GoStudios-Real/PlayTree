import pygame
import json
import os
import hashlib
import time

ACCOUNTS_FILE = "rhystech_accounts.json"
SESSION_FILE = "rhystech_session.json"

class RhystechAccount:
    def __init__(self):
        self.accounts = {}
        self.current_user = None
        self.state = "login"
        self.input_email = ""
        self.input_password = ""
        self.input_name = ""
        self.input_confirm = ""
        self.active_field = "email"
        self.error_msg = ""
        self.error_timer = 0
        self.success_msg = ""
        self.success_timer = 0
        self.cursor_blink = 0
        self.load_accounts()
        self.load_session()

    def load_accounts(self):
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE, "r") as f:
                    self.accounts = json.load(f)
        except Exception:
            self.accounts = {}

    def save_accounts(self):
        try:
            with open(ACCOUNTS_FILE, "w") as f:
                json.dump(self.accounts, f, indent=2)
        except Exception:
            pass

    def load_session(self):
        try:
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "r") as f:
                    session = json.load(f)
                    if session.get("email") in self.accounts:
                        self.current_user = session["email"]
        except Exception:
            pass

    def save_session(self):
        try:
            if self.current_user:
                with open(SESSION_FILE, "w") as f:
                    json.dump({"email": self.current_user}, f)
            elif os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
        except Exception:
            pass

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def login(self, email, password):
        email = email.strip().lower()
        if not email or not password:
            self.error_msg = "Fill in all fields"
            self.error_timer = 120
            return False
        if email not in self.accounts:
            self.error_msg = "Account not found"
            self.error_timer = 120
            return False
        if self.accounts[email]["password"] != self.hash_password(password):
            self.error_msg = "Wrong password"
            self.error_timer = 120
            return False
        self.current_user = email
        self.save_session()
        self.success_msg = "Welcome back, " + self.accounts[email]["name"] + "!"
        self.success_timer = 90
        return True

    def register(self, name, email, password, confirm):
        email = email.strip().lower()
        name = name.strip()
        if not name or not email or not password or not confirm:
            self.error_msg = "Fill in all fields"
            self.error_timer = 120
            return False
        if len(password) < 6:
            self.error_msg = "Password must be 6+ chars"
            self.error_timer = 120
            return False
        if password != confirm:
            self.error_msg = "Passwords do not match"
            self.error_timer = 120
            return False
        if email in self.accounts:
            self.error_msg = "Email already registered"
            self.error_timer = 120
            return False
        self.accounts[email] = {
            "name": name,
            "email": email,
            "password": self.hash_password(password),
            "created": time.strftime("%Y-%m-%d"),
            "hours": 0,
            "rounds": 0,
            "bosses": 0
        }
        self.save_accounts()
        self.current_user = email
        self.save_session()
        self.success_msg = "Account created! Welcome, " + name + "!"
        self.success_timer = 90
        return True

    def logout(self):
        self.current_user = None
        self.save_session()
        self.state = "login"

    def auto_login_guest(self):
        guest_email = "guest@playtree.local"
        if guest_email not in self.accounts:
            self.accounts[guest_email] = {
                "name": "Guest",
                "email": guest_email,
                "password": self.hash_password("guest"),
                "created": time.strftime("%Y-%m-%d"),
                "hours": 0,
                "rounds": 0,
                "bosses": 0,
            }
            self.save_accounts()
        self.current_user = guest_email
        self.save_session()

    def get_user_data(self):
        if self.current_user and self.current_user in self.accounts:
            return self.accounts[self.current_user]
        return None

    def update_stats(self, hours=0, rounds=0, bosses=0):
        if self.current_user and self.current_user in self.accounts:
            u = self.accounts[self.current_user]
            u["hours"] = u.get("hours", 0) + hours
            u["rounds"] = u.get("rounds", 0) + rounds
            u["bosses"] = u.get("bosses", 0) + bosses
            self.save_accounts()

    def handle_event(self, event):
        if self.error_timer > 0:
            self.error_timer -= 1
        if self.success_timer > 0:
            self.success_timer -= 1

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                if self.state == "login":
                    fields = ["email", "password", "login_btn", "signup_btn"]
                    idx = fields.index(self.active_field) if self.active_field in fields else 0
                    self.active_field = fields[(idx + 1) % len(fields)]
                elif self.state == "register":
                    fields = ["name", "email", "password", "confirm"]
                    idx = fields.index(self.active_field) if self.active_field in fields else 0
                    self.active_field = fields[(idx + 1) % len(fields)]
                return True

            if event.key == pygame.K_RETURN:
                if self.state == "login":
                    if self.active_field == "signup_btn":
                        self.state = "register"
                        self.error_msg = ""
                        self.success_msg = ""
                        self.active_field = "name"
                        return True
                    if self.login(self.input_email, self.input_password):
                        return "logged_in"
                elif self.state == "register":
                    if self.register(self.input_name, self.input_email, self.input_password, self.input_confirm):
                        return "logged_in"
                return True

            if event.key == pygame.K_ESCAPE:
                if self.state == "register":
                    self.state = "login"
                    self.error_msg = ""
                    self.success_msg = ""
                    self.active_field = "email"
                    return True
                return "back"

            if event.key == pygame.K_BACKSPACE:
                if self.active_field == "email":
                    self.input_email = self.input_email[:-1]
                elif self.active_field == "password":
                    self.input_password = self.input_password[:-1]
                elif self.active_field == "name":
                    self.input_name = self.input_name[:-1]
                elif self.active_field == "confirm":
                    self.input_confirm = self.input_confirm[:-1]
                return True

            if event.unicode and event.unicode.isprintable():
                if self.active_field == "email":
                    self.input_email += event.unicode
                elif self.active_field == "password":
                    self.input_password += event.unicode
                elif self.active_field == "name":
                    self.input_name += event.unicode
                elif self.active_field == "confirm":
                    self.input_confirm += event.unicode
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            W, H = pygame.display.get_surface().get_size() if hasattr(pygame, 'display') else (1280, 720)
            try:
                W, H = pygame.display.get_surface().get_size()
            except:
                W, H = 1280, 720
            cx = W // 2
            box_w = 360
            bx = cx - box_w // 2
            by = 150
            hx = bx + 24
            btn_w = (box_w - 48 - 12) // 2
            btn_y = by + 20 + 40 + 56 + 56 + 8
            up_x = hx + btn_w + 12

            if self.state == "login":
                if up_x <= mx <= up_x + btn_w and btn_y <= my <= btn_y + 36:
                    self.state = "register"
                    self.error_msg = ""
                    self.success_msg = ""
                    self.active_field = "name"
                    return True
                if hx <= mx <= hx + btn_w and btn_y <= my <= btn_y + 36:
                    if self.login(self.input_email, self.input_password):
                        return "logged_in"
                    return True

        return False

    def draw(self, screen, font, small_font):
        W, H = screen.get_size()
        screen.fill((8, 12, 8))

        self.cursor_blink = (self.cursor_blink + 1) % 60

        title_surf = font.render("RHYSTECH", True, (80, 255, 120))
        screen.blit(title_surf, (W // 2 - title_surf.get_width() // 2, 60))

        sub_surf = small_font.render("Account System", True, (100, 160, 100))
        screen.blit(sub_surf, (W // 2 - sub_surf.get_width() // 2, 110))

        cx = W // 2
        box_w = 360
        box_h = 320 if self.state == "login" else 400
        bx = cx - box_w // 2
        by = 150

        pygame.draw.rect(screen, (13, 20, 13), (bx, by, box_w, box_h), border_radius=8)
        pygame.draw.rect(screen, (32, 160, 64), (bx, by, box_w, box_h), 2, border_radius=8)

        if self.state == "login":
            self._draw_login(screen, font, small_font, bx, by, box_w)
        else:
            self._draw_register(screen, font, small_font, bx, by, box_w)

        if self.error_timer > 0 and self.error_msg:
            err_surf = small_font.render(self.error_msg, True, (255, 64, 96))
            screen.blit(err_surf, (W // 2 - err_surf.get_width() // 2, by + box_h + 16))

        if self.success_timer > 0 and self.success_msg:
            ok_surf = small_font.render(self.success_msg, True, (80, 255, 120))
            screen.blit(ok_surf, (W // 2 - ok_surf.get_width() // 2, by + box_h + 16))

        hint = small_font.render("TAB switch  ENTER submit  ESC back", True, (60, 90, 60))
        screen.blit(hint, (W // 2 - hint.get_width() // 2, H - 50))

    def _draw_login(self, screen, font, small_font, bx, by, box_w):
        hx = bx + 24
        hy = by + 20

        lbl = small_font.render("Sign in to RHYSTECH", True, (160, 200, 160))
        screen.blit(lbl, (hx, hy))
        hy += 40

        self._draw_field(screen, small_font, "Email", self.input_email, self.active_field == "email", hx, hy, box_w - 48)
        hy += 56

        self._draw_field(screen, small_font, "Password", self.input_password, self.active_field == "password", hx, hy, box_w - 48, masked=True)
        hy += 56

        btn_y = hy + 8
        btn_w = (box_w - 48 - 12) // 2

        # Sign In button (left)
        in_color = (80, 255, 120) if self.active_field == "login_btn" else (32, 160, 64)
        pygame.draw.rect(screen, in_color, (hx, btn_y, btn_w, 36), border_radius=4)
        in_txt = font.render("Sign In", True, (8, 12, 8))
        screen.blit(in_txt, (hx + btn_w // 2 - in_txt.get_width() // 2, btn_y + 6))

        # Sign Up button (right)
        up_color = (60, 180, 255) if self.active_field == "signup_btn" else (30, 100, 180)
        up_x = hx + btn_w + 12
        pygame.draw.rect(screen, up_color, (up_x, btn_y, btn_w, 36), border_radius=4)
        up_txt = font.render("Sign Up", True, (8, 12, 8))
        screen.blit(up_txt, (up_x + btn_w // 2 - up_txt.get_width() // 2, btn_y + 6))

        link_y = btn_y + 52
        link = small_font.render("No account? Press TAB to register", True, (100, 160, 100))
        screen.blit(link, (hx, link_y))

    def _draw_register(self, screen, font, small_font, bx, by, box_w):
        hx = bx + 24
        hy = by + 20

        lbl = small_font.render("Create RHYSTECH Account", True, (160, 200, 160))
        screen.blit(lbl, (hx, hy))
        hy += 36

        self._draw_field(screen, small_font, "Display Name", self.input_name, self.active_field == "name", hx, hy, box_w - 48)
        hy += 52

        self._draw_field(screen, small_font, "Email", self.input_email, self.active_field == "email", hx, hy, box_w - 48)
        hy += 52

        self._draw_field(screen, small_font, "Password", self.input_password, self.active_field == "password", hx, hy, box_w - 48, masked=True)
        hy += 52

        self._draw_field(screen, small_font, "Confirm", self.input_confirm, self.active_field == "confirm", hx, hy, box_w - 48, masked=True)
        hy += 52

        btn_y = hy + 4
        btn_color = (80, 255, 120)
        pygame.draw.rect(screen, btn_color, (hx, btn_y, box_w - 48, 34), border_radius=4)
        btn_txt = font.render("Create Account", True, (8, 12, 8))
        screen.blit(btn_txt, (hx + (box_w - 48) // 2 - btn_txt.get_width() // 2, btn_y + 6))

        link_y = btn_y + 48
        link = small_font.render("Already have account? Press ESC to login", True, (100, 160, 100))
        screen.blit(link, (hx, link_y))

    def _draw_field(self, screen, font, label, value, active, x, y, w, masked=False):
        lbl = font.render(label, True, (100, 160, 100))
        screen.blit(lbl, (x, y))

        iy = y + 20
        bg = (20, 30, 20) if not active else (25, 40, 25)
        border = (32, 160, 64) if active else (30, 60, 30)
        pygame.draw.rect(screen, bg, (x, iy, w, 26), border_radius=3)
        pygame.draw.rect(screen, border, (x, iy, w, 26), 1, border_radius=3)

        display = "*" * len(value) if masked else value
        if active and self.cursor_blink < 30:
            display += "|"

        val_surf = font.render(display, True, (208, 240, 208))
        screen.blit(val_surf, (x + 8, iy + 4))
