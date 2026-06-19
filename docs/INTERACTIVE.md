# Interactive frontend

This document explains the interactive controls in `frontend/index.html` and how to run a small static server to play with the simulations.

Run the local server (this will open your browser):

```bash
python3 scripts/serve_frontend.py --port 8001
```

Controls in the page:
- Symbol: ticker to fetch (or use default `^GSPC`)
- Simulations: number of Monte Carlo simulations
- AR weight: slider (0-1) to blend AR(1) model with GBM
- Load & Simulate: fetches data from the backend and renders percentiles
- Play: animates the simulation time series (shows growth over the horizon)
- Speed: animation frames per second
- VaR display: shows simple 5% Value-at-Risk for the final step

Notes:
- The frontend animation progressively reveals data points across the time axis. It is intended for exploration and demonstration. For large `sims` you may want to reduce the number of returned sample series to keep the browser responsive.
- If you open the frontend directly via the file system and get CORS errors when contacting the backend, use the server above instead.
