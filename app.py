# app.py
import yfinance as yf
import pandas as pd
import streamlit as st
import datetime

st.set_page_config(layout="wide")
st.title("📊 Relative Strength Analysis: Sectors vs NIFTY 50")

# ✅ Sector mapping as a clean dictionary
sector_symbols = {
    "IT": "^CNXIT",
    "BANK": "^NSEBANK",
    "FMCG": "^CNXFMCG",
    "AUTO": "^CNXAUTO",
    "PHARMA": "^CNXPHARMA",
    "METAL": "^CNXMETAL",
    "REALTY": "^CNXREALTY",
    "NIFTY_50": "^NSEI"
}

# Sidebar
st.sidebar.header("🕒 Time Range for Analysis")
lookback_days = st.sidebar.selectbox("Lookback Period (in days):", [30, 60, 90, 180, 365], index=2)

end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=lookback_days)
st.sidebar.markdown(f"**From:** {start_date}  \n**To:** {end_date}")

# ✅ Fetch data function
@st.cache_data
def fetch_price_data(symbols_dict, start, end):
    all_data = []
    for label, symbol in symbols_dict.items():
        df = yf.download(symbol, start=start, end=end)
        if not df.empty:
            df = df[['Close']].copy()
            df.rename(columns={"Close": label}, inplace=True)
            all_data.append(df)
    if not all_data:
        return pd.DataFrame()
    return pd.concat(all_data, axis=1)

# ✅ Fetch price data
st.info("📡 Fetching data from Yahoo Finance...")
data = fetch_price_data(sector_symbols, start_date, end_date)

if data.empty or "NIFTY_50" not in data.columns:
    st.error("❌ Failed to load NIFTY or sector data.")
    st.stop()

# ✅ Calculate RS values
rs_df = data.drop(columns=["NIFTY_50"]).div(data["NIFTY_50"], axis=0)

# ✅ Show RS trend
st.subheader("📈 Relative Strength Trend (Sector / NIFTY)")
st.line_chart(rs_df)

# ✅ Show RS percentage change
st.subheader(f"🏆 RS % Change over {lookback_days} Days")
rs_change = rs_df.iloc[-1] / rs_df.iloc[0] - 1
rs_change = rs_change.sort_values(ascending=False)
st.dataframe(rs_change.map(lambda x: f"{x:.2%}"))

# ✅ Show outperforming sectors
st.subheader("✅ Outperforming Sectors")
outperformers = rs_change[rs_change > 0]
if not outperformers.empty:
    st.write(outperformers.map(lambda x: f"{x:.2%}"))
else:
    st.info("No sectors are currently outperforming NIFTY in this period.")

# ✅ Download button
st.download_button(
    label="📥 Download RS Summary as CSV",
    data=rs_change.to_csv().encode("utf-8"),
    file_name="relative_strength_summary.csv",
    mime="text/csv"
)
