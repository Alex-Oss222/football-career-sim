#!/usr/bin/env python3
"""Second pass for library/passer_interception_persistence_study.md: rebuild every
passer-season from the play-by-play files alone (no stats file) and refit every
season pair with numpy's normal equations, then compare with the first pass's
JSON. Research only. Usage: python scripts/research/verify_passer_interception_persistence.py SOURCE_DIR
"""
# Second pass: independent recomputation from the play-by-play files alone (no stats file),
# with numpy weighted least squares, then compare with the JSON written by the first pass.
import csv, gzip, json, math, sys
from collections import defaultdict
import numpy as np
SRC = sys.argv[1]
exclude = {'00-0029604'}  # the protagonist's passer: real post-divergence lines never read
J = json.load(open('library/data/passer_interception_persistence.json'))
seasons = {}
for s in (2010, 2011, 2012, 2013, 2014):
    acc = defaultdict(lambda: [0, 0, 0]); names = {}
    with gzip.open(f'{SRC}/play_by_play_{s}.csv.gz', 'rt', newline='') as f:
        for r in csv.DictReader(f):
            if r['season_type'] != 'REG' or not r['passer_player_id'] or r['two_point_attempt'] == '1':
                continue
            p = r['passer_player_id']; names[p] = r['passer_player_name']
            if r['play_type'] == 'pass':
                if r['sack'] == '1': acc[p][1] += 1
                else: acc[p][0] += 1
                if r['interception'] == '1': acc[p][2] += 1
            elif r['play_type'] == 'qb_spike':
                acc[p][0] += 1
    seasons[s] = {p: (a, k, i) for p, (a, k, i) in acc.items() if a + k >= 200 and not (s >= 2013 and p in exclude)}
    j = {r['player_id']: r for r in J['seasons'][str(s)]['rows']}
    assert set(j) == set(seasons[s]), (s, set(j) ^ set(seasons[s]))
    for p, (a, k, i) in seasons[s].items():
        assert (j[p]['attempts'], j[p]['sacks'], j[p]['interceptions']) == (a, k, i), (s, p)
    print(s, 'qualifiers', len(seasons[s]), 'all counts match the first pass')

def fit(rows):
    x = np.array([r[0] for r in rows]); y = np.array([r[1] for r in rows]); w = np.array([r[2] for r in rows], float)
    w = w / w.mean()
    X = np.column_stack([np.ones_like(x), x])
    W = np.diag(w)
    beta = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
    resid = y - X @ beta
    s2 = (w * resid**2).sum() / (len(x) - 2)
    se = math.sqrt(s2 * np.linalg.inv(X.T @ W @ X)[1, 1])
    # leave one out
    e, e0 = [], []
    for i in range(len(x)):
        m = np.ones(len(x), bool); m[i] = False
        Xi, Wi = X[m], np.diag(w[m])
        b = np.linalg.solve(Xi.T @ Wi @ Xi, Xi.T @ Wi @ y[m])
        e.append(y[i] - X[i] @ b); e0.append(y[i] - np.average(y[m], weights=w[m]))
    skill = 1 - (np.mean(np.square(e)) / np.mean(np.square(e0)))
    return beta[0], beta[1], se, skill, np.corrcoef(x, y)[0, 1]

pairs = {}
for t in (2010, 2011, 2012, 2013):
    a, b = seasons[t], seasons[t + 1]
    n = np.array([v[0] + v[1] for v in a.values()], float); ints = np.array([v[2] for v in a.values()], float)
    mean = ints.sum() / n.sum(); p = ints / n
    obs = np.average((p - mean)**2, weights=n); bino = np.average(mean * (1 - mean) / n, weights=n)
    sig = obs - bino; k = mean * (1 - mean) / sig if sig > 0 else None
    rows = []
    for pid in sorted(set(a) & set(b)):
        if t + 1 >= 2013 and pid in exclude: continue
        na = a[pid][0] + a[pid][1]; ra = a[pid][2] / na
        nb = b[pid][0] + b[pid][1]; rb = b[pid][2] / nb
        sh = ((na * ra + k * mean) / (na + k) - mean) if k else 0.0
        rows.append((ra - mean, rb, nb, sh))
    pairs[t] = rows
    lab = f'{t}->{t+1}'
    for name, idx in (('raw', 0), ('shrunk', 3)):
        if name == 'shrunk' and k is None:
            print(lab, name, 'degenerate (k infinite)'); continue
        a0, b1, se, skill, c = fit([(r[idx], r[1], r[2]) for r in rows])
        jf = J['results'][lab][name]
        print(f'{lab} {name:6s} n={len(rows)} corr {c:.3f} slope {b1:.4f} se {se:.4f} int {a0:.4f} loo {skill:.4f} | first pass slope {jf["slope"]:.4f} loo {jf["loo"]["skill"]:.4f} -> {"match" if abs(b1-jf["slope"])<1e-9 and abs(skill-jf["loo"]["skill"])<1e-9 else "DIFF"}')
    print(f'   reliability k {k if k is None else round(k)} first pass {J["results"][lab]["season_t_reliability"]["k"]}')
pooled = pairs[2010] + pairs[2011]
for name, idx in (('raw', 0), ('shrunk', 3)):
    a0, b1, se, skill, c = fit([(r[idx], r[1], r[2]) for r in pooled])
    jf = J['results']['pooled_2010_2012'][name]
    print(f'pooled {name:6s} n={len(pooled)} corr {c:.3f} slope {b1:.4f} se {se:.4f} int {a0:.4f} loo {skill:.4f} | first pass slope {jf["slope"]:.4f} loo {jf["loo"]["skill"]:.4f} -> {"match" if abs(b1-jf["slope"])<1e-9 and abs(skill-jf["loo"]["skill"])<1e-9 else "DIFF"}')
# predictor spreads for the implied-SD comparison
for lab, rows in (('pooled', pooled),):
    xr = np.array([r[0] for r in rows]); xs = np.array([r[3] for r in rows])
    print('pooled predictor SD raw-dev', xr.std(ddof=1), 'shrunk-dev', xs.std(ddof=1))
for s in (2010, 2011, 2012):
    v = seasons[s]; n = np.array([a + k for a, k, i in v.values()], float); p = np.array([i for a, k, i in v.values()]) / n
    print(s, 'qualifier raw-rate SD', p.std(ddof=1), 'mean dropbacks', n.mean())
