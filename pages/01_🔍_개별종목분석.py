import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go

stocks_dict = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS",
    "네이버": "035420.KS", "애플 (AAPL)": "AAPL", "마이크로소프트 (MSFT)": "MSFT",
    "테슬라 (TSLA)": "TSLA", "엔비디아 (NVDA)": "NVDA"
}

@st.cache_data
def load_single_stock(ticker, start, end):
    return yf.download(ticker, start=start, end=end, progress=False)

st.title("🔍 :blue[단일 기업 심층 스캐너]")
st.markdown("선택한 기업의 캔들스틱 추세와 거래량을 심도 있게 분석합니다.")

# 입력창을 예쁜 박스 안에 넣기
with st.container(border=True):
    col_sel, col_start, col_end = st.columns([2, 1, 1])
    selected = col_sel.selectbox("🏢 분석할 기업 선택:", list(stocks_dict.keys()))
    end_date = col_end.date_input("종료일", datetime.today())
    start_date = col_start.date_input("시작일", end_date - timedelta(days=180))

if selected:
    ticker = stocks_dict[selected]
    with st.spinner(f"{selected}의 빅데이터를 렌더링 중입니다... 📊"):
        df = load_single_stock(ticker, start_date, end_date)
        
    if not df.empty:
        # 요약 정보 카드
        c1, c2, c3 = st.columns(3)
        current_price = df['Close'].iloc[-1].item()
        high_price = df['High'].max().item()
        c1.metric("최근 종가", f"{current_price:,.0f}")
        c2.metric("조회기간 내 최고가", f"{high_price:,.0f}")
        c3.metric("총 거래일 수", f"{len(df)} 일")

        # 탭으로 화면 분할 (깔끔한 레이아웃)
        tab1, tab2 = st.tabs(["📊 캔들스틱 & 이평선", "📋 원본 데이터 표"])
        
        with tab1:
            fig = go.Figure(data=[go.Candlestick(x=df.index,
                            open=df['Open'].squeeze(), high=df['High'].squeeze(),
                            low=df['Low'].squeeze(), close=df['Close'].squeeze(),
                            name="캔들차트", increasing_line_color='red', decreasing_line_color='blue')])
            
            ma20 = df['Close'].squeeze().rolling(window=20).mean()
            fig.add_trace(go.Scatter(x=df.index, y=ma20, line=dict(color='orange', width=2), name="20일 이동평균선"))
            
            # 차트 배경색 등 어두운 테마나 세련된 테마 적용
            fig.update_layout(title=f"<b>{selected} 주가 흐름</b>", xaxis_rangeslider_visible=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            st.dataframe(df.sort_index(ascending=False), use_container_width=True)
