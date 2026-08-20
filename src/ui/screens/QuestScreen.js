// Quest screen: active story + side quests with progress, and completed list.

import { el, button, clearChildren } from '../../core/UI.js';
import { QUESTS } from '../../content/quests.js';

export class QuestScreen {
  constructor(ui) {
    this.ui = ui;
    this.el = el('div', { class: 'screen hidden' });
    this._build();
  }

  _build() {
    const r = this.el;
    const wrap = el('div', { class: 'screen-wrap', style: { maxWidth: '680px' } });
    wrap.append(el('h1', {}, 'Quests'));
    this.activeList = el('div', { class: 'quest-list' });
    this.completedList = el('div', { class: 'quest-list' });
    wrap.append(this.activeList, el('h2', { class: 'mt8' }, 'Completed'), this.completedList);
    wrap.append(el('div', { class: 'row mt8' }, button('Close', () => this.ui.toggleQuests(), 'ghost')));
    r.append(wrap);
  }

  show() { this.refresh(); }

  refresh() {
    const g = this.ui.game;
    if (!g?.quests) return;
    clearChildren(this.activeList);
    clearChildren(this.completedList);

    const active = g.quests.activeDefs();
    const unlocked = QUESTS.filter(q => g.quests.isUnlocked(q.id));
    const available = unlocked.filter(q => !active.find(a => a.id === q.id) && !g.quests.completed.includes(q.id));

    if (active.length) {
      for (const q of active) this._card(this.activeList, q, 'active');
    }
    if (available.length) {
      for (const q of available) {
        const card = el('div', { class: 'quest-card' });
        card.append(el('div', { class: 'quest-title' }, q.title));
        card.append(el('div', { class: 'muted small' }, q.desc));
        card.append(el('div', { class: 'row mt8' }, button('Start', () => { g.quests.startQuest(q.id); this.refresh(); }, 'small primary')));
        this.activeList.append(card);
      }
    }
    if (!active.length && !available.length) {
      this.activeList.append(el('div', { class: 'muted' }, 'No active quests. Talk to NPCs in the grove.'));
    }

    const done = QUESTS.filter(q => g.quests.completed.includes(q.id));
    if (done.length) {
      for (const q of done) {
        this.completedList.append(el('div', { class: 'quest-card done' }, `✓ ${q.title}`));
      }
    } else {
      this.completedList.append(el('div', { class: 'muted' }, 'Nothing completed yet.'));
    }
  }

  _card(parent, q, kind) {
    const card = el('div', { class: 'quest-card' });
    card.append(el('div', { class: 'quest-title' }, q.title));
    card.append(el('div', { class: 'muted small' }, q.desc));
    for (let i = 0; i < q.objectives.length; i++) {
      const o = q.objectives[i];
      const cur = q.progress ? q.progress[i] : 0;
      card.append(el('div', { class: `qt-goal${cur >= o.count ? ' done' : ''}` }, `• ${o.desc || o.target} (${cur}/${o.count})`));
    }
    if (q.rewards) {
      card.append(el('div', { class: 'muted small' }, `Rewards: ${q.rewards.xp ? q.rewards.xp + ' XP' : ''} ${q.rewards.seasonXp ? q.rewards.seasonXp + ' Season XP' : ''} ${q.rewards.coins ? q.rewards.coins + ' coins' : ''}`));
    }
    parent.append(card);
  }
}

export default QuestScreen;