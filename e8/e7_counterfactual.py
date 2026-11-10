"""E7: which candidates would have cleared F=9 had they reached the last round? irv-2 replica (flow/irv.py), MATCH checked first."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'flow'))
from irv import count; from replay import load
ballots, names, res = load(7); N = res['electorate_size']
opts = list(res['rounds'][0]['continuing'])
for c in opts:
    if c == 'vacancy': continue
    cov = sum(1 for b in ballots if c in b and ('vacancy' not in b or b.index(c) < b.index('vacancy')))
    _, out, reason, w, F = count(ballots, [c, 'vacancy'], N)   # c alone against vacancy = its final-round tally
    print(f"{names.get(c, c[:8]):28s} above vacancy on {cov}/{len(ballots)} ballots; alone vs vacancy -> {out} {reason or ''} (F={F})")
_, out, reason, w, F = count(ballots, opts, N); print('actual count:', out, reason, names.get(w, w))
