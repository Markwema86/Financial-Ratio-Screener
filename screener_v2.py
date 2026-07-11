import yfinance as yf
import pandas as pd

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "JPM", "JNJ", "WMT", "KO"]

data = []

for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    try:
        company_name = info.get("shortName", ticker)
        sector = info.get("sector", "N/A")
        market_cap = info.get("marketCap", None)
        
        # ---- V1 metrics ----
        pe_ratio = info.get("trailingPE", None)
        roe = info.get("returnOnEquity", None)
        revenue_growth = info.get("revenueGrowth", None)
        debt_to_equity = info.get("debtToEquity", None)
        dividend_yield = info.get("dividendYield", None)
        if dividend_yield:
            dividend_yield = dividend_yield * 100
        
        # ---- V2 NEW METRICS ----
        # Free Cash Flow
        free_cashflow = info.get("freeCashflow", None)
        operating_cashflow = info.get("operatingCashflow", None)
        
        # Earnings (net income) for quality check
        net_income = info.get("netIncomeToCommon", None)
        
        # Enterprise Value (better than market cap for valuation)
        enterprise_value = info.get("enterpriseValue", None)
        
        # EBITDA for EV/EBITDA ratio
        ebitda = info.get("ebitda", None)
        
        # Gross margin
        gross_margins = info.get("grossMargins", None)
        
        # PEG ratio (P/E divided by growth rate — measures value adjusted for growth)
        peg_ratio = info.get("pegRatio", None)
        
        # Return on Invested Capital (more reliable than ROE)
        roic = info.get("returnOnCapital", None)
        
        # ---- CALCULATED METRICS ----
        # Free Cash Flow Margin: what % of revenue becomes usable cash
        fcf_margin = None
        if free_cashflow and info.get("totalRevenue"):
            fcf_margin = (free_cashflow / info["totalRevenue"]) * 100
        
        # Cash Flow to Net Income ratio (earnings quality check)
        cf_to_ni = None
        if operating_cashflow and net_income and net_income > 0:
            cf_to_ni = operating_cashflow / net_income
        
        # EV/EBITDA (better valuation metric than P/E for debt-heavy companies)
        ev_ebitda = None
        if enterprise_value and ebitda and ebitda > 0:
            ev_ebitda = enterprise_value / ebitda
        
        # ---- RED FLAGS ----
        red_flags = []
        
        # Negative equity warning (like Coke)
        if debt_to_equity and debt_to_equity > 100:
            red_flags.append("Extreme D/E (>100): likely negative equity situation")
        
        # Cash flow warning
        if cf_to_ni and cf_to_ni < 0.5:
            red_flags.append(f"Low cash conversion (OCF/NI = {cf_to_ni:.2f})")
        
        # Negative FCF
        if free_cashflow and free_cashflow < 0:
            red_flags.append("Negative Free Cash Flow")
        
        # Overvalued growth check
        if peg_ratio and peg_ratio > 3:
            red_flags.append(f"High PEG ({peg_ratio:.1f}): expensive relative to growth")
        
        data.append({
            "Ticker": ticker,
            "Company": company_name,
            "Sector": sector,
            "Market Cap ($B)": round(market_cap / 1e9, 2) if market_cap else None,
            
            # V1
            "P/E Ratio": round(pe_ratio, 2) if pe_ratio else None,
            "ROE (%)": round(roe * 100, 2) if roe else None,
            "Revenue Growth (%)": round(revenue_growth * 100, 2) if revenue_growth else None,
            "Debt/Equity": round(debt_to_equity, 2) if debt_to_equity else None,
            
            # V2 new metrics
            "FCF Margin (%)": round(fcf_margin, 2) if fcf_margin else None,
            "OCF/Net Income": round(cf_to_ni, 2) if cf_to_ni else None,
            "EV/EBITDA": round(ev_ebitda, 2) if ev_ebitda else None,
            "Gross Margin (%)": round(gross_margins * 100, 2) if gross_margins else None,
            "PEG Ratio": round(peg_ratio, 2) if peg_ratio else None,
            "ROIC (%)": round(roic * 100, 2) if roic else None,
            
            "RED FLAGS": "; ".join(red_flags) if red_flags else "None"
        })
        
    except Exception as e:
        print(f"Couldn't fetch data for {ticker}: {e}")

df = pd.DataFrame(data)

# ---- IMPROVED SCREENING ----
# Now we care about: profitability, reasonable valuation, AND cash generation
screened = df[
    (df["P/E Ratio"] > 0) &
    (df["P/E Ratio"] < 50) &
    (df["ROE (%)"] > 0) &
    (df["Revenue Growth (%)"] > 0) &
    # V2 addition: must generate positive cash flow
    (df["FCF Margin (%)"].notna()) &
    (df["FCF Margin (%)"] > 0)
].copy()

# ---- NEW SCORING: multi-dimensional ----
# We rank across: profitability (ROE), value (P/E), growth, cash quality
screened["ROE Rank"] = screened["ROE (%)"].rank(ascending=False)
screened["PE Rank"] = screened["P/E Ratio"].rank(ascending=True)
screened["Growth Rank"] = screened["Revenue Growth (%)"].rank(ascending=False)
screened["FCF Rank"] = screened["FCF Margin (%)"].rank(ascending=False)

# Equal-weighted composite (you can adjust weights later)
screened["Composite Score"] = (
    screened["ROE Rank"] + 
    screened["PE Rank"] + 
    screened["Growth Rank"] + 
    screened["FCF Rank"]
)

screened = screened.sort_values("Composite Score")

# ---- DISPLAY ----
print("\n" + "="*100)
print("INVESTMENT SCREENER V2")
print("Scoring: Profitability (ROE) + Value (P/E) + Growth + Cash Generation (FCF)")
print("="*100)

print("\n--- ALL COMPANIES WITH V2 METRICS ---")
display_cols = ["Ticker", "Company", "Sector", "P/E Ratio", "ROE (%)", "Revenue Growth (%)",
                "FCF Margin (%)", "EV/EBITDA", "PEG Ratio", "ROIC (%)", "RED FLAGS"]
print(df[display_cols].to_string(index=False))

print("\n--- SCREENED & RANKED (positive FCF required) ---")
result_cols = ["Ticker", "Company", "Sector", "P/E Ratio", "ROE (%)", 
               "Revenue Growth (%)", "FCF Margin (%)", "PEG Ratio", 
               "Composite Score", "RED FLAGS"]
print(screened[result_cols].to_string(index=False))

print("\n--- RED FLAG SUMMARY ---")
for _, row in df.iterrows():
    if row["RED FLAGS"] != "None":
        print(f"⚠️  {row['Ticker']} ({row['Company']}): {row['RED FLAGS']}")