"""Coverage ceiling: in IRV with a floor F, a candidate can only reach F if at least F ballots rank
them somewhere above vacancy. Count, per candidate, the ballots that rank them at all (before 'vacancy')."""
import json, sys, collections
f = sys.argv[1] if len(sys.argv) > 1 else 'e3_votes_cands.json'
d = json.load(open(f)); votes, cands = d['votes'], d['cands']
name = {c['agent_id']: c['name'] for c in cands}
cov = collections.Counter(); lens = []
for b in votes:
    r = b['ranking']
    r = r[:r.index('vacancy')] if 'vacancy' in r else r
    lens.append(len(r)); cov.update(set(r))
print(f"ballots {len(votes)}, candidates {len(cands)}")
print("ranking length (before vacancy):", sorted(lens))
for a, n in cov.most_common(8): print(f"  {name.get(a, a)[:28]:28s} ranked on {n}")
mine = [b for b in votes if b['name'] == 'fable-terminal']
print("my ballot length:", [len(b['ranking']) for b in mine], mine[0]['ranking'][-1:] if mine else '')
