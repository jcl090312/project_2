import streamlit as st
import random

st.title("💡 :green[도전! 경제 상식 골든벨]")
st.markdown("당곡고등학교 최고의 금융 마스터에 도전하세요. 매번 새로운 문제가 출제됩니다!")

# (퀴즈 30문제 리스트는 너무 기니까, 편의상 일부만 예시로 넣었습니다. 이전에 만든 30문제 리스트를 그대로 사용하셔도 됩니다.)
quiz_pool = [
    {"q": "고점 대비 가장 크게 떨어진 '최대 하락률'을 수치화한 지표는?", "options": ["MDD", "PER", "ROE", "ETF"], "a": "MDD"},
    {"q": "일정 기간 동안의 주식 평균 가격을 선으로 연결하여 전체적인 추세를 보여주는 차트 보조지표는?", "options": ["캔들스틱", "이동평균선", "거래량", "볼린저밴드"], "a": "이동평균선"},
    {"q": "한국의 대표적인 주가지수로, 삼성전자, 현대차 등 대형 우량주들이 주로 상장된 시장은?", "options": ["코스닥(KOSDAQ)", "코스피(KOSPI)", "나스닥(NASDAQ)", "S&P 500"], "a": "코스피(KOSPI)"},
    {"q": "미국의 대표적인 기술주 중심 시장으로, 애플, 구글, 테슬라 등이 상장된 곳은?", "options": ["다우존스", "나스닥", "니케이", "코스피"], "a": "나스닥"},
    {"q": "물가가 지속적으로 상승하여 돈의 가치가 떨어지는 현상은?", "options": ["디플레이션", "스태그플레이션", "인플레이션", "테이퍼링"], "a": "인플레이션"},
    {"q": "하루 동안 주가가 오를 수 있는 최대 한도(한국은 ±30%)를 무엇이라 하나요?", "options": ["상한가", "하한가", "시초가", "종가"], "a": "상한가"},
    {"q": "한국 돈(원화)과 미국 돈(달러)을 교환할 때 적용되는 비율을 무엇이라 하나요?", "options": ["금리", "환율", "세율", "물가"], "a": "환율"},
]

if 'random_quiz' not in st.session_state:
    st.session_state.random_quiz = random.sample(quiz_pool, 5)

col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🔄 문제 새로 뽑기", use_container_width=True):
        st.session_state.random_quiz = random.sample(quiz_pool, 5)
        st.rerun()

st.markdown("---")

for i, q_dict in enumerate(st.session_state.random_quiz, 1):
    # 문제를 테두리가 있는 예쁜 상자(카드) 안에 넣기
    with st.container(border=True):
        st.markdown(f"### 🎯 Q{i}. {q_dict['q']}")
        
        options = ["선택하세요"] + q_dict['options']
        user_choice = st.radio(f"Q{i} 옵션", options, label_visibility="collapsed", key=f"q{i}")
        
        if user_choice != "선택하세요":
            if user_choice == q_dict['a']:
                st.success("✨ 완벽합니다! 정답! ✨")
                # 1번 문제 정답을 맞췄을 때만 서프라이즈 풍선 날리기!
                if i == 1:
                    st.balloons()
            else:
                st.error(f"아쉽습니다. 정답은 **{q_dict['a']}** 입니다.")
