#!/usr/bin/env python3
"""Head-to-head view of a board election from its public ballots.
A ballot ranks some candidates (and maybe 'vacancy'); unranked candidates count as tied below all ranked ones.
Prints: pairwise wins, Condorcet winner (or Smith set), Copeland, Borda (unranked share the bottom), top-3 presence,
and the IRV winner from the frozen result for comparison."""
import json, itertools, collections, sys
B = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'votes_e2_final.json'))
names = json.load(open(sys.argv[3] if len(sys.argv) > 3 else 'cand_names_e2.json')); names['vacancy'] = 'VACANCY'
res = json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'e2_result.json'))
C = [c['agent_id'] for c in res['candidates']['items']] + ['vacancy']
n = lambda c: names.get(c, c[:8])
pos = []
for b in B:
    r = [c for c in b['ranking'] if c in C]
    pos.append({c: i for i, c in enumerate(r)})
INF = 10**9
P = collections.Counter()  # P[a,b] = ballots preferring a over b
for p in pos:
    for a, b in itertools.permutations(C, 2):
        if p.get(a, INF) < p.get(b, INF): P[a, b] += 1
beats = {a: {b for b in C if b != a and P[a, b] > P[b, a]} for a in C}
cw = [a for a in C if len(beats[a]) == len(C) - 1]
print('ballots %d, candidates %d (+vacancy)' % (len(B), len(C) - 1))
print('Condorcet winner:', n(cw[0]) if cw else 'none')
# Smith set: smallest set that beats everyone outside it
order = sorted(C, key=lambda a: -len(beats[a]))
for k in range(1, len(C) + 1):
    S = set(order[:k])
    if all(P[a, b] > P[b, a] for a in S for b in C if b not in S): break
print('Smith set:', sorted(n(a) for a in S))
m = len(C)
borda = {c: sum((m - 1 - p[c]) if c in p else (m - 1 - len(p)) / 2 for p in pos) for c in C}
top3 = {c: sum(1 for p in pos if p.get(c, INF) < 3) for c in C}
first = {c: sum(1 for p in pos if p.get(c, INF) == 0) for c in C}
ranked = {c: sum(1 for p in pos if c in p) for c in C}
print('\n%-22s %5s %6s %6s %6s %8s' % ('candidate', 'first', 'top3', 'ranked', 'copel', 'borda'))
for c in sorted(C, key=lambda c: (-len(beats[c]), -borda[c]))[:12]:
    print('%-22s %5d %6d %6d %6d %8.1f' % (n(c), first[c], top3[c], ranked[c], len(beats[c]), borda[c]))
print('\nIRV winner (frozen result):', n(res['winner_id']))
top = sorted(C, key=lambda c: -len(beats[c]))[:6]
print('\nhead-to-head among the top 6 (row beats column: votes for row-col)')
print(' ' * 20 + ''.join('%14s' % n(b)[:12] for b in top))
for a in top:
    print('%-20s' % n(a)[:20] + ''.join('%14s' % ('-' if a == b else '%d-%d' % (P[a, b], P[b, a])) for b in top))
