"""PlayTree — Live Player Count, Doggo Legend, Dancing Bots, Admin Abuse"""
import pygame
import math
import random
from config import WIDTH, HEIGHT, GOLD, GREEN_GLOW


class PlayerCount:
    """Live global player count with 100,000,000 bot players."""
    BOTS_BASE = 100_000_000
    REAL_BASE = 8_473_921
    PEAK_BASE = 14_283_950
    SERVERS = 12_400
    DOGGO_ARMY = 1_000_000
    ASTRO_NPCS = 50_000_000

    def __init__(self):
        self.real = self.REAL_BASE
        self.bots = self.BOTS_BASE
        self.peak = self.PEAK_BASE
        self.matches = 482_931
        self.tick_timer = 0.0
        self.display_real = 0
        self.display_total = 0

    def update(self, dt):
        self.tick_timer += dt
        if self.tick_timer >= 1.0:
            self.tick_timer = 0.0
            drift = random.randint(-int(self.REAL_BASE * 0.003), int(self.REAL_BASE * 0.003))
            self.real = max(1_000_000, self.REAL_BASE + drift)
            self.bots = self.BOTS_BASE + random.randint(-10_000, 10_000)
            self.matches += random.randint(-40, 45)
            self.matches = max(400_000, self.matches)
            total = self.real + self.bots
            if total > self.peak:
                self.peak = total
            self.display_real = self.real
            self.display_total = total

    @property
    def total(self):
        return self.real + self.bots

    def draw(self, screen, font, small_font, x=None, y=None):
        """Draw compact player count panel."""
        if x is None:
            x = WIDTH // 2
        if y is None:
            y = HEIGHT - 70
        pw, ph = 520, 54
        rect = pygame.Rect(x - pw // 2, y - ph // 2, pw, ph)
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((0, 20, 40, 200))
        pygame.draw.rect(bg, (0, 0, 0, 0), rect, border_radius=8)
        screen.blit(bg, rect.topleft)
        pygame.draw.rect(screen, (80, 180, 255), rect, 2, border_radius=8)

        # Green live dot
        pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.004)) * 155 + 100)
        pygame.draw.circle(screen, (0, pulse, 0), (rect.x + 14, rect.centery), 5)

        f = pygame.font.Font(None, 22)
        label = f.render("LIVE PLAYERS:", True, (120, 200, 255))
        screen.blit(label, (rect.x + 26, rect.y + 6))

        # Real players
        n_f = pygame.font.Font(None, 26)
        real_s = n_f.render(f"{self.display_real:,}", True, (126, 211, 33))
        screen.blit(real_s, (rect.x + 26, rect.y + 26))
        rl = small_font.render("real", True, (100, 160, 120))
        screen.blit(rl, (rect.x + 26 + real_s.get_width() + 4, rect.y + 32))

        # Bot players — 100M
        bot_s = n_f.render("100,000,000", True, GOLD)
        bx = rect.x + 200
        screen.blit(bot_s, (bx, rect.y + 26))
        bl = small_font.render("bots", True, (180, 150, 60))
        screen.blit(bl, (bx + bot_s.get_width() + 4, rect.y + 32))

        # Total
        tot_s = n_f.render(f"{self.display_total:,}", True, (80, 180, 255))
        tx = rect.x + 400
        screen.blit(tot_s, (tx, rect.y + 26))
        tl = small_font.render("total", True, (80, 140, 180))
        screen.blit(tl, (tx + tot_s.get_width() + 4, rect.y + 32))


