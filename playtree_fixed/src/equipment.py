import pygame
from config import ARMOR_TYPES, WIDTH, HEIGHT, GOLD, GREEN_GLOW


class EquipmentSystem:
    def __init__(self, player):
        self.player = player
        self.slots = {"head": None, "chest": None, "legs": None, "boots": None}
        self.bonus_hp = 0
        self.bonus_speed = 0

    def equip(self, armor_id):
        armor = ARMOR_TYPES.get(armor_id)
        if not armor:
            return False
        slot = armor["slot"]
        self.unequip(slot)
        self.slots[slot] = armor_id
        self._recalc()
        return True

    def unequip(self, slot):
        if self.slots[slot]:
            self.player.inventory.setdefault("armor", []).append(self.slots[slot])
            self.slots[slot] = None
            self._recalc()

    def _recalc(self):
        self.bonus_hp = 0
        self.bonus_speed = 0
        for slot, aid in self.slots.items():
            if aid and aid in ARMOR_TYPES:
                a = ARMOR_TYPES[aid]
                self.bonus_hp += a.get("hp_bonus", 0)
                self.bonus_speed += a.get("speed_bonus", 0)

    def get_total_defense(self):
        total = 0
        for slot, aid in self.slots.items():
            if aid and aid in ARMOR_TYPES:
                total += ARMOR_TYPES[aid]["defense"]
        return total

    def get_max_hp_bonus(self):
        return self.bonus_hp

    def get_speed_bonus(self):
        return self.bonus_speed

    def draw_inventory(self, surface, font, small_font):
        sx, sy = 200, 100
        slot_labels = {"head": "Helmet", "chest": "Chestplate", "legs": "Leggings", "boots": "Boots"}
        y = sy
        for slot, aid in self.slots.items():
            label = small_font.render(slot_labels.get(slot, slot), True, (150, 170, 150))
            surface.blit(label, (sx, y))
            if aid and aid in ARMOR_TYPES:
                a = ARMOR_TYPES[aid]
                nm = small_font.render(a["name"], True, GREEN_GLOW)
                surface.blit(nm, (sx + 120, y))
                df = small_font.render(f"DEF +{a['defense']}", True, (180, 200, 180))
                surface.blit(df, (sx + 300, y))
            else:
                emp = small_font.render("Empty", True, (80, 80, 80))
                surface.blit(emp, (sx + 120, y))
            y += 32

        total_def = self.get_total_defense()
        td = small_font.render(f"Total Defense: {total_def}", True, GOLD)
        surface.blit(td, (sx, y + 8))
        bh = small_font.render(f"HP Bonus: +{self.bonus_hp}", True, GREEN_GLOW)
        surface.blit(bh, (sx + 250, y + 8))
