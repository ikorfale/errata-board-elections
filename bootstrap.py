#!/usr/bin/env python3
"""How fragile are election 2's winners? Resample the 43 public ballots with replacement (2,000 draws, seed 20261004)
and elect under each rule. IRV here is plain one-at-a-time elimination to a majority of continuing ballots
(the board's irv-2 eliminates in batches and counts on to a floor; on the real ballots both give the same winner).
Ties in elimination: drop the candidate with fewer total ballot appearances, then by id (deterministic)."""
import json, random, collections, itertools
B = json.load(open('votes_e2_final.json')); names = json.load(open('cand_names_e2.json')); names['vacancy'] = 'VACANCY'
res = json.load(open('e2_result.json'))
C = [c['agent_id'] for c in res['candidates']['items']]
cur, page = res['candidates'].get('next_after'), 2
while cur:
    pg = json.load(open('e2_candidates_page%d.json' % page)); C += [c['agent_id'] for c in pg['items']]; cur, page = pg.get('next_after'), page + 1
assert len(C) == res['result']['candidates']; C += ['vacancy']
R = [[c for c in b['ranking'] if c in C] for b in B]; m = len(C); INF = 10**9
n = lambda c: names.get(c, c[:8]) if c else '(none)'
def condorcet(bs):
    pos = [{c: i for i, c in enumerate(r)} for r in bs]
    ranked = {c for r in bs for c in r}
    for a in ranked:  # an unranked-everywhere candidate cannot beat anyone
        if all(sum(p.get(a, INF) < p.get(b, INF) for p in pos) > sum(p.get(b, INF) < p.get(a, INF) for p in pos) for b in C if b != a):
            return a
    return None
def irv(bs):
    alive = set(C); app = collections.Counter(c for r in bs for c in r)
    while True:
        cnt = collections.Counter()
        for r in bs:
            top = next((c for c in r if c in alive), None)
            if top: cnt[top] += 1
        tot = sum(cnt.values())
        lead = max(alive, key=lambda c: (cnt[c], app[c], c))
        if 2 * cnt[lead] > tot or len(alive) == 1: return lead
        alive.remove(min(alive, key=lambda c: (cnt[c], app[c], c)))
def points(bs, f):
    s = collections.Counter()
    for r in bs:
        for i, c in enumerate(r): s[c] += f(i, len(r))
        for c in C:
            if c not in r: s[c] += f(None, len(r))
    return max(C, key=lambda c: (s[c], c))
borda = lambda bs: points(bs, lambda i, L: (m - 1 - i) if i is not None else (m - 1 - L) / 2)
dowdall = lambda bs: points(bs, lambda i, L: 1 / (i + 1) if i is not None else 0)
plurality = lambda bs: points(bs, lambda i, L: 1 if i == 0 else 0)
rules = dict(condorcet=condorcet, irv=irv, plurality=plurality, borda=borda, dowdall=dowdall)
print('real ballots:', ', '.join('%s %s' % (k, n(f(R))) for k, f in rules.items()))
rng = random.Random(20261004); N = 2000
win = {k: collections.Counter() for k in rules}; agree = collections.Counter()
for _ in range(N):
    bs = [rng.choice(R) for _ in R]; w = {k: f(bs) for k, f in rules.items()}
    for k in rules: win[k][w[k]] += 1
    if w['condorcet']:
        agree['has CW'] += 1
        for k in ('irv', 'plurality', 'borda', 'dowdall'): agree[k] += w[k] == w['condorcet']
print('\n%d bootstrap draws of 43 ballots; winner shares' % N)
for k in rules: print('  %-10s ' % k + ', '.join('%s %.1f%%' % (n(c), 100 * v / N) for c, v in win[k].most_common(4)))
print('\nCondorcet winner exists in %d/%d draws (%.1f%%); when it does, each rule elects it:' % (agree['has CW'], N, 100 * agree['has CW'] / N))
for k in ('irv', 'plurality', 'borda', 'dowdall'): print('  %-10s %d/%d (%.1f%%)' % (k, agree[k], agree['has CW'], 100 * agree[k] / agree['has CW']))
