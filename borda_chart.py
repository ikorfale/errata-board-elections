import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# numbers copied from borda_split_e2.txt
rows = [('hermione ranked higher\n(18 ballots)', -61.0), ('mira ranked higher\n(6 ballots)', 11.0),
        ('only hermione ranked\n(4 ballots)', -78.0), ('only mira ranked\n(9 ballots)', 166.0), ('neither ranked\n(6 ballots)', 0.0)]
fig, ax = plt.subplots(figsize=(10, 4.6), dpi=130); fig.patch.set_facecolor('#f4efe4'); ax.set_facecolor('#f4efe4')
y = range(len(rows))[::-1]
ax.barh(list(y), [v for _, v in rows], color=['#1a4f8a' if v < 0 else '#b3261e' for _, v in rows], height=0.6)
ax.set_yticks(list(y)); ax.set_yticklabels([r for r, _ in rows], fontsize=10)
for yy, (_, v) in zip(y, rows): ax.text(v + (4 if v >= 0 else -4), yy, '%+.0f' % v, va='center', ha='left' if v >= 0 else 'right', fontsize=10)
ax.axvline(0, color='#555', lw=0.8); ax.set_xlim(-130, 210)
ax.set_xlabel('Borda points: mira minus hermione (total +38, so Borda elects mira)')
ax.set_title('Election 2: hermione wins head-to-head 22-15, Borda flips it on 9 ballots that left her unranked', fontsize=11, loc='left')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig('borda_gap_e2.png')
