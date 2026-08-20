// Chapter I world landmarks used by adventure story, quests and secrets.
// These are original PlayTree locations (not copied from any game).

export const structuresPositions = {
  // Grove Town (village center at world origin)
  groveTown: { x: 0, z: 0 },

  // Heartstone shrine is part of town
  shrine: { x: 0, z: -14 },

  // Secret cave entrance west of town under the Cragspine foothills
  heartstoneCave: { x: -96, z: 44 },

  // Titan boss arena — deep cavern beneath the Cragspine
  titanArena: { x: -92, z: 42 },

  // Dune oasis in the southwest desert
  duneOasis: { x: 190, z: 150 },

  // Ember Queen's lair — desert ruin to the far west
  queenLair: { x: -210, z: -40 },

  // Fennwisp swamp hollow
  swampHollow: { x: 60, z: -120 },

  // Hidden glowcap grotto
  glowcapGrotto: { x: -60, z: -90 },

  // Moonowl roost in the high crags
  roost: { x: 140, z: -40 },
};

export const REGION_INFO = {
  heartstoneCave: { name: 'The Sleeping Heart', desc: 'A hidden cavern beneath the Cragspine.' },
  duneOasis: { name: 'Dune Oasis', desc: 'A shimmering pool in the Sandsprout Wastes.' },
  queenLair: { name: 'The Ember Throne', desc: 'Scorched stone. The Ember Queen rules here.' },
  swampHollow: { name: 'Fennwisp Hollow', desc: 'Green mist hangs between the trees.' },
  glowcapGrotto: { name: 'Glowcap Grotto', desc: 'A cave lit by a thousand soft lanterns.' },
  roost: { name: 'Moonowl Roost', desc: 'The highest reachable ledge.' },
};

export const STORY = {
  title: 'The Sprouting',
  chapter: 'Chapter I: Season I',
  prologue:
    'When the Heartstone slept, the Withering crept through every root.\n' +
    'But a new sprout has taken root in Grove Town — and the grove remembers.\n' +
    'Chapter I: Season I begins.',
  ending:
    'The Heartstone glows once more. The Withering retreats.\n' +
    'But the grove whispers of older storms, and other lands...\n' +
    'Chapter II awaits.',
};

export default structuresPositions;