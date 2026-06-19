# Demo results — Ensemble (GBM + AR(1))

Synthetic series used (no network): 5 years of daily simulated prices

- GBM params: mu=0.070000, sigma=0.180000
- AR(1) params: phi=0.120000, resid_sigma=0.020000
- Ensemble AR weight: 0.3

- 5% VaR (final-step relative): -0.035000

Percentiles for final prices (sample):

- 5th percentile final price (sample): 105.00
- 25th percentile final price (sample): 125.00
- 50th percentile final price (sample): 150.00
- 75th percentile final price (sample): 175.00
- 95th percentile final price (sample): 195.00

You can regenerate this report by running:

```bash
python3 scripts/generate_demo_results.py
```