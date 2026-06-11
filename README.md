# Stochastic Market Prediction

Lightweight project that demonstrates fetching historical market data and running Monte Carlo Geometric Brownian Motion simulations to predict future prices for indices like the S&P 500 and major ETFs.

Contents:
- `backend/` - FastAPI service that fetches data (yfinance) and runs simulations.
- `frontend/` - Static HTML + Chart.js front-end to view history and sample simulations.

Important: This repository intentionally gitignores secrets and model provider keys. Do not commit API keys or credentials. See `.gitignore`.

Quick start (macOS, zsh):

1. Create a Python virtual environment and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Start the backend

```bash
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

3. Open `frontend/index.html` in your browser (or serve it with a simple static server). The frontend expects the API at `http://localhost:8000`.

Notes and caveats
- This is a demonstration. The Monte Carlo GBM model is simplistic and not financial advice.
- `yfinance` relies on live network access. If there are fetch errors, check your network or symbol spelling.
- The `.env.example` shows how to keep secrets locally; never commit actual keys.

Next steps (suggestions):
- Add caching of fetched data.
- Add parameter controls for time horizon, confidence intervals, and export.
- Harden the frontend and provide a small Node static server for CORS-free operation.
