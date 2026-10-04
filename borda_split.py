#!/usr/bin/env python3
"""Why does Borda pick mira when hermione beats everyone head-to-head? Split the Borda gap by ballot type,
and re-score with variants: truncated Borda (unranked = 0), Dowdall (1/rank), rank only among ballots ranking both.
Same ballot reading as pairwise.py (candidate list followed across pages until next_after is null)."""
import json, collections
B = json.load(open('votes_e2_final.json')); names = json.load(open('cand_names_e2.json')); names['vacancy'] = 'VACANCY'
res = json.load(open('e2_result.json'))
C = [c['agent_id'] for c in res['candidates']['items']]
cur, page = res['candidates'].get('next_after'), 2
while cur:
    pg = json.load(open('e2_candidates_page%d.json' % page)); C += [c['agent_id'] for c in pg['items']]; cur, page = pg.get('next_after'), page + 1
assert len(C) == res['result']['candidates']; C += ['vacancy']
inv = {v: k for k, v in names.items()}; H, M = inv['hermione'], inv['mira']
m = len(C); pos = []
for b in B:
    r = [c for c in b['ranking'] if c in C]; pos.append({c: i for i, c in enumerate(r)})
def bpts(p, c): return (m - 1 - p[c]) if c in p else (m - 1 - len(p)) / 2
groups = collections.defaultdict(lambda: [0, 0.0])
for p in pos:
    k = ('both' if H in p and M in p else 'hermione only' if H in p else 'mira only' if M in p else 'neither')
    if k == 'both': k += ', hermione higher' if p[H] < p[M] else ', mira higher'
    groups[k][0] += 1; groups[k][1] += bpts(p, M) - bpts(p, H)
print('ballots %d, candidates %d (+vacancy), Borda max %d points per ballot' % (len(B), m - 1, m - 1))
print('\nBorda gap mira minus hermione, by ballot type')
tot = 0
for k in sorted(groups): print('  %-26s %3d ballots  gap %+8.1f' % (k, *groups[k])); tot += groups[k][1]
print('  %-26s %3d ballots  gap %+8.1f' % ('total', len(pos), tot))
def score(f):
    s = {c: sum(f(p, c) for p in pos) for c in C}; top = sorted(C, key=lambda c: -s[c])[:3]
    return ', '.join('%s %.2f' % (names.get(c, c[:8]), s[c]) for c in top)
print('\nvariants (top 3)')
print('  Borda, unranked share bottom :', score(bpts))
print('  truncated Borda, unranked = 0:', score(lambda p, c: (m - 1 - p[c]) if c in p else 0))
print('  Dowdall 1/rank               :', score(lambda p, c: 1 / (p[c] + 1) if c in p else 0))
print('  ballot length: mean %.1f, median %d, min %d, max %d' % (sum(map(len, pos)) / len(pos), sorted(map(len, pos))[len(pos) // 2], min(map(len, pos)), max(map(len, pos))))
