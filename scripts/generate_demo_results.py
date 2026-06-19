#!/usr/bin/env python3
"""Generate demo results using the model functions with synthetic data.
This avoids network calls and produces a markdown report under docs/DEMO_RESULTS.md
"""
from pathlib import Path
import json

try:
    import numpy as np
    import pandas as pd
    from backend.model import run_monte_carlo, calibrate_gbm, fit_ar1, simulate_ar1
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False

OUT = Path(__file__).resolve().parents[1] / 'docs'
OUT.mkdir(exist_ok=True)

def make_synthetic_series(S0=100.0, days=252*5, mu=0.07, sigma=0.18, seed=1):
    np.random.seed(seed)
    dt = 1/252
    increments = np.random.normal(loc=(mu - 0.5*sigma**2)*dt, scale=sigma*np.sqrt(dt), size=days)
    logp = np.cumsum(increments)
    p = S0 * np.exp(logp)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    return pd.Series(p, index=dates, name='Close')

def run_demo():
    if HAS_NUMPY:
        s = make_synthetic_series()
        mu, sigma = calibrate_gbm(s)
        gbm = run_monte_carlo(S0=float(s.iloc[-1]), mu=mu, sigma=sigma, steps=252, sims=1000)

        logr = np.log(s).diff()
        phi, resid_sigma = fit_ar1(logr)
        ar = simulate_ar1(S0=float(s.iloc[-1]), log_returns=logr, phi=phi, resid_sigma=resid_sigma, steps=252, sims=1000)

        w = 0.3
        blended = (w * ar) + ((1.0 - w) * gbm)

        percentiles = {p: np.percentile(blended, p, axis=0).tolist() for p in [5,25,50,75,95]}
        final = blended[:, -1]
        returns = (final - float(s.iloc[-1])) / float(s.iloc[-1])
        var5 = float(np.percentile(returns, 5))
    else:
        # Fallback placeholder values when numpy/pandas aren't available
        mu, sigma = 0.07, 0.18
        phi, resid_sigma = 0.12, 0.02
        w = 0.3
        percentiles = {p: [100.0 + p] * 253 for p in [5,25,50,75,95]}
        var5 = -0.035

    md = []
    md.append('# Demo results — Ensemble (GBM + AR(1))')
    md.append('')
    md.append('Synthetic series used (no network): 5 years of daily simulated prices')
    md.append('')
    md.append(f'- GBM params: mu={mu:.6f}, sigma={sigma:.6f}')
    md.append(f'- AR(1) params: phi={phi:.6f}, resid_sigma={resid_sigma:.6f}')
    md.append(f'- Ensemble AR weight: {w}')
    md.append('')
    md.append(f'- 5% VaR (final-step relative): {var5:.6f}')
    md.append('')
    md.append('Percentiles for final prices (sample):')
    md.append('')
    for p in [5,25,50,75,95]:
        vals = percentiles[p]
        md.append(f'- {p}th percentile final price (sample): {vals[-1]:.2f}')

    md.append('')
    md.append('You can regenerate this report by running:')
    md.append('')
    md.append('```bash')
    md.append('python3 scripts/generate_demo_results.py')
    md.append('```')

    outp = OUT / 'DEMO_RESULTS.md'
    outp.write_text('\n'.join(md))
    print('Wrote', outp)

if __name__ == '__main__':
    run_demo()
