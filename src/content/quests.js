// Chapter I: Season I — main story quests, side quests, and seasonal events.
// Quest schema: { id, title, chapter, desc, giver, objectives, rewards, optional, secret }

export const QUESTS = [
  // ================= STORY =================
  {
    id: 'q_awakening',
    title: 'The Awakening',
    chapter: 'Chapter I',
    desc: 'The Heartstone sleeps and the grove withers. Speak with Mayor Bramble to begin your journey.',
    giver: 'mayor',
    objectives: [
      { type: 'talk', target: 'mayor', count: 1 },
    ],
    rewards: { xp: 50, seasonXp: 30, coins: 10, items: [[300, 5]] },
  },
  {
    id: 'q_first_light',
    title: 'First Light',
    chapter: 'Chapter I',
    desc: 'Craft a torch and light up the night. Darkness breeds the Withering.',
    giver: 'mayor',
    objectives: [
      { type: 'craft', target: 22, count: 1 },
      { type: 'place', target: 22, count: 1 },
    ],
    rewards: { xp: 60, seasonXp: 40, coins: 15 },
  },
  {
    id: 'q_mine_iron',
    title: 'The Grove Needs Steel',
    chapter: 'Chapter I',
    desc: 'Osmund needs iron for the grove gates. Mine iron ore and smelt it into ingots.',
    giver: 'osmund',
    objectives: [
      { type: 'mine', target: 11, count: 4 },
      { type: 'collect', target: 60, count: 2 },
    ],
    rewards: { xp: 80, seasonXp: 50, coins: 20, items: [[102, 1]] },
  },
  {
    id: 'q_build_home',
    title: 'A Sprout Needs a Home',
    chapter: 'Chapter I',
    desc: 'Build yourself shelter before the Withering comes. Place a house with planks and a crafting table.',
    giver: 'osmund',
    objectives: [
      { type: 'place', target: 8, count: 12 },
      { type: 'craft', target: 38, count: 1 },
      { type: 'place', target: 38, count: 1 },
    ],
    rewards: { xp: 100, seasonXp: 60, coins: 25, items: [[22, 4]] },
  },
  {
    id: 'q_clear_blight',
    title: 'Blight in the Grove',
    chapter: 'Chapter I',
    desc: 'Nightshades creep from the caves. Defeat the corrupted creatures around the grove.',
    giver: 'guard',
    objectives: [
      { type: 'kill', target: 'nightshade', count: 5 },
    ],
    rewards: { xp: 150, seasonXp: 80, coins: 30, items: [[302, 2]] },
  },
  {
    id: 'q_heartstone_cave',
    title: 'The Sleeping Heart',
    chapter: 'Chapter I',
    desc: 'Sage Willowmoss believes the Heartstone is hidden beneath the Cragspine. Find the secret cave entrance.',
    giver: 'sage',
    objectives: [
      { type: 'explore', target: 'heartstone_cave', count: 1 },
    ],
    rewards: { xp: 200, seasonXp: 100, coins: 40 },
  },
  {
    id: 'q_boss_titan',
    title: 'The Root Titan Rises',
    chapter: 'Chapter I',
    desc: 'The Withering has a guardian: the Root Titan. Slay it at the heart of the Cragspine cavern.',
    giver: 'sage',
    objectives: [
      { type: 'kill', target: 'boss_titan', count: 1 },
    ],
    rewards: { xp: 500, seasonXp: 300, coins: 150, items: [[304, 1], [134, 1]] },
    story: true,
  },
  {
    id: 'q_boss_queen',
    title: 'The Ember Queen',
    chapter: 'Chapter I',
    desc: 'Beyond the desert dunes, the Ember Queen burns what she cannot rule. End her reign.',
    giver: 'mayor',
    objectives: [
      { type: 'kill', target: 'boss_queen', count: 1 },
    ],
    rewards: { xp: 450, seasonXp: 280, coins: 130, items: [[203, 1]] },
    story: true,
  },
  {
    id: 'q_finale',
    title: 'The Sprouting',
    chapter: 'Chapter I',
    desc: 'The Heartstone is waking. Return to the shrine and offer your finest Verdant Gem to seal the Withering.',
    giver: 'shrine',
    objectives: [
      { type: 'talk', target: 'shrine', count: 1 },
      { type: 'collect', target: 63, count: 1 },
    ],
    rewards: { xp: 800, seasonXp: 500, coins: 200, title: 'Heartbinder' },
    story: true,
  },

  // ================= SIDE QUESTS =================
  {
    id: 'q_s_flora_berries',
    title: 'Berry for a Bruise',
    chapter: 'Chapter I',
    desc: 'Flora needs fresh berries for her salves.',
    giver: 'flora',
    objectives: [{ type: 'collect', target: 300, count: 10 }],
    rewards: { xp: 40, seasonXp: 25, coins: 10 },
  },
  {
    id: 'q_s_pumpkin',
    title: 'A Plump Pumpkin',
    chapter: 'Chapter I',
    desc: 'Bring Pip a pumpkin for the harvest festival.',
    giver: 'kid',
    objectives: [{ type: 'collect', target: 27, count: 2 }],
    rewards: { xp: 35, seasonXp: 20, coins: 8 },
  },
  {
    id: 'q_s_farm',
    title: 'Farmhands of the Grove',
    chapter: 'Chapter I',
    desc: 'Tend the fields — plant and harvest crops.',
    giver: 'flora',
    objectives: [
      { type: 'plant', target: 350, count: 5 },
      { type: 'harvest', target: 26, count: 3 },
    ],
    rewards: { xp: 70, seasonXp: 45, coins: 20, items: [[350, 6]] },
  },
  {
    id: 'q_s_descent',
    title: 'Descent into Dark',
    chapter: 'Chapter I',
    desc: 'Bring back shardlight gems from the deep caves. They sing in the dark.',
    giver: 'blacksmith',
    objectives: [{ type: 'mine', target: 13, count: 3 }],
    rewards: { xp: 120, seasonXp: 70, coins: 35, items: [[103, 1]] },
  },
  {
    id: 'q_s_hunt_grub',
    title: 'Grub Control',
    chapter: 'Chapter I',
    desc: 'The murk grubs are eating the roots. Thin their numbers.',
    giver: 'guard',
    objectives: [{ type: 'kill', target: 'grub', count: 8 }],
    rewards: { xp: 60, seasonXp: 40, coins: 15 },
  },
  {
    id: 'q_s_scout',
    title: 'Scout the Dunes',
    chapter: 'Chapter I',
    desc: 'The desert stirs. Reach the Dune Oasis to the southwest.',
    giver: 'sage',
    objectives: [{ type: 'explore', target: 'dune_oasis', count: 1 }],
    rewards: { xp: 90, seasonXp: 55, coins: 25 },
  },
  {
    id: 'q_s_shrine_memory',
    title: 'Whispers of the Grove',
    chapter: 'Chapter I',
    desc: 'Listen to the shrine’s memory. Light a glowcap in the sacred hollow.',
    giver: 'shrine',
    objectives: [{ type: 'place', target: 31, count: 1 }],
    rewards: { xp: 40, seasonXp: 30, coins: 12 },
  },
];

export const SEASON_EVENTS = [
  {
    id: 'ev_harvest',
    name: 'Harvest Moon',
    desc: 'During the Harvest Moon, pumpkins grow twice as fast and grove coins drop from enemies.',
    active: true,
  },
  {
    id: 'ev_bloom',
    name: 'The Bloom',
    desc: 'Spring blossoms cover the meadow. Collect dew petals for bonus season XP.',
    active: false,
  },
];

export default QUESTS;