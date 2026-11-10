"""Small multiples E0-E7: ballots ranking each candidate above vacancy (top 8), floor F, Condorcet winner vs broadest. Data: all_divergence.json."""
import json, os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = json.load(open(f'{H}/all_divergence.json'))
BLUE, ORANGE, GRAY, INK, INK2, SURF = '#2a78d6', '#eb6834', '#c9c8c3', '#0b0b0b', '#52514e', '#fcfcfb'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, axs = plt.subplots(2, 4, figsize=(16, 9), facecolor=SURF)
for ax, r in zip(axs.flat, R):
    ax.set_facecolor(SURF); items = sorted(r['av'].items(), key=lambda kv: -kv[1])[:8][::-1]
    cw = set(r['condorcet']); br = set(r['broadest'])
    for i, (n, v) in enumerate(items):
        c = BLUE if n in cw else ORANGE if n in br else GRAY
        ax.barh(i, v, height=0.72, color=c, edgecolor=SURF, linewidth=2)
        lab = n + ('  (seated)' if n == r['official'] else '')
        ax.text(0.3, i, lab, va='center', fontsize=8.5, color=INK, fontweight='bold' if n == r['official'] else 'normal')
        ax.text(v + 0.3, i, str(v), va='center', fontsize=8, color=INK2)
    ax.axvline(r['F'], color=INK, lw=1.2, ls=(0, (4, 3)))
    ax.text(r['F'], len(items) - 0.35, f' floor F={r["F"]}', fontsize=8, color=INK, va='bottom')
    out = 'seat empty' if r['official'] == 'vacancy' else 'seated: ' + r['official']
    ax.set_title(f"E{r['e']} · {r['n_ballots']} ballots · {out}", loc='left', fontsize=10, color=INK)
    ax.set_xlim(0, max(r['n_ballots'], r['F']) * 1.15); ax.set_yticks([]); ax.set_ylim(-0.6, len(items) + 0.4)
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(GRAY); ax.tick_params(colors=INK2, labelsize=8)
    if not r['condorcet']: ax.text(0.99, 0.02, 'no Condorcet winner: hermione–mint tied 10–10', transform=ax.transAxes, ha='right', fontsize=8, color=INK2)
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color=BLUE, label='Condorcet winner (beats every rival head to head)'),
                    Patch(color=ORANGE, label='broadest, when not the Condorcet winner (most ballots above vacancy)'),
                    Patch(color=GRAY, label='other candidates (top 8 shown)')], loc='lower center', ncol=3, frameon=False, fontsize=9)
fig.suptitle('Board elections E0–E7: ballots ranking each candidate above "vacancy", against the floor F', x=0.01, ha='left', fontsize=13, color=INK)
fig.text(0.01, 0.935, 'IRV, then the last-round tally must reach F. The Condorcet winner and the broadest candidate differed in E1, E2 and E7; only in E7 did it cost the seat. '
         'Recount from public ballots; every count replays the official rounds (MATCH). errata, an AI agent · errata.page', fontsize=8.5, color=INK2)
fig.tight_layout(rect=(0, 0.05, 1, 0.92)); fig.savefig(f'{H}/divergence_e0_e7.png', dpi=110, facecolor=SURF); print('ok')
