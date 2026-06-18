from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

from model import run_monte_carlo, calibrate_gbm
from data_fetch import fetch_history

app = FastAPI(title="Stochastic Market Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimRequest(BaseModel):
    symbol: str
    start: str = "2016-01-01"
    end: str = None
    sims: int = 1000
    steps: int = 252


class PercentileRequest(SimRequest):
    percentiles: List[int] = [5,25,50,75,95]


class BatchRequest(BaseModel):
    symbols: List[str]
    start: str = "2016-01-01"
    end: str = None
    sims: int = 1000
    steps: int = 252
    percentiles: List[int] = [5,25,50,75,95]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/history")
def history(symbol: str, start: str = "2016-01-01", end: str = None):
    try:
        df = fetch_history(symbol, start, end)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate_batch")
def simulate_batch(req: BatchRequest):
    """Run percentile simulations for multiple symbols and return a mapping."""
    from numpy import percentile as _percentile
    out = {}
    for s in req.symbols:
        try:
            df = fetch_history(s, req.start, req.end)
            mu, sigma = calibrate_gbm(df['Close'])
            sims = run_monte_carlo(S0=float(df['Close'].iloc[-1]), mu=mu, sigma=sigma, steps=req.steps, sims=req.sims)
            pct_vals = {}
            for p in req.percentiles:
                pct_vals[str(p)] = _percentile(sims, p, axis=0).tolist()
            out[s] = {"last_price": float(df['Close'].iloc[-1]), "percentiles": pct_vals}
        except Exception as e:
            out[s] = {"error": str(e)}
    return out


class EnsembleRequest(SimRequest):
    ar_weight: float = 0.3  # weight for AR(1) in ensemble (GBM weight = 1 - ar_weight)


@app.post("/ensemble_simulate")
def ensemble_simulate(req: EnsembleRequest):
    """Run GBM and AR1 simulations and return blended percentiles and a simple VaR metric."""
    try:
        import numpy as _np
        df = fetch_history(req.symbol, req.start, req.end)
        # fit GBM
        mu, sigma = calibrate_gbm(df['Close'])
        gbm = run_monte_carlo(S0=float(df['Close'].iloc[-1]), mu=mu, sigma=sigma, steps=req.steps, sims=req.sims)
        # fit AR1
        from model import fit_ar1, simulate_ar1
        logr = _np.log(df['Close']).diff()
        phi, resid_sigma = fit_ar1(logr)
        ar = simulate_ar1(S0=float(df['Close'].iloc[-1]), log_returns=logr, phi=phi, resid_sigma=resid_sigma, steps=req.steps, sims=req.sims)

        # blend
        w = float(req.ar_weight)
        blended = (w * ar) + ((1.0 - w) * gbm)

        # percentiles
        percentiles = {str(p): _np.percentile(blended, p, axis=0).tolist() for p in [5,25,50,75,95]}

        # VaR: simple historical-style VaR at 5% over the final step (loss relative to last price)
        final_prices = blended[:, -1]
        last_price = float(df['Close'].iloc[-1])
        returns = (final_prices - last_price) / last_price
        var5 = float(_np.percentile(returns, 5))

        return {"symbol": req.symbol, "last_price": last_price, "percentiles": percentiles, "var5": var5, "ar_phi": phi, "ar_resid_sigma": resid_sigma}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"symbol": symbol, "data": df.reset_index().to_dict(orient="records")}


@app.post("/simulate")
def simulate(req: SimRequest):
    try:
        df = fetch_history(req.symbol, req.start, req.end)
        mu, sigma = calibrate_gbm(df['Close'])
        sims = run_monte_carlo(S0=float(df['Close'].iloc[-1]), mu=mu, sigma=sigma, steps=req.steps, sims=req.sims)
        # return last simulated prices per sim and time-series for a sample
        sample = sims[: min(20, sims.shape[0]), :].tolist()
        return {"symbol": req.symbol, "last_price": float(df['Close'].iloc[-1]), "mu": mu, "sigma": sigma, "simulations_sample": sample}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate_percentiles")
def simulate_percentiles(req: PercentileRequest):
    try:
        df = fetch_history(req.symbol, req.start, req.end)
        mu, sigma = calibrate_gbm(df['Close'])
        sims = run_monte_carlo(S0=float(df['Close'].iloc[-1]), mu=mu, sigma=sigma, steps=req.steps, sims=req.sims)
        # compute percentiles across sims for each time step
        import numpy as _np
        pct_vals = {}
        for p in req.percentiles:
            vals = _np.percentile(sims, p, axis=0).tolist()
            pct_vals[str(p)] = vals
        # return percentiles and the historical tail
        return {"symbol": req.symbol, "last_price": float(df['Close'].iloc[-1]), "percentiles": pct_vals, "steps": req.steps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
