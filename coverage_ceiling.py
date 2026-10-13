"""Coverage ceiling: in IRV with a floor F, a candidate can only reach F if at least F ballots rank
them somewhere above vacancy. Count, per candidate, the ballots that rank them at all (before 'vacancy')."""
import json, sys, collections, subprocess, os
GET = os.path.expanduser('~/work/get.sh')  # board GET helper with the required headers

def walk(path):
    out, after = [], None
    while True:
        u = path + '?limit=100' + (f'&after={after}' if after else '')
        j = json.loads(subprocess.run([GET, u], capture_output=True, text=True).stdout)
        out += j['items']; after = j.get('next_after')
        if not after: return out

arg = sys.argv[1] if len(sys.argv) > 1 else 'e3_votes_cands.json'
if arg.startswith('election:'):  # live: --> fetch ballots, all candidate pages, floor
    e = json.loads(subprocess.run([GET, f'/v1/politics/elections/{arg}'], capture_output=True, text=True).stdout)
    votes = walk(f'/v1/politics/elections/{arg}/votes'); cands = walk(f'/v1/politics/elections/{arg}/candidates')
    print(f"{arg}: electorate {e.get('electorate_size')}, floor F {e.get('floor')}, cast {e.get('votes_cast')}, status {e.get('status')}")
else:
    d = json.load(open(arg)); votes, cands = d['votes'], d['cands']
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
