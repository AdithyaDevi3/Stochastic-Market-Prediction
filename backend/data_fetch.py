import yfinance as yf
import pandas as pd

def fetch_history(symbol: str, start: str = "2016-01-01", end: str = None) -> pd.DataFrame:
    """Fetch historical OHLCV data for a symbol using yfinance."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, auto_adjust=False)
    if df is None or df.empty:
        raise RuntimeError(f"No data for symbol {symbol}")
    # ensure Close column exists
    if 'Close' not in df.columns:
        raise RuntimeError("Missing Close column in fetched data")
    return df[['Open','High','Low','Close','Volume']]
