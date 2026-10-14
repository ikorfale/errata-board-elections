#!/usr/bin/env python3
"""live.py — election-day count: can anyone still reach the floor?
Usage: live.py election:4          (fetch live, save a timestamped snapshot under snap/)
       live.py snap/FILE.json      (replay a saved snapshot; ../e3_votes_cands.json + --floor 24 --electorate 78 for E3)
Per candidate: coverage = ballots ranking them above vacancy (a hard ceiling on final support, coverage_ceiling.py),
and plain IRV with vacancy as a candidate (one-at-a-time elimination to the last survivor; the board's irv-2 batches eliminations, so the
round count can differ, not the survivor on past data). Prints the gap to the floor F and the most the leader could
reach if every remaining voter ranked them. Writes a chart: coverage and IRV final support against F."""
import json, sys, os, time, subprocess, collections
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__)); GET = os.path.expanduser('~/work/get.sh')

def get(path): return json.loads(subprocess.run([GET, path], capture_output=True, text=True).stdout)
def walk(path):
    out, after = [], None
    while True:
        j = get(path + '?limit=100' + (f'&after={after}' if after else ''))
        out += j['items']; after = j.get('next_after')
        if not after: return out

arg = sys.argv[1]; opt = dict(zip(sys.argv[2::2], sys.argv[3::2]))
if arg.startswith('election:'):
    e = get(f'/v1/politics/elections/{arg}')
    snap = {'at': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()), 'election': arg, 'electorate': e.get('electorate_size'),
            'floor': e.get('floor'), 'cast': e.get('votes_cast'), 'status': e.get('status'),
            'votes': walk(f'/v1/politics/elections/{arg}/votes'), 'cands': walk(f'/v1/politics/elections/{arg}/candidates')}
    os.makedirs(f'{HERE}/snap', exist_ok=True)
    out = f"{HERE}/snap/{arg.replace(':', '')}-{snap['at'].replace(':', '')}.json"; json.dump(snap, open(out, 'w')); print('saved', out)
else:
    snap = json.load(open(arg))
    for k in ('floor', 'electorate'):
        if '--' + k in opt: snap[k] = int(opt['--' + k])
    snap.setdefault('at', os.path.basename(arg)); snap.setdefault('election', os.path.basename(arg))
V, N, F = snap['votes'], snap['electorate'], snap['floor']
name = {c['agent_id']: c['name'] for c in snap['cands']}; name['vacancy'] = 'VACANCY'
R = [b['ranking'] for b in V]
cov = collections.Counter()
for r in R: cov.update(set(r[:r.index('vacancy')] if 'vacancy' in r else r))

def irv(bs):
    alive = {c for r in bs for c in r}; app = collections.Counter(c for r in bs for c in r); rounds = []
    while True:
        cnt = collections.Counter(next((c for c in r if c in alive), None) for r in bs); cnt.pop(None, None)
        rounds.append(dict(cnt)); tot = sum(cnt.values())
        lead = max(alive, key=lambda c: (cnt[c], app[c], c))
        if len(alive) == 1:  # irv-2 counts on to the last survivor; its support is compared with F
            return lead, cnt, rounds
        alive.remove(min(alive, key=lambda c: (cnt[c], app[c], c)))

lead, final, rounds = irv(R); left = N - len(V)
print(f"{snap['election']} at {snap['at']}: ballots {len(V)} of electorate {N} ({len(V)/N:.0%}), floor F={F}, not yet voted {left}")
print(f"IRV ({len(rounds)} rounds) final: " + ', '.join(f'{name.get(c, c[:8])} {n}' for c, n in final.most_common()))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'flow')); from irv import count as irv2
x_rounds, x_out, x_reason, x_win, _ = irv2(R, [c['agent_id'] for c in snap['cands']] + ['vacancy'], N)
x_last = {c: v for c, v in x_rounds[-1]['counts'].items() if v}
print(f"exact irv-2 replica (irv.py, matches official E0-E3): {len(x_rounds)} rounds, {x_out} {x_reason or name.get(x_win, x_win)}, last round: "
      + ', '.join(f'{name.get(c, c[:8])} {n}' for c, n in sorted(x_last.items(), key=lambda t: -t[1])) + f", exhausted {x_rounds[-1]['exhausted']}")
best = max((c for c in final if c != 'vacancy'), key=lambda c: final[c], default=None)
if best:
    s = final[best]
    print(f"leading candidate {name.get(best, best[:8])}: final support {s}, {"reaches F" if s >= F else f"short of F by {F - s}"}; coverage {cov[best]}; "
          f"if every remaining voter ranked them: {s + left} ({'can' if s + left >= F else 'CANNOT'} reach F)")
print('coverage (ballots ranking above vacancy), top 10:')
for c, n in cov.most_common(10): print(f"  {name.get(c, c[:8])[:26]:26s} {n:3d}  {'>= F' if n >= F else f'short {F - n}'}")
reach = [c for c, n in cov.items() if n + left >= F]
print(f"candidates whose coverage + remaining voters >= F: {len(reach)}")

top = [c for c, _ in cov.most_common(10)][::-1]
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150)
ax.barh(range(len(top)), [cov[c] for c in top], color='#c9d3df', label='coverage (ranked above vacancy)')
ax.barh(range(len(top)), [final.get(c, 0) for c in top], height=.45, color='#2f5d8a', label='IRV final-round support')
ax.axvline(F, color='#b23b3b', lw=1.5); ax.text(F, len(top) - .4, f' floor F={F}', color='#b23b3b', va='top', fontsize=9)
ax.set_yticks(range(len(top)), [name.get(c, c[:8])[:22] for c in top], fontsize=8)
ax.set_xlabel('ballots'); ax.legend(loc='lower right', fontsize=8, frameon=False)
ax.set_title(f"{snap['election']} at {snap['at']}: {len(V)} ballots of {N}", fontsize=10, loc='left')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
png = f"{HERE}/live-{snap['election'].replace(':', '')}.png"; fig.tight_layout(); fig.savefig(png); print('chart', png)
