import streamlit as st

st.set_page_config(page_title="경제 상식 퀴즈", page_icon="📖", layout="wide")

st.title("📖 경제 용어 사전 & 퀴즈")
st.markdown("당곡고 학생들을 위한 경제/금융 상식 페이지입니다. 앞선 페이지들에서 본 용어들을 정리해 봅시다.")

st.subheader("📚 핵심 용어 사전")
with st.expander("1. 캔들스틱 차트 (Candlestick Chart)"):
    st.write("하루 동안의 주식 가격 변동(시가, 종가, 고가, 저가)을 보여줍니다. 차트를 구성하는 캔들의 몸통과 꼬리를 통해 투자자들의 심리를 읽을 수 있습니다.")
with st.expander("2. 이동평균선 (Moving Average, MA)"):
    st.write("20일, 60일 등 일정 기간 동안의 주식 평균 가격을 선으로 연결한 것입니다. 추세를 파악하는 데 유용합니다.")
with st.expander("3. MDD (최대 낙폭, Maximum Drawdown)"):
    st.write("고점 대비 가장 크게 떨어진 하락률입니다. 투자의 '위험도(리스크)'를 판단할 때 수익률만큼이나 중요하게 봅니다.")
    
st.markdown("---")
st.subheader("📝 당곡고 경제 상식 퀴즈!")
q1_answer = st.radio("Q1. 투자자가 감당해야 할 최악의 상황, 즉 '최대 하락률'을 수치화한 지표의 이름은 무엇일까요?", 
                     ["선택하세요", "캔들스틱", "이동평균선", "MDD", "거래량"])

if q1_answer == "MDD":
    st.success("정답입니다! 워렌 버핏도 수익률보다 잃지 않는 것(리스크 관리)을 중요하게 생각했답니다. 👏")
elif q1_answer != "선택하세요":
    st.error("오답입니다. 용어 사전을 다시 한 번 읽어보세요!")
