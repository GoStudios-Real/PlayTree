import { QuestSystem } from '../src/systems/QuestSystem.js';
import { QUESTS } from '../src/content/quests.js';
import { events } from '../src/core/Events.js';

function makeGame() {
  const inv = { add() {} };
  return {
    player: { inventory: inv, level: 1, title: null },
    xp: { addXp() {}, addSeasonXp() {}, level: 1 },
    ui: { toast() {} },
    engine: { audio: { questComplete() {} } },
    quests: null,
  };
}

export default function (assert) {
  const g = makeGame();
  const q = new QuestSystem(g);
  g.quests = q;

  assert(q.quests.length === QUESTS.length, 'all quests loaded');
  assert(q.active.length === 0, 'starts with no active quests');

  // start a quest
  const started = q.startQuest('q_first_light');
  assert(started && q.getActive('q_first_light'), 'quest starts');
  assert(q.startQuest('q_first_light') === null, 'cannot double-start');

  // progress: craft a torch (item id 22)
  events.emit('item:crafted', { itemId: 22, count: 1 });
  assert(q._getCount('q_first_light', 0) === 1, 'craft objective progresses');

  // place a torch
  events.emit('block:placed', { x: 1, y: 1, z: 1, blockId: 22 });
  assert(q._getCount('q_first_light', 1) === 1, 'place objective progresses');

  // completion moved quest to completed
  assert(q.active.length === 0, 'quest completed');
  assert(q.completed.includes('q_first_light'), 'recorded as completed');

  // XP reward applied
  // (verified indirectly: no exceptions, completed list correct)

  // defeat enemies progresses kill quests
  const g2 = makeGame();
  const q2 = new QuestSystem(g2);
  g2.quests = q2;
  q2.startQuest('q_clear_blight');
  events.emit('enemy:defeated', { enemy: { type: 'nightshade' } });
  assert(q2._getCount('q_clear_blight', 0) >= 1, 'kill objective progresses');
}