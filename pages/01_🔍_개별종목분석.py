import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="개별 종목 분석", page_icon="🔍", layout="wide")

stocks_dict = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS",
    "네이버": "035420.KS", "애플 (AAPL)": "AAPL", "마이크로소프트 (MSFT)": "MSFT",
    "테슬라 (TSLA)": "TSLA", "엔비디아 (NVDA)": "NVDA"
}

@st.cache_data
def load_single_stock(ticker, start, end):
    return yf.download(ticker, start=start, end=end, progress=False)

st.title("🔍 개별 종목 심층 분석")
st.markdown("캔들스틱 차트와 이동평균선(20일)을 활용하여 기업의 주가 흐름을 분석합니다.")

selected = st.selectbox("분석할 기업을 선택하세요:", list(stocks_dict.keys()))
col1, col2 = st.columns(2)
end_date = col2.date_input("종료일", datetime.today())
start_date = col1.date_input("시작일", end_date - timedelta(days=180)) 

if selected:
    ticker = stocks_dict[selected]
    with st.spinner("차트를 그리는 중..."):
        df = load_single_stock(ticker, start_date, end_date)
        
    if not df.empty:
        # 전문가용 캔들스틱 차트 생성
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['Open'].squeeze(), high=df['High'].squeeze(),
                        low=df['Low'].squeeze(), close=df['Close'].squeeze(),
                        name="캔들차트")])
        
        # 20일 이동평균선 추가
        ma20 = df['Close'].squeeze().rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=df.index, y=ma20, line=dict(color='orange', width=2), name="20일 이평선"))
        
        fig.update_layout(title=f"{selected} 주가 흐름", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
