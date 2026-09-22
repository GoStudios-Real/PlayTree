"""PLAYTREE 3D — GoStudios • Pure pygame + OpenGL (no panda3d/ursina)"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
import random

pygame.init()
WIDTH, HEIGHT = 1280, 720
pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("PLAYTREE 3D — GoStudios")

glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glEnable(GL_COLOR_MATERIAL)
glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
glShadeModel(GL_SMOOTH)
glClearColor(0.4, 0.6, 0.9, 1.0)
gluPerspective(70, WIDTH / HEIGHT, 0.1, 2000)

glLightfv(GL_LIGHT0, GL_POSITION, [0, 50, 0, 1])
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.7, 1])

cam_x, cam_y, cam_z = 0, 10, 30
cam_yaw, cam_pitch = 0, 0
mov_speed = 0.3
sens = 0.15

tree_x, tree_y, tree_z = 0, 0, 0

astro_toilets = []
for i, (x, z, typ, col, hp) in enumerate([
    (30, 30, "Trooper", (0.65, 0.68, 0.75), 2),
    (50, -40, "Rocketeer", (0.8, 0.25, 0.15), 3),
    (-40, 50, "Detainer", (0.2, 0.2, 0.35), 4),
    (-60, -60, "Juggernaut", (0.5, 0.5, 0.55), 8),
    (80, 20, "Astro Carrier", (0.3, 0.3, 0.4), 15),
    (-20, -80, "Parasitic Toilet", (0.55, 0.1, 0.1), 6),
    (70, -70, "Detainer Chief", (0.4, 0.1, 0.5), 20),
]):
    astro_toilets.append({
        'x': x, 'y': 2, 'z': z,
        'typ': typ, 'color': col, 'hp': hp, 'max_hp': hp,
        'ring_angle': random.uniform(0, 360),
        'base_y': 2
    })

score = 0
hp = 100
game_time = 0
system_name = "Sector 7 — Astro Toilet Warzone"
keys_held = set()
shot_effects = []
particles = []
font = None
hud_font = None
damage_flash = 0
attack_cooldown = 0
wave = 1

def draw_cube(sx, sy, sz, ex, ey, ez):
    glBegin(GL_QUADS)
    vertices = [
        (ex, sy, sz), (ex, ey, sz), (sx, ey, sz), (sx, sy, sz),
        (sx, sy, ez), (sx, ey, ez), (ex, ey, ez), (ex, sy, ez),
        (sx, ey, sz), (sx, ey, ez), (ex, ey, ez), (ex, ey, sz),
        (sx, sy, ez), (sx, sy, sz), (ex, sy, sz), (ex, sy, ez),
        (ex, sy, sz), (ex, sy, ez), (ex, ey, ez), (ex, ey, sz),
        (sx, sy, ez), (sx, sy, sz), (sx, ey, sz), (sx, ey, ez),
    ]
    normals = [
        (0, 0, -1), (0, 0, 1), (0, 1, 0),
        (0, -1, 0), (1, 0, 0), (-1, 0, 0)
    ]
    for i in range(6):
        glNormal3fv(normals[i])
        for j in range(4):
            glVertex3fv(vertices[i * 4 + j])
    glEnd()

def draw_cylinder(radius, height, segments=16):
    glBegin(GL_QUAD_STRIP)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        nx = math.cos(angle)
        nz = math.sin(angle)
        glNormal3f(nx, 0, nz)
        glVertex3f(nx * radius, 0, nz * radius)
        glVertex3f(nx * radius, height, nz * radius)
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glNormal3f(0, 1, 0)
    glVertex3f(0, height, 0)
    for i in range(segments + 1):
        angle = 2 * math.pi * i / segments
        glVertex3f(math.cos(angle) * radius, height, math.sin(angle) * radius)
    glEnd()

def draw_sphere(radius, slices=12, stacks=8):
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + i / stacks)
        lat1 = math.pi * (-0.5 + (i + 1) / stacks)
        y0, r0 = math.sin(lat0), math.cos(lat0)
        y1, r1 = math.sin(lat1), math.cos(lat1)
        glBegin(GL_QUAD_STRIP)
        for j in range(slices + 1):
            lng = 2 * math.pi * j / slices
            x, z = math.cos(lng), math.sin(lng)
            glNormal3f(x * r0, y0, z * r0)
            glVertex3f(x * r0 * radius, y0 * radius, z * r0 * radius)
            glNormal3f(x * r1, y1, z * r1)
            glVertex3f(x * r1 * radius, y1 * radius, z * r1 * radius)
        glEnd()

def draw_tree():
    glColor3f(0.35, 0.22, 0.1)
    draw_cylinder(1.5, 18)
    glColor3f(0.2, 0.55, 0.2)
    draw_sphere(8, 16, 12)
    glTranslatef(2, 6, 1)
    glColor3f(0.25, 0.65, 0.25)
    draw_sphere(5.5, 12, 8)
    glTranslatef(-2, 6, -1)
    glColor3f(0.3, 0.7, 0.3)
    draw_sphere(4.5, 10, 8)
    glTranslatef(0, 0, 0)

def draw_ground():
    size = 500
    step = 10
    glBegin(GL_QUADS)
    for x in range(-size, size, step):
        for z in range(-size, size, step):
            if ((x // step) + (z // step)) % 2 == 0:
                glColor3f(0.18, 0.42, 0.18)
            else:
                glColor3f(0.15, 0.38, 0.15)
            glNormal3f(0, 1, 0)
            glVertex3f(x, -2, z)
            glVertex3f(x + step, -2, z)
            glVertex3f(x + step, -2, z + step)
            glVertex3f(x, -2, z + step)
    glEnd()

def draw_astro_toilet(at):
    x, y, z = at['x'], at['y'], at['z']
    r, g, b = at['color']
    glPushMatrix()
    glTranslatef(x, y, z)
    glTranslatef(0, math.sin(time.time() * 2 + x * 0.1) * 0.3, 0)

    glColor3f(0.85, 0.85, 0.9)
    draw_sphere(1.8, 10, 8)

    glTranslatef(0, 1.5, 0.9)
    glColor3f(0.95, 0.95, 1.0)
    draw_sphere(0.5, 6, 6)
    glTranslatef(0, -1.5, -0.9)

    glTranslatef(-0.7, 1.2, 0.5)
    glColor3f(0.1, 0.1, 0.1)
    draw_sphere(0.3, 6, 4)
    glTranslatef(0.7, -1.2, -0.5)

    glTranslatef(0.7, 1.2, 0.5)
    draw_sphere(0.3, 6, 4)
    glTranslatef(-0.7, -1.2, -0.5)

    glTranslatef(0, -0.3, 1.0)
    glColor3f(0.15, 0.15, 0.15)
    draw_cube(-0.4, -0.1, -0.1, 0.4, 0.1, 0.3)
    glTranslatef(0, 0.3, -1.0)

    at['ring_angle'] += 1.5
    glRotatef(at['ring_angle'], 0, 1, 0)
    glColor4f(r, g, b, 0.6)
    glDisable(GL_LIGHTING)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    for i in range(48):
        a = 2 * math.pi * i / 48
        glVertex3f(math.cos(a) * 3.5, 0, math.sin(a) * 3.5)
    glEnd()
    glEnable(GL_LIGHTING)

    glPopMatrix()

def draw_shot_effect():
    for s in shot_effects[:]:
        glPushMatrix()
        glTranslatef(s['x'], s['y'], s['z'])
        glColor3f(1.0, 0.9, 0.2)
        glDisable(GL_LIGHTING)
        draw_sphere(0.4 - s['age'] * 2, 6, 4)
        glEnable(GL_LIGHTING)
        glPopMatrix()
        s['age'] += 0.05
        if s['age'] > 0.2:
            shot_effects.remove(s)

def draw_particle():
    for p in particles[:]:
        glPushMatrix()
        glTranslatef(p['x'], p['y'], p['z'])
        glColor4f(*p['color'])
        glDisable(GL_LIGHTING)
        glPointSize(3)
        glBegin(GL_POINTS)
        glVertex3f(0, 0, 0)
        glEnd()
        glEnable(GL_LIGHTING)
        glPopMatrix()
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['z'] += p['vz']
        p['vy'] -= 0.05
        p['life'] -= 0.02
        if p['life'] <= 0:
            particles.remove(p)

def spawn_particles(x, y, z, color, count=10):
    for _ in range(count):
        particles.append({
            'x': x, 'y': y, 'z': z,
            'vx': random.uniform(-0.3, 0.3),
            'vy': random.uniform(0.1, 0.5),
            'vz': random.uniform(-0.3, 0.3),
            'color': (*color, 1.0),
            'life': 1.0
        })

def draw_hud_3d():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glColor4f(0, 0, 0, 0.5)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(WIDTH, 0)
    glVertex2f(WIDTH, 50)
    glVertex2f(0, 50)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(0, HEIGHT - 40)
    glVertex2f(WIDTH, HEIGHT - 40)
    glVertex2f(WIDTH, HEIGHT)
    glVertex2f(0, HEIGHT)
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(0, HEIGHT - 80)
    glVertex2f(200, HEIGHT - 80)
    glVertex2f(200, HEIGHT - 50)
    glVertex2f(0, HEIGHT - 50)
    glEnd()
    bar_w = max(0, (hp / 100) * 196)
    glColor3f(0.1, 0.85, 0.1) if hp > 60 else (glColor3f(0.9, 0.8, 0.1) if hp > 30 else glColor3f(0.9, 0.1, 0.1))
    glBegin(GL_QUADS)
    glVertex2f(2, HEIGHT - 78)
    glVertex2f(2 + bar_w, HEIGHT - 78)
    glVertex2f(2 + bar_w, HEIGHT - 52)
    glVertex2f(2, HEIGHT - 52)
    glEnd()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud_text():
    global font, hud_font
    if font is None:
        try:
            font = pygame.font.SysFont("arial", 18)
            hud_font = pygame.font.SysFont("arial", 14)
        except:
            font = pygame.font.Font(None, 18)
            hud_font = pygame.font.Font(None, 14)

    hud_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    title = font.render(f"PLAYTREE 3D — GoConsole | {system_name}", True, (126, 211, 33))
    hud_surf.blit(title, (10, 8))

    info = hud_font.render(f"WASD Move | Mouse Look | Click Shoot | Space Jump | ESC Quit", True, (180, 220, 180))
    hud_surf.blit(info, (10, HEIGHT - 28))

    hp_text = hud_font.render(f"HP: {hp}/100", True, (255, 255, 255))
    hud_surf.blit(hp_text, (8, HEIGHT - 76))

    sc = font.render(f"Score: {score}  |  Wave: {wave}  |  Enemies: {len(astro_toilets)}", True, (255, 220, 50))
    hud_surf.blit(sc, (WIDTH - 380, 8))

    if damage_flash > 0:
        flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash_surf.fill((255, 0, 0, int(min(damage_flash * 120, 80))))
        hud_surf.blit(flash_surf, (0, 0))

    hud_data = pygame.image.tostring(hud_surf, "RGBA", True)
    glWindowPos2d = None
    try:
        from OpenGL.GL import glWindowPos2d as _gwp
        glWindowPos2d = _gwp
    except:
        pass
    if glWindowPos2d:
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPixelZoom(1, -1)
        glWindowPos2d(0, HEIGHT)
        glDrawPixels(WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, hud_data)
        glPixelZoom(1, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
    pygame.display.flip()

clock = pygame.time.Clock()
running = True
spawn_timer = 0

while running:
    dt = clock.tick(60) / 1000.0
    game_time += dt
    damage_flash = max(0, damage_flash - dt * 3)
    attack_cooldown = max(0, attack_cooldown - dt)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            keys_held.add(event.key)
            if event.key == K_ESCAPE:
                running = False
        elif event.type == KEYUP:
            keys_held.discard(event.key)
        elif event.type == MOUSEMOTION:
            cam_yaw += event.rel[0] * sens
            cam_pitch -= event.rel[1] * sens
            cam_pitch = max(-89, min(89, cam_pitch))
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if attack_cooldown <= 0:
                attack_cooldown = 0.3
                dx = -math.sin(math.radians(cam_yaw)) * math.cos(math.radians(cam_pitch))
                dy = math.sin(math.radians(cam_pitch))
                dz = -math.cos(math.radians(cam_yaw)) * math.cos(math.radians(cam_pitch))

                shot_effects.append({'x': cam_x, 'y': cam_y, 'z': cam_z, 'age': 0})

                hit = False
                for at in astro_toilets:
                    adx = at['x'] - cam_x
                    ady = at['y'] - cam_y
                    adz = at['z'] - cam_z
                    dist = math.sqrt(adx*adx + ady*ady + adz*adz)
                    if dist < 30:
                        dot = (adx*dx + ady*dy + adz*dz) / dist
                        if dot > 0.95:
                            at['hp'] -= 1
                            spawn_particles(at['x'], at['y'], at['z'], at['color'], 8)
                            if at['hp'] <= 0:
                                score += 10 * at['max_hp']
                                spawn_particles(at['x'], at['y'], at['z'], (1, 0.8, 0), 20)
                                astro_toilets.remove(at)
                                hit = True
                            break

    forward_x = -math.sin(math.radians(cam_yaw))
    forward_z = -math.cos(math.radians(cam_yaw))
    right_x = math.cos(math.radians(cam_yaw))
    right_z = -math.sin(math.radians(cam_yaw))

    if K_w in keys_held:
        cam_x += forward_x * mov_speed
        cam_z += forward_z * mov_speed
    if K_s in keys_held:
        cam_x -= forward_x * mov_speed
        cam_z -= forward_z * mov_speed
    if K_a in keys_held:
        cam_x -= right_x * mov_speed
        cam_z -= right_z * mov_speed
    if K_d in keys_held:
        cam_x += right_x * mov_speed
        cam_z += right_z * mov_speed
    if K_SPACE in keys_held:
        cam_y += mov_speed
    if K_LSHIFT in keys_held:
        cam_y -= mov_speed

    for at in astro_toilets:
        dx = cam_x - at['x']
        dz = cam_z - at['z']
        d = math.sqrt(dx*dx + dz*dz)
        if 5 < d < 40:
            at['x'] += dx / d * 0.05
            at['z'] += dz / d * 0.05
        if d < 4:
            damage_flash += dt * 5
            hp -= dt * 15
            spawn_particles(at['x'], at['y'], at['z'], (1, 0, 0), 3)
            if hp <= 0:
                hp = 0

    spawn_timer += dt
    if spawn_timer > 5 and len(astro_toilets) < 12:
        spawn_timer = 0
        wave += 1
        types = ["Trooper", "Rocketeer", "Detainer", "Juggernaut", "Astro Carrier"]
        cols = [(0.65, 0.68, 0.75), (0.8, 0.25, 0.15), (0.2, 0.2, 0.35), (0.5, 0.5, 0.55), (0.3, 0.3, 0.4)]
        for _ in range(min(wave, 4)):
            t = random.randint(0, len(types) - 1)
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(30, 80)
            astro_toilets.append({
                'x': cam_x + math.cos(angle) * dist,
                'y': 2,
                'z': cam_z + math.sin(angle) * dist,
                'typ': types[t], 'color': cols[t],
                'hp': 2 + wave, 'max_hp': 2 + wave,
                'ring_angle': random.uniform(0, 360),
                'base_y': 2
            })

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glRotatef(cam_pitch, 1, 0, 0)
    glRotatef(cam_yaw, 0, 1, 0)
    glTranslatef(-cam_x, -cam_y, -cam_z)

    draw_ground()
    glPushMatrix()
    glTranslatef(tree_x, 0, tree_z)
    draw_tree()
    glPopMatrix()

    for at in astro_toilets:
        draw_astro_toilet(at)

    draw_shot_effect()
    draw_particle()

    draw_hud_3d()
    draw_hud_text()

    if hp <= 0:
        death_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        death_surf.fill((0, 0, 0, 150))
        if font:
            dtxt = font.render("GAME OVER — Press R to Restart or ESC to Quit", True, (255, 50, 50))
            stxt = font.render(f"Final Score: {score} | Wave: {wave}", True, (255, 220, 50))
            death_surf.blit(dtxt, (WIDTH // 2 - dtxt.get_width() // 2, HEIGHT // 2 - 30))
            death_surf.blit(stxt, (WIDTH // 2 - stxt.get_width() // 2, HEIGHT // 2 + 10))

        death_data = pygame.image.tostring(death_surf, "RGBA", True)
        try:
            from OpenGL.GL import glWindowPos2d as _gwp
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            _gwp(0, HEIGHT)
            glPixelZoom(1, -1)
            glDrawPixels(WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, death_data)
            glPixelZoom(1, 1)
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
        except:
            pass
        pygame.display.flip()

        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    waiting = False
                    running = False
                elif ev.type == KEYDOWN:
                    if ev.key == K_ESCAPE:
                        waiting = False
                        running = False
                    elif ev.key == K_r:
                        hp = 100
                        score = 0
                        wave = 1
                        cam_x, cam_y, cam_z = 0, 10, 30
                        cam_yaw, cam_pitch = 0, 0
                        astro_toilets.clear()
                        for x, z, typ, col, hp_v in [
                            (30, 30, "Trooper", (0.65, 0.68, 0.75), 2),
                            (50, -40, "Rocketeer", (0.8, 0.25, 0.15), 3),
                            (-40, 50, "Detainer", (0.2, 0.2, 0.35), 4),
                            (-60, -60, "Juggernaut", (0.5, 0.5, 0.55), 8),
                        ]:
                            astro_toilets.append({
                                'x': x, 'y': 2, 'z': z,
                                'typ': typ, 'color': col,
                                'hp': hp_v, 'max_hp': hp_v,
                                'ring_angle': random.uniform(0, 360),
                                'base_y': 2
                            })
                        damage_flash = 0
                        spawn_timer = 0
                        waiting = False
                        break

pygame.quit()
