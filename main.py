import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# 페이지 기본 설정
st.set_page_config(page_title="당곡고 주식 분석 앱", page_icon="📈", layout="wide")

st.title("📈 한국 및 미국 주요 주식 수익률 비교")
st.markdown("당곡고등학교 학생들을 위한 주식 데이터 분석 웹앱입니다. 관심 있는 기업의 주가와 수익률을 비교해 보세요!")

# 사이드바 설정 (사용자 입력)
st.sidebar.header("⚙️ 분석 설정")

# 비교할 주식 목록 (한국 주식은 코스피의 경우 .KS, 코스닥의 경우 .KQ를 붙입니다)
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

# 다중 선택 박스
selected_stocks = st.sidebar.multiselect(
    "비교할 기업을 선택하세요:",
    options=list(stocks_dict.keys()),
    default=["삼성전자", "애플 (AAPL)", "엔비디아 (NVDA)"]
)

# 날짜 선택 (기본값: 오늘 기준으로 과거 1년)
end_date = st.sidebar.date_input("종료일", datetime.today())
start_date = st.sidebar.date_input("시작일", end_date - timedelta(days=365))

# 데이터 다운로드 함수 (캐시를 사용하여 속도 향상)
@st.cache_data
def load_data(tickers_dict, start, end):
    df_prices = pd.DataFrame()
    for name, ticker in tickers_dict.items():
        # yfinance를 통해 데이터 다운로드
        stock_data = yf.download(ticker, start=start, end=end, progress=False)
        if not stock_data.empty:
            # 'Close' (종가) 데이터만 추출하여 저장
            df_prices[name] = stock_data['Close'].squeeze() # squeeze()로 1차원 시리즈로 변환
    return df_prices

# 메인 화면 로직
if not selected_stocks:
    st.warning("👈 사이드바에서 비교할 주식을 하나 이상 선택해주세요.")
else:
    # 선택된 주식의 티커(종목코드)만 추출
    tickers_to_fetch = {name: stocks_dict[name] for name in selected_stocks}
    
    with st.spinner("데이터를 불러오는 중입니다... 잠시만 기다려주세요! ⏳"):
        df = load_data(tickers_to_fetch, start_date, end_date)
    
    if df.empty:
        st.error("데이터를 불러오지 못했습니다. 날짜 설정을 다시 확인해주세요.")
    else:
        # 결측치(빈 데이터) 처리: 이전 날짜의 가격으로 채움
        df = df.ffill()

        st.subheader("1. 주가 변동 차트 (단위: 원 / 달러)")
        st.markdown("한국 주식은 '원', 미국 주식은 '달러' 기준입니다. 절대적인 가격보다는 흐름을 참고하세요.")
        st.line_chart(df)
        
        st.subheader("2. 누적 수익률 비교 차트 (%)")
        st.markdown("선택한 기간의 **시작일 대비 얼마나 상승/하락했는지**를 백분율(%)로 보여줍니다.")
        
        # 수익률 계산: (현재가 - 시작가) / 시작가 * 100 
        # (첫 번째 행의 데이터를 시작가로 기준을 잡음)
        df_returns = (df / df.iloc[0] - 1) * 100
        st.line_chart(df_returns)
        
        st.subheader("3. 상세 종가 데이터")
        # 최신 데이터 5일 치를 보여줌 (인덱스의 시간 정보는 제거하고 날짜만 표시)
        df.index = df.index.strftime('%Y-%m-%d')
        st.dataframe(df.tail(5))
