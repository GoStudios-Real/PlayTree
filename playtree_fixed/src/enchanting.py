import pygame
import math
from config import ENCHANTMENTS, WIDTH, HEIGHT, GOLD, GREEN_GLOW, PURPLE


class EnchantingSystem:
    def __init__(self, audio=None):
        self.active = False
        self.audio = audio
        self.selected_weapon = None
        self.selected_enchant = None
        self.weapon_list = []
        self.enchant_list = list(ENCHANTMENTS.keys())

    def open(self, player):
        self.active = True
        self.weapon_list = player.inventory.get("weapons", [])
        self.selected_weapon = None
        self.selected_enchant = None

    def close(self):
        self.active = False

    def enchant_weapon(self, player, weapon_id):
        if not self.selected_enchant or not weapon_id:
            return False
        ench = ENCHANTMENTS[self.selected_enchant]
        gold = player.inventory.get("resources", {}).get("Gold Leaves", 0)
        if gold < ench["cost"]:
            return False
        player.inventory["resources"]["Gold Leaves"] = gold - ench["cost"]
        if "enchants" not in player.inventory:
            player.inventory["enchants"] = {}
        existing = player.inventory["enchants"].get(weapon_id, [])
        if len(existing) < 3:
            existing.append(self.selected_enchant)
            player.inventory["enchants"][weapon_id] = existing
        return True

    def handle_event(self, event, player):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            sx, sy = 80, 60
            sw = WIDTH - 160

            wy = sy + 50
            for i, wid in enumerate(self.weapon_list):
                if sx <= mx <= sx + sw and wy <= my <= wy + 36:
                    self.selected_weapon = wid
                    return True
                wy += 40

            ey = sy + 50
            ex = sx + sw // 2 + 20
            ew = sw // 2 - 20
            for eid in self.enchant_list:
                if ex <= mx <= ex + ew and ey <= my <= ey + 36:
                    self.selected_enchant = eid
                    return True
                ey += 40

            buy_x = sx + sw // 2 - 80
            buy_y = sy + 380
            if buy_x <= mx <= buy_x + 160 and buy_y <= my <= buy_y + 40:
                if self.selected_weapon and self.selected_enchant:
                    success = self.enchant_weapon(player, self.selected_weapon)
                    if self.audio:
                        self.audio.play("collect" if success else "menu_confirm")
                    return True
        return False

    def draw(self, surface, player, font, small_font):
        if not self.active:
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        sx, sy = 80, 60
        sw, sh = WIDTH - 160, HEIGHT - 120
        pygame.draw.rect(surface, (15, 15, 25), (sx, sy, sw, sh), border_radius=12)
        pygame.draw.rect(surface, (*PURPLE[:3], 60), (sx, sy, sw, sh), border_radius=12, width=2)

        title = font.render("ENCHANTING TABLE", True, PURPLE)
        surface.blit(title, (sx + 20, sy + 12))

        gold = player.inventory.get("resources", {}).get("Gold Leaves", 0)
        gold_txt = small_font.render(f"Gold: {gold}", True, GOLD)
        surface.blit(gold_txt, (sx + sw - 150, sy + 18))

        from config import WEAPONS
        wy = sy + 50
        lbl = small_font.render("WEAPONS", True, (150, 150, 150))
        surface.blit(lbl, (sx + 20, wy - 18))
        for wid in self.weapon_list:
            wdata = WEAPONS.get(wid, {})
            wname = wdata.get("name", wid)
            selected = self.selected_weapon == wid
            bg = (30, 30, 50) if selected else (20, 20, 25)
            border_c = PURPLE if selected else (40, 40, 60)
            pygame.draw.rect(surface, bg, (sx + 20, wy, sw // 2 - 40, 36), border_radius=4)
            pygame.draw.rect(surface, border_c, (sx + 20, wy, sw // 2 - 40, 36), 1, border_radius=4)
            nm = small_font.render(wname, True, border_c)
            surface.blit(nm, (sx + 30, wy + 8))
            existing = player.inventory.get("enchants", {}).get(wid, [])
            if existing:
                e_txt = small_font.render(f"{len(existing)} enchants", True, (180, 140, 255))
                surface.blit(e_txt, (sx + 200, wy + 10))
            wy += 40

        ey = sy + 50
        ex = sx + sw // 2 + 20
        ew = sw // 2 - 20
        lbl2 = small_font.render("ENCHANTMENTS", True, (150, 150, 150))
        surface.blit(lbl2, (ex, ey - 18))
        for eid in self.enchant_list:
            edata = ENCHANTMENTS[eid]
            selected = self.selected_enchant == eid
            bg = (30, 30, 50) if selected else (20, 20, 25)
            border_c = PURPLE if selected else (40, 40, 60)
            pygame.draw.rect(surface, bg, (ex, ey, ew, 36), border_radius=4)
            pygame.draw.rect(surface, border_c, (ex, ey, ew, 36), 1, border_radius=4)
            nm = small_font.render(edata["name"], True, border_c)
            surface.blit(nm, (ex + 10, ey + 2))
            cost = small_font.render(f"{edata['cost']}g", True, GOLD)
            surface.blit(cost, (ex + ew - 60, ey + 2))
            ds = small_font.render(edata["desc"], True, (120, 120, 120))
            surface.blit(ds, (ex + 10, ey + 18))
            ey += 40

        if self.selected_weapon and self.selected_enchant:
            buy_x = sx + sw // 2 - 80
            buy_y = sy + 380
            ench = ENCHANTMENTS[self.selected_enchant]
            gold_ok = gold >= ench["cost"]
            btn_color = GREEN_GLOW if gold_ok else (80, 80, 80)
            pygame.draw.rect(surface, btn_color, (buy_x, buy_y, 160, 40), border_radius=6)
            btn_txt = font.render("ENCHANT", True, (8, 12, 8))
            surface.blit(btn_txt, (buy_x + 80 - btn_txt.get_width() // 2, buy_y + 8))

        hint = small_font.render("Select weapon + enchant  |  ESC to close", True, (80, 100, 80))
        surface.blit(hint, (sx + 20, sy + sh - 30))
