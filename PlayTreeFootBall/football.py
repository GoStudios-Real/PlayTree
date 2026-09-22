"""PLAYTREE FootBall — GoStudios • PlayTree Corporation • 2026"""
import pygame, sys, math, random
W,H=1280,720
GREEN=(50,150,50); DARK_GREEN=(30,100,30); WHITE=(255,255,255); BLACK=(0,0,0)
LIME=(126,211,33); GOLD=(255,215,0); RED=(220,40,40); BLUE=(50,120,255)
Title="PLAYTREE FootBall"

class Ball:
    def __init__(self):
        self.x, self.y=W//2, H//2
        self.vx, self.vy=0,0
        self.r=14
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vx*=0.98; self.vy*=0.98
        if self.y < 80 or self.y > H-40:
            self.vy*=-0.8
            self.y=max(80,min(H-40,self.y))
        if self.x < 0 or self.x > W:
            self.vx*=-0.8
        # goal check
        if 280 < self.y < 440:
            if self.x < 40: return "right"
            if self.x > W-40: return "left"
        return None
    def draw(self,surf):
        pygame.draw.circle(surf, (20,20,20), (int(self.x), int(self.y)), self.r+2)
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.r, 2)
        # pentagon
        for i in range(5):
            a=i*72*math.pi/180
            x=self.x+math.cos(a)*6; y=self.y+math.sin(a)*6
            pygame.draw.circle(surf, BLACK, (int(x),int(y)), 3)

