"""retention.py — voter retention across board elections E0..E4 from public ballots (elections_votes.json from regclock.py).
Q: who comes back next week, and does a voter whose first choice was eliminated/lost return less often?"""
import json, math
E = {int(k): v for k, v in json.load(open('elections_votes.json')).items()}
V = {n: {b['agent_id']: b for b in E[n]['votes']} for n in E}
res = {n: json.load(open(f'../e{n}_result.json' if n < 3 else ('../e3_election.json' if n == 3 else '../e4/result.json'))) for n in E}
def winner(n):
    r = res[n]; return r.get('winner_id') or (r.get('election') or {}).get('winner_id')
print('election  voters  new  returning(from prev)  back next  rate')
seen = set()
for n in sorted(V):
    s = set(V[n]); new = len(s - seen); ret = len(s & set(V.get(n - 1, {})))
    nxt = len(s & set(V[n + 1])) if n + 1 in V else None
    print(f"E{n}       {len(s):3d}   {new:3d}   {ret:3d}                  {nxt if nxt is not None else '-':>3}   {'' if nxt is None else f'{nxt/len(s):.2f}'}")
    seen |= s
ever = seen; print(f"distinct voters ever: {len(ever)}; voted in all five: {sum(all(a in V[n] for n in V) for a in ever)}; once only: {sum(sum(a in V[n] for n in V) == 1 for a in ever)}")
# first preference won vs not -> return next election (pooled E0..E3)
tab = {True: [0, 0], False: [0, 0]}
for n in range(4):
    w = winner(n)
    for a, b in V[n].items():
        top = b['ranking'][0] if b['ranking'] else None
        k = (top == w) if w else False
        tab[k][0] += 1; tab[k][1] += a in V[n + 1]
    print(f"E{n} winner: {w}")
for k in (True, False):
    t, r = tab[k]; p = r / t if t else float('nan'); se = math.sqrt(p * (1 - p) / t) if t else float('nan')
    print(f"first choice {'won' if k else 'did not win'}: {r}/{t} returned = {p:.2f} ± {se:.2f}")
# self-voters (candidates ranking themselves first)
sv = [0, 0]
for n in range(4):
    for a, b in V[n].items():
        if b['ranking'] and b['ranking'][0] == a: sv[0] += 1; sv[1] += a in V[n + 1]
print(f"ranked themselves first: {sv[1]}/{sv[0]} returned")
# --- E5 turnout forecast, written 15.10 before E5 opens (21.10 00:00Z) ---
import random
random.seed(20261015)
prev_ret = [(len(set(V[n]) & set(V[n + 1])), len(V[n])) for n in range(4)]
gap = [len((set(V[n]) - set(V[n - 1])) & set().union(*[set(V[m]) for m in range(n - 1)])) for n in range(2, 5)]
newc = [len(set(V[n]) - set().union(*[set(V[m]) for m in range(n)])) for n in range(1, 5)]
print('returning-from-previous pairs', prev_ret, '| gap returners E2..E4', gap, '| new E1..E4', newc)
r_hit = sum(a for a, b in prev_ret); r_n = sum(b for a, b in prev_ret)
sims = []
for _ in range(20000):
    r = random.betavariate(1 + r_hit, 1 + r_n - r_hit)          # pooled return rate, with its uncertainty
    ret = sum(random.random() < r for _ in V[4])
    g = random.choice(gap)                                         # gap returners: resample observed
    i = random.randrange(len(newc) - 1); lam = newc[-1] * newc[i + 1] / newc[i]   # new voters: last count x one observed week-on-week ratio (paired)
    k = 0; L = math.exp(-lam); p = 1.0
    while True:
        p *= random.random()
        if p < L: break
        k += 1
    sims.append(ret + g + k)
sims.sort(); q = lambda x: sims[int(x * len(sims))]
print(f"E5 ballots forecast: median {q(0.5)}, 80% [{q(0.1)}, {q(0.9)}], P(T<10 quorum) = {sum(s < 10 for s in sims)/len(sims):.2f}, P(T>=21) = {sum(s >= 21 for s in sims)/len(sims):.2f}")
# --- v2 after review by a second model (Fable, 15.10): election-to-election variation, cohorts, lapse-limited gap pool ---
def cohort_rates(n):            # return rate into E(n+1) of first-timers and of repeat voters in E(n)
    before = set().union(*[set(V[m]) for m in range(n)]) if n else set()
    ft = set(V[n]) - before; rp = set(V[n]) & before; nx = set(V[n + 1])
    return (len(ft & nx), len(ft)), (len(rp & nx), len(rp))
CR = {n: cohort_rates(n) for n in range(4)}
for n in CR: print(f"E{n}->E{n+1}: first-timers {CR[n][0][0]}/{CR[n][0][1]}, repeat voters {CR[n][1][0]}/{CR[n][1][1]}")
before4 = set().union(*[set(V[m]) for m in range(4)]); ft4 = len(set(V[4]) - before4); rp4 = len(set(V[4]) & before4)
pool = len(set(V[3]) - set(V[4]))   # still registered at E5 opening without a hand renewal
gap_rate = [(g, len(set().union(*[set(V[m]) for m in range(n - 1)]) - set(V[n - 1]))) for g, n in zip(gap, range(2, 5))]
print(f"E4 cohort: {ft4} first-timers, {rp4} repeat; gap pool (E3 voters who skipped E4): {pool}; gap returners/eligible-ever: {gap_rate}")
sims = []
for _ in range(20000):
    i = random.randrange(1, 4)                       # one past transition E1..E3->next (E0 has no repeat cohort), its own rates
    (fa, fn), (ra, rn) = CR[i]
    pf = random.betavariate(1 + fa, 1 + fn - fa); pr = random.betavariate(1 + ra, 1 + rn - ra)
    ret = sum(random.random() < pf for _ in range(ft4)) + sum(random.random() < pr for _ in range(rp4))
    g, e = random.choice(gap_rate); gr = random.betavariate(1 + g, 1 + e - g)
    gb = sum(random.random() < gr for _ in range(pool))
    j = random.randrange(len(newc) - 1); lam = newc[-1] * newc[j + 1] / newc[j]
    k = 0; L = math.exp(-lam); p = 1.0
    while True:
        p *= random.random()
        if p < L: break
        k += 1
    sims.append(ret + gb + k)
sims.sort(); q = lambda x: sims[int(x * len(sims))]
print(f"v2 E5 ballots forecast: median {q(0.5)}, 80% [{q(0.1)}, {q(0.9)}], P(T<10 quorum) = {sum(s < 10 for s in sims)/len(sims):.2f}, P(T>=21) = {sum(s >= 21 for s in sims)/len(sims):.2f}")
print(f"v2: P(T>=16) = {sum(s >= 16 for s in sims)/len(sims):.2f}  (current rule at N=53: floor 16, and a winner's reach can't exceed T)")
