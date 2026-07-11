import yfinance as yf
import pandas as pd

# List of companies to screen (feel free to add more)
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "JPM", "JNJ", "WMT", "KO"]

data = []

for ticker in tickers:
    stock = yf.Ticker(ticker)
    
    # Get key financial data
    info = stock.info
    
    # Extract what we need (with error handling)
    try:
        company_name = info.get("shortName", ticker)
        sector = info.get("sector", "N/A")
        market_cap = info.get("marketCap", None)  # in dollars
        
        # Valuation ratio: Price to Earnings (P/E)
        pe_ratio = info.get("trailingPE", None)
        
        # Profitability ratio: Return on Equity (ROE)
        roe = info.get("returnOnEquity", None)
        
        # Growth indicator: Revenue Growth (YoY)
        revenue_growth = info.get("revenueGrowth", None)
        
        # Debt safety: Debt to Equity
        debt_to_equity = info.get("debtToEquity", None)
        
        # Dividend yield (for income investors)
        dividend_yield = info.get("dividendYield", None)
        if dividend_yield:
            dividend_yield = dividend_yield * 100  # convert to percentage
        
        data.append({
            "Ticker": ticker,
            "Company": company_name,
            "Sector": sector,
            "Market Cap ($B)": round(market_cap / 1e9, 2) if market_cap else None,
            "P/E Ratio": round(pe_ratio, 2) if pe_ratio else None,
            "ROE (%)": round(roe * 100, 2) if roe else None,
            "Revenue Growth (%)": round(revenue_growth * 100, 2) if revenue_growth else None,
            "Debt/Equity": round(debt_to_equity, 2) if debt_to_equity else None,
            "Dividend Yield (%)": round(dividend_yield, 2) if dividend_yield else None
        })
        
    except Exception as e:
        print(f"Couldn't fetch data for {ticker}: {e}")

# Create DataFrame
df = pd.DataFrame(data)

# ---- SCREENING LOGIC ----
# We'll filter for companies that are:
# 1. Profitable (positive P/E)
# 2. Have reasonable valuation (P/E under 50, no negative)
# 3. Have positive ROE
# 4. Revenue is actually growing

screened = df[
    (df["P/E Ratio"] > 0) &
    (df["P/E Ratio"] < 50) &
    (df["ROE (%)"] > 0) &
    (df["Revenue Growth (%)"] > 0)
].copy()

# Rank them: lower P/E is "cheaper", higher ROE is "more profitable"
# We'll create a simple score: rank by ROE (higher better) + rank by P/E (lower better)
screened["ROE Rank"] = screened["ROE (%)"].rank(ascending=False)
screened["PE Rank"] = screened["P/E Ratio"].rank(ascending=True)
screened["Composite Score"] = screened["ROE Rank"] + screened["PE Rank"]

# Sort by composite score (lower is better)
screened = screened.sort_values("Composite Score")

# ---- DISPLAY ----
print("\n" + "="*80)
print("INVESTMENT SCREENER RESULTS")
print("Ranked by: High Profitability (ROE) + Reasonable Valuation (Low P/E)")
print("="*80)
print("\nAll companies fetched:")
print(df.to_string(index=False))

print("\n\nScreened & Ranked (positive P/E, growing revenue, profitable):")
print(screened[["Ticker", "Company", "Sector", "P/E Ratio", "ROE (%)", 
                "Revenue Growth (%)", "Debt/Equity", "Composite Score"]].to_string(index=False))