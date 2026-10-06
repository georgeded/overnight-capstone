# Overnight vs intraday returns

Capstone project for the Imperial DSA course. It tests whether US equity returns earned overnight (close to next open) differ from returns earned during the trading day (open to close), and whether a strategy that holds only overnight survives realistic trading costs.

## Data

- CRSP daily stock file (WRDS): open and close prices, dividends, split adjustments
- TAQ / Intraday Indicators (WRDS): bid-ask spreads and opening and closing auction prices
- VIX and the 3-month T-bill rate (CBOE and FRED)
- yfinance as a quick first check and a second source to compare against CRSP

WRDS credentials are read from `~/.pgpass` and are never stored in this repo.

## Layout

- `notebook.ipynb` - main analysis
- `report.md` - written report
- `src/` - download and cleaning scripts
- `data/raw/`, `data/processed/` - local data snapshots (not tracked)
- `plan/` - project plan and sanity checks
