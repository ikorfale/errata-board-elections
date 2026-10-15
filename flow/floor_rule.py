"""floor_rule.py — replay every board election's full public ballot set under the election:5 floor draft (hermes-works #88164,
#88336; novyway #88449 asked for this): F = max(quorum, floor(T/2)+1), T = ballots cast, counted against ALL T.
Same irv-2 count as irv.py (which reproduces all five official results), only F changes. Prints T, F, the final round,
continuing_final, exhausted_final, outcome, and the current-rule outcome next to it. Plus synthetic even-T cases.
Run: python3 floor_rule.py [quorum]   (quorum default 10)"""
import math, sys
import irv
from replay import load

Q = int(sys.argv[1]) if len(sys.argv) > 1 else 10

def count_T(ballots, options, quorum=Q):
    T = len(ballots); F = max(quorum, T // 2 + 1)
    orig = math.ceil; irv.math = type('M', (), {'ceil': staticmethod(lambda x: F)})   # irv.count's F = max(5, ceil(0.3N)) -> F
    try: rounds, outcome, reason, w, _ = irv.count(ballots, options, 0)
    finally: irv.math = math
    if T < quorum: outcome, reason, w = 'vacancy', 'quorum_not_met', None
    return T, F, rounds, outcome, reason, w

print(f'proposed F = max({Q}, floor(T/2)+1), counted against all T\n')
print('elec  T   F | final round (continuing)            exhausted_final | proposed           | current rule (official)')
for n in range(5):
    ballots, names, res = load(n); off = res['rounds']
    options = list(off[0]['continuing']) if 'continuing' in off[0] else list(off[0]['counts'])
    T, F, rounds, outcome, reason, w = count_T(ballots, options)
    fin = rounds[-1]; cont = sum(fin['counts'].values())
    top = ', '.join(f"{names.get(c, c[:8])} {v}" for c, v in sorted(fin['counts'].items(), key=lambda x: -x[1]) if v)
    prop = f"winner {names.get(w)}" if outcome == 'winner' else f"vacancy ({reason})"
    cur = f"winner {names.get(res.get('winner_id'))}" if res['outcome'] == 'winner' else f"vacancy ({res.get('reason')})"
    print(f"E{n}  {T:3d} {F:3d} | {top:34s} {cont:2d} cont | exh {fin['exhausted']:2d}  | {prop:18s} | {cur}, F={res.get('floor')}")

print('\nsynthetic (two candidates A, B; vacancy ranked by nobody):')
cases = {'T=22, 11-11': [['A']] * 11 + [['B']] * 11,
         'T=22, 12-10': [['A']] * 12 + [['B']] * 10,
         'T=22, 11-10 + 1 exhausted (ranked only C, eliminated)': [['A']] * 11 + [['B']] * 10 + [['C']],
         'T=9, 9-0 (below quorum)': [['A']] * 9}
for k, b in cases.items():
    T, F, rounds, outcome, reason, w = count_T(b, ['A', 'B', 'C', 'vacancy'])
    print(f"  {k}: F={F}, final {dict((c, v) for c, v in rounds[-1]['counts'].items() if v)}, exh {rounds[-1]['exhausted']} -> {outcome} {reason or w}")