class DoggoLegend:
    """Doggo the PlayTree Legend — hall of fame panel."""
    QUOTES = [
        ("RHYS", "I don't play to win. I play so Doggo notices me."),
        ("WILLOW", "Doggo carried our whole ranked season. Absolute unit."),
        ("DOGGO", "Woof."),
    ]
    STATS = [
        ("9999", "Win Streak"),
        ("1M+", "Astro Toilets"),
        ("\u221e", "Good Boy Pts"),
        ("S+", "Rank"),
        ("0", "Losses"),
    ]

    def __init__(self):
        self.time = 0.0

    def update(self, dt):
        self.time += dt

    def draw(self, screen, font, small_font):
        # Dim backdrop
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pw, ph = 720, 560
        rect = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2, pw, ph)
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((26, 20, 5, 245))
        screen.blit(bg, rect.topleft)
        # Gold border with glow pulse
        glow = int(abs(math.sin(self.time * 2)) * 80 + 150)
        pygame.draw.rect(screen, (255, 215, glow), rect, 3, border_radius=16)

        cx = rect.centerx
        y = rect.y + 18

        # Banner
        bf = pygame.font.Font(None, 28)
        banner = bf.render("* PLAYTREE HALL OF LEGENDS *", True, (0, 0, 0))
        bbg = pygame.Surface((banner.get_width() + 30, 30), pygame.SRCALPHA)
        bbg.fill((255, 215, 0, 230))
        screen.blit(bbg, (cx - bbg.get_width() // 2, y))
        screen.blit(banner, (cx - banner.get_width() // 2, y + 5))
        y += 44

        # DOGGO name — big gold with pulse
        pulse = int(abs(math.sin(self.time * 1.5)) * 60 + 195)
        nf = pygame.font.Font(None, 80)
        name = nf.render("DOGGO", True, (255, 215, pulse))
        screen.blit(name, (cx - name.get_width() // 2, y))
        y += 70

        # Subtitle
        sf = pygame.font.Font(None, 24)
        sub = sf.render("THE PLAYTREE LEGEND", True, (255, 232, 154))
        screen.blit(sub, (cx - sub.get_width() // 2, y))
        y += 36

        # Doggo avatar — crown + dog emoji style drawing
        bounce = int(math.sin(self.time * 3) * 8)
        dx, dy = cx, y + 50 + bounce
        # Aura glow
        for r in range(60, 0, -6):
            a = max(0, 100 - r)
            aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura, (255, 215, 0, a), (r, r), r)
            screen.blit(aura, (dx - r, dy - r))
        # Crown
        cf = pygame.font.Font(None, 40)
        crown = cf.render("\u265b", True, (255, 215, 0))
        screen.blit(crown, (dx - crown.get_width() // 2, dy - 52 + bounce // 2))
        # Dog head (simple pixel style)
        pygame.draw.rect(screen, (210, 161, 90), (dx - 24, dy - 30, 48, 40), border_radius=8)
        # Ears
        pygame.draw.rect(screen, (160, 110, 60), (dx - 30, dy - 34, 14, 22), border_radius=4)
        pygame.draw.rect(screen, (160, 110, 60), (dx + 16, dy - 34, 14, 22), border_radius=4)
        # Eyes
        pygame.draw.circle(screen, (20, 20, 20), (dx - 10, dy - 12), 5)
        pygame.draw.circle(screen, (20, 20, 20), (dx + 10, dy - 12), 5)
        pygame.draw.circle(screen, (255, 255, 255), (dx - 8, dy - 14), 2)
        pygame.draw.circle(screen, (255, 255, 255), (dx + 12, dy - 14), 2)
        # Nose
        pygame.draw.ellipse(screen, (30, 30, 30), (dx - 5, dy + 2, 10, 7))
        # Tongue
        pygame.draw.ellipse(screen, (255, 100, 120), (dx - 4, dy + 12, 8, 10))
        # Body
        pygame.draw.rect(screen, (255, 215, 0), (dx - 18, dy + 14, 36, 26), border_radius=6)
        pygame.draw.rect(screen, (200, 160, 0), (dx - 18, dy + 14, 36, 6))
        y = dy + 52

        # Title
        tf = pygame.font.Font(None, 22)
        tt = tf.render("- ETERNAL CHAMPION OF THE TREE -", True, (255, 215, 0))
        screen.blit(tt, (cx - tt.get_width() // 2, y))
        y += 30

        # Stats row
        sw = 120
        sx = cx - (len(self.STATS) * (sw + 8)) // 2
        for val, lab in self.STATS:
            srect = pygame.Rect(sx, y, sw, 56)
            sbg = pygame.Surface((sw, 56), pygame.SRCALPHA)
            sbg.fill((0, 0, 0, 160))
            screen.blit(sbg, srect.topleft)
            pygame.draw.rect(screen, (255, 215, 0), srect, 1, border_radius=8)
            vf = pygame.font.Font(None, 30)
            vs = vf.render(val, True, (255, 215, 0))
            screen.blit(vs, (srect.centerx - vs.get_width() // 2, srect.y + 6))
            lf = pygame.font.Font(None, 14)
            ls = lf.render(lab.upper(), True, (200, 170, 255))
            screen.blit(ls, (srect.centerx - ls.get_width() // 2, srect.y + 38))
            sx += sw + 8
        y += 68

        # Quotes
        qy = y
        for who, q in self.QUOTES:
            qf = pygame.font.Font(None, 18)
            w_s = qf.render(f"{who}:", True, (255, 215, 0))
            screen.blit(w_s, (rect.x + 30, qy))
            # word wrap quote
            words = q.split()
            line = ""
            ly = qy + 18
            qw = pw - 60
            for w in words:
                test = (line + " " + w).strip()
                if qf.size(test)[0] > qw:
                    ls = qf.render(line, True, (245, 230, 184))
                    screen.blit(ls, (rect.x + 30, ly))
                    ly += 18
                    line = w
                else:
                    line = test
            if line:
                ls = qf.render(line, True, (245, 230, 184))
                screen.blit(ls, (rect.x + 30, ly))
                ly += 18
            qy = ly + 6
        y = qy + 4

        # Rank badge
        rf = pygame.font.Font(None, 24)
        rank = rf.render("#1 ALL-TIME - UNTOUCHABLE", True, (0, 0, 0))
        rbg = pygame.Surface((rank.get_width() + 40, 30), pygame.SRCALPHA)
        rbg.fill((255, 215, 0, 230))
        screen.blit(rbg, (cx - rbg.get_width() // 2, y))
        screen.blit(rank, (cx - rank.get_width() // 2, y + 5))
        y += 38

        # Bones
        bf2 = pygame.font.Font(None, 24)
        bones = bf2.render("\U0001F9B4 \U0001F9B4 \U0001F9B4 \U0001F9B4 \U0001F9B4", True, (255, 215, 0))
        screen.blit(bones, (cx - bones.get_width() // 2, y))

        # Hint
        hint_f = pygame.font.Font(None, 16)
        hint = hint_f.render("Press L or ESC to close", True, (120, 120, 120))
        screen.blit(hint, (cx - hint.get_width() // 2, rect.bottom - 22))


class DancingBots:
    """Dancing NPC bots shown on the main menu."""
    NAMES = ["Bot_Astro", "xX_NoScope", "WillowFan", "GemCrusher", "DriftKing",
             "LootLord", "BubbleBlast", "ChainLight", "Frogger77", "ShadowTile",
             "NeonDiver", "TurboToad", "PixelPirate", "CoralQueen", "SniperBot"]
    COLORS = [
        (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
        (255, 100, 255), (100, 255, 255), (255, 180, 60), (200, 120, 255),
        (120, 255, 180), (255, 120, 180), (180, 220, 80), (80, 200, 220),
        (240, 140, 90), (160, 240, 140), (220, 100, 160),
    ]

    def __init__(self, count=12):
        self.bots = []
        # Spread bots across width, keeping clear of Profile/Steve zone on the right
        margin = 50
        right_gap = 160
        left = margin
        right = WIDTH - right_gap
        usable = right - left
        for i in range(count):
            self.bots.append({
                "name": self.NAMES[i % len(self.NAMES)],
                "color": self.COLORS[i % len(self.COLORS)],
                "x": left + int(i * usable / max(1, count - 1)),
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(2.5, 4.5),
                "dance": random.randint(0, 2),
                "scale": random.uniform(0.7, 1.1),
            })
        self.time = 0.0

    def update(self, dt):
        self.time += dt

    def draw(self, screen, base_y=None):
        if base_y is None:
            base_y = HEIGHT - 140
        f = pygame.font.Font(None, 16)
        for bot in self.bots:
            t = self.time * bot["speed"] + bot["phase"]
            bob = int(math.sin(t) * 10)
            sway = int(math.sin(t * 0.7) * 6)
            s = bot["scale"]
            bx = bot["x"] + sway
            by = base_y + bob
            col = bot["color"]

            # Body
            bw, bh = int(14 * s), int(22 * s)
            pygame.draw.rect(screen, col, (bx - bw // 2, by - bh, bw, bh), border_radius=4)
            # Head
            hr = int(9 * s)
            pygame.draw.circle(screen, (230, 190, 150), (bx, by - bh - hr), hr)
            # Arms (dance animation)
            arm_len = int(14 * s)
            left_angle = math.sin(t) * 1.2 - 0.5
            right_angle = -math.sin(t) * 1.2 + 0.5
            la = (bx - bw // 2, by - bh + 4)
            lb = (int(la[0] + math.cos(left_angle) * arm_len), int(la[1] + math.sin(left_angle) * arm_len))
            ra = (bx + bw // 2, by - bh + 4)
            rb = (int(ra[0] + math.cos(math.pi - right_angle) * arm_len), int(ra[1] + math.sin(right_angle) * arm_len))
            pygame.draw.line(screen, (230, 190, 150), la, lb, max(2, int(3 * s)))
            pygame.draw.line(screen, (230, 190, 150), ra, rb, max(2, int(3 * s)))
            # Legs
            leg_len = int(12 * s)
            ll = math.sin(t * 1.3) * 0.4
            lla = (bx - 4 * s, by)
            llb = (int(lla[0] + math.sin(ll) * leg_len * 0.3), int(lla[1] + leg_len))
            lra = (bx + 4 * s, by)
            lrb = (int(lra[0] - math.sin(ll) * leg_len * 0.3), int(lra[1] + leg_len))
            pygame.draw.line(screen, (40, 40, 80), lla, llb, max(2, int(4 * s)))
            pygame.draw.line(screen, (40, 40, 80), lra, lrb, max(2, int(4 * s)))
            # Name tag
            tag = f.render(bot["name"], True, (150, 190, 230))
            screen.blit(tag, (bx - tag.get_width() // 2, by + 4))

        # MJ and King Von special stars
        self._draw_star(screen, base_y, WIDTH // 3, (255, 255, 255), "MJ", self.time * 3.2)
        self._draw_star(screen, base_y, 2 * WIDTH // 3, (60, 170, 80), "KING VON", self.time * 2.4)

    def _draw_star(self, screen, base_y, x, col, name, t):
        bob = int(math.sin(t) * 14)
        sway = int(math.sin(t * 0.6) * 10)
        bx, by = x + sway, base_y - 20 + bob
        # Glow
        for r in range(30, 0, -8):
            a = max(0, 80 - r * 2)
            g = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(g, (255, 215, 0, a), (r, r), r)
            screen.blit(g, (bx - r, by - 40 - r))
        # Body
        pygame.draw.rect(screen, col, (bx - 14, by - 30, 28, 34), border_radius=6)
        pygame.draw.rect(screen, (180, 180, 180), (bx - 14, by - 30, 28, 6))
        # Head
        pygame.draw.circle(screen, (240, 200, 160), (bx, by - 42), 12)
        # Crown/star
        sf = pygame.font.Font(None, 28)
        star = sf.render("*", True, (255, 215, 0))
        screen.blit(star, (bx - star.get_width() // 2, by - 66))
        # Arms up (performing)
        pygame.draw.line(screen, (240, 200, 160), (bx - 14, by - 24), (bx - 26, by - 44), 3)
        pygame.draw.line(screen, (240, 200, 160), (bx + 14, by - 24), (bx + 26, by - 44), 3)
        # Mic
        pygame.draw.circle(screen, (255, 215, 0), (bx + 26, by - 46), 4)
        # Name
        nf = pygame.font.Font(None, 18)
        ns = nf.render(name, True, (255, 215, 0))
        screen.blit(ns, (bx - ns.get_width() // 2, by + 6))


class AdminAbuse:
    """Admin abuse console for Rhys & Willow."""
    ACTIONS = [
        ("GOLD COIN RAIN", "rain"),
        ("FORCE DANCE", "dance"),
        ("MEGA JUMP", "mega"),
        ("TPP ALL", "tpp"),
        ("GOD MODE", "god"),
        ("WILLOW RAGE", "willow"),
        ("ENLARGE ALL", "size"),
        ("360 SPIN", "spin"),
        ("ASTRO RAID", "raid"),
        ("RAINBOW", "rainbow"),
        ("SPAWN BOTS", "spawn"),
        ("FREEZE ALL", "freeze"),
        ("ROOT TITAN", "boss"),
        ("DISCO MODE", "disco"),
        ("SCREEN GLITCH", "glitch"),
        ("KICK BOT", "kick"),
    ]
    RHYS_LINES = [
        "Admin abuse activate!", "God mode ON. Try hitting me.",
        "More chaos please.", "They can't report us, we OWN this server.",
        "This is what I live for.", "Willow hit them with rage mode!",
    ]
    WILLOW_LINES = [
        "RAGE MODE!!! Everyone down!", "Chaos is a ladder.",
        "Wait till they see wave 3.", "Rhys you're going too easy.",
        "I've been waiting for this.", "Disco mode activated!",
    ]

    def __init__(self):
        self.open = False
        self.time = 0.0
        self.log = ["[BOOT] Admin Abuse Console v1.0 online",
                    "[AUTH] Rhys - ADMIN granted",
                    "[AUTH] Willow - ADMIN granted"]
        self.effects = {}
        self.selected = 0
        self.chat = []
        self.chat_timer = 0.0
        self.chat_speaker = "rhys"

    def update(self, dt):
        self.time += dt
        # Expire effects
        expired = [k for k, v in self.effects.items() if v <= 0]
        for k in expired:
            del self.effects[k]
        for k in list(self.effects.keys()):
            self.effects[k] -= dt
        # Chat lines
        self.chat_timer += dt
        if self.chat_timer > 4.0:
            self.chat_timer = 0.0
            self.chat_speaker = "willow" if self.chat_speaker == "rhys" else "rhys"
            lines = self.RHYS_LINES if self.chat_speaker == "rhys" else self.WILLOW_LINES
            who = "RHYS" if self.chat_speaker == "rhys" else "WILLOW"
            self.chat.append((who, random.choice(lines)))
            if len(self.chat) > 6:
                self.chat.pop(0)

    def trigger(self, action_id):
        names = {a[1]: a[0] for a in self.ACTIONS}
        name = names.get(action_id, action_id)
        self.log.append(f"[ABUSE] {name} activated")
        if len(self.log) > 30:
            self.log.pop(0)
        self.effects[action_id] = 5.0
        who = "RHYS" if random.random() > 0.5 else "WILLOW"
        lines = self.RHYS_LINES if who == "RHYS" else self.WILLOW_LINES
        self.chat.append((who, random.choice(lines)))
        if len(self.chat) > 6:
            self.chat.pop(0)
        return name

    def draw(self, screen, font, small_font):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        pw, ph = 760, 540
        rect = pygame.Rect(WIDTH // 2 - pw // 2, HEIGHT // 2 - ph // 2, pw, ph)
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((12, 5, 5, 250))
        screen.blit(bg, rect.topleft)
        flicker = int(abs(math.sin(self.time * 6)) * 60 + 195)
        pygame.draw.rect(screen, (flicker, 60, 60), rect, 3, border_radius=14)

        cx = rect.centerx
        y = rect.y + 14

        # Title
        tf = pygame.font.Font(None, 34)
        blink = int(abs(math.sin(self.time * 4)) * 100 + 155)
        title = tf.render("!  ADMIN ABUSE CONSOLE  !", True, (blink, 60, 60))
        screen.blit(title, (cx - title.get_width() // 2, y))
        y += 38

        sub_f = pygame.font.Font(None, 18)
        sub = sub_f.render("CHAPTER 1 : SEASON 1 - RHYS & WILLOW HAVE FULL CONTROL", True, (255, 155, 155))
        screen.blit(sub, (cx - sub.get_width() // 2, y))
        y += 26

        # Log panel
        log_h = 140
        log_rect = pygame.Rect(rect.x + 16, y, pw - 32, log_h)
        log_bg = pygame.Surface((log_rect.w, log_h), pygame.SRCALPHA)
        log_bg.fill((0, 0, 0, 220))
        screen.blit(log_bg, log_rect.topleft)
        pygame.draw.rect(screen, (65, 20, 20), log_rect, 1, border_radius=6)

        lf = pygame.font.Font(None, 17)
        visible = self.log[-8:]
        ly = log_rect.y + 6
        for line in visible:
            color = (126, 211, 33) if "[OK" in line or "[AUTH]" in line else \
                    (255, 215, 0) if "[SYS]" in line else (255, 128, 128)
            ls = lf.render(line[:78], True, color)
            screen.blit(ls, (log_rect.x + 8, ly))
            ly += 17
        y += log_h + 12

        # Buttons grid — 4 cols
        cols = 4
        bw, bh = (pw - 50) // cols, 38
        gap = 8
        for i, (label, aid) in enumerate(self.ACTIONS):
            row, col = divmod(i, cols)
            bx = rect.x + 16 + col * (bw + gap)
            by = y + row * (bh + gap)
            active = aid in self.effects
            bcol = (255, 60, 60) if active else (42, 10, 10)
            bfill = (80, 15, 15) if not active else (140, 40, 40)
            brect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(screen, bfill, brect, border_radius=6)
            pygame.draw.rect(screen, bcol, brect, 2, border_radius=6)
            bf = pygame.font.Font(None, 18)
            # wrap long labels
            txt = label[:16]
            bs = bf.render(txt, True, (255, 120, 120) if not active else (255, 220, 220))
            screen.blit(bs, (brect.centerx - bs.get_width() // 2, brect.centery - bs.get_height() // 2))
        y += ((len(self.ACTIONS) + cols - 1) // cols) * (bh + gap) + 8

        # Rhys & Willow chat strip
        chat_y = rect.bottom - 70
        cf = pygame.font.Font(None, 17)
        for i, (who, msg) in enumerate(self.chat[-3:]):
            color = (109, 168, 255) if who == "RHYS" else (208, 128, 255)
            cs = cf.render(f"{who}: {msg[:70]}", True, color)
            screen.blit(cs, (rect.x + 20, chat_y + i * 18))

        hint = pygame.font.Font(None, 16).render("Press F9 to toggle | Click buttons or press 1-9", True, (120, 80, 80))
        screen.blit(hint, (cx - hint.get_width() // 2, rect.bottom - 18))
