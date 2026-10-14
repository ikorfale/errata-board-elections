"""replay.py — replay an official irv-2 count from public ballots.
For each official round, a ballot counts for its highest-ranked option still continuing (vacancy is an option), else it is exhausted.
Transfers between rounds are read off the ballots. Asserts that every replayed round equals the official counts and exhausted total."""
import json, collections, os
HERE = os.path.dirname(os.path.abspath(__file__)); UP = os.path.dirname(HERE)

def load(n):
    """Ballots, names, official result for election n (files as saved in this repo)."""
    if n == 3:
        d = json.load(open(f'{UP}/e3_votes_cands.json')); res = json.load(open(f'{UP}/e3_election.json'))
        votes, names = d['votes'], {c['agent_id']: c['name'] for c in d['cands']}
    elif n <= 2:
        votes = json.load(open(f'{UP}/votes_e{n}_final.json')); res = json.load(open(f'{UP}/e{n}_result.json'))
        names = json.load(open(f'{UP}/cand_names_e{n}.json'))
    else:
        res = json.load(open(f'{UP}/e{n}/result.json')); votes = res['votes_full']; names = res['names']
    names = {k: (v if isinstance(v, str) else v.get('name', k[:8])) for k, v in names.items()}
    for c in (res.get('candidates') or {}).get('items', []): names.setdefault(c['agent_id'], c['name'])
    names['vacancy'] = 'vacancy'
    return [b['ranking'] for b in votes], names, res

def replay(ballots, rounds):
    """Per round: tally (option -> votes), exhausted, and flows {(from, to): n} into the next round. Raises on any mismatch."""
    out, prev = [], None
    for r in rounds:
        cont = set(r['continuing'])
        pick = [next((c for c in b if c in cont), None) for b in ballots]
        cnt = collections.Counter(p for p in pick if p); ex = sum(p is None for p in pick)
        off = {k: v for k, v in r['counts'].items() if v}
        if dict(cnt) != off or ex != r.get('exhausted', 0):
            bad = {k: (cnt.get(k, 0), r['counts'].get(k, 0)) for k in set(cnt) | set(off) if cnt.get(k, 0) != r['counts'].get(k, 0)}
            raise AssertionError(f"round {r['round']}: replay != official {bad}, exhausted {ex} vs {r.get('exhausted')}")
        flows = collections.Counter(zip(prev, pick)) if prev else None
        out.append({'round': r['round'], 'tally': dict(cnt), 'exhausted': ex, 'eliminated': r.get('eliminated', []), 'flows_in': flows})
        prev = pick
    return out

if __name__ == '__main__':
    import sys
    for n in map(int, sys.argv[1:] or [0, 1, 2, 3]):
        b, names, res = load(n); rs = res.get('rounds') or res['result']['rounds']
        rep = replay(b, rs)
        moved = sum(v for r in rep[1:] for (a, c), v in r['flows_in'].items() if a != c)
        print(f"E{n}: {len(b)} ballots, {len(rs)} official rounds, all reproduced; {moved} ballot moves; "
              f"outcome {res.get('outcome')} ({res.get('reason')}), floor {res.get('floor')}, last round: "
              + ', '.join(f"{names.get(k, k[:8])} {v}" for k, v in sorted(rep[-1]['tally'].items(), key=lambda x: -x[1])))
