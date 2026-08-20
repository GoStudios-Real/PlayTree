# PlayTree — Seasons

PlayTree releases content in chapters and seasons. The current release is
**Chapter I: Season I — "The Sprouting"**.

## Metadata

- `CONFIG.season` = `'I'`, `CONFIG.seasonName` = `'The Sprouting'`,
  `CONFIG.title` = `'Chapter I: Season I'`.
- The main menu and adventure intro both brand the world as "The Heartwood Grove".

## Progression — `src/systems/XPProgress.js`

Two parallel tracks:

1. **XP / Level** — earned from kills, quests, crafting, wins, achievements. Levels
   gate achievements (e.g. `level_10` → "Seasoned Sprout").
2. **Season XP / Tier** — a seasonal battle-pass track:
   - `SEASON_TIERS` = 10 tiers, `SEASON_XP_PER_TIER` = 500 XP.
   - `addSeasonXp(amount)` advances tiers, emits `season:xp` and `season:tier`
     events, and toasts the cosmetic reward.
   - `SEASON_REWARDS` holds one cosmetic per tier.

## Sources of season XP

- Killing enemies (`Enemy` → `awardKill`), defeating bosses.
- Completing quests (`QuestSystem` rewards include `seasonXp`).
- Winning battle royale matches / mini-games (Canopy Dash, BoomBarrel Brawl,
  Capture the Sprout all grant season XP).
- Seasonal events (see `SEASON_EVENTS` in `src/content/quests.js`).

## UI

- **Season Pass tab** in the Store screen (`StoreScreens._renderSeason`) renders the
  tier track with locked/unlocked cells and the current tier/XP readout.
- Season pass progress persists via the XP progress save (`save`/`load`).

## Adding a new season

1. Bump `CONFIG.season` / `CONFIG.seasonName` / `CONFIG.title`.
2. Replace `SEASON_REWARDS` with the new cosmetic track.
3. Add new `SEASON_EVENTS` and quests in `src/content/quests.js`.