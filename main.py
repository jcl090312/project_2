import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px  # 🌟 멋진 인터랙티브 차트를 위한 추가 라이브러리!

# 페이지 기본 설정 (와이드 모드로 더 넓고 전문가처럼 보이게)
st.set_page_config(page_title="당곡고 주식 퀀트 분석 앱", page_icon="📈", layout="wide")

st.title("📈 퀀트(Quant) 투자 분석 대시보드")
st.markdown("단순한 주가 비교를 넘어, **이동평균선**과 **인터랙티브 차트**를 제공하는 심화 데이터 분석 웹앱입니다.")

# 사이드바 설정 (사용자 입력)
st.sidebar.header("⚙️ 분석 설정")

stocks_dict = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "현대차": "005380.KS",
    "네이버": "035420.KS",
    "애플 (AAPL)": "AAPL",
    "마이크로소프트 (MSFT)": "MSFT",
    "테슬라 (TSLA)": "TSLA",
    "엔비디아 (NVDA)": "NVDA"
}

selected_stocks = st.sidebar.multiselect(
    "비교할 기업을 선택하세요:",
    options=list(stocks_dict.keys()),
    default=["삼성전자", "엔비디아 (NVDA)"]
)

end_date = st.sidebar.date_input("종료일", datetime.today())
start_date = st.sidebar.date_input("시작일", end_date - timedelta(days=365))

st.sidebar.markdown("---")
# 🌟 고급 기능: 이동평균선 선택 (체크박스)
show_ma = st.sidebar.checkbox("📉 20일 이동평균선 표시", value=False, help="최근 20일간의 평균 주가를 연결한 선입니다. 추세를 볼 때 사용합니다.")

@st.cache_data
def load_data(tickers_dict, start, end):
    df_prices = pd.DataFrame()
    for name, ticker in tickers_dict.items():
        stock_data = yf.download(ticker, start=start, end=end, progress=False)
        if not stock_data.empty:
            df_prices[name] = stock_data['Close'].squeeze()
    return df_prices

# 메인 화면 로직
if not selected_stocks:
    st.warning("👈 사이드바에서 비교할 주식을 하나 이상 선택해주세요.")
else:
    tickers_to_fetch = {name: stocks_dict[name] for name in selected_stocks}
    
    with st.spinner("빅데이터를 분석 중입니다... 잠시만 기다려주세요! ⏳"):
        df = load_data(tickers_to_fetch, start_date, end_date)
    
    if df.empty:
        st.error("데이터를 불러오지 못했습니다. 날짜를 확인해주세요.")
    else:
        df = df.ffill()

        # 🌟 1. 대시보드 KPI (핵심 지표) - 전일 대비 등락률 표시
        st.subheader("📊 주요 종목 요약 (최근 1일 기준)")
        cols = st.columns(len(selected_stocks)) # 선택한 주식 수만큼 화면을 세로로 쪼갬
        
        for i, stock in enumerate(selected_stocks):
            if len(df) >= 2:
                current_price = df[stock].iloc[-1]
                prev_price = df[stock].iloc[-2]
                diff = current_price - prev_price
                diff_pct = (diff / prev_price) * 100
                
                with cols[i]:
                    # st.metric을 사용하면 화살표와 함께 숫자가 예쁘게 표시됩니다.
                    st.metric(label=stock, 
                              value=f"{current_price:,.1f}", 
                              delta=f"{diff:,.1f} ({diff_pct:.2f}%)")

        st.markdown("---")

        # 🌟 2. Plotly를 활용한 인터랙티브 주가 차트
        st.subheader("1. 주가 변동 차트 (마우스를 올려보세요!)")
        
        df_plot = df.copy()
        # 이동평균선 계산 로직 (수학/통계 적용)
        if show_ma:
            for stock in selected_stocks:
                df_plot[f"{stock}_20일_MA"] = df_plot[stock].rolling(window=20).mean()

        # Plotly 라이브러리로 차트 그리기
        fig_price = px.line(df_plot, x=df_plot.index, y=df_plot.columns, 
                            title="드래그하여 원하는 구간을 확대해 볼 수 있습니다.",
                            labels={"value": "주가", "variable": "종목명", "index": "날짜"})
        st.plotly_chart(fig_price, use_container_width=True)
        
        # 🌟 3. Plotly를 활용한 누적 수익률 차트
        st.subheader("2. 누적 수익률 비교 차트 (%)")
        df_returns = (df / df.iloc[0] - 1) * 100
        fig_returns = px.line(df_returns, x=df_returns.index, y=df_returns.columns,
                              title="내가 시작일에 샀다면 지금 몇 % 올랐을까?",
                              labels={"value": "수익률 (%)", "variable": "종목명", "index": "날짜"})
        st.plotly_chart(fig_returns, use_container_width=True)
        
        st.subheader("3. 빅데이터 원본 (상세 종가)")
        df_display = df.copy()
        df_display.index = df_display.index.strftime('%Y-%m-%d')
        st.dataframe(df_display.tail(5))
