"""PlayTree Cloud Gaming — Hub for Fighting / Roleplay / Obby +"""
import sys, os, subprocess, json, time
from pathlib import Path
ROOT=Path(__file__).parent
STORE=ROOT / "cloud_profiles.json"
try:
    import pygame
except: print("need pygame"); sys.exit(1)
W,H=1280,720
LIME=(126,211,33); DARK=(47,107,0); CYAN=(43,201,226); WHITE=(255,255,255); BLACK=(0,0,0)
GAMES=[
    ("Fighting","PvP Arena • 6 classes vs Astro Toilets","fighting", (200,60,60)),
    ("Roleplay","Town • Housing • GoStudios chat","roleplay", (80,180,90)),
    ("Obby","9000×9000 obstacle course • 100 stages","obby", (80,120,200)),
    ("FootBall","PlayTree FootBall • 3v3 • GoStudios Cup","football", (50,180,90)),
    ("Tycoon","Build to Crystal Empire","tycoon", (200,170,80)),
    ("Fishing","5 fish • Leviathan","fishing", (60,180,180)),
    ("Battle Royale","28 last stand","royale", (180,80,180)),
]
def get_font(s,b=False):
    try: return pygame.font.SysFont("Courier New", s, bold=b)
    except: return pygame.font.Font(None, s)
