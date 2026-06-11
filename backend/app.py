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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/history")
def history(symbol: str, start: str = "2016-01-01", end: str = None):
    try:
        df = fetch_history(symbol, start, end)
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
