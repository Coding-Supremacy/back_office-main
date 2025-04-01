import streamlit as st
from streamlit_option_menu import option_menu

from yeseul.ui.mini1_eda import run_eda
from yeseul.ui.mini1_home import run_home
from yeseul.ui.mini1_input_new_customer_info import run_input_customer_info
from yeseul.ui.mini2_eda_hyundai import run_eda_hyundai
from yeseul.ui.mini2_eda_kia import run_eda_kia
from yeseul.ui.mini2_prediction_climate import run_prediction_climate
from yeseul.ui.mini2_prediction_region import run_prediction_region
from yeseul.ui.mini2_trend import run_trend

# 페이지 설정은 항상 먼저
st.set_page_config(page_title="Hyundai 고객 관리 시스템", layout="wide")


def main():

    # 본문 타이틀
    st.title("🚘 현대자동차 고객 관리 시스템")

    # --- 사이드바 네비게이션 ---
    with st.sidebar:
        # 1단계: 대시보드 유형 선택
        dashboard_type = option_menu(
            menu_title="대시보드 선택",
            options=["👤 딜러 전용 대시보드", "📈 영업 기획·분석 대시보드"],
            icons=["person-badge", "bar-chart"],
            default_index=0,
        )

        # 2단계: 선택된 대시보드에 따라 서브 메뉴 구성
        if dashboard_type == "👤 딜러 전용 대시보드":
            # 국가 선택
            country = st.selectbox(
                "국가 선택",
                ["미국", "서유럽", "아시아", "중동아프리카", "중남미", "캐나다", "동유럽", "멕시코"]
            )
            st.session_state["country"] = country

            # 딜러용 서브 메뉴
            dealer_menu = option_menu(
                menu_title=None,
                options=["🏠 홈", "🧾 고객 상담", "📊 고객 분석"],
                icons=["house", "chat-dots", "pie-chart"],
                default_index=0
            )

        elif dashboard_type == "📈 영업 기획·분석 대시보드":
            analysis_menu = option_menu(
                menu_title="분석 항목",
                options=["📍 지역별 예측", "🌦️ 기후별 예측", "🚗 기아 분석", "🚙 현대 분석", "📈 시장 트렌드"],
                icons=["geo-alt", "cloud-sun", "truck", "car-front", "graph-up"],
                default_index=0
            )

    # --- 본문 콘텐츠 ---
    if dashboard_type == "👤 딜러 전용 대시보드":
        st.header(f"{country} - {dealer_menu} 페이지")

        if dealer_menu == "🏠 홈":
            run_home()

        elif dealer_menu == "🧾 고객 상담":
            run_input_customer_info()

        elif dealer_menu == "📊 고객 분석":
            run_eda()

    elif dashboard_type == "📈 영업 기획·분석 대시보드":
        st.header(f"영업 분석 - {analysis_menu}")

        if analysis_menu == "📍 지역별 예측":
            run_prediction_region()

        elif analysis_menu == "🌦️ 기후별 예측":
            run_prediction_climate()

        elif analysis_menu == "🚗 기아 분석":
            run_eda_kia()

        elif analysis_menu == "🚙 현대 분석":
            run_eda_hyundai()

        elif analysis_menu == "📈 시장 트렌드":
            run_trend()

if __name__ == "__main__":
    main()


