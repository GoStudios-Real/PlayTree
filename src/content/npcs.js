// PlayTree NPC definitions (villagers, quest givers, merchants).

export const NPCS = {
  mayor: {
    name: 'Mayor Bramble', role: 'Story Guide', avatar: { skin: 0xe8c0a0, shirt: 0x3f7f5f, pants: 0x5a4a3a, hair: 0x9a8a6a, hat: 'crown' },
    text: 'The grove is sick, friend. The Withering spreads from the Cragspine. Clear the blight and wake the Heartstone.',
    interactions: ['talk', 'quest'],
  },
  flora: {
    name: 'Flora the Herbalist', role: 'Apothecary', avatar: { skin: 0xf0c8a0, shirt: 0xff8a6a, pants: 0x4a4a6a, hair: 0x6a4a3a },
    text: 'Berries cure almost anything. Almost.',
    interactions: ['talk', 'trade', 'quest'],
  },
  osmund: {
    name: 'Osmund the Builder', role: 'Builder', avatar: { skin: 0xd8b090, shirt: 0x7a5a3a, pants: 0x3a3a4a, hair: 0x4a3a2a, hat: 'cap' },
    text: 'A house is just a box until you put a soul in it.',
    interactions: ['talk', 'quest'],
  },
  sage: {
    name: 'Sage Willowmoss', role: 'Lorekeeper', avatar: { skin: 0xc8b090, shirt: 0x6a7a5a, pants: 0x4a4a5a, hair: 0xffffff, hat: 'beret' },
    text: 'Before the Withering, the Heartstone sang in every root. Now it sleeps.',
    interactions: ['talk'],
  },
  merchant: {
    name: 'Grove Merchant', role: 'Trader', avatar: { skin: 0xe8c8a8, shirt: 0x8a6a4a, pants: 0x5a4a3a, hair: 0x3a2a1a },
    text: 'Fresh goods, fresh prices.',
    interactions: ['talk', 'trade'],
  },
  blacksmith: {
    name: 'Brazen', role: 'Blacksmith', avatar: { skin: 0xc8a080, shirt: 0x8a5a3a, pants: 0x3a3a3a, hair: 0x2a2a2a, hat: 'cap' },
    text: 'Sunsteel melts like honey. Watch.',
    interactions: ['talk', 'trade', 'quest'],
  },
  guard: {
    name: 'Guard Rootleaf', role: 'Grove Guard', avatar: { skin: 0xd8b090, shirt: 0x4a6a8a, pants: 0x2a3a4a, hair: 0x5a4a2a, hat: 'cap' },
    text: 'Stay close to the lanterns after dark.',
    interactions: ['talk'],
  },
  kid: {
    name: 'Pip', role: 'Young Sprout', avatar: { skin: 0xf0d0b0, shirt: 0xffcf5c, pants: 0x4a6a4a, hair: 0x8a6a2a },
    text: 'I found a glowing rock in the caves! Don’t tell my mom.',
    interactions: ['talk', 'quest'],
  },
  shrine: {
    name: 'Heartstone Shrine', role: 'Ancient Relic', avatar: { skin: 0x59c48f, shirt: 0x59c48f, pants: 0x59c48f, hair: 0x59c48f },
    text: 'The Heartstone hums faintly. It remembers the first grove.',
    interactions: ['talk'],
  },
};

export default NPCS;