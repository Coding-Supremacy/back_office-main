import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 설정은 항상 먼저
st.set_page_config(page_icon="🚗", page_title="Hyundai 고객 관리 시스템", layout="wide")

# 화면 모듈 임포트
from project_1.ui_mini1.mini1_description import run_description1
from project_2.ui_mini2.mini2_description import run_description2
from project_1.ui_mini1.mini1_eda import run_eda
from project_1.ui_mini1.mini1_home import run_home1
from hoyeon.main.project_1.ui_mini1.Car_insurance import run_input_customer_info
from project_2.ui_mini2.mini2_eda_hyundai import run_eda_hyundai
from project_2.ui_mini2.mini2_eda_kia import run_eda_kia
from project_2.ui_mini2.mini2_prediction_climate import run_prediction_climate
from project_2.ui_mini2.mini2_prediction_region import run_prediction_region
from project_2.ui_mini2.mini2_trend import run_trend
from project_2.ui_mini2.mini2_home import run_home2
from project_2.ui_mini2.yeon import run_yeon



def main():
    analysis_menu = None 
    with st.sidebar:
        # ✅ 1. 브랜드 선택 (항상 상단
        brand = option_menu(
            menu_title="브랜드 선택",
            options=["현대", "기아"],
            icons=["car-front", "truck"],
            default_index=0,
            orientation="horizontal"
        )
        st.session_state["brand"] = brand

        # ✅ 2. 대시보드 유형 선택
        dashboard_type = option_menu(
            menu_title="대시보드 선택",
            options=["👤 딜러 전용 대시보드", "📈 영업 기획·분석 대시보드"],
            icons=["person-badge", "bar-chart"],
            default_index=0,
        )

        # ✅ 3. 하위 메뉴
        if dashboard_type == "👤 딜러 전용 대시보드":
            # 국가 선택
            country = st.selectbox(
                "국가 선택",
                ["대한민국","미국", "캐나다", "멕시코"]
            )
            st.session_state["country"] = country

            # 딜러 서브 메뉴
            dealer_menu = option_menu(
                menu_title="딜러 메뉴",
                options=["🏠 홈", "🧾 고객 상담", "📊 고객 분석","👩‍💻개발과정"],
                icons=["house", "chat-dots", "pie-chart"],
                default_index=0
            )

        elif dashboard_type == "📈 영업 기획·분석 대시보드":
            # 브랜드에 따라 분석 메뉴 다르게
            if brand == "기아":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 기아 기후별 예측", "🚗 기아 분석", "📈 시장 트렌드","🧑‍💻개발과정"],
                    icons=["house", "geo-alt", "cloud-sun", "truck", "graph-up"],
                    default_index=0
                )
            elif brand == "현대":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 현대 기후별 예측", "🚙 현대 분석", "📈 시장 트렌드","🧑‍💻개발과정"],
                    icons=["house", "geo-alt", "cloud-sun", "car-front", "graph-up"],
                    default_index=0
                )

    # --- 본문 콘텐츠 출력 ---
    if dashboard_type == "👤 딜러 전용 대시보드":

        if dealer_menu == "🏠 홈":
            run_home1()
        elif dealer_menu == "🧾 고객 상담":
            run_input_customer_info()
        elif dealer_menu == "📊 고객 분석":
            run_eda()
        elif dealer_menu == "👩‍💻개발과정":
            run_description1()

    elif dashboard_type == "📈 영업 기획·분석 대시보드":
        if analysis_menu == "🏠 홈":
            run_home2()
        elif analysis_menu == "📍 지역별 예측":
            run_prediction_region()
        elif analysis_menu == "🌦️ 기아 기후별 예측":
            run_prediction_climate()
        elif analysis_menu == "🌦️ 현대 기후별 예측":
            run_yeon()
        elif analysis_menu == "🚗 기아 분석":
            run_eda_kia()
        elif analysis_menu == "🚙 현대 분석":
            run_eda_hyundai()
        elif analysis_menu == "📈 시장 트렌드":
            run_trend()
        elif analysis_menu == "🧑‍💻개발과정":
            run_description2()
        elif dealer_menu == "👩‍💻개발과정":
            run_description1()


if __name__ == "__main__":
    main()
