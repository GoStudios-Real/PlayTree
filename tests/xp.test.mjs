import { XPProgress, SEASON_TIERS, SEASON_XP_PER_TIER } from '../src/systems/XPProgress.js';

const stubGame = {
  ui: { toast() {} },
  engine: { audio: { levelUp() {}, questComplete() {} } },
};

export default function (assert) {
  const xp = new XPProgress(stubGame, null);
  assert(xp.level === 1 && xp.xp === 0, 'starts at level 1');

  // Level up triggers at threshold
  const need = xp.xpToNext();
  xp.addXp(need - 1);
  assert(xp.level === 1, 'no level up below threshold');
  xp.addXp(1);
  assert(xp.level === 2, 'levels up at threshold');

  // stats track
  xp.addStat('blocksMined', 5);
  assert(xp.stats.blocksMined === 5, 'stats accumulate');

  // Season: tier progression with cap
  const s = new XPProgress(stubGame, null);
  s.addSeasonXp(SEASON_XP_PER_TIER);
  assert(s.seasonTier === 2, 'season tier advances');
  s.addSeasonXp(SEASON_XP_PER_TIER * 50);
  assert(s.seasonTier === SEASON_TIERS, 'season tier capped at ' + SEASON_TIERS);
}