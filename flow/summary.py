"""summary.py — one line per election: leader's first preferences, ballots gained by transfer, final, floor, exhausted at the end."""
import sys
from replay import load, replay
print('election  ballots  leader               first  +transfers  final  F   exhausted  result')
for n in map(int, sys.argv[1:] or [0, 1, 2, 3]):
    b, names, res = load(n); rep = replay(b, res.get('rounds') or res['result']['rounds']); fin = rep[-1]['tally']
    L = max((c for c in fin if c != 'vacancy'), key=lambda c: fin[c]); f1 = rep[0]['tally'].get(L, 0)
    print(f"E{n:<8} {len(b):7d}  {names[L][:20]:20s} {f1:5d}  {fin[L] - f1:+10d}  {fin[L]:5d}  {res['floor']:<3d} {rep[-1]['exhausted']:9d}  {res['outcome']}")
