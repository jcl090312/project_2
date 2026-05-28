import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 페이지 기본 설정 (와이드 모드)
st.set_page_config(page_title="당곡고 퀀트 투자 대시보드", page_icon="📈", layout="wide")

st.title("📈 프로페셔널 퀀트 분석 대시보드")
st.markdown("환율 연동, MDD(최대 낙폭), 거래량 분석까지 포함된 **고급 데이터 분석 웹앱**입니다.")

# 사이드바 설정
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
st.sidebar.subheader("🔧 고급 옵션")
show_ma = st.sidebar.checkbox("📉 20일 이동평균선 표시", value=False)
apply_fx = st.sidebar.checkbox("💵 미국 주식을 원화(KRW)로 환산", value=True, help="실시간 원/달러 환율을 가져와 미국 주식 가격에 곱합니다.")

# 데이터 다운로드 함수 (주가, 거래량, 환율 모두 가져오기)
@st.cache_data
def load_data(tickers_dict, start, end):
    df_prices = pd.DataFrame()
    df_volumes = pd.DataFrame()
    
    # 1. 주식 데이터 가져오기
    for name, ticker in tickers_dict.items():
        stock_data = yf.download(ticker, start=start, end=end, progress=False)
        if not stock_data.empty:
            df_prices[name] = stock_data['Close'].squeeze()
            df_volumes[name] = stock_data['Volume'].squeeze()
            
    # 2. 환율 데이터(원/달러) 가져오기
    fx_data = yf.download("USDKRW=X", start=start, end=end, progress=False)
    if not fx_data.empty:
        df_fx = fx_data['Close'].squeeze()
    else:
        df_fx = pd.Series(1300, index=df_prices.index) # 환율을 못 불러오면 임시로 1300 적용
        
    return df_prices, df_volumes, df_fx

# 메인 화면 로직
if not selected_stocks:
    st.warning("👈 사이드바에서 비교할 주식을 하나 이상 선택해주세요.")
else:
    tickers_to_fetch = {name: stocks_dict[name] for name in selected_stocks}
    
    with st.spinner("빅데이터 및 실시간 환율을 분석 중입니다... ⏳"):
        df_prices, df_volumes, df_fx = load_data(tickers_to_fetch, start_date, end_date)
    
    if df_prices.empty:
        st.error("데이터를 불러오지 못했습니다.")
    else:
        df_prices = df_prices.ffill()
        df_volumes = df_volumes.ffill()
        
        # 주식 시장 휴장일 차이로 인한 환율 데이터 빈칸 채우기
        df_fx = df_fx.reindex(df_prices.index).ffill().bfill()
        
        # 환율 적용 로직 (미국 주식에만 환율 곱하기)
        if apply_fx:
            for stock, ticker in tickers_to_fetch.items():
                # .KS (한국주식) 기호가 안 붙은 종목은 미국 주식으로 간주
                if not ticker.endswith(".KS") and not ticker.endswith(".KQ"):
                    df_prices[stock] = df_prices[stock] * df_fx

        # 🌟 1. 고급 KPI 대시보드 (MDD 추가)
        st.subheader("📊 핵심 요약 및 리스크 지표")
        cols = st.columns(len(selected_stocks))
        
        for i, stock in enumerate(selected_stocks):
            if len(df_prices) >= 2:
                current_price = df_prices[stock].iloc[-1]
                prev_price = df_prices[stock].iloc[-2]
                diff = current_price - prev_price
                diff_pct = (diff / prev_price) * 100
                
                # MDD (최대 낙폭) 계산 공식
                peak = df_prices[stock].expanding(min_periods=1).max()
                drawdown = (df_prices[stock] / peak) - 1
                mdd = drawdown.min() * 100
                
                with cols[i]:
                    st.metric(label=f"{stock} (최근 종가)", 
                              value=f"{current_price:,.0f} 원" if apply_fx or ".KS" in tickers_to_fetch[stock] else f"${current_price:,.2f}", 
                              delta=f"{diff_pct:.2f}% (전일 대비)")
                    st.caption(f"⚠️ 최고점 대비 최대 하락률(MDD): **{mdd:.2f}%**")

        st.markdown("---")

        # 🌟 2. 탭(Tabs)을 이용한 화면 분할 레이아웃
        tab1, tab2, tab3 = st.tabs(["📈 차트 및 수익률", "📊 거래량 분석", "💵 환율 데이터"])
        
        with tab1:
            st.markdown("#### 🔍 주가 변동 차트")
            df_plot = df_prices.copy()
            if show_ma:
                for stock in selected_stocks:
                    df_plot[f"{stock}_20일_MA"] = df_plot[stock].rolling(window=20).mean()

            fig_price = px.line(df_plot, x=df_plot.index, y=df_plot.columns, 
                                title="마우스로 드래그하여 확대/축소하세요.",
                                labels={"value": "주가", "variable": "종목명", "index": "날짜"})
            st.plotly_chart(fig_price, use_container_width=True)
            
            st.markdown("#### 🚀 누적 수익률 비교 (%)")
            df_returns = (df_prices / df_prices.iloc[0] - 1) * 100
            fig_returns = px.line(df_returns, x=df_returns.index, y=df_returns.columns,
                                  labels={"value": "수익률 (%)", "variable": "종목명", "index": "날짜"})
            st.plotly_chart(fig_returns, use_container_width=True)

        with tab2:
            st.markdown("#### 📉 주식별 거래량 (Volume) 추이")
            st.markdown("거래량이 급증하는 날은 주로 주가에 큰 이슈(실적발표, 뉴스 등)가 있는 날입니다.")
            fig_vol = px.bar(df_volumes, x=df_volumes.index, y=df_volumes.columns,
                             labels={"value": "거래량", "variable": "종목명", "index": "날짜"},
                             barmode="group")
            st.plotly_chart(fig_vol, use_container_width=True)
            
        with tab3:
            st.markdown("#### 🇰🇷 원/달러 환율 (USD/KRW) 흐름")
            st.markdown("조회하신 기간 동안의 원/달러 환율 변동입니다. 환율이 오르면 수출 기업에 어떤 영향을 미칠지 생각해 보세요.")
            fig_fx = px.line(df_fx, x=df_fx.index, y=df_fx.name, 
                             labels={"value": "1달러당 원화 가격", "index": "날짜"})
            fig_fx.update_layout(showlegend=False)
            st.plotly_chart(fig_fx, use_container_width=True)