def main():
    pygame.init()
    pygame.display.set_caption("PlayTree Cloud Gaming — GoConsole Cloud")
    screen=pygame.display.set_mode((W,H))
    clock=pygame.time.Clock()
    sel=0
    # cloud status
    cloud_online=True
    # load recent
    t0=time.time()
    running=True
    while running:
        dt=clock.tick(60)/1000; t=time.time()-t0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: running=False
            elif ev.type==pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w): sel=(sel-1)%len(GAMES)
                elif ev.key in (pygame.K_DOWN, pygame.K_s): sel=(sel+1)%len(GAMES)
                elif ev.key in (pygame.K_RETURN, pygame.K_SPACE):
                    name,desc,mode,col=GAMES[sel]
                    print(f"Launching PlayTree Cloud {mode}")
                    try:
                        if mode=="football":
                            exe=ROOT.parent / "PlayTree FootBall.exe"
                            if not exe.exists(): exe=Path(r"C:\Users\RhysC\Downloads\NEW\PlayTree FootBall.exe")
                        else:
                            exe=ROOT.parent / "PLAYTREE.exe"
                            if not exe.exists(): exe=Path(r"C:\Users\RhysC\Downloads\NEW\PLAYTREE.exe")
                        if exe.exists():
                            args=[str(exe)] if mode=="football" else [str(exe), f"--mode={mode}"]
                            subprocess.Popen(args, cwd=str(exe.parent))
                    except Exception as e: print(e)
                elif ev.key==pygame.K_ESCAPE: running=False
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                for i,(name,desc,mode,col) in enumerate(GAMES):
                    r=pygame.Rect(W//2 -260, 140+i*78, 520, 68)
                    if r.collidepoint(ev.pos):
                        sel=i
                        # launch — FootBall has its own exe
                        try:
                            if mode=="football":
                                exe=ROOT.parent / "PlayTree FootBall.exe"
                                if not exe.exists(): exe=Path(r"C:\Users\RhysC\Downloads\NEW\PlayTree FootBall.exe")
                                args=[str(exe)] if exe.exists() else []
                            else:
                                exe=ROOT.parent / "PLAYTREE.exe"
                                if not exe.exists(): exe=Path(r"C:\Users\RhysC\Downloads\NEW\PLAYTREE.exe")
                                args=[str(exe), f"--mode={mode}"] if exe.exists() else []
                            if args:
                                subprocess.Popen(args, cwd=str(Path(args[0]).parent))
                        except: pass
            elif ev.type==pygame.MOUSEWHEEL:
                sel=(sel + (-1 if ev.y>0 else 1))%len(GAMES)

        # draw
        for y in range(H):
            k=y/H
            r=int(max(0,min(255,10*(1-k)+43*k*0.7))); g=int(max(0,min(255,30*(1-k)+90))); b=int(max(0,min(255,80*(1-k)+180)))
            pygame.draw.line(screen,(r,g,b),(0,y),(W,y))
        # cloud bar
        bar=pygame.Surface((W,36), pygame.SRCALPHA)
        bar.fill((0,0,0,160))
        screen.blit(bar,(0,0))
        title=get_font(18,True).render("PlayTree Cloud Gaming  •  GoConsole Cloud  •  PlayTree Corporation", True, (180,220,200))
        screen.blit(title,(20,10))
        cloud_txt=get_font(12).render(f"Cloud: {'ONLINE' if cloud_online else 'OFFLINE'} • {int(t)}s", True, (80,255,120) if cloud_online else (255,80,80))
        screen.blit(cloud_txt,(W-cloud_txt.get_width()-20,12))
        # hub title
        hdr=get_font(42,True).render("PLAYTREE CLOUD", True, (255,255,255))
        screen.blit(hdr,(W//2 - hdr.get_width()//2, 70))
        sub=get_font(13).render("Fighting  •  Roleplay  •  Obby  •  FootBall  •  Tycoon  •  Fishing  •  Royale — All PlayTrees", True, (200,220,200))
        screen.blit(sub,(W//2 - sub.get_width()//2, 110))
        # games grid — like Roblox/Fortnite hub
        for i,(name,desc,mode,col) in enumerate(GAMES):
            r=pygame.Rect(W//2 -260, 140+i*78, 520, 68)
            sel_now=(i==sel)
            # card
            pygame.draw.rect(screen, (0,0,0), r, border_radius=10)
            inner=r.inflate(-4,-4)
            bg=col if not sel_now else (min(255,col[0]+30),min(255,col[1]+30),min(255,col[2]+30))
            pygame.draw.rect(screen, bg, inner, border_radius=8)
            pygame.draw.rect(screen, LIME if sel_now else (80,80,80), inner, 2, border_radius=8)
            # icon
            icon=pygame.Rect(r.x+12, r.y+12, 44,44)
            pygame.draw.rect(screen, (255,255,255), icon, border_radius=8)
            pygame.draw.rect(screen, (0,0,0), icon, 2, border_radius=8)
            init=get_font(18,True).render(name[0], True, col)
            screen.blit(init,(icon.centerx - init.get_width()//2, icon.centery - init.get_height()//2))
            # texts
            ntxt=get_font(20,True).render(name, True, (20,20,20))
            screen.blit(ntxt,(r.x+70, r.y+12))
            dtxt=get_font(12).render(desc, True, (40,40,40))
            screen.blit(dtxt,(r.x+70, r.y+36))
            # Play button small like Fortnite
            pr=pygame.Rect(r.right-90, r.centery-14, 76, 28)
            pygame.draw.rect(screen, LIME, pr, border_radius=6)
            pygame.draw.rect(screen, DARK, pr, 2, border_radius=6)
            pt=get_font(12,True).render("PLAY", True, (0,0,0))
            screen.blit(pt,(pr.centerx - pt.get_width()//2, pr.centery - pt.get_height()//2))
            if sel_now:
                # arrow
                arr=get_font(20,True).render("▶", True, (255,255,0))
                screen.blit(arr,(r.x-22, r.centery - arr.get_height()//2))

        # footer like Minecraft launcher
        foot=pygame.Surface((W,40), pygame.SRCALPHA)
        foot.fill((0,0,0,120))
        screen.blit(foot,(0,H-40))
        ft=get_font(11).render("PlayTree Cloud Gaming 1.0.0 • GoConsole • 7 PlayTrees • Cloud Save GoStudios • Press Play or ENTER", True, (180,220,180))
        screen.blit(ft,(W//2 - ft.get_width()//2, H-26))
        pygame.display.flip()
    pygame.quit(); sys.exit(0)
if __name__=="__main__": main()
