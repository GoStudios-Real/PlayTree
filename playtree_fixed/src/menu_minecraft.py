import pygame, math, random
from config import *

def draw_minecraft_world(screen, t):
    # Sky
    for y in range(HEIGHT):
        k=y/HEIGHT
        r=int(100+k*40)
        g=int(180+k*40)
        b=int(255)
        pygame.draw.line(screen, (r,g,b), (0,y),(WIDTH,y))
    # Clouds — blocky
    for i in range(6):
        cx = (i*300 + int(t*10)%400) - 50
        cy = 40 + (i%3)*20
        for j in range(4):
            pygame.draw.rect(screen, (255,255,255), (cx+j*30, cy, 40, 18))
            pygame.draw.rect(screen, (220,220,220), (cx+j*30, cy, 40, 18), 1)
    # Hills
    for i in range(20):
        x = i*80 - int(t*5)%80
        h = 180 + math.sin(i*0.8)*40 + math.sin(t*0.2+i)*10
        y = HEIGHT - 220 - h//2
        pygame.draw.rect(screen, (90, 60, 35), (x, y+60, 80, h))
        pygame.draw.rect(screen, (60, 120, 40), (x, y+40, 80, 60))
        # grass top
        pygame.draw.rect(screen, (80,180,50), (x, y+40, 80, 12))
    # Water
    pygame.draw.rect(screen, (40, 100, 180), (0, HEIGHT-160, WIDTH, 80))
    for i in range(30):
        wx = (i*50 + int(t*20)%50)
        pygame.draw.line(screen, (60,140,220), (wx, HEIGHT-100), (wx+20, HEIGHT-100), 1)
    # Trees
    for i in range(4):
        tx = 80 + i*280
        pygame.draw.rect(screen, (90,60,20), (tx, HEIGHT-220, 16, 60))
        pygame.draw.rect(screen, (30,100,30), (tx-20, HEIGHT-240, 56, 50))
    # Flowers
    for i in range(12):
        fx = 40 + i*90 + int(math.sin(i)*20)
        fy = HEIGHT - 170 + (i%3)*15
        col = [(255,0,60),(255,220,0),(255,255,255)][i%3]
        pygame.draw.circle(screen, col, (fx,fy), 4)
        pygame.draw.circle(screen, (255,255,0), (fx,fy), 2)

def draw_minecraft_button(surf, rect, text, active=False):
    # Minecraft stone button: light gray with dark border
    base = (200,200,200) if not active else (220,220,220)
    border = (0,0,0)
    shadow = (85,85,85)
    # outer black
    pygame.draw.rect(surf, border, rect, border_radius=0)
    # inner
    inner = rect.inflate(-4,-4)
    pygame.draw.rect(surf, base, inner, border_radius=0)
    # top highlight
    pygame.draw.line(surf, (255,255,255), (inner.x, inner.y), (inner.right, inner.y), 2)
    pygame.draw.line(surf, shadow, (inner.x, inner.bottom-2), (inner.right, inner.bottom-2), 2)
    # text
    f = pygame.font.Font(None, 22)
    txt = f.render(text, True, (30,30,30))
    surf.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2 + 1))
