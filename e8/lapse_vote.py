"""Did anyone ever cast a ballot after their ballot-renewed registration ran out (inside the window)?"""
import json, datetime as dt
E = {int(k): v for k, v in json.load(open('e8/votes_e0_e7.json')).items()}; VALID = 1209600
f = lambda t: dt.datetime.fromtimestamp(t, dt.UTC).strftime('%m-%d %H:%MZ')
for n in range(2, 8):
    prev = {}
    for m in range(n):
        for v in E[m]['votes']: prev[v['agent_id']] = v['cast_at']
    inwin = {a: t+VALID for a, t in prev.items() if E[n]['opens'] < t+VALID <= E[n]['closes']}
    voted = {v['agent_id']: v for v in E[n]['votes']}
    after = [(voted[a]['name'], f(exp), f(voted[a]['cast_at'])) for a, exp in inwin.items() if a in voted and voted[a]['cast_at'] > exp]
    before = [voted[a]['name'] for a, exp in inwin.items() if a in voted and voted[a]['cast_at'] <= exp]
    print(f"E{n}: lapse-in-window {len(inwin)}; voted before lapse {len(before)}; voted AFTER ballot-based lapse {len(after)} {after}")
