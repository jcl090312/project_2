import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="주식 수익률 비교", page_icon="🆚", layout="wide")

stocks_dict = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS",
    "네이버": "035420.KS", "애플 (AAPL)": "AAPL", "마이크로소프트 (MSFT)": "MSFT",
    "테슬라 (TSLA)": "TSLA", "엔비디아 (NVDA)": "NVDA"
}

@st.cache_data
def load_multiple_data(tickers_dict, start, end):
    df_prices = pd.DataFrame()
    for name, ticker in tickers_dict.items():
        stock_data = yf.download(ticker, start=start, end=end, progress=False)
        if not stock_data.empty:
            df_prices[name] = stock_data['Close'].squeeze()
    return df_prices

st.title("🆚 수익률 및 리스크(MDD) 비교")
st.markdown("여러 기업을 동시에 선택하여 누가 더 많이 올랐고, 누가 덜 떨어졌는지 비교해 봅니다.")

selected_stocks = st.multiselect("비교할 기업을 선택하세요:", list(stocks_dict.keys()), default=["삼성전자", "엔비디아 (NVDA)"])
col1, col2 = st.columns(2)
end_date = col2.date_input("종료일", datetime.today())
start_date = col1.date_input("시작일", end_date - timedelta(days=365))

if selected_stocks:
    tickers_to_fetch = {name: stocks_dict[name] for name in selected_stocks}
    with st.spinner("빅데이터 분석 중..."):
        df_prices = load_multiple_data(tickers_to_fetch, start_date, end_date)
        
    if not df_prices.empty:
        df_prices = df_prices.ffill()
        
        st.subheader("🚀 누적 수익률 비교 (%)")
        df_returns = (df_prices / df_prices.iloc[0] - 1) * 100
        fig_returns = px.line(df_returns, x=df_returns.index, y=df_returns.columns, labels={"value": "수익률 (%)", "variable": "종목명", "index": "날짜"})
        st.plotly_chart(fig_returns, use_container_width=True)
        
        st.subheader("⚠️ 투자 리스크 (MDD: 최대 낙폭) 분석")
        cols = st.columns(len(selected_stocks))
        for i, stock in enumerate(selected_stocks):
            peak = df_prices[stock].expanding(min_periods=1).max()
            drawdown = (df_prices[stock] / peak) - 1
            mdd = drawdown.min() * 100
            with cols[i]:
                st.metric(label=f"{stock} MDD", value=f"{mdd:.2f}%")
