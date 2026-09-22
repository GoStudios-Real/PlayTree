import pygame, json, os, hashlib, time

ACCOUNTS_FILE = "gostudios_accounts.json"
SESSION_FILE = "gostudios_session.json"

class GoStudiosAccount:
    def __init__(self):
        self.accounts={}
        self.current_user=None
        self.state="login"
        self.input_email=""; self.input_password=""; self.input_name=""; self.input_confirm=""
        self.active_field="email"
        self.keep_logged=True
        self.error_msg=""; self.error_timer=0
        self.success_msg=""; self.success_timer=0
        self.cursor_blink=0
        self.lang="English - United States"
        self.load_accounts(); self.load_session()
    def load_accounts(self):
        try:
            if os.path.exists(ACCOUNTS_FILE):
                with open(ACCOUNTS_FILE) as f: self.accounts=json.load(f)
        except: self.accounts={}
    def save_accounts(self):
        try: open(ACCOUNTS_FILE,"w").write(json.dumps(self.accounts,indent=2))
        except: pass
    def load_session(self):
        try:
            if os.path.exists(SESSION_FILE):
                s=json.load(open(SESSION_FILE))
                if s.get("email") in self.accounts: self.current_user=s["email"]
        except: pass
    def save_session(self):
        try:
            if self.current_user: open(SESSION_FILE,"w").write(json.dumps({"email":self.current_user}))
            elif os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
        except: pass
    def hash_password(self,p): return hashlib.sha256(p.encode()).hexdigest()
    def login(self,email,password):
        email=email.strip().lower()
        if not email or not password:
            self.error_msg="Fill in all fields"; self.error_timer=120; return False
        if email not in self.accounts:
            self.error_msg="Account not found"; self.error_timer=120; return False
        if self.accounts[email]["password"]!=self.hash_password(password):
            self.error_msg="Wrong password"; self.error_timer=120; return False
        self.current_user=email; self.save_session()
        self.success_msg="Welcome back, "+self.accounts[email]["name"]+"!"; self.success_timer=90
        return True
    def register(self,name,email,password,confirm):
        email=email.strip().lower(); name=name.strip()
        if not name or not email or not password or not confirm:
            self.error_msg="Fill in all fields"; self.error_timer=120; return False
        if len(password)<6:
            self.error_msg="Password must be 6+ chars"; self.error_timer=120; return False
        if password!=confirm:
            self.error_msg="Passwords do not match"; self.error_timer=120; return False
        if email in self.accounts:
            self.error_msg="Email already registered"; self.error_timer=120; return False
        self.accounts[email]={"name":name,"email":email,"password":self.hash_password(password),"created":time.strftime("%Y-%m-%d")}
        self.save_accounts(); self.current_user=email; self.save_session()
        self.success_msg="Account created! Welcome, "+name+"!"; self.success_timer=90
        return True
    def logout(self): self.current_user=None; self.save_session(); self.state="login"
    def auto_login_guest(self):
        ge="guest@playtree.local"
        if ge not in self.accounts:
            self.accounts[ge]={"name":"Guest","email":ge,"password":self.hash_password("guest"),"created":time.strftime("%Y-%m-%d")}
            self.save_accounts()
        self.current_user=ge; self.save_session()
    def get_user_data(self):
        return self.accounts.get(self.current_user) if self.current_user else None
    def handle_event(self,event):
        if self.error_timer>0: self.error_timer-=1
        if self.success_timer>0: self.success_timer-=1
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_TAB:
                fields=["email","password"] if self.state=="login" else ["name","email","password","confirm"]
                idx=fields.index(self.active_field) if self.active_field in fields else 0
                self.active_field=fields[(idx+1)%len(fields)]; return True
            if event.key==pygame.K_RETURN:
                if self.state=="login":
                    if self.login(self.input_email,self.input_password): return "logged_in"
                elif self.register(self.input_name,self.input_email,self.input_password,self.input_confirm): return "logged_in"
                return True
            if event.key==pygame.K_ESCAPE:
                if self.state=="register": self.state="login"; self.active_field="email"; return True
                return "back"
            if event.key==pygame.K_BACKSPACE:
                if self.active_field=="email": self.input_email=self.input_email[:-1]
                elif self.active_field=="password": self.input_password=self.input_password[:-1]
                elif self.active_field=="name": self.input_name=self.input_name[:-1]
                elif self.active_field=="confirm": self.input_confirm=self.input_confirm[:-1]
                return True
            if event.unicode and event.unicode.isprintable():
                if self.active_field=="email": self.input_email+=event.unicode
                elif self.active_field=="password": self.input_password+=event.unicode
                elif self.active_field=="name": self.input_name+=event.unicode
                elif self.active_field=="confirm": self.input_confirm+=event.unicode
                return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            mx,my=event.pos
            W,H=pygame.display.get_surface().get_size()
            cx=W//2; bw=380; bx=cx-bw//2; by=150
            # fields
            if self.state=="login":
                # email field
                if pygame.Rect(bx+20,by+70, bw-40, 28).collidepoint(mx,my): self.active_field="email"; return True
                if pygame.Rect(bx+20,by+120, bw-40, 28).collidepoint(mx,my): self.active_field="password"; return True
                # keep logged checkbox
                if pygame.Rect(bx+20,by+158, 14,14).collidepoint(mx,my): self.keep_logged=not self.keep_logged; return True
                # forgot
                if pygame.Rect(bx+220,by+160, 80,14).collidepoint(mx,my): return True
                # LOG IN button
                if pygame.Rect(bx+20,by+185, bw-40, 36).collidepoint(mx,my):
                    if self.login(self.input_email,self.input_password): return "logged_in"
                    return True
                # Sign up link
                if pygame.Rect(cx-50,by+235,100,14).collidepoint(mx,my): self.state="register"; self.active_field="name"; return True
            else:
                if pygame.Rect(bx+20,by+60, bw-40, 24).collidepoint(mx,my): self.active_field="name"; return True
                if pygame.Rect(bx+20,by+110, bw-40, 24).collidepoint(mx,my): self.active_field="email"; return True
                if pygame.Rect(bx+20,by+160, bw-40, 24).collidepoint(mx,my): self.active_field="password"; return True
                if pygame.Rect(bx+20,by+210, bw-40, 24).collidepoint(mx,my): self.active_field="confirm"; return True
                if pygame.Rect(bx+20,by+250, bw-40, 32).collidepoint(mx,my):
                    if self.register(self.input_name,self.input_email,self.input_password,self.input_confirm): return "logged_in"
                    return True
                if pygame.Rect(cx-60,by+295,120,14).collidepoint(mx,my): self.state="login"; return True
        return False

    def _draw_world(self, screen, t=0):
        import math
        W,H=screen.get_size()
        for y in range(H):
            k=y/H
            r=int(110+k*30); g=int(190+k*20); b=255
            pygame.draw.line(screen,(r,g,b),(0,y),(W,y))
        # simple hills
        for i in range(8):
            x=i*300-50
            pygame.draw.rect(screen,(120,95,55),(x, H-280, 260, 120))
            pygame.draw.rect(screen,(75,140,50),(x, H-280, 260, 40))
        pygame.draw.rect(screen,(45,110,185),(0,H-180,W,90))

    def draw(self, screen, font, small_font):
        W,H=screen.get_size()
        self.cursor_blink=(self.cursor_blink+1)%60
        # background world blurred
        self._draw_world(screen)
        # dark overlay
        overlay=pygame.Surface((W,H),pygame.SRCALPHA)
        overlay.fill((0,0,0,40))
        screen.blit(overlay,(0,0))
        # lang top left like screenshot
        lang_bg=pygame.Surface((130,18),pygame.SRCALPHA)
        lang_bg.fill((0,0,0,120))
        screen.blit(lang_bg,(6,4))
        lang_txt=small_font.render(self.lang, True, (255,255,255))
        screen.blit(lang_txt,(10,6))
        pygame.draw.polygon(screen,(255,255,255),[(124,10),(134,10),(129,15)])
        # PLAYTREE logo top center like MINECRAFT stone
        logo_y=54
        for dx,dy in [(3,3),(-1,1)]:
            sh=pygame.font.Font(None,64).render("PLAYTREE", True, (30,30,30))
            screen.blit(sh,(W//2 - sh.get_width()//2 + dx, logo_y+dy))
        logo=pygame.font.Font(None,64).render("PLAYTREE", True, (210,210,210))
        # cracks
        tmp=logo.copy()
        import random
        for i in range(24):
            x=random.randint(0, logo.get_width()-1); y=random.randint(0, logo.get_height()-1)
            pygame.draw.line(tmp,(160,160,160),(x,y),(x+random.randint(-5,5), y+random.randint(-2,2)),1)
        screen.blit(tmp,(W//2 - tmp.get_width()//2, logo_y))
        # Center dark panel like Minecraft login
        cx=W//2; bw=420; bh= 320 if self.state=="login" else 380
        bx=cx-bw//2; by=120
        panel=pygame.Surface((bw,bh),pygame.SRCALPHA)
        panel.fill((18,18,22,230))
        pygame.draw.rect(panel,(60,60,65), panel.get_rect(), 2)
        screen.blit(panel,(bx,by))
        if self.state=="login":
            # EMAIL OR USERNAME
            lbl=small_font.render("EMAIL OR USERNAME", True, (200,200,200))
            screen.blit(lbl,(bx+20,by+18))
            self._draw_mc_field(screen, bx+20,by+38, bw-40, self.input_email, self.active_field=="email", False, "email")
            # PASSWORD
            lbl2=small_font.render("PASSWORD", True, (200,200,200))
            screen.blit(lbl2,(bx+20,by+78))
            self._draw_mc_field(screen, bx+20,by+98, bw-40, self.input_password, self.active_field=="password", True, "password")
            # help icon ?
            pygame.draw.circle(screen,(80,80,80),(bx+bw-30, by+18),7,1)
            q=small_font.render("?", True, (180,180,180))
            screen.blit(q,(bx+bw-32, by+13))
            # Keep me logged in + Forgot
            # checkbox
            cb_rect=pygame.Rect(bx+20,by+138,12,12)
            pygame.draw.rect(screen,(0,0,0),cb_rect)
            pygame.draw.rect(screen,(100,100,100),cb_rect,1)
            if self.keep_logged:
                pygame.draw.rect(screen,(60,200,80),cb_rect.inflate(-4,-4))
            klbl=small_font.render("Keep me logged in", True, (180,180,180))
            screen.blit(klbl,(bx+38,by+138))
            forgot=small_font.render("Forgot password?", True, (100,160,220))
            screen.blit(forgot,(bx+bw-140,by+138))
            # LOG IN green button like Minecraft
            btn=pygame.Rect(bx+20,by+168, bw-40, 34)
            pygame.draw.rect(screen,(30,120,30),btn)
            pygame.draw.rect(screen,(60,200,80),btn,2)
            txt=pygame.font.Font(None,22).render("LOG IN", True, (255,255,255))
            screen.blit(txt,(btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            # Don't have account? Sign up
            dont=small_font.render("Don't have an account? ", True, (180,180,180))
            sign=small_font.render("Sign up", True, (100,200,255))
            tx=cx - (dont.get_width()+sign.get_width())//2
            screen.blit(dont,(tx, by+220))
            screen.blit(sign,(tx+dont.get_width(), by+220))
            # error
            if self.error_timer>0 and self.error_msg:
                err=small_font.render(self.error_msg, True, (255,80,80))
                screen.blit(err,(cx - err.get_width()//2, by+bh+14))
        else:
            # Register — GoStudios branded
            title=small_font.render("Create GoStudios Account", True, (180,220,180))
            screen.blit(title,(cx - title.get_width()//2, by+14))
            self._draw_mc_field(screen, bx+20,by+38, bw-40, self.input_name, self.active_field=="name", False, "Display Name")
            self._draw_mc_field(screen, bx+20,by+88, bw-40, self.input_email, self.active_field=="email", False, "Email")
            self._draw_mc_field(screen, bx+20,by+138, bw-40, self.input_password, self.active_field=="password", True, "Password")
            self._draw_mc_field(screen, bx+20,by+188, bw-40, self.input_confirm, self.active_field=="confirm", True, "Confirm")
            btn=pygame.Rect(bx+20,by+230, bw-40, 32)
            pygame.draw.rect(screen,(80,200,80),btn)
            pygame.draw.rect(screen,(60,180,60),btn,2)
            txt=pygame.font.Font(None,22).render("Create Account", True, (20,30,20))
            screen.blit(txt,(btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))
            back=small_font.render("Already have account? Sign in", True, (100,180,255))
            screen.blit(back,(cx - back.get_width()//2, by+278))
            if self.error_timer>0 and self.error_msg:
                err=small_font.render(self.error_msg, True, (255,80,80))
                screen.blit(err,(cx - err.get_width()//2, by+bh+10))

    def _draw_mc_field(self, screen, x,y,w, value, active, masked, placeholder):
        bg=(0,0,0) if not active else (20,20,20)
        border=(100,100,100) if not active else (255,255,255)
        pygame.draw.rect(screen, bg, (x,y,w,26))
        pygame.draw.rect(screen, border, (x,y,w,26),1)
        txt = "*" * len(value) if masked else value
        if active and self.cursor_blink<30: txt += "|"
        if not txt and not active:
            ph=pygame.font.Font(None,18).render(placeholder, True, (120,120,120))
            screen.blit(ph,(x+6, y+6))
        else:
            f=pygame.font.Font(None,18)
            surf=f.render(txt, True, (255,255,255))
            screen.blit(surf,(x+6, y+5))
