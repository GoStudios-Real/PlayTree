"""Astro Toilets — research from Skibidi Toilet wiki (Episodes 51-79)
Faction: extraterrestrial conquerors, warp levitators, high durability, tactical.
Added to PlayTree as elite round 3-4 enemies + bosses."""
import pygame, math, random
from config import WIDTH, HEIGHT, WORLD_W, WORLD_H, RED, GOLD, CYAN

ASTRO_TYPES = {
    "trooper": {"name":"Trooper Astro", "hp":80, "attack":12, "speed":2.2, "color":(160,170,190), "size":18, "rank":1, "ability":"levitate"},
    "rocketeer": {"name":"Rocketeer Astro", "hp":140, "attack":18, "speed":2.8, "color":(200,60,40), "size":24, "rank":2, "ability":"rockets"},
    "detainer": {"name":"Detainer Astro", "hp":220, "attack":22, "speed":2.0, "color":(45,45,55), "size":28, "rank":3, "ability":"detaining_claws"},
    "assailant": {"name":"Assailant Astro", "hp":340, "attack":28, "speed":2.4, "color":(180,40,40), "size":32, "rank":4, "ability":"photon_cannon"},
    "juggernaut": {"name":"Juggernaut Astro", "hp":480, "attack":32, "speed":1.6, "color":(90,90,95), "size":38, "rank":5, "ability":"emp_shockwave"},
    "duchess": {"name":"Duchess Astro", "hp":600, "attack":36, "speed":1.9, "color":(200,100,180), "size":36, "rank":5, "ability":"laser_eyes"},
    "mothership": {"name":"Mothership Astro", "hp":1200, "attack":45, "speed":0.7, "color":(30,40,60), "size":70, "rank":6, "ability":"warp_summon"},
}

class AstroToilet:
    def __init__(self, x, y, astro_type="trooper"):
        cfg = ASTRO_TYPES.get(astro_type, ASTRO_TYPES["trooper"])
        self.astro_type = astro_type
        self.name = cfg["name"]
        self.max_hp = cfg["hp"]
        self.hp = cfg["hp"]
        self.attack = cfg["attack"]
        self.speed = cfg["speed"]
        self.color = cfg["color"]
        self.size = cfg["size"]
        self.rank = cfg["rank"]
        self.ability = cfg["ability"]
        self.x, self.y = x, y
        self.vx, self.vy = 0,0
        self.levitate_h = 0
        self.warp_timer = random.uniform(3,7)
        self.shoot_timer = random.uniform(1,2)
        self.alive = True

    def update(self, player, dt):
        # levitate hover
        self.levitate_h = math.sin(pygame.time.get_ticks()*0.004 + hash(self.x)%10)*4
        # chase player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx,dy) or 1
        if dist>40:
            self.vx = dx/dist * self.speed
            self.vy = dy/dist * self.speed
        else:
            self.vx *= 0.85; self.vy *=0.85
        self.x += self.vx
        self.y += self.vy
        # warp occasionally
        self.warp_timer -= dt
        if self.warp_timer<=0 and random.random()<0.08:
            self.x += random.randint(-120,120)
            self.y += random.randint(-120,120)
            self.x = max(40, min(WORLD_W-40, self.x))
            self.y = max(40, min(WORLD_H-40, self.y))
            self.warp_timer = random.uniform(4,8)
        self.shoot_timer -= dt

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp<=0:
            self.alive=False
            return True
        return False

    def can_shoot(self): return self.shoot_timer<=0

    def shoot(self):
        self.shoot_timer = 1.5 + random.random()
        # return projectile type based on ability
        if self.ability=="rockets": return "rocket"
        if self.ability=="photon_cannon": return "photon"
        if self.ability=="emp_shockwave": return "emp"
        if self.ability=="laser_eyes": return "laser"
        return "blaster"

    def draw(self, surf, cam_x, cam_y):
        sx, sy = int(self.x - cam_x), int(self.y - cam_y + self.levitate_h)
        # warp ring
        if self.rank>=2:
            pygame.draw.ellipse(surf, (100,240,255,80), (sx-self.size-6, sy-6, self.size*2+12, 10))
            pygame.draw.ellipse(surf, (80,200,255), (sx-self.size-6, sy-6, self.size*2+12, 10),1)
        # bowl
        pygame.draw.ellipse(surf, (230,230,240), (sx-self.size, sy, self.size*2, self.size))
        pygame.draw.ellipse(surf, (180,180,190), (sx-self.size, sy, self.size*2, self.size),2)
        # helmet
        helm_col = (60,60,70) if self.rank<3 else (90,30,30) if self.rank<5 else (160,30,30)
        pygame.draw.rect(surf, helm_col, (sx-self.size//2, sy-18, self.size, 18), border_radius=4)
        # stripes for rank
        for i in range(self.rank):
            pygame.draw.rect(surf, (255,220,80), (sx-8+i*7, sy-14, 5, 8))
        # eyes
        eye_col = (255,40,40) if self.rank>=4 else (80,240,255)
        pygame.draw.circle(surf, eye_col, (sx-6, sy-8), 4)
        pygame.draw.circle(surf, eye_col, (sx+6, sy-8), 4)
        # mech arms for high ranks
        if self.rank>=3:
            pygame.draw.rect(surf, (70,70,80), (sx-self.size-10, sy+6, 12, 14))
            pygame.draw.rect(surf, (70,70,80), (sx+self.size-2, sy+6, 12, 14))
        # HP bar
        if self.hp < self.max_hp:
            w=int(40*(self.hp/self.max_hp))
            pygame.draw.rect(surf,(0,0,0),(sx-20,sy-28,40,4))
            pygame.draw.rect(surf,RED,(sx-20,sy-28,w,4))
        # name
        if self.size>30:
            f=pygame.font.Font(None,12)
            txt=f.render(self.name, True, (200,220,255))
            surf.blit(txt,(sx - txt.get_width()//2, sy+self.size+6))
