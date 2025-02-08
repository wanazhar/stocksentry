import streamlit as st
import yfinance as yf
from utils.stock_data import get_stock_data, get_company_info, save_user_preference, format_number
from utils.visualizations import create_price_chart, create_volume_chart, create_metrics_chart
from utils.database import init_db
import plotly.io as pio
from utils.data_export import export_to_excel, get_historical_data, get_peer_comparison
import datetime
import io
import pandas as pd

# Initialize database
init_db()

# Set default plotly theme
pio.templates.default = "plotly_dark"

# Page config
st.set_page_config(
    page_title="StockSentry",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
with open('styles/custom.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title and Description
st.title('StockSentry 🎯')
st.markdown("""
Your comprehensive stock analysis companion. Get real-time insights, detailed metrics, 
and advanced visualizations to make informed investment decisions.
""")

# Input Section
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    symbol = st.text_input('Enter Stock Symbol:', value='AAPL', help="""
    Enter stock symbol (examples):
    - US stocks: AAPL, GOOGL, MSFT
    - Hong Kong: 0700.HK, 9988.HK
    - London: BP.L, HSBA.L
    - Tokyo: 7203.T, 6758.T
    - Singapore: D05.SI, Z74.SI
    """).upper()

with col2:
    period = st.selectbox(
        'Select Time Period:',
        ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
    )

with col3:
    st.write("**Custom Date Range**")
    use_date_range = st.checkbox("Use Date Range")

# Date Range Selector (shown only if checkbox is selected)
if use_date_range:
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input(
            "Start Date",
            datetime.date(2010, 1, 1)
        )
    with date_col2:
        end_date = st.date_input(
            "End Date",
            datetime.date.today()
        )

    # Bulk Analysis Option
    st.write("**Bulk Analysis**")
    additional_symbols = st.text_area(
        "Enter additional symbols (one per line):",
        help="Enter multiple stock symbols for bulk analysis"
    )

    if st.button("Download Historical Data"):
        symbols = [symbol] + [s.strip() for s in additional_symbols.split('\n') if s.strip()]
        historical_data = get_historical_data(symbols, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

        # Create Excel file with multiple sheets
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sym, data in historical_data.items():
                data.to_excel(writer, sheet_name=sym[:31])  # Excel sheet names limited to 31 chars

        output.seek(0)
        st.download_button(
            label="📥 Download Excel File",
            data=output,
            file_name=f"historical_data_{start_date}_{end_date}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

try:
    # Get data based on selected time range
    if use_date_range:
        df = get_stock_data(symbol, 'max')
        df = df[start_date.strftime('%Y-%m-%d'):end_date.strftime('%Y-%m-%d')]
    else:
        df = get_stock_data(symbol, period)

    info = get_company_info(symbol)

    # Store charts for export
    charts = []

    # Company Profile Section
    st.subheader("Company Profile")
    profile_col1, profile_col2 = st.columns([1, 1])

    with profile_col1:
        st.write(f"**Company:** {info['longName']}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Market Cap:** {format_number(info.get('marketCap'), symbol)}")
        st.write(f"**Enterprise Value:** {format_number(info.get('enterpriseValue'), symbol)}")

    with profile_col2:
        st.write("**Current Trading Info**")
        st.write(f"Price: {format_number(info.get('currentPrice'), symbol)}")
        st.write(f"Day Range: {format_number(info.get('dayLow'), symbol)} - {format_number(info.get('dayHigh'), symbol)}")
        st.write(f"52W Range: {format_number(info.get('fiftyTwoWeekLow'), symbol)} - {format_number(info.get('fiftyTwoWeekHigh'), symbol)}")
        st.write(f"Volume: {format_number(info.get('volume'), symbol, False)}")

    # Trading Metrics Section
    st.subheader("Trading Metrics")
    trading_col1, trading_col2, trading_col3 = st.columns(3)

    with trading_col1:
        st.write("**Valuation Metrics**")
        st.write(f"P/E Ratio: {format_number(info.get('trailingPE'), symbol, False)}")
        st.write(f"Forward P/E: {format_number(info.get('forwardPE'), symbol, False)}")
        st.write(f"PEG Ratio: {format_number(info.get('pegRatio'), symbol, False)}")
        st.write(f"Price/Book: {format_number(info.get('priceToBook'), symbol, False)}")
        st.write(f"EV/EBITDA: {format_number(info.get('enterpriseToEbitda'), symbol, False)}")
        st.write(f"EV/Revenue: {format_number(info.get('enterpriseToRevenue'), symbol, False)}")

    with trading_col2:
        st.write("**Growth & Performance**")
        st.write(f"Beta: {format_number(info.get('beta'), symbol, False)}")
        st.write(f"Year Change: {format_number(info.get('52WeekChange', 0) * 100, symbol, False)}%")
        st.write(f"YTD Return: {format_number(info.get('ytdReturn', 0) * 100, symbol, False)}%")
        st.write(f"Revenue Growth: {format_number(info.get('revenueGrowth', 0) * 100, symbol, False)}%")
        st.write(f"Earnings Growth: {format_number(info.get('earningsGrowth', 0) * 100, symbol, False)}%")
        st.write(f"Profit Margin: {format_number(info.get('profitMargins', 0) * 100, symbol, False)}%")

    with trading_col3:
        st.write("**Income & Returns**")
        st.write(f"Dividend Rate: {format_number(info.get('dividendRate', 0), symbol)}")
        st.write(f"Dividend Yield: {format_number(info.get('dividendYield', 0) * 100, symbol, False)}%")
        st.write(f"ROE: {format_number(info.get('returnOnEquity', 0) * 100, symbol, False)}%")
        st.write(f"ROA: {format_number(info.get('returnOnAssets', 0) * 100, symbol, False)}%")
        st.write(f"Operating Margin: {format_number(info.get('operatingMargins', 0) * 100, symbol, False)}%")
        st.write(f"Gross Margin: {format_number(info.get('grossMargins', 0) * 100, symbol, False)}%")

    # Financial Health Section
    st.subheader("Financial Health")
    health_col1, health_col2 = st.columns(2)

    with health_col1:
        st.write("**Balance Sheet Metrics**")
        st.write(f"Total Cash: {format_number(info.get('totalCash'), symbol)}")
        st.write(f"Total Debt: {format_number(info.get('totalDebt'), symbol)}")
        st.write(f"Quick Ratio: {format_number(info.get('quickRatio'), symbol, False)}")
        st.write(f"Current Ratio: {format_number(info.get('currentRatio'), symbol, False)}")
        st.write(f"Debt/Equity: {format_number(info.get('debtToEquity'), symbol, False)}")

    with health_col2:
        st.write("**Revenue & Earnings**")
        st.write(f"Revenue TTM: {format_number(info.get('totalRevenue'), symbol)}")
        st.write(f"Revenue/Share: {format_number(info.get('revenuePerShare'), symbol)}")
        st.write(f"EPS (TTM): {format_number(info.get('trailingEps'), symbol)}")
        st.write(f"Forward EPS: {format_number(info.get('forwardEps'), symbol)}")
        st.write(f"Book Value/Share: {format_number(info.get('bookValue'), symbol)}")

    # Charts Section (Collapsible)
    with st.expander("📊 Price Analysis", expanded=False):
        price_chart = create_price_chart(df, symbol)
        st.plotly_chart(price_chart, use_container_width=True)
        charts.append(price_chart)

    with st.expander("📈 Volume Analysis", expanded=False):
        volume_chart = create_volume_chart(df)
        st.plotly_chart(volume_chart, use_container_width=True)
        charts.append(volume_chart)

    with st.expander("📉 Financial Metrics", expanded=False):
        metrics_chart = create_metrics_chart(info)
        st.plotly_chart(metrics_chart, use_container_width=True)
        charts.append(metrics_chart)

    # Export Section
    st.subheader("Export Data")
    if st.button("Generate Excel Report"):
        excel_file = export_to_excel(symbol, df, info, charts)
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_file,
            file_name=f"{symbol}_analysis_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check the stock symbol and try again.")

# Footer
st.markdown("""
---
<div style='text-align: center; color: #666;'>
    vibecoded by wanazhar on replit
</div>
""", unsafe_allow_html=True)