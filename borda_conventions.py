#!/usr/bin/env python3
"""Borda for hermione vs mint in election 0 under each convention: vacancy counted as an option or not;
if not, ballots compacted (vacancy deleted) or vacancy's slot kept empty; unranked share the bottom or get 0.
Usage: borda_conventions.py [E]  (default 0)"""
import json, sys
E = sys.argv[1] if len(sys.argv) > 1 else '0'
B = json.load(open('votes_e%s_final.json' % E)); res = json.load(open('e%s_result.json' % E)); names = json.load(open('cand_names_e%s.json' % E))
C = [c['agent_id'] for c in res['candidates']['items']]
assert len(C) == res['result']['candidates'], 'candidate list incomplete'
print('ballots %d, ballots ranking vacancy %d' % (len(B), sum('vacancy' in b['ranking'] for b in B)))
def borda(opts, keep_slot, share):
    m = len(opts); S = {c: 0.0 for c in opts}
    for b in B:
        full = [c for c in b['ranking'] if c in opts or c == 'vacancy']
        seq = full if keep_slot else [c for c in full if c in opts]
        r = [c for c in seq if c in opts]
        for i, c in enumerate(seq):
            if c in opts: S[c] += max(m - 1 - i, 0)
        u = [c for c in opts if c not in r]
        if share and u:
            avg = sum(max(m - 1 - i, 0) for i in range(len(seq), len(seq) + len(u))) / len(u)
            for c in u: S[c] += avg
    return S
for label, opts, keep in [('vacancy as option', C + ['vacancy'], False), ('no vacancy, compacted', C, False), ('no vacancy, slot kept', C, True)]:
    for share in (True, False):
        S = borda(opts, keep, share); top = sorted(C, key=lambda c: -S[c])[:2]
        print('%-22s %-6s %s' % (label, 'shared' if share else 'zero', '  '.join('%s %.2f' % (names.get(c, c[:8]), S[c]) for c in top)),
              ' lead %.2f' % (S[top[0]] - S[top[1]]))
