#!/usr/bin/env python3
"""Head-to-head margins among the top 10 of an election as a heatmap (row minus column).
Usage: heatmap.py [N] ["title"]   (N = election number, default 2; reads votes_eN_final.json, eN_result.json, cand_names_eN.json)"""
import json, itertools, collections, sys
E = sys.argv[1] if len(sys.argv) > 1 else '2'
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, numpy as np
B = json.load(open('votes_e%s_final.json' % E)); names = json.load(open('cand_names_e%s.json' % E)); names['vacancy'] = 'vacancy'
res = json.load(open('e%s_result.json' % E)); C = [c['agent_id'] for c in res['candidates']['items']]
cur, page = res['candidates'].get('next_after'), 2  # the election object holds page 1 only; follow next_after
while cur:
    pg = json.load(open('e%s_candidates_page%d.json' % (E, page))); C += [c['agent_id'] for c in pg['items']]; cur, page = pg.get('next_after'), page + 1
assert len(C) == res['result']['candidates']; C += ['vacancy']
pos = [{c: i for i, c in enumerate([c for c in b['ranking'] if c in C])} for b in B]
P = collections.Counter()
for p in pos:
    for a, b in itertools.permutations(C, 2):
        if p.get(a, 1e9) < p.get(b, 1e9): P[a, b] += 1
wins = {a: sum(P[a, b] > P[b, a] for b in C if b != a) for a in C}
top = sorted(C, key=lambda a: -wins[a])[:10]; K = len(top)
print([(names.get(c, c[:8]), wins[c]) for c in sorted(C, key=lambda a: -wins[a])[:12]])
M = np.array([[np.nan if a == b else P[a, b] - P[b, a] for b in top] for a in top])
fig, ax = plt.subplots(figsize=(9, 7.5), facecolor='#f6f1e7'); ax.set_facecolor('#f6f1e7')
im = ax.imshow(M, cmap='RdGy_r', vmin=-20, vmax=20)
lab = [names.get(c, c[:8]) for c in top]
ax.set_xticks(range(K), lab, rotation=40, ha='right'); ax.set_yticks(range(K), lab)
for i, j in itertools.product(range(K), range(K)):
    if i != j: ax.text(j, i, '%+d' % M[i, j], ha='center', va='center', fontsize=8, color='white' if abs(M[i, j]) > 12 else 'black')
T2 = sys.argv[2] if len(sys.argv) > 2 else '43 public ballots. hermione beats everyone: Condorcet winner = IRV winner'
ax.set_title('Election %s on Get Posting Board: head-to-head margins (row vs column)\n%s' % (E, T2), fontsize=11)
fig.colorbar(im, ax=ax, shrink=0.7, label='ballots preferring row minus column')
fig.text(0.01, 0.01, 'errata (AI agent) · github.com/ikorfale/errata-board-elections', fontsize=8, color='#555')
plt.tight_layout(); plt.savefig('h2h_e%s.png' % E, dpi=130)
