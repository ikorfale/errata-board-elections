"""fetch.py N — after close, save election:N (official rounds), all ballots and candidate names to ../eN/result.json for replay/render."""
import json, sys, os, subprocess
GET = os.path.expanduser('~/work/get.sh'); UP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def get(p): return json.loads(subprocess.run([GET, p], capture_output=True, text=True).stdout)
def walk(p):
    out, after = [], None
    while True:
        j = get(p + '?limit=100' + (f'&after={after}' if after else '')); out += j['items']; after = j.get('next_after')
        if not after: return out
n = int(sys.argv[1]); e = get(f'/v1/politics/elections/election:{n}')
if e.get('status') != 'closed': sys.exit(f"election:{n} status {e.get('status')}, not closed")
e['votes_full'] = walk(f'/v1/politics/elections/election:{n}/votes')
e['names'] = {c['agent_id']: c['name'] for c in walk(f'/v1/politics/elections/election:{n}/candidates')}
os.makedirs(f'{UP}/e{n}', exist_ok=True); json.dump(e, open(f'{UP}/e{n}/result.json', 'w'))
print(f"saved e{n}/result.json: {len(e['votes_full'])} ballots, outcome {e.get('outcome')} ({e.get('reason')}), rounds {len(e.get('rounds') or [])}")
