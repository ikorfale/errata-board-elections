#!/usr/bin/env python3
"""forecast_e4.py — written 13.10, before election:4 opens. Will anyone reach the floor?
Model: winner iff final-round support >= F. Past: F/electorate ~0.31 (21/67, 27/87, 24/78);
final support / ballots s = 21/37, 28/43, 17/25 (0.57, 0.65, 0.68); turnout t = ballots/electorate 0.55, 0.49, 0.32.
So a winner needs s*t >= 0.31: with s ~ 0.64 that is turnout >= ~0.48. E1 and E2 cleared F by 0 and 1 vote."""
import numpy as np
r = np.random.default_rng(4); N = 200_000
past = [(67, 21, 37, 21), (87, 27, 43, 28), (78, 24, 25, 17)]   # electorate, F, ballots, final support of last survivor
for E, F, B, S in past: print(f"E={E} F/E={F/E:.3f} t={B/E:.2f} s={S/B:.2f} s*t={S/E:.3f} margin={S-F:+d}")
for tm in (.35, .40, .45):
    t = r.normal(tm, .09, N); s = r.normal(.64, .06, N)
    print(f"turnout mean {tm:.2f}: P(winner) = {((t*s) >= .31).mean():.3f}")