class Player:
    def __init__(self,x,y,col, is_ai=False):
        self.x,self.y=x,y
        self.col=col
        self.is_ai=is_ai
        self.speed=4.2
        self.r=18
    def update(self, keys, ball, teammates):
        if self.is_ai:
            # chase ball
            dx=ball.x-self.x; dy=ball.y-self.y
            d=math.hypot(dx,dy)
            if d>1:
                self.x+=dx/d*self.speed*0.9
                self.y+=dy/d*self.speed*0.9
            # avoid teammates
            for t in teammates:
                if t is not self:
                    d2=math.hypot(self.x-t.x, self.y-t.y)
                    if d2<30 and d2>0:
                        self.x+=(self.x-t.x)/d2*0.8
                        self.y+=(self.y-t.y)/d2*0.8
        else:
            if keys[pygame.K_w] or keys[pygame.K_UP]: self.y-=self.speed
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.y+=self.speed
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.x-=self.speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.x+=self.speed
        self.x=max(30,min(W-30,self.x))
        self.y=max(80,min(H-40,self.y))
        # kick
        d=math.hypot(self.x-ball.x, self.y-ball.y)
        if d < self.r+ball.r+2:
            ang=math.atan2(ball.y-self.y, ball.x-self.x)
            # if player is moving, kick harder
            power=9 if not self.is_ai else 7
            if keys[pygame.K_SPACE] or self.is_ai and d<22:
                ball.vx=math.cos(ang)*power + random.uniform(-1,1)
                ball.vy=math.sin(ang)*power + random.uniform(-1,1)
                return True
            else:
                # nudge
                ball.x+=math.cos(ang)*2
                ball.y+=math.sin(ang)*2
        return False
    def draw(self,surf):
        # shadow
        pygame.draw.ellipse(surf,(0,0,0,80),(int(self.x-14),int(self.y+14),28,10))
        # body
        pygame.draw.circle(surf, self.col, (int(self.x),int(self.y)), self.r)
        pygame.draw.circle(surf, BLACK, (int(self.x),int(self.y)), self.r,2)
        # face
        pygame.draw.circle(surf,(255,220,170),(int(self.x),int(self.y-6)),6)
        # number
        f=pygame.font.Font(None,18)
        txt=f.render("7" if not self.is_ai else "9", True, WHITE)
        surf.blit(txt,(int(self.x-txt.get_width()//2), int(self.y-6)))

def main():
    pygame.init()
    pygame.display.set_caption("PLAYTREE FootBall — GoStudios • EA SPORTS FC 27 Features")
    screen=pygame.display.set_mode((W,H))
    clock=pygame.time.Clock()
    font_big=pygame.font.Font(None,64)
    font_mid=pygame.font.Font(None,28)
    font_small=pygame.font.Font(None,18)
    # FC 27 — The Grounds / FUT Gallery / Career
    mode="menu"  # menu | match | fut | career | grounds
    Gallery = {"level": 3, "sets": 12, "favorites": ["PlayTree XI", "Astro FC"] }
    TransferMarket = {"players": [{"name":"Mbappe","ovr":91,"price":120},{"name":"Bellingham","ovr":90,"price":110},{"name":"PlayTree Star","ovr":85,"price":40}]}
    DynamicOVR = {"Mbappe":91, "PlayTree Star":85}
    ball=Ball()
    # teams: PlayTree (green) vs Astro (red)
    team_play=[Player(300, H//2, (80,180,90)), Player(380, H//2-80, (80,180,90)), Player(380, H//2+80, (80,180,90))]
    team_astro=[Player(W-300, H//2, (180,60,60), True), Player(W-380, H//2-80, (180,60,60), True), Player(W-380, H//2+80, (180,60,60), True)]
    score_l=score_r=0
    time_left=90
    # --- EA SPORTS FC 27 Hub — Grounds / FUT Gallery / Career ---
    hub_choice=None
    if True:
        # show FC 27 hub once, then go to match
        hub_buttons=[("PLAY MATCH","Kick-off 3v3"),("ULTIMATE TEAM","Gallery • Hall of FUT"),("CAREER","Transfer Market • Dynamic OVR"),("THE GROUNDS","Social playground — Clubs")]
        hub_sel=0
        hub_running=True
        while hub_running:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit(); sys.exit(0)
                if ev.type==pygame.KEYDOWN:
                    if ev.key in (pygame.K_UP, pygame.K_w): hub_sel=(hub_sel-1)%len(hub_buttons)
                    if ev.key in (pygame.K_DOWN, pygame.K_s): hub_sel=(hub_sel+1)%len(hub_buttons)
                    if ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                        hub_choice=hub_buttons[hub_sel][0]
                        hub_running=False
                    if ev.key==pygame.K_ESCAPE: hub_running=False
                if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                    for i,(n,d) in enumerate(hub_buttons):
                        r=pygame.Rect(W//2-200, 220+i*90, 400, 70)
                        if r.collidepoint(ev.pos):
                            hub_sel=i; hub_choice=n; hub_running=False
            # draw hub like FC 27
            for y in range(H):
                k=y/H
                r=int(12*(1-k)+30); g=int(20*(1-k)+60); b=int(40*(1-k)+90)
                pygame.draw.line(screen,(r,g,b),(0,y),(W,y))
            title=font_big.render("PLAYTREE FOOTBALL", True, LIME)
            screen.blit(title,(W//2-title.get_width()//2, 40))
            sub=font_mid.render("EA SPORTS FC 27 — The Grounds • FUT Gallery • Career", True, GOLD)
            screen.blit(sub,(W//2-sub.get_width()//2, 110))
            # gallery preview
            gal = font_small.render(f"FUT Gallery Lv.{Gallery['level']} • Sets {Gallery['sets']} • Dynamic OVR Mbappe {DynamicOVR['Mbappe']}", True, (180,220,180))
            screen.blit(gal,(W//2-gal.get_width()//2, 150))
            for i,(name,desc) in enumerate(hub_buttons):
                r=pygame.Rect(W//2-200, 220+i*90, 400, 70)
                sel=(i==hub_sel)
                pygame.draw.rect(screen, (0,0,0), r, border_radius=10)
                inner=r.inflate(-4,-4)
                pygame.draw.rect(screen, LIME if sel else (60,60,60), inner, border_radius=8)
                pygame.draw.rect(screen, (255,255,255) if sel else (100,100,100), inner, 2, border_radius=8)
                ntxt=font_mid.render(name, True, BLACK)
                screen.blit(ntxt,(r.centerx - ntxt.get_width()//2, r.y+12))
                dtxt=font_small.render(desc, True, (40,40,40))
                screen.blit(dtxt,(r.centerx - dtxt.get_width()//2, r.y+38))
            hint=font_small.render("UP/DOWN select • ENTER Play • The Grounds is social like NBA 2K City", True, (160,200,160))
            screen.blit(hint,(W//2-hint.get_width()//2, H-30))
            pygame.display.flip()
            clock.tick(30)
        # handle hub_choice — show quick overlay for non-match modes
        if hub_choice in ("ULTIMATE TEAM","CAREER","THE GROUNDS"):
            # show FC 27 feature screen for 2 sec then continue to match
            overlay = pygame.Surface((W,H),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
            bw,bh=700,360; bx,by=W//2-bw//2, H//2-bh//2
            pygame.draw.rect(screen,(20,25,20),(bx,by,bw,bh), border_radius=12)
            pygame.draw.rect(screen,LIME,(bx,by,bw,bh),2, border_radius=12)
            if hub_choice=="ULTIMATE TEAM":
                lines=["FUT Gallery — permanent record of every card","Hall of FUT — 17 cult heroes (Hulk, Akinfenwa)","Campaign Hub — Objectives + Evolutions + Tokens","Single-player Live Events vs AI"]
            elif hub_choice=="CAREER":
                lines=["Transfer Market — TransferRoom xTV, stages, bidding wars","Dynamic OVR — form/fitness/injuries change ratings","Manager Live Creator Challenges — phone → FC 27","Player Rivalries + Authentic Gameplay 2.0"]
            else:
                lines=["The Grounds — open-world social like NBA 2K City","Kickabouts 1v1 — Clubs expand beyond pitch","Connect with Mbappé mentor, share Creator Challenges"]
            t1=font_mid.render(hub_choice, True, GOLD)
            screen.blit(t1,(bx+bw//2 - t1.get_width()//2, by+20))
            y=by+60
            for ln in lines:
                txt=font_small.render(ln, True, WHITE)
                screen.blit(txt,(bx+20, y)); y+=30
            cont=font_small.render("Press ENTER to Play Match", True, LIME)
            screen.blit(cont,(bx+bw//2 - cont.get_width()//2, by+bh-30))
            pygame.display.flip()
            waiting=True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): waiting=False
                clock.tick(30)
    # touch
    touch_btns=[]
    try: from src.touch_controls import TouchButton
    except: TouchButton=None
    running=True
    while running:
        dt=clock.tick(60)/1000
        time_left=max(0, time_left-dt)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: running=False
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_r:
                ball.x,ball.y=W//2,H//2; ball.vx=ball.vy=0
        keys=pygame.key.get_pressed()
        # update
        for p in team_play: p.update(keys, ball, team_play)
        for p in team_astro: p.update(keys, ball, team_astro)
        g=ball.update()
        if g=="left":
            score_r+=1
            ball.x,ball.y=W//2,H//2; ball.vx,ball.vy=0,0
        elif g=="right":
            score_l+=1
            ball.x,ball.y=W//2,H//2; ball.vx,ball.vy=0,0
        if time_left<=0:
            running=False

        # draw field — like Minecraft grass + water but football
        # sky
        for y in range(80):
            k=y/80
            r=int(110+k*30); g=int(190+k*20); b=255
            pygame.draw.line(screen,(r,g,b),(0,y),(W,y))
        # field
        pygame.draw.rect(screen, GREEN, (0,80,W,H-80))
        # stripes dark/light
        for i in range(0,W,80):
            col=GREEN if (i//80)%2==0 else DARK_GREEN
            pygame.draw.rect(screen,col,(i,80,80,H-80))
        # lines
        pygame.draw.rect(screen, WHITE, (0,80,W,H-80),3)
        pygame.draw.line(screen,WHITE,(W//2,80),(W//2,H),3)
        pygame.draw.circle(screen,WHITE,(W//2,H//2),80,3)
        pygame.draw.circle(screen,WHITE,(W//2,H//2),4)
        # goals
        pygame.draw.rect(screen,WHITE,(0,280,40,160),3)
        pygame.draw.rect(screen,WHITE,(W-40,280,40,160),3)
        # nets
        for y in range(280,440,12):
            pygame.draw.line(screen,(200,200,200),(5,y),(35,y),1)
            pygame.draw.line(screen,(200,200,200),(W-35,y),(W-5,y),1)

        # ball
        ball.draw(screen)
        for p in team_play+team_astro: p.draw(screen)

        # HUD like Minecraft homescreen stone
        # top bar
        bar=pygame.Surface((W,80),pygame.SRCALPHA); bar.fill((0,0,0,110)); screen.blit(bar,(0,0))
        title=font_mid.render("PLAYTREE FootBall", True, LIME)
        screen.blit(title,(20,16))
        sub=font_small.render("GoStudios • PlayTree Corporation • Beta", True, (180,220,180))
        screen.blit(sub,(20,42))
        # score
        score_txt=font_big.render(f"{score_l}  :  {score_r}", True, WHITE)
        # shadow
        sh=font_big.render(f"{score_l}  :  {score_r}", True, BLACK)
        screen.blit(sh,(W//2 - score_txt.get_width()//2+2, 12+2))
        screen.blit(score_txt,(W//2 - score_txt.get_width()//2, 12))
        # time
        ttxt=font_mid.render(f"{int(time_left//60):02d}:{int(time_left%60):02d}", True, GOLD)
        screen.blit(ttxt,(W//2 - ttxt.get_width()//2, 56))
        # controls hint
        hint=font_small.render("WASD Move • SPACE Kick • R Reset • Touch joystick bottom-left", True, (200,220,200))
        screen.blit(hint,(W//2 - hint.get_width()//2, H-18))
        # touch joystick visual (if mobile)
        if pygame.display.get_surface():
            # draw simple joystick at bottom left for show
            pygame.draw.circle(screen,(80,255,120,40),(100,H-80),40)
            pygame.draw.circle(screen,(80,255,120,100),(100,H-80),40,2)

        pygame.display.flip()
    # game over like Minecraft panel
    overlay=pygame.Surface((W,H),pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay,(0,0))
    bw,bh=500,280
    bx,by=W//2-bw//2, H//2-bh//2
    pygame.draw.rect(screen,(32,32,35),(bx,by,bw,bh))
    pygame.draw.rect(screen,BLACK,(bx,by,bw,bh),2)
    pygame.draw.rect(screen,(85,85,85),(bx+2,by+2,bw-4,bh-4),2)
    win="PlayTree Wins!" if score_l>score_r else "Astro Wins!" if score_r>score_l else "Draw!"
    col=LIME if score_l>score_r else RED if score_r>score_l else GOLD
    t1=font_big.render(win, True, col)
    screen.blit(t1,(bx+bw//2 - t1.get_width()//2, by+30))
    t2=font_mid.render(f"{score_l} - {score_r}", True, WHITE)
    screen.blit(t2,(bx+bw//2 - t2.get_width()//2, by+90))
    # buttons
    def btn(rect,txt):
        pygame.draw.rect(screen,BLACK,rect)
        inner=rect.inflate(-4,-4)
        pygame.draw.rect(screen,(200,200,200),inner)
        f=pygame.font.Font(None,18)
        s=f.render(txt, True, BLACK)
        screen.blit(s,(rect.centerx - s.get_width()//2, rect.centery - s.get_height()//2))
    b1=pygame.Rect(bx+30, by+160, bw-60, 36)
    b2=pygame.Rect(bx+30, by+210, bw-60, 36)
    btn(b1,"Play Again (R)")
    btn(b2,"Quit (ESC)")
    pygame.display.flip()
    # wait
    waiting=True
    while waiting:
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: waiting=False
            if ev.type==pygame.KEYDOWN and ev.key in (pygame.K_r, pygame.K_RETURN): waiting=False
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE: pygame.quit(); sys.exit(0)
            if ev.type==pygame.MOUSEBUTTONDOWN and b1.collidepoint(ev.pos): waiting=False
            if ev.type==pygame.MOUSEBUTTONDOWN and b2.collidepoint(ev.pos): pygame.quit(); sys.exit(0)
        clock.tick(30)
    pygame.quit()
    sys.exit(0)

if __name__=="__main__": main()
