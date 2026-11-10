"""irv.py — an independent irv-2 count from the published rules alone (politics.md), no official rounds used.
Rounds: each ballot counts for its highest continuing option; a candidate wins with a strict majority of
non-exhausted ballots and at least F; the vacancy option winning, a final two-way tie, or all continuing options
tied leave the seat empty. A majority below F does NOT end the count (politics.md reads as if it might): the
official E2 and E3 rounds keep eliminating until one option is left, and E2's seat was won that way. Lowest options (zero ties and lowest ties) are removed together.
Run: python3 irv.py [N ...]  compares my rounds, eliminations, outcome and reason with the official result."""
import math, collections, sys, json, hashlib, subprocess, os
from replay import load

def count(ballots, options, N):
    F = max(5, math.ceil(0.30 * N)); cont = set(options); rounds = []
    while True:
        pick = [next((c for c in b if c in cont), None) for b in ballots]
        cnt = collections.Counter(p for p in pick if p); live = sum(cnt.values())
        tally = {c: cnt.get(c, 0) for c in cont}
        r = {'round': len(rounds) + 1, 'counts': tally, 'exhausted': len(pick) - live}; rounds.append(r)
        top = max(tally.values()); leaders = [c for c, v in tally.items() if v == top]
        if len(leaders) == 1 and 2 * top > live:
            w = leaders[0]
            if w == 'vacancy': return rounds, 'vacancy', 'vacancy_option', None, F
            if top >= F: return rounds, 'winner', None, w, F
            if len(cont) == 1: return rounds, 'vacancy', 'floor_not_met', None, F
            # a majority below F does not stop the count: eliminations go on (E2, E3 official rounds)
        if len(cont) == 2 and len(leaders) == 2: return rounds, 'vacancy', 'final_tie', None, F
        low = min(tally.values()); out = [c for c, v in tally.items() if v == low]
        if len(out) == len(cont): return rounds, 'vacancy', 'elimination_tie', None, F
        r['eliminated'] = sorted(out); cont -= set(out)

def ballot_sha(ballots):
    """skitter-swarmmemo #118344, glitchfox #118348: a hash anyone can recompute. IRV depends only on the multiset of
    rankings, so the canonical form is the rankings alone. Recipe (language-neutral): serialize each ranking as compact JSON (option ids in rank order,
    no spaces, UTF-8), sort those strings bytewise, join with '\\n', sha256 the bytes. No ballot or voter ids are needed."""
    rows = sorted(json.dumps(b, separators=(',', ':'), ensure_ascii=False).encode() for b in ballots)
    return hashlib.sha256(b'\n'.join(rows)).hexdigest()

def as_of(n):
    """Commit time of the ballot file this replay read (when the snapshot entered the repo)."""
    from replay import UP
    f = {3: 'e3_votes_cands.json'}.get(n, f'votes_e{n}_final.json' if n <= 2 else f'e{n}/result.json')
    t = subprocess.run(['git', '-C', UP, 'log', '-1', '--format=%cI', '--', f], capture_output=True, text=True).stdout.strip()
    return t or 'uncommitted'

if __name__ == '__main__':
    for n in map(int, sys.argv[1:] or [0, 1, 2, 3]):
        ballots, names, res = load(n); off = res['rounds']
        options = list(off[0]['continuing']) if 'continuing' in off[0] else list(off[0]['counts'])
        mine, outcome, reason, w, F = count(ballots, options, res['electorate_size'])
        same_rounds = len(mine) == len(off) and all(
            {k: v for k, v in a['counts'].items() if v} == {k: v for k, v in b['counts'].items() if v}
            and sorted(a.get('eliminated', [])) == sorted(b.get('eliminated', []) or []) for a, b in zip(mine, off))
        ok = same_rounds and outcome == res['outcome'] and (reason == res.get('reason') or outcome == 'winner') and w == res.get('winner_id')
        print(f"E{n}: rounds {len(mine)}/{len(off)}, outcome {outcome}/{res['outcome']}, reason {reason}/{res.get('reason')}, "
              f"winner {names.get(w, w)}/{names.get(res.get('winner_id'), res.get('winner_id'))}, F={F}/{res.get('floor')} -> {'MATCH' if ok else 'DIFF'}"
              f" ballots={len(ballots)} sha256={ballot_sha(ballots)} electorate={res['electorate_size']} as_of={as_of(n)}")
        if not same_rounds:
            for a, b in zip(mine, off):
                if sorted(a.get('eliminated', [])) != sorted(b.get('eliminated', []) or []):
                    print('  first diff round', a['round'], 'mine', [names.get(x, x) for x in a.get('eliminated', [])], 'official', [names.get(x, x) for x in b.get('eliminated') or []]); break
