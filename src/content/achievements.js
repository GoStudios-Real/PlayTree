// PlayTree achievements (original).

export const ACHIEVEMENTS = [
  { id: 'first_steps', name: 'First Steps', desc: 'Move 1,000 blocks.', icon: 'step', stat: 'distance', threshold: 1000, xp: 50 },
  { id: 'first_mine', name: 'Grove Digger', desc: 'Mine your first block.', stat: 'blocksMined', threshold: 1, xp: 20 },
  { id: 'miner', name: 'Miner of the Deep', desc: 'Mine 500 blocks.', stat: 'blocksMined', threshold: 500, xp: 100 },
  { id: 'builder', name: 'Sprout Architect', desc: 'Place 100 blocks.', stat: 'blocksPlaced', threshold: 100, xp: 80 },
  { id: 'crafter', name: 'Maker of Things', desc: 'Craft 50 items.', stat: 'itemsCrafted', threshold: 50, xp: 60 },
  { id: 'hunter', name: 'Creature Vanquisher', desc: 'Defeat 50 enemies.', stat: 'enemiesKilled', threshold: 50, xp: 120 },
  { id: 'boss_slayer', name: 'Bane of Bosses', desc: 'Defeat a boss.', stat: 'bossesKilled', threshold: 1, xp: 300 },
  { id: 'level_10', name: 'Seasoned Sprout', desc: 'Reach level 10.', stat: 'level', threshold: 10, xp: 150 },
  { id: 'level_25', name: 'Grove Guardian', desc: 'Reach level 25.', stat: 'level', threshold: 25, xp: 400 },
  { id: 'quest_10', name: 'Helper of the Grove', desc: 'Complete 10 quests.', stat: 'questsCompleted', threshold: 10, xp: 200 },
  { id: 'quest_master', name: 'Champion of the Grove', desc: 'Complete 25 quests.', stat: 'questsCompleted', threshold: 25, xp: 500 },
  { id: 'survivor', name: 'Night Survivor', desc: 'Survive a full night.', stat: 'nightsSurvived', threshold: 1, xp: 80 },
  { id: 'br_win', name: 'Last Grove Standing', desc: 'Win a Battle Royale match.', stat: 'brWins', threshold: 1, xp: 500 },
  { id: 'br_kills', name: 'Storm Chaser', desc: 'Get 10 eliminations in Battle Royale.', stat: 'brKills', threshold: 10, xp: 200 },
  { id: 'fisher', name: 'Harvest Bloom', desc: 'Harvest 25 crops.', stat: 'cropsHarvested', threshold: 25, xp: 80 },
  { id: 'story', name: 'Heartbinder', desc: 'Complete the Chapter I story.', stat: 'chapterComplete', threshold: 1, xp: 1000 },
  { id: 'collector', name: 'Collector of Wonders', desc: 'Obtain 40 unique items.', stat: 'uniqueItems', threshold: 40, xp: 150 },
  { id: 'explorer', name: 'World Wanderer', desc: 'Explore 5 distinct regions.', stat: 'regions', threshold: 5, xp: 100 },
  { id: 'glider', name: 'Sky Bound', desc: 'Glide 1,000 blocks in total.', stat: 'glideDistance', threshold: 1000, xp: 100 },
  { id: 'emoter', name: 'Expressive Sprout', desc: 'Use 5 different emotes.', stat: 'emotes', threshold: 5, xp: 30 },
];

export default ACHIEVEMENTS;