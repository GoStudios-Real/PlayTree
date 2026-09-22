import pygame, math, random
from config import *

class MainMenu:
    def __init__(self, screen, has_save=False):
        self.screen = screen
        self.time = 0
        self.selected = 0
        self.hovered = -1
        self.menu_items = ["Play","Settings","Marketplace"]
        self.has_save = has_save
        self.font_big = pygame.font.Font(None, 90)
        self.font_mid = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 18)
        self.menu_rects = []
        self.signin_rect = pygame.Rect(40, HEIGHT-80, 100, 32)
        self.profile_rect = pygame.Rect(WIDTH-120, HEIGHT-80, 100, 32)
        self.audio = None

    def _update_menu_rects(self):
        self.menu_rects = []
        for i, item in enumerate(self.menu_items):
            y = 280 + i*56
            rect = pygame.Rect(WIDTH//2 - 160, y, 320, 44)
            self.menu_rects.append(rect)

    def _get_item_at(self, pos):
        self._update_menu_rects()
        for i, r in enumerate(self.menu_rects):
            if r.collidepoint(pos): return i
        if self.signin_rect.collidepoint(pos): return 100
        if self.profile_rect.collidepoint(pos): return 101
        return -1

    def _activate_item(self, idx):
        if idx==0: return "character_create" if not self.has_save else "continue"
        if idx==1: return "settings"
        if idx==2: return "marketplace"
        if idx==100: return "signin"
        if idx==101: return "profile"
        return None

    def update(self, dt):
        self.time += dt

    def handle_event(self, event):
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w): self.selected=(self.selected-1)%len(self.menu_items); return None
            if event.key in (pygame.K_DOWN, pygame.K_s): self.selected=(self.selected+1)%len(self.menu_items); return None
            if event.key in (pygame.K_RETURN, pygame.K_SPACE): return self._activate_item(self.selected)
            if event.key==pygame.K_ESCAPE: return "quit"
        elif event.type==pygame.MOUSEMOTION:
            self.hovered = self._get_item_at(event.pos)
            if self.hovered>=0 and self.hovered<3: self.selected=self.hovered
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            idx=self._get_item_at(event.pos)
            if idx>=0: return self._activate_item(idx)
        elif event.type==pygame.JOYBUTTONDOWN:
            if event.button==0: return self._activate_item(self.selected)
            if event.button==1: return "quit"
        return None

    def _draw_world(self):
        # Sky + clouds + hills like Minecraft Beta
        for y in range(HEIGHT):
            k=y/HEIGHT
            r=int(110+k*30); g=int(190+k*20); b=255
            pygame.draw.line(self.screen,(r,g,b),(0,y),(WIDTH,y))
        # Clouds blocky
        for i in range(7):
            cx=(i*260 + int(self.time*15)%500)-80
            cy=40+(i%3)*18
            for j in range(5):
                pygame.draw.rect(self.screen,(255,255,255),(cx+j*34, cy, 44, 20))
                pygame.draw.rect(self.screen,(220,220,220),(cx+j*34, cy, 44, 20),1)
        # Far hills
        for i in range(12):
            x=i*140- int(self.time*4)%140
            h=120+math.sin(i)*30
            y= HEIGHT-260
            pygame.draw.rect(self.screen,(120,95,55),(x,y,140,h))
            pygame.draw.rect(self.screen,(75,140,50),(x,y,140,40))
            pygame.draw.rect(self.screen,(95,180,65),(x,y,140,12))
        # Water
        pygame.draw.rect(self.screen,(45,110,185),(0,HEIGHT-180,WIDTH,90))
        for i in range(32):
            wx=(i*45+int(self.time*25)%45)
            pygame.draw.line(self.screen,(65,150,225),(wx,HEIGHT-120),(wx+18,HEIGHT-120),2)
        # Trees & grass
        for i in range(5):
            tx=60+i*240
            pygame.draw.rect(self.screen,(95,65,22),(tx,HEIGHT-240,18,70))
            pygame.draw.rect(self.screen,(35,110,35),(tx-22,HEIGHT-260,62,54))
            pygame.draw.rect(self.screen,(45,130,45),(tx-16,HEIGHT-250,50,18))
        # Flowers
        for i in range(14):
            fx=30+i*85+int(math.sin(i)*15)
            fy=HEIGHT-175+(i%3)*14
            col=[(255,40,70),(255,225,0),(255,255,255)][i%3]
            pygame.draw.circle(self.screen,col,(fx,fy),5)
            pygame.draw.circle(self.screen,(255,255,0),(fx,fy),2)
        # Grass ground
        pygame.draw.rect(self.screen,(75,150,55),(0,HEIGHT-100,WIDTH,100))
        for i in range(WIDTH//10):
            gx=i*10
            gy=HEIGHT-100+math.sin(i*0.9)*3
            pygame.draw.line(self.screen,(90,170,65),(gx,gy),(gx,gy+6),1)

    def _draw_button(self, rect, text, sel=False):
        # Minecraft stone button
        bg=(205,205,205) if not sel else (220,220,220)
        pygame.draw.rect(self.screen,(0,0,0),rect)
        inner=rect.inflate(-4,-4)
        pygame.draw.rect(self.screen,bg,inner)
        # highlight top
        pygame.draw.line(self.screen,(255,255,255),inner.topleft, inner.topright,2)
        pygame.draw.line(self.screen,(85,85,85),inner.bottomleft, inner.bottomright,2)
        f=pygame.font.Font(None,24)
        txt=f.render(text, True,(30,30,30))
        self.screen.blit(txt,(rect.centerx-txt.get_width()//2, rect.centery-txt.get_height()//2))
        if sel:
            pygame.draw.rect(self.screen,(255,255,255,80),rect,2)

    def draw(self):
        self._draw_world()
        # Top version text like beta ...
        top = pygame.font.Font(None,14).render("beta 1.0.0 GoStudios, Windows 10 UWP Build, GoConsole GoStudios", True, (255,255,255))
        self.screen.blit(top,(WIDTH//2 - top.get_width()//2, 6))
        # Logo PLAYTREE stone cracked
        logo_y=90
        # shadow
        for dx,dy in [(4,4),(-2,2)]:
            sh=pygame.font.Font(None,92).render("PLAYTREE", True, (30,30,30))
            self.screen.blit(sh,(WIDTH//2 - sh.get_width()//2 + dx, logo_y+dy))
        # main stone
        fbig=pygame.font.Font(None,92)
        # cracked stone effect: draw with texture lines
        logo=fbig.render("PLAYTREE", True, (210,210,210))
        # add crack lines
        tmp=logo.copy()
        for i in range(30):
            x=random.randint(0, logo.get_width()-1)
            y=random.randint(0, logo.get_height()-1)
            pygame.draw.line(tmp,(160,160,160),(x,y),(x+random.randint(-6,6), y+random.randint(-3,3)),1)
        self.screen.blit(tmp,(WIDTH//2 - tmp.get_width()//2, logo_y))
        # Beta!!! yellow angled like Minecraft
        beta=pygame.font.Font(None,36).render("Beta!!!", True, (255,255,0))
        beta=pygame.transform.rotate(beta, -18)
        self.screen.blit(beta,(WIDTH//2 + 220, logo_y+30))
        # Center buttons Play/Settings/Marketplace
        self._update_menu_rects()
        labels=["Play","Settings","Marketplace"]
        for i,lab in enumerate(labels):
            sel=(i==self.selected or i==self.hovered)
            self._draw_button(self.menu_rects[i], lab, sel)
        # Bottom left Sign In
        self._draw_button(self.signin_rect, "Sign In")
        # Bottom right Profile with Steve-like PlayTree character
        self._draw_button(self.profile_rect, "Profile")
        # Steve character
        cx=self.profile_rect.centerx
        cy=self.profile_rect.y - 90
        # head
        pygame.draw.rect(self.screen,(222,180,140),(cx-16, cy, 32, 28))
        pygame.draw.rect(self.screen,(80,60,30),(cx-16, cy, 32, 8)) # hair
        pygame.draw.rect(self.screen,(40,40,40),(cx-8, cy+12, 6, 4)) # eyes
        pygame.draw.rect(self.screen,(40,40,40),(cx+2, cy+12, 6, 4))
        # body
        pygame.draw.rect(self.screen,(60,180,180),(cx-14, cy+28, 28, 32))
        # legs
        pygame.draw.rect(self.screen,(60,60,180),(cx-12, cy+60, 12, 24))
        pygame.draw.rect(self.screen,(60,60,180),(cx+2, cy+60, 12, 24))
        # name Steve -> PlayTree player
        nametxt=pygame.font.Font(None,16).render("Steve", True, (255,255,255))
        # shadow
        sh2=pygame.font.Font(None,16).render("Steve", True, (0,0,0))
        self.screen.blit(sh2,(cx - nametxt.get_width()//2 +1, cy-18+1))
        self.screen.blit(nametxt,(cx - nametxt.get_width()//2, cy-18))
        # Bottom copyright
        copyr=pygame.font.Font(None,14).render("\u00a9PlayTree Corporation", True, (255,255,255))
        self.screen.blit(copyr,(10, HEIGHT-18))
        ver=pygame.font.Font(None,14).render("v1.0.0", True, (255,255,255))
        self.screen.blit(ver,(WIDTH - ver.get_width()-10, HEIGHT-18))
