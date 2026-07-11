# Financial-Ratio-Screener

A small Python-based investment screener that fetches financial metrics from Yahoo Finance and ranks companies by profitability, valuation, growth, and cash-generation quality. Includes an interactive Streamlit app (app.py) for exploration and two command-line screening scripts (screener.py and screener_v2.py) that demonstrate progressive screening logic and additional metrics for earnings/cash-quality checks.

## What this is
A lightweight toolkit for screening publicly traded companies using Yahoo Finance data. It helps investors and analysts quickly compare valuation (P/E, EV/EBITDA), profitability (ROE, ROIC), growth (revenue growth), and cash-quality (free cash flow margin, OCF/Net Income) across a list of tickers.

### Stack
- **Language(s):** Python (primary)
- **Framework / runtime:** Streamlit for the interactive UI
- **Notable libraries:** yfinance (data source), pandas (data manipulation), plotly (visualization), streamlit (UI)

## How it's organized
````
app.py                          # Streamlit interactive application (main UI)
Screener scripts
  screener.py                   # v1: simple screening (P/E, ROE, revenue growth) + composite score
  screener_v2.py                # v2: adds cash-quality metrics (FCF margin, OCF/NI, EV/EBITDA), red-flags, improved scoring
Technology Sector Investment Thesis Report.docx  # Supporting doc (binary) included in repo root
README.md                       # This file
````

How it fits together: The core data flow is: 1) fetch company data from Yahoo Finance via yfinance (calls to ticker.info), 2) compute derived metrics (FCF margin, EV/EBITDA, OCF/Net Income, etc.), 3) apply screening filters and ranking rules, and 4) present results either in the console (screener scripts) or in the Streamlit interactive UI (app.py). screener_v2.py builds on screener.py by introducing cash-quality checks and red-flag warnings.

## Key files and responsibilities
- app.py: Interactive Streamlit app. Lets the user enter tickers, choose filters (min ROE, min FCF margin, max P/E, exclude negative FCF), sort results, visualize P/E vs ROE, and download screened data as CSV. Uses caching for fetched data.
- screener.py: Command-line/script version that demonstrates a basic screening approach and a simple composite score (ROE rank + P/E rank).
- screener_v2.py: An enhanced script that calculates additional metrics for earnings and cash-quality (free cash flow, operating cash flow, OCF/Net Income), computes EV/EBITDA, PEG, ROIC, flags red conditions (e.g., high D/E, low cash conversion, negative FCF), and scores across four dimensions (ROE, P/E, Growth, FCF).
- Technology Sector Investment Thesis Report.docx: Supplementary document included in the repo; not parsed by the scripts but useful as a reference for strategy and assumptions.

## How to run it
Requirements: Python 3.8+ recommended. The project relies on these Python packages:
- streamlit
- yfinance
- pandas
- plotly

Install quickly with pip:

```bash
python -m pip install --upgrade pip
python -m pip install streamlit yfinance pandas plotly
```

Run the interactive Streamlit app (recommended for exploration):

```bash
streamlit run app.py
```

Run the screening scripts from the command line (prints results to stdout):

```bash
python screener.py
# or
python screener_v2.py
```

Notes:
- yfinance relies on Yahoo Finance public endpoints and may be rate-limited for large lists of tickers or frequent calls. The Streamlit app uses @st.cache_data to reduce repeat requests during a session.
- Metric availability depends on what Yahoo Finance returns for each ticker; some fields may be None and are handled in the code with guards.

## Metrics computed (what they mean)
- P/E Ratio (trailingPE): Price divided by trailing twelve months earnings. Lower suggests cheaper relative to earnings.
- EV/EBITDA: Enterprise value divided by EBITDA. Useful for valuation comparisons that account for debt.
- ROE (%): Return on Equity. A profitability measure showing how effectively a company turns equity into profit.
- ROIC (%): Return on Invested Capital. Similar to ROE but focuses on total capital employed.
- Revenue Growth (%): Year-on-year revenue change (where Yahoo supplies it).
- FCF Margin (%): Free cash flow divided by revenue. Shows how much of revenue converts to free cash.
- OCF/Net Income: Operating cash flow divided by net income — an earnings-quality indicator (values < 1 may indicate weaker cash conversion).
- PEG Ratio: P/E divided by growth rate. Contextualizes valuation by expected growth.

## Screening logic summary
- screener.py (v1): Keeps tickers with positive P/E < 50, positive ROE, and positive revenue growth. Ranks by composite score combining ROE (higher is better) and P/E (lower is better).
- screener_v2.py (v2): Requires positive FCF margin in addition to the v1 filters, computes multi-dimensional ranks across ROE, P/E, Growth, and FCF, and produces a composite score. Also generates red-flag messages for items like negative FCF, low cash conversion, extreme D/E, or high PEG.
- app.py (Streamlit): Allows interactive filtering by ROE, FCF margin, P/E and can exclude negative FCF. Provides tabular view and an interactive P/E vs ROE bubble chart.

## Limitations & caveats
- Data source: yfinance scrapes Yahoo Finance summary data; it is not a replacement for official filings or a financial data provider with guaranteed completeness/accuracy. Always cross-check before making investment decisions.
- Field availability: Some tickers (especially small or foreign companies) may lack fields like freeCashflow or enterpriseValue. The scripts defensively handle missing fields but results will vary by ticker.
- No persistence: This repo fetches data at runtime; it does not store historical snapshots. If you need history, consider adding caching to disk or integrating a data provider that supports bulk historical downloads.

## Contributing
Contributions welcome. Ideas:
- Add a requirements.txt or pyproject.toml for reproducible installs
- Add tests for metric calculations and guardrails around missing fields
- Add rate-limit/backoff logic when fetching many tickers
- Support bulk ticker input from CSV or watchlists (instead of inline lists)
- Add unit tests and CI for formatting/quality

## Try asking
- "Can you add a requirements.txt with pinned versions and a GitHub Actions workflow to run basic linting?"
- "Where in the code is FCF Margin computed, and can it be adjusted to use a trailing-12-months calculation from cash flow statements?"
- "How would I add support for reading tickers from a CSV file and preserving previous results to compare change over time?"

---

Licensed under the terms you prefer. (Add a LICENSE file if you want to make the project open-source.)
