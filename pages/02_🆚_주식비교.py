import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

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

st.title("🆚 :orange[수익률 & 리스크 빅매치]")
st.markdown("선택한 기업들의 성과를 한눈에 비교하는 멀티 차트 대시보드입니다.")

with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    selected_stocks = col1.multiselect("종목 다중 선택 (최대 추천: 4개):", list(stocks_dict.keys()), default=["삼성전자", "엔비디아 (NVDA)"])
    end_date = col2.date_input("종료일", datetime.today(), key="end")
    start_date = col2.date_input("시작일", end_date - timedelta(days=365), key="start")

if selected_stocks:
    tickers_to_fetch = {name: stocks_dict[name] for name in selected_stocks}
    with st.spinner("종목 간 상관관계를 분석 중입니다... ⏳"):
        df_prices = load_multiple_data(tickers_to_fetch, start_date, end_date)
        
    if not df_prices.empty:
        df_prices = df_prices.ffill()
        df_returns = (df_prices / df_prices.iloc[0] - 1) * 100
        
        st.subheader("📈 :green[누적 수익률 레이스]")
        fig_returns = px.line(df_returns, x=df_returns.index, y=df_returns.columns, 
                              labels={"value": "수익률 (%)", "variable": "종목명", "index": "날짜"},
                              template="plotly_white") # 세련된 흰색 테마
        # 선 두께 굵게 만들기
        fig_returns.update_traces(line=dict(width=3))
        st.plotly_chart(fig_returns, use_container_width=True)
        
        st.markdown("---")
        st.subheader("⚠️ :red[투자 리스크 (MDD) 분석]")
        st.markdown("각 종목이 고점 대비 얼마나 폭락했었는지 보여줍니다. 숫자가 클수록 위험한 주식입니다.")
        
        cols = st.columns(len(selected_stocks))
        for i, stock in enumerate(selected_stocks):
            peak = df_prices[stock].expanding(min_periods=1).max()
            drawdown = (df_prices[stock] / peak) - 1
            mdd = drawdown.min() * 100
            
            with cols[i]:
                # 카드 형태로 묶어서 돋보이게 만들기
                with st.container(border=True):
                    st.metric(label=f"📉 {stock} MDD", value=f"{mdd:.2f}%")
