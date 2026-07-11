import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Investment Screener - Fundamentals + Cash Quality")
st.markdown("Real-time financial data from Yahoo Finance. Built with Python.")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Filters")
tickers_input = st.sidebar.text_area("Tickers (comma separated)", "AAPL, MSFT, GOOGL, AMZN, META, NVDA, JPM, JNJ, WMT, KO")
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

min_roe = st.sidebar.slider("Minimum ROE (%)", 0, 100, 10)
min_fcf_margin = st.sidebar.slider("Minimum FCF Margin (%)", 0, 50, 0)
max_pe = st.sidebar.slider("Maximum P/E", 5, 100, 50)
exclude_negative_fcf = st.sidebar.checkbox("Exclude Negative FCF", True)

# --- DATA FETCHING ---
@st.cache_data
def fetch_data(tickers):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        info = stock.info
        try:
            fcf = info.get("freeCashflow")
            op_cf = info.get("operatingCashflow")
            ni = info.get("netIncomeToCommon")
            revenue = info.get("totalRevenue")
            fcf_margin = (fcf / revenue * 100) if fcf and revenue else None
            cf_ni = (op_cf / ni) if (op_cf and ni and ni > 0) else None
            ev = info.get("enterpriseValue")
            ebitda = info.get("ebitda")
            ev_ebitda = (ev / ebitda) if (ev and ebitda and ebitda > 0) else None
            
            data.append({
                "Ticker": ticker,
                "Company": info.get("shortName", ticker),
                "Sector": info.get("sector", "N/A"),
                "Market Cap ($B)": info.get("marketCap", 0) / 1e9,
                "P/E Ratio": info.get("trailingPE"),
                "ROE (%)": info.get("returnOnEquity") * 100 if info.get("returnOnEquity") else None,
                "Revenue Growth (%)": info.get("revenueGrowth") * 100 if info.get("revenueGrowth") else None,
                "FCF Margin (%)": round(fcf_margin, 2) if fcf_margin else None,
                "Debt/Equity": info.get("debtToEquity"),
                "PEG Ratio": info.get("pegRatio"),
                "EV/EBITDA": round(ev_ebitda, 2) if ev_ebitda else None,
                "OCF/Net Income": round(cf_ni, 2) if cf_ni else None,
                "Gross Margin (%)": info.get("grossMargins") * 100 if info.get("grossMargins") else None,
            })
        except:
            pass
    return pd.DataFrame(data)

df = fetch_data(tickers)

# Apply filters
filtered = df[
    (df["ROE (%)"].notna()) & (df["ROE (%)"] >= min_roe) &
    (df["P/E Ratio"].notna()) & (df["P/E Ratio"] > 0) & (df["P/E Ratio"] <= max_pe) &
    (df["FCF Margin (%)"].notna())
]
if exclude_negative_fcf:
    filtered = filtered[filtered["FCF Margin (%)"] > 0]
if min_fcf_margin > 0:
    filtered = filtered[filtered["FCF Margin (%)"] >= min_fcf_margin]

# Sort selector
sort_by = st.selectbox("Sort by", ["ROE (%)", "FCF Margin (%)", "Revenue Growth (%)", "P/E Ratio", "PEG Ratio"])
ascending = st.checkbox("Ascending", False)
filtered = filtered.sort_values(sort_by, ascending=ascending)

# --- MAIN DISPLAY ---
col1, col2 = st.columns([3, 2])
with col1:
    st.subheader("Company Metrics")
    st.dataframe(filtered.style.format({
        "Market Cap ($B)": "{:.1f}",
        "P/E Ratio": "{:.1f}",
        "ROE (%)": "{:.1f}",
        "Revenue Growth (%)": "{:.1f}",
        "FCF Margin (%)": "{:.1f}",
        "Debt/Equity": "{:.1f}",
        "PEG Ratio": "{:.2f}",
    }), use_container_width=True)

with col2:
    st.subheader("Valuation vs Profitability")
    if not filtered.empty:
        fig = px.scatter(
            filtered, x="P/E Ratio", y="ROE (%)", size="Market Cap ($B)",
            color="Sector", hover_name="Ticker", text="Ticker",
            title="P/E vs ROE (bubble size = market cap)"
        )
        fig.update_traces(textposition="top center")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No companies match filters.")

# Download button
csv = filtered.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Screened Data", csv, "screened_stocks.csv", "text/csv")