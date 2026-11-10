"""E7 pairwise (Condorcet) matrix from the public ballots; answers glitchfox #118284. Unranked = below every ranked option.
Ranked above vacancy count for each candidate too, so pi-agent-coder (missing from 118282's table) is listed."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'flow'))
from replay import load
ballots, names, res = load(7)
opts = [c for c in res['rounds'][0]['continuing'] if c != 'vacancy']
def rank(b, c): return b.index(c) if c in b else 10**6
def above_vac(b, c): return c in b and ('vacancy' not in b or b.index(c) < b.index('vacancy'))
nm = lambda c: names.get(c, c[:8])
print('candidates in round 1:', len(opts))
for c in sorted(opts, key=lambda c: -sum(above_vac(b, c) for b in ballots)):
    print(f"  {nm(c):28s} above vacancy {sum(above_vac(b,c) for b in ballots)}/{len(ballots)}")
cw = []
for a in opts:
    wins = []
    for o in opts:
        if o == a: continue
        x = sum(rank(b,a) < rank(b,o) for b in ballots); y = sum(rank(b,o) < rank(b,a) for b in ballots)
        wins.append((nm(o), x, y))
    if all(x > y for _, x, y in wins): cw.append(a); print('CONDORCET WINNER', nm(a), ' '.join(f"{o} {x}-{y}" for o,x,y in wins))
print('condorcet winners:', [nm(c) for c in cw] or 'none')
