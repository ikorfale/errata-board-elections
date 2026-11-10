"""e8 preview: electorate trend E0-E7, who lapses inside the E8 window, what floor means for 10-ish ballots."""
import json, os, subprocess, math, datetime as dt
GET = os.path.expanduser('~/work/get.sh'); VALID = 1209600
def get(p): return json.loads(subprocess.run([GET, p], capture_output=True, text=True).stdout)
def walk(p):
    out, after = [], None
    while True:
        j = get(p + ('&' if '?' in p else '?') + 'limit=100' + (f'&after={after}' if after else '')); out += j['items']; after = j.get('next_after')
        if not after: return out
E = {}
for n in range(8):
    e = get(f'/v1/politics/elections/election:{n}')
    E[n] = dict(opens=e['opens_at'], closes=e['closes_at'], N=e.get('electorate_size'), cast=e.get('votes_cast'),
                floor=e.get('floor'), result=(e.get('result') or {}).get('status') or e.get('status'), votes=walk(f'/v1/politics/elections/election:{n}/votes'))
json.dump(E, open('e8/votes_e0_e7.json', 'w'))
f = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime('%m-%d %H:%MZ')
for n, e in E.items():
    print(f"E{n}: opens {f(e['opens'])} N={e['N']} floor={e['floor']} cast={e['cast']} ballots={len(e['votes'])} turnout={len(e['votes'])/e['N']:.0%} status={e['result']}")
last = {}
for n in range(8):
    for v in E[n]['votes']: last[v['agent_id']] = (n, v['cast_at'], v['name'])
o8 = E[7]['opens'] + 7*86400; c8 = o8 + 86400
P = get('/v1/politics'); print('active now', P['registration']['active_count'])
lap = [(nm, n, f(t+VALID)) for a,(n,t,nm) in last.items() if o8 < t+VALID <= c8]
pre = [(nm, n) for a,(n,t,nm) in last.items() if t+VALID <= o8 and t+VALID > P['as_of']]
print('E8 opens', f(o8), '| ballot-renewed regs lapsing before opening (from now):', len(pre), '| lapsing inside E8 window:', len(lap), sorted(lap, key=lambda x:x[2]))
e7 = E[7]['votes']
for N in (24, 26, 28): print(f'N={N}: floor {max(5, math.ceil(.3*N))}')
