import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

def generate_pdf_report(title, details, metrics):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    styles["Normal"].fontName = "DejaVu"
    styles["Title"].fontName = "DejaVu"
    styles["Heading2"].fontName = "DejaVu"
    story = []

    story.append(Paragraph(
        "<b>TRENDPULSE</b>",
        styles["Title"]
    ))
    story.append(Paragraph(
        "Investment Research Report",
        styles["Heading2"]
    ))
    story.append(Spacer(1, 15))

    story.append(Paragraph(
        f"<b>Investment:</b> {title}",
        styles["Normal"]
    ))
    story.append(Paragraph(
        f"<b>Report generated:</b> {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        styles["Normal"]
    ))

    story.append(Spacer(1, 15))
    story.append(Paragraph("Investment Details", styles["Heading2"]))

    detail_data = [["Parameter", "Details"]]
    for key, value in details.items():
        detail_data.append([str(key), str(value)])

    detail_table = Table(detail_data, colWidths=[180, 300])
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(detail_table)

    story.append(Spacer(1, 15))
    story.append(Paragraph("Performance Metrics", styles["Heading2"]))

    metric_data = [["Metric", "Value"]]
    for key, value in metrics.items():
        metric_data.append([str(key), str(value)])

    metric_table = Table(metric_data, colWidths=[180, 300])
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(metric_table)

    story.append(Spacer(1, 20))
    story.append(Paragraph("Research Limitations", styles["Heading2"]))
    story.append(Paragraph(
        "Historical performance does not guarantee future results. "
        "Risk metrics and forecasts are experimental research outputs. "
        "Market data availability depends on the data provider. "
        "This report is for educational and research purposes only "
        "and is not investment advice.",
        styles["Normal"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import requests
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

st.set_page_config(page_title="TrendPulse | Investment Research", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 2.2rem; max-width: 1450px;}
.hero {padding: 1.35rem 1.5rem; border-radius: 18px; margin-bottom: 1rem;
background: linear-gradient(115deg, #14243b, #234a68); color: white;}
.hero h1 {color: white; margin: 0; font-size: 2.1rem;}
.hero p {color: #e4edf7; margin: .35rem 0 0 0; font-size: 1rem;}
[data-testid="stMetric"] {background: #263247 !important; border: 1px solid #43516a !important;
border-radius: 14px !important; padding: 15px 17px !important; min-width: 0 !important; min-height: 104px;}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p {white-space: normal !important;
overflow-wrap: anywhere !important; color: #e8eef8 !important; font-weight: 650 !important;}
[data-testid="stMetricValue"] {color: #ffffff !important; font-weight: 800 !important;
white-space: normal !important; overflow-wrap: anywhere !important; font-size: clamp(1.15rem, 2.4vw, 2rem) !important;}
[data-testid="stMetricDelta"] {color: #b8f2cf !important;}
div[data-testid="stTabs"] button {font-weight: 650; white-space: normal;}
div[data-testid="stAlert"] {border-radius: 12px;}
@media (max-width: 700px) {
.block-container {padding-left: .8rem; padding-right: .8rem;}
.hero {padding: 1rem;} .hero h1 {font-size: 1.65rem;}
[data-testid="stMetric"] {padding: 11px 12px !important; min-height: 92px;}
[data-testid="stMetricValue"] {font-size: 1.25rem !important;}
h1 {font-size: 1.65rem !important;} h2 {font-size: 1.4rem !important;}
}
</style>
""", unsafe_allow_html=True)

US_STOCKS = {
    "Apple": "AAPL", "Microsoft": "MSFT", "Alphabet (Google)": "GOOGL",
    "Amazon": "AMZN", "Tesla": "TSLA", "NVIDIA": "NVDA",
    "Meta Platforms": "META", "Netflix": "NFLX"
}
NSE_STOCKS = {
    "Reliance Industries": "RELIANCE.NS", "Tata Consultancy Services": "TCS.NS",
    "Infosys": "INFY.NS", "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS", "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS", "ITC": "ITC.NS"
}
BSE_STOCKS = {
    "Reliance Industries": "RELIANCE.BO", "Tata Consultancy Services": "TCS.BO",
    "Infosys": "INFY.BO", "HDFC Bank": "HDFCBANK.BO",
    "ICICI Bank": "ICICIBANK.BO", "State Bank of India": "SBIN.BO",
    "Bharti Airtel": "BHARTIARTL.BO", "ITC": "ITC.BO"
}
INDIA_ETFS = {
    "Gold BeES": "GOLDBEES.NS", "SBI Gold ETF": "SETFGOLD.NS",
    "HDFC Gold ETF": "HDFCGOLD.NS", "Nippon India Silver ETF": "SILVERBEES.NS",
    "Nifty 50 ETF (Nippon)": "NIFTYBEES.NS", "Bank Nifty ETF (Nippon)": "BANKBEES.NS",
    "CPSE ETF": "CPSEETF.NS", "Bharat Bond ETF 2033": "EBBETF0433.NS"
}
GLOBAL_ETFS = {
    "S&P 500 ETF (SPDR)": "SPY", "Nasdaq 100 ETF (Invesco)": "QQQ",
    "Gold ETF (SPDR)": "GLD", "Gold ETF (iShares)": "IAU",
    "US Treasury Bond ETF (iShares)": "TLT", "Total US Stock Market ETF (Vanguard)": "VTI"
}

st.markdown("""
<div class="hero"><h1>📈 TrendPulse</h1>
<p>Understand investments through market data, financial news and experimental AI analysis.</p></div>
""", unsafe_allow_html=True)
st.caption("Educational research tool • Not investment advice • Forecasts are experimental")
st.info("Start in the left panel: choose an investment type, market and instrument. Use the tabs to explore its history, news and AI analysis.")

st.sidebar.title("🔎 Explore TrendPulse")
st.sidebar.caption("Choose an investment to begin. You can change it anytime.")
asset_class = st.sidebar.selectbox("1. What would you like to explore?",
    ["Stocks", "Exchange-Traded Funds (ETFs)", "Mutual Funds"])

if asset_class == "Stocks":
    market = st.sidebar.selectbox("2. Select market", ["US / International", "India — NSE", "India — BSE", "Custom ticker"])
    if market == "US / International":
        company = st.sidebar.selectbox("3. Choose a company", list(US_STOCKS.keys())); ticker = US_STOCKS[company]
    elif market == "India — NSE":
        company = st.sidebar.selectbox("3. Choose a company", list(NSE_STOCKS.keys())); ticker = NSE_STOCKS[company]
    elif market == "India — BSE":
        company = st.sidebar.selectbox("3. Choose a company", list(BSE_STOCKS.keys())); ticker = BSE_STOCKS[company]
    else:
        ticker = st.sidebar.text_input("3. Enter stock ticker", "AAPL").upper().strip(); company = ticker
    data_kind = "Market-traded stock"
elif asset_class == "Exchange-Traded Funds (ETFs)":
    etf_market = st.sidebar.selectbox("2. Select ETF market", ["India", "US / International"])
    etf_map = INDIA_ETFS if etf_market == "India" else GLOBAL_ETFS
    company = st.sidebar.selectbox("3. Choose an ETF", list(etf_map.keys())); ticker = etf_map[company]
    data_kind = "Exchange-traded fund"
else:
    import requests

    st.sidebar.subheader("🇮🇳 Indian Mutual Funds")

    mf_mode = st.sidebar.radio(
        "Analysis mode",
        ["Single Fund Analysis", "Compare Mutual Funds"]
    )
    fund_query = st.sidebar.text_input(
        "2. Search mutual fund",
        "Parag Parikh Flexi Cap"
    )

    @st.cache_data(ttl=900)
    def search_mutual_funds(query):
        try:
            response = requests.get(
                "https://mfnav.in/api/funds/search",
                params={"q": query},
                timeout=20
            )
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            st.error(f"Fund search failed: {e}")
            return []

    funds = search_mutual_funds(fund_query) if fund_query.strip() else []

    if not funds:
        st.warning("No funds found. Try another fund name.")
        st.stop()

    fund_options = {
        item["scheme_name"]: item["scheme_code"]
        for item in funds
    }

    if mf_mode == "Single Fund Analysis":
        company = st.sidebar.selectbox(
            "3. Select fund",
            list(fund_options.keys())
        )
        scheme_code = fund_options[company]
        ticker = str(scheme_code)
    else:
        selected_funds = st.sidebar.multiselect(
            "3. Select up to 4 funds",
            list(fund_options.keys()),
            default=list(fund_options.keys())[:2]
        )
        if len(selected_funds) > 4:
            st.sidebar.warning("Please select a maximum of 4 funds.")

    data_kind = "Indian mutual fund NAV"

    period = st.sidebar.selectbox(
        "Historical data period",
        ["1y", "2y", "5y"],
        index=2
    )
    horizon = 5
    uploaded_news = None

    @st.cache_data(ttl=900)
    def fetch_mutual_fund_nav(code):
        try:
            response = requests.get(
                f"https://mfnav.in/api/nav/{code}",
                params={"page": 1, "page_size": 5000},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            frame = pd.DataFrame(result.get("data", []))
            if frame.empty:
                return pd.DataFrame(), result.get("fund_details", {})

            frame["Date"] = pd.to_datetime(frame["nav_date"])
            frame["Close"] = pd.to_numeric(frame["nav"], errors="coerce")
            frame = frame[["Date", "Close"]].dropna()
            frame = frame.sort_values("Date").reset_index(drop=True)

            return frame, result.get("fund_details", {})
        except Exception as e:
            st.error(f"NAV download failed: {e}")
            return pd.DataFrame(), {}


    if mf_mode == "Compare Mutual Funds":
        st.title("📊 Mutual Fund Comparison")
        st.caption("Compare historical performance and risk of Indian mutual funds.")

        if len(selected_funds) < 2:
            st.warning("Please select at least 2 mutual funds.")
            st.stop()

        period_days = {"1y": 365, "2y": 730, "5y": 1825}
        cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(
            days=period_days[period]
        )

        comparison_rows = []
        nav_series = []

        for fund_name in selected_funds:
            fund_code = fund_options[fund_name]
            fund_data, details = fetch_mutual_fund_nav(fund_code)

            if fund_data.empty:
                st.warning(f"Could not load NAV data for {fund_name}.")
                continue

            fund_data = fund_data[fund_data["Date"] >= cutoff].copy()
            fund_data = fund_data.sort_values("Date")

            if len(fund_data) < 2:
                st.warning(f"Not enough historical data for {fund_name}.")
                continue

            first_nav = fund_data["Close"].iloc[0]
            latest_nav = fund_data["Close"].iloc[-1]

            total_return = (latest_nav / first_nav - 1) * 100

            years = (
                fund_data["Date"].iloc[-1] -
                fund_data["Date"].iloc[0]
            ).days / 365.25

            cagr = (
                ((latest_nav / first_nav) ** (1 / years) - 1) * 100
                if years > 0 else 0
            )

            daily_returns = fund_data["Close"].pct_change().dropna()
            volatility = daily_returns.std() * (252 ** 0.5) * 100

            peak = fund_data["Close"].cummax()
            drawdown = (fund_data["Close"] / peak - 1) * 100
            max_drawdown = drawdown.min()

            comparison_rows.append({
                "Mutual Fund": fund_name,
                "Latest NAV (₹)": latest_nav,
                "Total Return (%)": total_return,
                "CAGR (%)": cagr,
                "Annualized Volatility (%)": volatility,
                "Maximum Drawdown (%)": max_drawdown
            })

            normalized = fund_data[["Date", "Close"]].copy()
            normalized[fund_name] = (
                normalized["Close"] / first_nav
            ) * 100

            nav_series.append(
                normalized[["Date", fund_name]].set_index("Date")
            )

        if not comparison_rows:
            st.error("No mutual fund data could be loaded.")
            st.stop()

        summary = pd.DataFrame(comparison_rows)

        st.subheader("Performance Comparison")
        st.dataframe(
            summary.round(2),
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Growth of ₹100")
        growth_chart = pd.concat(nav_series, axis=1).sort_index()
        st.line_chart(growth_chart)

        st.subheader("Risk Comparison")
        risk_data = summary.set_index("Mutual Fund")[
            ["Annualized Volatility (%)", "Maximum Drawdown (%)"]
        ]
        st.bar_chart(risk_data)

        st.download_button(
            "⬇️ Download Comparison Report",
            summary.to_csv(index=False).encode("utf-8"),
            file_name="TrendPulse_Mutual_Fund_Comparison.csv",
            mime="text/csv"
        )

        st.info(
            "Returns are calculated over the selected historical period. "
            "Volatility is annualized using 252 trading days. "
            "Past performance does not guarantee future results."
        )
        st.stop()

    data, fund_details = fetch_mutual_fund_nav(scheme_code)

    if data.empty:
        st.error("Historical NAV data could not be loaded.")
        st.stop()

    period_days = {"1y": 365, "2y": 730, "5y": 1825}
    cutoff = pd.Timestamp.today().normalize() - pd.Timedelta(
        days=period_days[period]
    )
    data = data[data["Date"] >= cutoff].copy()

    st.sidebar.success(f"Selected: {company}")
    st.title("📚 Mutual Fund NAV Analysis")
    st.caption("NAV-based historical analysis • Not live exchange prices")

    st.subheader("Fund details")
    st.write(f"**Fund house:** {fund_details.get('fund_house', 'N/A')}")
    st.write(f"**Category:** {fund_details.get('category', 'N/A')}")
    st.write(f"**Plan:** {fund_details.get('plan_type', 'N/A')}")
    st.write(f"**Option:** {fund_details.get('option_type', 'N/A')}")

    latest = data.iloc[-1]
    first = data.iloc[0]
    total_return = (latest["Close"] / first["Close"] - 1) * 100

    years = (latest["Date"] - first["Date"]).days / 365.25
    cagr = (
        ((latest["Close"] / first["Close"]) ** (1 / years) - 1) * 100
        if years > 0 else 0
    )

    data["Daily_Return"] = data["Close"].pct_change()
    volatility = data["Daily_Return"].std() * (252 ** 0.5) * 100

    data["Peak"] = data["Close"].cummax()
    data["Drawdown"] = (
        data["Close"] / data["Peak"] - 1
    ) * 100
    max_drawdown = data["Drawdown"].min()

    st.subheader("📊 Fund Performance")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Latest NAV", f"₹{latest['Close']:.2f}")
        st.metric("CAGR", f"{cagr:.2f}%")

    with c2:
        st.metric("Total Return", f"{total_return:.2f}%")
        st.metric("Annualized Volatility", f"{volatility:.2f}%")

    st.metric("Maximum Drawdown", f"{max_drawdown:.2f}%")

    st.subheader("Historical NAV")
    st.line_chart(data.set_index("Date")["Close"])

    st.subheader("NAV Drawdown")
    st.area_chart(data.set_index("Date")["Drawdown"])

    st.subheader("Recent NAV records")
    st.dataframe(data.tail(20), use_container_width=True)

    st.download_button(
        "⬇️ Download NAV history (CSV)",
        data.to_csv(index=False).encode("utf-8"),
        file_name="TrendPulse_Mutual_Fund_NAV.csv",
        mime="text/csv"
    )


    pdf_details = {
        "Fund House": fund_details.get("fund_house", "N/A"),
        "Category": fund_details.get("category", "N/A"),
        "Plan": fund_details.get("plan", "N/A"),
        "Option": fund_details.get("option", "N/A"),
        "Scheme Code": scheme_code,
        "Data Period": f"{data['Date'].min().date()} to {data['Date'].max().date()}"
    }

    pdf_metrics = {
        "Latest NAV": f"₹{latest['Close']:.4f}",
        "Total Return": f"{total_return:.2f}%",
        "CAGR": f"{cagr:.2f}%",
        "Annualized Volatility": f"{volatility:.2f}%",
        "Maximum Drawdown": f"{max_drawdown:.2f}%"
    }

    pdf_report = generate_pdf_report(
        company,
        pdf_details,
        pdf_metrics
    )

    st.download_button(
        "📄 Download PDF Research Report",
        data=pdf_report,
        file_name="TrendPulse_Mutual_Fund_Report.pdf",
        mime="application/pdf"
    )

    st.info(
        "Returns and risk metrics are calculated from the selected historical "
        "NAV period. Volatility is annualized using 252 trading days. "
        "Past performance does not guarantee future results."
    )
    st.stop()

st.sidebar.success(f"Selected: {company} · {ticker}")
with st.sidebar.expander("⚙️ Analysis settings", expanded=True):
    period = st.selectbox("Historical data period", ["1y", "2y", "5y"], index=2)
    horizon = st.selectbox("Forecast horizon", [5, 10, 20], index=0, help="Number of trading days ahead.")
uploaded_news = st.sidebar.file_uploader("Upload news CSV (optional)", type=["csv"])
if st.sidebar.button("🔄 Refresh financial news", use_container_width=True):
    st.cache_data.clear()

@st.cache_data(ttl=900)
def fetch_stock(symbol, selected_period):
    try:
        frame = yf.download(symbol, period=selected_period, auto_adjust=True, progress=False, threads=False)
        if frame is None or frame.empty:
            frame = yf.Ticker(symbol).history(period=selected_period, auto_adjust=True)
    except Exception:
        try: frame = yf.Ticker(symbol).history(period=selected_period, auto_adjust=True)
        except Exception: return pd.DataFrame()
    if frame is None or frame.empty: return pd.DataFrame()
    if isinstance(frame.columns, pd.MultiIndex): frame.columns = frame.columns.get_level_values(0)
    frame = frame.reset_index()
    date_col = "Date" if "Date" in frame.columns else "Datetime" if "Datetime" in frame.columns else None
    if date_col is None or "Close" not in frame.columns: return pd.DataFrame()
    frame = frame.rename(columns={date_col: "Date"})
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    try:
        if frame["Date"].dt.tz is not None: frame["Date"] = frame["Date"].dt.tz_localize(None)
    except Exception: pass
    frame = frame.dropna(subset=["Date", "Close"]).sort_values("Date").copy()
    frame["Close"] = pd.to_numeric(frame["Close"], errors="coerce")
    frame = frame.dropna(subset=["Close"])
    frame["Daily_Return"] = frame["Close"].pct_change() * 100
    frame["Volatility"] = frame["Daily_Return"].rolling(20).std() * np.sqrt(252)
    return frame

@st.cache_data(ttl=900)
def read_news(uploaded_bytes, symbol):
    if uploaded_bytes is not None:
        try: news = pd.read_csv(pd.io.common.BytesIO(uploaded_bytes))
        except Exception: return pd.DataFrame()
    else:
        try: news = pd.read_csv("/content/apple_news_data.csv")
        except Exception: return pd.DataFrame()
    if "date" not in news.columns: return pd.DataFrame()
    news["date"] = pd.to_datetime(news["date"], errors="coerce", utc=True).dt.tz_localize(None)
    news = news.dropna(subset=["date"]).copy()
    if "symbols" in news.columns and news["symbols"].notna().any():
        news = news[news["symbols"].astype(str).str.contains(symbol.split(".")[0], case=False, na=False)].copy()
    if {"sentiment_pos", "sentiment_neg"}.issubset(news.columns):
        news["Sentiment"] = pd.to_numeric(news["sentiment_pos"], errors="coerce").fillna(0) - pd.to_numeric(news["sentiment_neg"], errors="coerce").fillna(0)
    elif "sentiment_polarity" in news.columns:
        news["Sentiment"] = pd.to_numeric(news["sentiment_polarity"], errors="coerce")
    else: return pd.DataFrame()
    news = news.dropna(subset=["Sentiment"]); news["TradingDate"] = news["date"].dt.normalize()
    return news

NEWS_SEARCH_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet", "AMZN": "Amazon",
    "TSLA": "Tesla", "NVDA": "NVIDIA", "META": "Meta Platforms Facebook", "NFLX": "Netflix",
    "RELIANCE": "Reliance Industries", "TCS": "Tata Consultancy Services", "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank", "ICICIBANK": "ICICI Bank", "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel", "ITC": "ITC"
}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_live_news(symbol, display_company, api_key):
    if not api_key: return pd.DataFrame(), "NEWS_API_KEY is not set in the Colab runtime."
    base_symbol = str(symbol).upper().split(".")[0]
    search_name = NEWS_SEARCH_NAMES.get(base_symbol, display_company or base_symbol)
    params = {"q": f'"{search_name}"', "language": "en", "sortBy": "publishedAt", "pageSize": 100}
    try:
        response = requests.get("https://newsapi.org/v2/everything", params=params,
                                headers={"X-Api-Key": api_key}, timeout=25)
        payload = response.json()
        if response.status_code != 200 or payload.get("status") != "ok":
            return pd.DataFrame(), payload.get("message", f"NewsAPI error ({response.status_code})")
        rows, analyzer = [], SentimentIntensityAnalyzer()
        search_terms = [term.lower() for term in search_name.split() if len(term) > 2]
        for article in payload.get("articles", []):
            title, description, content = article.get("title") or "", article.get("description") or "", article.get("content") or ""
            combined = f"{title} {description} {content}".strip()
            if not combined: continue
            if len(search_terms) >= 2 and not any(term in combined.lower() for term in search_terms): continue
            score = analyzer.polarity_scores(combined)["compound"]
            rows.append({"date": article.get("publishedAt"), "title": title, "description": description,
                "content": content, "link": article.get("url"), "source": (article.get("source") or {}).get("name", "Unknown"),
                "Sentiment": score})
        result = pd.DataFrame(rows)
        if result.empty: return result, "No relevant articles were returned for this company."
        result["date"] = pd.to_datetime(result["date"], errors="coerce", utc=True).dt.tz_localize(None)
        result = result.dropna(subset=["date"]).copy(); result["TradingDate"] = result["date"].dt.normalize()
        result["Sentiment_Label"] = np.select([result["Sentiment"] >= .05, result["Sentiment"] <= -.05],
                                              ["Positive", "Negative"], default="Neutral")
        return result.sort_values("date", ascending=False), None
    except requests.RequestException as exc: return pd.DataFrame(), f"Could not connect to NewsAPI: {exc}"
    except Exception as exc: return pd.DataFrame(), f"News processing error: {exc}"

with st.spinner(f"Loading market data for {company} ({ticker})..."):
    stock = fetch_stock(ticker, period)
if stock.empty:
    st.error(f"No stock data was returned for {ticker}. Check the ticker, internet connection, or try again later.")
    st.info("Try AAPL, MSFT, RELIANCE.NS or TCS.NS. Data-provider availability can vary.")
    st.stop()

news_error = None
if uploaded_news is not None:
    news = read_news(uploaded_news.getvalue(), ticker); news_source_label = "Uploaded CSV"
else:
    news, news_error = fetch_live_news(ticker, company, os.environ.get("NEWS_API_KEY", ""))
    news_source_label = "Live NewsAPI"
    if news.empty:
        fallback_news = read_news(None, ticker)
        if not fallback_news.empty: news = fallback_news; news_source_label = "Local CSV fallback"

if not news.empty:
    daily_news = news.groupby("TradingDate").agg(Sentiment_Daily=("Sentiment", "mean"), News_Count=("Sentiment", "size")).reset_index().rename(columns={"TradingDate": "Date"})
    data = stock.merge(daily_news, on="Date", how="left")
else:
    data = stock.copy(); data["Sentiment_Daily"] = np.nan; data["News_Count"] = 0

data["News_Count"] = data["News_Count"].fillna(0)
data["Has_News"] = (data["News_Count"] > 0).astype(int)
data["Sentiment_Daily"] = data["Sentiment_Daily"].fillna(0)
data["Sentiment_5D"] = data["Sentiment_Daily"].rolling(5, min_periods=1).mean()
data["Sentiment_20D"] = data["Sentiment_Daily"].rolling(20, min_periods=1).mean()
data["Return_5D"] = data["Daily_Return"].rolling(5).mean()
data["Volatility_5D"] = data["Daily_Return"].rolling(5).std() * np.sqrt(252)
valid_vol = data["Volatility"].dropna()
latest_vol = float(valid_vol.iloc[-1]) if len(valid_vol) else np.nan

r1 = st.columns(2); r1[0].metric("Selected investment", company); r1[1].metric("Latest closing price", f"{float(data['Close'].iloc[-1]):,.2f}")
r2 = st.columns(2); r2[0].metric("20-day annualized volatility", f"{latest_vol:.2f}%" if pd.notna(latest_vol) else "N/A"); r2[1].metric("Historical trading days", f"{len(data):,}")

tab_market, tab_sentiment, tab_model, tab_compare, tab_about = st.tabs(
    ["🏠 Overview", "📰 News & Sentiment", "🤖 AI Analysis", "⚖️ Compare Investments", "ℹ️ How to use"])

with tab_market:
    st.header(f"{company} — Investment Overview")
    st.caption(f"{data_kind} • Symbol: {ticker} • Historical market-traded price data")
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.line(data, x="Date", y="Close", title=f"{ticker} closing price", template="plotly_white"), use_container_width=True)
    with c2: st.plotly_chart(px.line(data, x="Date", y="Volatility", title="20-day annualized historical volatility", template="plotly_white"), use_container_width=True)
    st.subheader("Recent market data")
    st.dataframe(data[["Date", "Close", "Daily_Return", "Volatility"]].tail(10), use_container_width=True, hide_index=True)

with tab_sentiment:
    st.header("News & Sentiment")
    st.write("See how recent financial headlines are classified by their language: positive, neutral or negative.")
    st.caption(f"News source: {news_source_label} • Live news cache: 15 minutes")
    if news.empty:
        st.warning("No news articles are currently available for this company.")
        if news_error: st.info(f"NewsAPI message: {news_error}")
        st.caption("Check the API key, provider limits, company search terms, or refresh. CSV upload remains available.")
    else:
        news["Sentiment_Label"] = np.select([news["Sentiment"] > .05, news["Sentiment"] < -.05],
                                           ["Positive", "Negative"], default="Neutral")
        p = int((news["Sentiment_Label"] == "Positive").sum()); n = int((news["Sentiment_Label"] == "Negative").sum()); z = int((news["Sentiment_Label"] == "Neutral").sum())
        a, b, c = st.columns(3); a.metric("Positive articles", f"{p:,}"); b.metric("Neutral articles", f"{z:,}"); c.metric("Negative articles", f"{n:,}")
        counts = news["Sentiment_Label"].value_counts().rename_axis("Sentiment").reset_index(name="Articles")
        st.plotly_chart(px.bar(counts, x="Sentiment", y="Articles", color="Sentiment", title="News sentiment distribution", template="plotly_white"), use_container_width=True)
        daily = news.groupby("TradingDate")["Sentiment"].mean().reset_index()
        st.plotly_chart(px.line(daily, x="TradingDate", y="Sentiment", title="Daily average financial-news sentiment", template="plotly_white"), use_container_width=True)
        st.subheader("Sentiment and market relationship")
        matched = data.dropna(subset=["Daily_Return", "Volatility"])
        corr_r = matched["Sentiment_Daily"].corr(matched["Daily_Return"]); corr_v = matched["Sentiment_Daily"].corr(matched["Volatility"])
        x, y = st.columns(2); x.metric("Sentiment vs daily return", f"{corr_r:.3f}" if pd.notna(corr_r) else "N/A"); y.metric("Sentiment vs volatility", f"{corr_v:.3f}" if pd.notna(corr_v) else "N/A")
        st.caption("Correlation indicates association, not causation.")
        display_cols = [col for col in ["date", "title", "description", "source", "Sentiment", "Sentiment_Label", "link"] if col in news.columns]
        st.subheader("Latest financial news")
        st.dataframe(news.sort_values("date", ascending=False)[display_cols].head(20), use_container_width=True, hide_index=True)

with tab_model:
    st.header("AI Volatility Analysis")
    st.write("Compare historical market patterns with an experimental machine-learning forecast.")
    st.caption(f"Forecast target: volatility {horizon} trading days ahead. Chronological 80/20 train/test split.")
    model_data = data.copy(); model_data["Target"] = model_data["Volatility"].shift(-horizon)
    market_features = ["Close", "Daily_Return", "Volatility", "Return_5D", "Volatility_5D"]
    sentiment_features = market_features + ["Sentiment_5D", "Sentiment_20D", "Has_News"]
    model_data = model_data.replace([np.inf, -np.inf], np.nan).dropna(subset=["Target"] + market_features + ["Sentiment_5D", "Sentiment_20D"])
    if len(model_data) < 120:
        st.warning("Not enough valid observations for this model. Choose a longer historical period.")
    else:
        split = int(len(model_data) * .8); y_train, y_test = model_data["Target"].iloc[:split], model_data["Target"].iloc[split:]
        def evaluate(features):
            model = RandomForestRegressor(n_estimators=180, max_depth=8, min_samples_leaf=3, random_state=42, n_jobs=-1)
            model.fit(model_data[features].iloc[:split], y_train); pred = model.predict(model_data[features].iloc[split:])
            scores = {"MAE": mean_absolute_error(y_test, pred), "RMSE": np.sqrt(mean_squared_error(y_test, pred)), "R²": r2_score(y_test, pred)}
            return model, pred, scores
        market_model, market_pred, market_scores = evaluate(market_features); full_model, full_pred, full_scores = evaluate(sentiment_features)
        results = pd.DataFrame([{"Model": "Market Only", **market_scores}, {"Model": "Market + Sentiment", **full_scores}])
        st.subheader("Model performance comparison")
        q1, q2, q3 = st.columns(3); q1.metric("MAE (Market + Sentiment)", f"{full_scores['MAE']:.3f}"); q2.metric("RMSE", f"{full_scores['RMSE']:.3f}"); q3.metric("R²", f"{full_scores['R²']:.3f}")
        st.dataframe(results.round(4), use_container_width=True, hide_index=True)
        metric = st.selectbox("Compare metric", ["MAE", "RMSE", "R²"])
        st.plotly_chart(px.bar(results, x="Model", y=metric, color="Model", title=f"{metric} comparison", template="plotly_white"), use_container_width=True)
        predictions = pd.DataFrame({"Date": model_data["Date"].iloc[split:].values, "Actual Volatility": y_test.values, "Market Only": market_pred, "Market + Sentiment": full_pred})
        st.subheader("Actual vs predicted volatility")
        st.plotly_chart(px.line(predictions, x="Date", y=["Actual Volatility", "Market Only", "Market + Sentiment"], template="plotly_white"), use_container_width=True)
        importance = pd.DataFrame({"Feature": sentiment_features, "Importance": full_model.feature_importances_}).sort_values("Importance", ascending=False)
        st.subheader("Feature importance")
        st.plotly_chart(px.bar(importance, x="Importance", y="Feature", orientation="h", template="plotly_white"), use_container_width=True)
        st.caption("Experimental results are instrument-specific. Validate with time-series methods; forecasts are not investment advice.")

with tab_compare:
    st.header("Investment Comparison")
    st.write("Compare up to four stocks or ETFs over the same historical period.")
    st.caption("Metrics use adjusted closing prices returned by Yahoo Finance. This is historical analysis, not a recommendation.")
    available_assets = {**US_STOCKS, **{f"{k} (NSE)": v for k, v in NSE_STOCKS.items()},
                        **{f"{k} (BSE)": v for k, v in BSE_STOCKS.items()},
                        **{f"{k} (India ETF)": v for k, v in INDIA_ETFS.items()},
                        **{f"{k} (Global ETF)": v for k, v in GLOBAL_ETFS.items()}}
    current_label = f"{company} ({ticker})"
    choices = list(available_assets.keys())
    defaults = []
    for label, symbol in available_assets.items():
        if symbol == ticker and not defaults:
            defaults.append(label)
    selected_labels = st.multiselect("Select 2–4 investments", choices, default=defaults, max_selections=4,
                                     help="Choose stocks and ETFs. Mutual funds are not included in this comparison yet.")
    if len(selected_labels) < 2:
        st.info("Select at least two investments to see the comparison.")
    else:
        selected_symbols = [available_assets[label] for label in selected_labels]
        with st.spinner("Downloading comparison data..."):
            price_series = {}
            failed = []
            for label, symbol in zip(selected_labels, selected_symbols):
                hist = fetch_stock(symbol, period)
                if hist.empty:
                    failed.append(f"{label} ({symbol})")
                else:
                    series = hist.set_index("Date")["Close"].rename(label)
                    price_series[label] = series
        if failed:
            st.warning("Data could not be loaded for: " + ", ".join(failed))
        if len(price_series) >= 2:
            prices = pd.concat(price_series.values(), axis=1).sort_index()
            # Align on common dates to make return comparisons fair.
            daily_returns = prices.pct_change() * 100
            common_returns = daily_returns.dropna(how="any")
            if len(common_returns) < 30:
                st.warning("There are too few overlapping trading days. Choose assets with more common history.")
            else:
                growth = (1 + common_returns / 100).cumprod()
                normalized = growth * 100
                summary_rows = []
                for col in common_returns.columns:
                    r = common_returns[col].dropna() / 100
                    wealth = (1 + r).cumprod()
                    total_return = (wealth.iloc[-1] - 1) * 100
                    years = len(r) / 252
                    cagr = ((wealth.iloc[-1] ** (1 / years)) - 1) * 100 if years > 0 and wealth.iloc[-1] > 0 else np.nan
                    annual_vol = r.std() * np.sqrt(252) * 100
                    sharpe = (r.mean() / r.std() * np.sqrt(252)) if r.std() and pd.notna(r.std()) else np.nan
                    running_peak = wealth.cummax()
                    max_drawdown = ((wealth / running_peak) - 1).min() * 100
                    summary_rows.append({"Investment": col, "Total Return": total_return, "Annualized Return (CAGR)": cagr,
                                         "Annualized Volatility": annual_vol, "Sharpe Ratio (rf=0)": sharpe,
                                         "Maximum Drawdown": max_drawdown})
                summary = pd.DataFrame(summary_rows)
                st.subheader("Performance metrics")
                st.dataframe(summary.style.format({"Total Return": "{:.2f}%", "Annualized Return (CAGR)": "{:.2f}%",
                    "Annualized Volatility": "{:.2f}%", "Sharpe Ratio (rf=0)": "{:.2f}", "Maximum Drawdown": "{:.2f}%"}),
                    use_container_width=True, hide_index=True)
                st.subheader("Growth of 100 (common dates)")
                st.plotly_chart(px.line(normalized, title="Relative investment growth (starting value = 100)", labels={"value": "Portfolio value", "index": "Date"}, template="plotly_white"), use_container_width=True)
                st.subheader("Risk comparison")
                risk_chart = summary.melt(id_vars="Investment", value_vars=["Annualized Volatility", "Maximum Drawdown"],
                                          var_name="Risk measure", value_name="Percent")
                st.plotly_chart(px.bar(risk_chart, x="Investment", y="Percent", color="Risk measure", barmode="group",
                                       title="Historical risk measures", template="plotly_white"), use_container_width=True)
                csv = summary.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download comparison metrics (CSV)", csv, "trendpulse_investment_comparison.csv", "text/csv")
                st.caption("Sharpe Ratio assumes a 0% risk-free rate. CAGR is an annualized historical growth estimate. Past performance does not predict future results.")
        else:
            st.error("At least two selected investments returned usable price data.")

with tab_about:
    st.header("How to use TrendPulse")
    st.markdown("""
1. **Choose an investment type** in the left panel.
2. **Select a market and investment** from the dropdown lists.
3. Open **Overview** to explore historical prices and volatility.
4. Open **News & Sentiment** to review relevant headlines and sentiment.
5. Open **AI Analysis** to compare experimental forecasting models.
6. Open **Compare Investments** and select two to four stocks or ETFs.

**Tip:** Start with a familiar instrument such as Apple, Reliance Industries, Gold BeES or SPY.
""")
    st.subheader("About TrendPulse")
    st.markdown("""
**TrendPulse** is a multi-market AI research prototype for analysing Indian and international equities and ETFs.

**Users:** Students, researchers, financial analysts and investors interested in educational market analysis.

**Workflow:** Select an instrument, retrieve historical market data, examine available financial-news sentiment, compare experimental volatility models, and compare historical investment performance.

**Limitations:** Market-data availability depends on the provider. Live news depends on NewsAPI access, plan limits, search relevance and connectivity. VADER may misread financial context. Mutual funds need a separate NAV data source. Correlation does not imply causation. Forecasts and historical metrics are not investment advice.
""")

st.divider()
st.caption(f"TrendPulse • {company} ({ticker}) • News: {news_source_label} • Educational research prototype • Not financial advice")
