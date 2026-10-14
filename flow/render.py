"""render.py — draw an election's instant-runoff count as a ribbon diagram (SVG), from replay.py's checked rounds.
Columns are official rounds; each bar is one option's ballots in that round; ribbons carry ballots to the next round
(same-colour ribbon = ballots that stayed, coloured by their source when they moved). Exhausted ballots are the grey
bar at the bottom. The dashed rule in the last column is the floor F, measured from the top of the final leader's bar.
Usage: python3 render.py 0 1 2 3   -> flow_eN.svg"""
import sys, html
from replay import load, replay, HERE

PAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4']   # validated categorical slots 1-5 (dataviz reference palette)
PAL_D = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181']
OTHER, OTHER_D, VAC, EXH = '#a3a29c', '#6b6a64', '#52514e', '#d9d8d2'

def draw(n):
    ballots, names, res = load(n); rounds = res.get('rounds') or res['result']['rounds']
    rep = replay(ballots, rounds); F = res.get('floor'); B = len(ballots); R = len(rep)
    # order: by the last round an option holds ballots, then by its votes there (survivors on top)
    last = {}
    for i, r in enumerate(rep):
        for c, v in r['tally'].items(): last[c] = (i, v)
    order = sorted(last, key=lambda c: (-last[c][0], -last[c][1], names.get(c, c)))
    top = [c for c in order if c != 'vacancy'][:5]
    cls = {c: f's{i}' for i, c in enumerate(top)}
    def kind(c): return 'exh' if c is None else 'vac' if c == 'vacancy' else cls.get(c, 'oth')
    W_COL, BAR, GAP, H_PLOT = 170, 12, 3, 560
    nmax = max(len(r['tally']) + (1 if r['exhausted'] else 0) for r in rep)
    k = (H_PLOT - GAP * nmax) / B                                   # px per ballot
    LEFT, TOP = 190, 92; W = max(LEFT + W_COL * (R - 1) + BAR + 260, 900); H = TOP + H_PLOT + 70
    pos = []                                                         # per round: option -> (y0, height)
    for r in rep:
        y, p = TOP, {}
        for c in order + [None]:
            v = r['exhausted'] if c is None else r['tally'].get(c, 0)
            if v: p[c] = (y, v * k); y += v * k + GAP
        pos.append(p)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" class="viz-root" '
           f'role="img" aria-labelledby="t{n} d{n}" font-family="system-ui, -apple-system, Segoe UI, sans-serif">',
           '<style>.viz-root{--bg:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;' + ''.join(f'--s{i}:{c};' for i, c in enumerate(PAL)) +
           f'--oth:{OTHER};--vac:{VAC};--exh:{EXH}}}'
           '@media (prefers-color-scheme: dark){.viz-root{--bg:#1a1a19;--ink:#fff;--ink2:#c3c2b7;' +
           ''.join(f'--s{i}:{c};' for i, c in enumerate(PAL_D)) + f'--oth:{OTHER_D};--vac:#9a9890;--exh:#3a3a37}}}}'
           '.bg{fill:var(--bg)}.t{fill:var(--ink)}.t2{fill:var(--ink2)}'
           + ''.join(f'.{x}{{fill:var(--{x})}}' for x in ['s0', 's1', 's2', 's3', 's4', 'oth', 'vac', 'exh']) +
           '.rb{opacity:.28}.rb.mv{opacity:.55}.rb:hover,.bar:hover{opacity:.95}.fl{fill:none;stroke:var(--ink2);stroke-dasharray:4 3}'
           '</style>',
           f'<title id="t{n}">Election {n} on Get Posting Board: instant-runoff count, {B} ballots</title>',
           f'<desc id="d{n}">Official rounds replayed from the public ballots; every round matches the board\'s counts. '
           f'Outcome: {res.get("outcome")} ({res.get("reason")}), floor {F}.</desc>',
           f'<rect class="bg" width="{W}" height="{H:.0f}"/>']
    win = res.get('winner_id'); fin = rep[-1]['tally']
    lead = max((c for c in fin if c != 'vacancy'), key=lambda c: fin[c], default=None)
    head = (f'Election {n}: {names.get(win, "?")} elected' if res.get('outcome') == 'winner'
            else f'Election {n}: no winner, the seat stays vacant')
    sub = (f'{B} ballots, {R} round{'s' * (R != 1)} of instant runoff. Floor F = {F}: the final count must reach it. '
           f'Final round: {names.get(lead, "?")} {fin.get(lead, 0)}' + (f', vacancy {fin["vacancy"]}' if fin.get('vacancy') else '') + '.')
    out += [f'<text class="t" x="24" y="30" font-size="19" font-weight="600">{html.escape(head)}</text>',
            f'<text class="t2" x="24" y="52" font-size="13">{html.escape(sub)}</text>']
    # ribbons
    for i in range(1, R):
        a, b = pos[i - 1], pos[i]; fl = rep[i]['flows_in']
        so = {c: a[c][0] for c in a}; ti = {c: b[c][0] for c in b}
        # sources: stay first, then by target order; targets: own ballots first, then by source order
        rank = {c: j for j, c in enumerate(order + [None])}
        items = sorted(fl.items(), key=lambda kv: (rank[kv[0][0]], kv[0][0] != kv[0][1], rank[kv[0][1]]))
        tgt_order = sorted(fl.items(), key=lambda kv: (rank[kv[0][1]], kv[0][0] != kv[0][1], rank[kv[0][0]]))
        tpos = {}
        for (s, t), v in tgt_order: tpos[(s, t)] = ti[t]; ti[t] += v * k
        x0 = LEFT + W_COL * (i - 1) + BAR; x1 = LEFT + W_COL * i; xm = (x0 + x1) / 2
        for (s, t), v in items:
            y0 = so[s]; so[s] += v * k; y1 = tpos[(s, t)]; h = v * k
            mv = s != t
            tip = (f'{v} ballot{"s" * (v != 1)} ' + (f'move from {names.get(s, "exhausted") if s else "exhausted"} to {names.get(t, t) if t else "exhausted"}'
                   if mv else f'stay with {names.get(s, s) if s else "exhausted"}') + f' (round {rep[i-1]["round"]} to {rep[i]["round"]})')
            out.append(f'<path class="rb {"mv " if mv else ""}{kind(s)}" d="M{x0},{y0:.1f} C{xm},{y0:.1f} {xm},{y1:.1f} {x1},{y1:.1f} '
                       f'L{x1},{y1 + h:.1f} C{xm},{y1 + h:.1f} {xm},{y0 + h:.1f} {x0},{y0 + h:.1f}Z"><title>{html.escape(tip)}</title></path>')
    # bars, labels
    for i, (r, p) in enumerate(zip(rep, pos)):
        x = LEFT + W_COL * i
        out.append(f'<text class="t2" x="{x + BAR / 2}" y="{TOP - 10}" font-size="11" text-anchor="middle">round {r["round"]}</text>')
        for c, (y, h) in p.items():
            v = r['exhausted'] if c is None else r['tally'][c]; nm = 'exhausted' if c is None else names.get(c, c[:8])
            out.append(f'<rect class="bar {kind(c)}" x="{x}" y="{y:.1f}" width="{BAR}" height="{max(h, 1):.1f}" rx="2">'
                       f'<title>{html.escape(nm)}: {v} in round {r["round"]}</title></rect>')
            gone = c in r['eliminated'] or i == R - 1 or (c is not None and c not in rep[i + 1]['tally'])
            if i == 0 or gone:                                        # label where a bar starts (left) and where it ends (right)
                if i == 0 and not (gone and i == R - 1):
                    out.append(f'<text class="t" x="{x - 6}" y="{y + h / 2 + 4:.1f}" font-size="11" text-anchor="end">{html.escape(nm[:24])} {v}</text>')
                if gone and (i > 0 or R == 1):
                    out.append(f'<text class="{"t" if i == R - 1 else "t2"}" x="{x + BAR + 5}" y="{y + h / 2 + 4:.1f}" font-size="{12 if i == R - 1 else 10}"'
                               f'{" font-weight=\"600\"" if i == R - 1 and c == lead else ""}>{html.escape(nm[:24])} {v}{"" if i == R - 1 else " ✕"}</text>')
    if lead is not None and F:                                       # the floor as a dashed rule across the final column
        x = LEFT + W_COL * (R - 1); y = pos[-1][lead][0] + F * k; ok = fin[lead] >= F
        out += [f'<line x1="{x - 40}" x2="{x + BAR + 150}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="5 3"/>',
                f'<text class="t" x="{x + BAR + 6}" y="{y + 14:.1f}" font-size="11">floor F = {F}: '
                f'{names.get(lead, "?")} {"reaches it" if ok else f"short by {F - fin[lead]}"}</text>']
    out.append(f'<text class="t2" x="24" y="{H - 20:.0f}" font-size="11">Replayed from public ballots; every round equals the board\'s official '
               'irv-2 counts. Grey bottom bar: ballots with no continuing choice. ✕ = eliminated. Hover for counts. errata.page</text></svg>')
    f = f'{HERE}/flow_e{n}.svg'; open(f, 'w').write('\n'.join(out)); return f

if __name__ == '__main__':
    for n in map(int, sys.argv[1:] or [0, 1, 2, 3]): print(draw(n))
