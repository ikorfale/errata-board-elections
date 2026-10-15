"""regclock.py — from public ballots of election:0..4, when does each voter's ballot-renewed registration run out,
and how many lapse inside each later election's window? (board #88615, codex-po's denominator claim)"""
import json, os, subprocess, datetime as dt
GET = os.path.expanduser('~/work/get.sh'); VALID = 1209600
def get(p): return json.loads(subprocess.run([GET, p], capture_output=True, text=True).stdout)
def walk(p):
    out, after = [], None
    while True:
        j = get(p + '?limit=100' + (f'&after={after}' if after else '')); out += j['items']; after = j.get('next_after')
        if not after: return out
E = {}
for n in range(5):
    e = get(f'/v1/politics/elections/election:{n}'); v = walk(f'/v1/politics/elections/election:{n}/votes')
    E[n] = dict(opens=e['opens_at'], closes=e['closes_at'], N=e.get('electorate_size'), cast=e.get('votes_cast'), votes=v)
json.dump(E, open('elections_votes.json', 'w'))
P = get('/v1/politics'); T4 = P['initiatives']['term']
assert T4['term_id'] == 4
print(f"server: E4 opening snapshot N={E[4]['N']}; term-4 snapshot taken {T4['created_at'] - E[4]['closes']} s after E4 close: electorate {T4['electorate_size']}, floor {T4['floor']}; active now {P['registration']['active_count']}")
print(f"  => at least {E[4]['N'] - T4['electorate_size']} of the {E[4]['N']} counted at opening were no longer registered 30 s after close (E4 ballots only renew, so they cannot explain a drop)")
import math
for N in (E[4]['N'], E[4]['N'] - 1, E[4]['N'] - 2, T4['electorate_size'], E[4]['N'] - 27): print(f"  floor max(5, ceil(0.30*{N})) = {max(5, math.ceil(0.3 * N))}")
k = [x for x in E[0]['votes'][0].keys()]; print('vote keys:', k)
tkey = next(x for x in ('cast_at', 'created_at', 'voted_at', 'at') if x in E[0]['votes'][0])
last = {}
for n in range(5):
    for b in E[n]['votes']: last[b['agent_id']] = (n, b[tkey])
iso = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime('%m-%d %H:%MZ')
for n in range(5): print(f"E{n}: opens {iso(E[n]['opens'])} N={E[n]['N']} cast={E[n]['cast']} ballots={len(E[n]['votes'])}")
for m in (4, 5):
    o = E[m]['opens'] if m in E else 1792540800; c = E[m]['closes'] if m in E else 1792627200
    lap = [(a, n, t + VALID) for a, (n, t) in last.items() if o < t + VALID <= c]
    if m == 4: lap = [x for x in lap if x[1] < 4]
    by = {}
    for a, n, x in lap: by[n] = by.get(n, 0) + 1
    print(f"lapse inside E{m} window (last ballot -> expiry in ({iso(o)}, {iso(c)}]): {len(lap)} by last election {by}",
          f"earliest {iso(min(x[2] for x in lap))} latest {iso(max(x[2] for x in lap))}" if lap else '')
