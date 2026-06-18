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


def fit_ar1(log_returns: 'pd.Series'):
    """Fit a simple AR(1) model to log returns: r_t = phi * r_{t-1} + eps
    Returns phi and residual std.
    """
    import numpy as _np
    y = log_returns.dropna().values
    if len(y) < 2:
        return 0.0, float(_np.std(y) if len(y)>0 else 0.0)
    x = y[:-1]
    y1 = y[1:]
    phi = (x * y1).sum() / (x * x).sum() if (x*x).sum() != 0 else 0.0
    resid = y1 - phi * x
    return float(phi), float(_np.std(resid, ddof=1))


def simulate_ar1(S0: float, log_returns: 'pd.Series', phi: float, resid_sigma: float, steps: int = 252, sims: int = 1000, seed: int = 123):
    """Simulate price paths by simulating log returns with AR(1) dynamics and converting to prices."""
    import numpy as _np
    _np.random.seed(seed)
    last_return = float(log_returns.dropna().iloc[-1]) if len(log_returns.dropna())>0 else 0.0
    paths = _np.zeros((sims, steps+1))
    paths[:,0] = S0
    r_t = _np.full(sims, last_return)
    for t in range(1, steps+1):
        eps = _np.random.normal(loc=0.0, scale=resid_sigma, size=sims)
        r_t = phi * r_t + eps
        # update price: S_t = S_{t-1} * exp(r_t)
        paths[:,t] = paths[:,t-1] * _np.exp(r_t)
    return paths
