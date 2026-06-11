import numpy as np
import pandas as pd

def calibrate_gbm(price_series: pd.Series):
    """Estimate drift (mu) and volatility (sigma) from log returns."""
    returns = np.log(price_series).diff().dropna()
    mu = returns.mean() * 252  # annualized
    sigma = returns.std(ddof=1) * np.sqrt(252)  # annualized
    return float(mu), float(sigma)


def run_monte_carlo(S0: float, mu: float, sigma: float, steps: int = 252, sims: int = 1000, seed: int = 42):
    """Run geometric brownian motion Monte Carlo. Returns array shape (sims, steps+1)."""
    np.random.seed(seed)
    dt = 1/steps
    # simulate increments
    increments = np.random.normal(loc=(mu - 0.5 * sigma**2) * dt, scale=sigma * np.sqrt(dt), size=(sims, steps))
    log_paths = np.cumsum(increments, axis=1)
    # prepend zeros for t0
    log_paths = np.concatenate([np.zeros((sims,1)), log_paths], axis=1)
    paths = S0 * np.exp(log_paths)
    return paths
