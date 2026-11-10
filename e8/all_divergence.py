"""E0-E7: Condorcet winner vs broadest candidate (most ballots ranking them above vacancy) vs official winner and floor."""
import sys, os, json; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'flow'))
from replay import load; from irv import count
rows = []
for e in range(8):
    ballots, names, res = load(e); N = res['electorate_size']
    opts = [c for c in res['rounds'][0]['continuing'] if c != 'vacancy']; nm = lambda c: names.get(c, c[:8])
    rk = lambda b, c: b.index(c) if c in b else 10**6
    av = {c: sum(1 for b in ballots if c in b and ('vacancy' not in b or b.index(c) < b.index('vacancy'))) for c in opts}
    pw = {(a, o): sum(rk(b, a) < rk(b, o) for b in ballots) for a in opts for o in opts if a != o}
    cw = [a for a in opts if all(pw[a, o] > pw[o, a] for o in opts if o != a)]
    _, out, reason, w, F = count(ballots, list(res['rounds'][0]['continuing']), N)
    top = max(av.values()); broad = [c for c in opts if av[c] == top]
    r = dict(e=e, n_ballots=len(ballots), N=N, F=F, n_cand=len(opts), official=nm(w) if w else out, reason=reason,
             condorcet=[nm(c) for c in cw], condorcet_av=[av[c] for c in cw], broadest=[nm(c) for c in broad], broadest_av=top,
             clear_F=[nm(c) for c in opts if av[c] >= F], av={nm(c): av[c] for c in opts},
             pw={f'{nm(a)}>{nm(o)}': pw[a, o] for a in opts for o in opts if a != o})
    rows.append(r)
    print(f"E{e}: ballots {len(ballots)} F={F} cand {len(opts)} | official {r['official']} ({reason or ''}) | Condorcet {r['condorcet'] or 'none'} av{r['condorcet_av']} | broadest {r['broadest']} av {top} | clear F: {r['clear_F'] or 'none'}")
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'all_divergence.json'), 'w'), indent=1)
