import streamlit as st

def run_home():
    # 타이틀 및 소개
    st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>🏠 현대 & 기아 판매현황 분석 시스템</h1>
    <h4 style='text-align: center;'>📊 브랜드별 판매 데이터 자동 분석 및 전략 보고서 제공</h4>
    <hr>
    """, unsafe_allow_html=True)

    # KPI 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📁 분석 항목", "국가별, 차종별, 공장별")
    with col2:
        st.metric("📅 분석 기간", "2023 ~ 2025")
    with col3:
        st.metric("🧾 AI 리포트", "전략 요약 보고서 제공")

    st.markdown("---")

    # 주요 기능
    st.markdown("### 🔧 주요 기능")
    st.markdown(""" 
    - ✅ **브랜드별 맞춤 분석**: 현대차와 기아차의 사업구조에 맞춰 분석 항목 구분  
    - ✅ **시각화 제공**: Plotly 기반 트렌드 분석 시각화  
    - ✅ **AI 리포트**: GPT-4 기반, 마케팅팀·생산기획팀·경영진을 위한 전략 보고서 제공  
    - ✅ **향후 확장성**: 예측 모델 고도화 및 추천 시스템 연계 가능
    """)

    st.markdown("---")

    # 분석 항목
    st.markdown("### 🔍 분석 항목")

    st.markdown("#### 🚗 현대차")
    st.info("""
    - 🌍 **지역별 수출 분석**: 주요 국가별 수출량 추이  
    - 🚙 **차종별 판매 분석**: 차급·차종별 트렌드 및 인기 모델 파악
    """)

    st.markdown("#### 🚚 기아차")
    st.success("""
    - 🌍 **지역별 수출 분석**: 글로벌 국가별 수출 흐름  
    - 🚙 **차종별 판매 분석**: 차급별 변화 및 인기 차종 분석  
    - 🏭 **해외공장 판매 분석**: 해외 생산 거점별 판매 실적 분석  
    - 🛒 **해외현지 판매 분석**: 현지 딜러 판매 실적 기반의 수요 분석
    """)

    st.markdown("---")

    # 사용 방법
    st.markdown("### 📌 사용 방법")
    st.markdown("""
    1️⃣ **왼쪽 메뉴에서 브랜드 및 분석 항목 선택**  
    2️⃣ **자동 분석된 데이터 확인 또는 직접 업로드**  
    3️⃣ **시각화 및 전략 리포트 확인**  
    """)

    st.markdown("---")

    # 하단
    st.markdown("<p style='text-align: center;'>ⓒ 2025 판매현황 자동 분석 시스템 | Streamlit 기반 프로젝트</p>", unsafe_allow_html=True)
