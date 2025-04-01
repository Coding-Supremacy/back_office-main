import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 설정은 항상 먼저
st.set_page_config(page_icon="🚗", page_title="Hyundai 고객 관리 시스템", layout="wide")

# 화면 모듈 임포트
from ui.mini1_eda import run_eda
from ui.mini1_home import run_home1
from ui.mini1_input_new_customer_info import run_input_customer_info
from ui.mini2_eda_hyundai import run_eda_hyundai
from ui.mini2_eda_kia import run_eda_kia
from ui.mini2_prediction_climate import run_prediction_climate
from ui.mini2_prediction_region import run_prediction_region
from ui.mini2_trend import run_trend
from ui.mini2_home import run_home2
from ui.yeon import run_yeon


def main():
    analysis_menu = None

    with st.sidebar:
        # ✅ 1. 브랜드 선택
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
            country = st.selectbox(
                "국가 선택",
                ["미국", "캐나다", "멕시코", "한국"]
            )
            st.session_state["country"] = country

            dealer_menu = option_menu(
                menu_title="딜러 메뉴",
                options=["🏠 홈", "🧾 고객 상담", "📊 고객 분석"],
                icons=["house", "chat-dots", "pie-chart"],
                default_index=0
            )
            current_page = f"딜러-{dealer_menu}"

        elif dashboard_type == "📈 영업 기획·분석 대시보드":
            if brand == "기아":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 기아 기후별 예측", "🚗 기아 분석", "📈 시장 트렌드"],
                    icons=["house", "geo-alt", "cloud-sun", "truck", "graph-up"],
                    default_index=0
                )
            elif brand == "현대":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 현대 기후별 예측", "🚙 현대 분석", "📈 시장 트렌드"],
                    icons=["house", "geo-alt", "cloud-sun", "car-front", "graph-up"],
                    default_index=0
                )
            current_page = f"{brand}-{analysis_menu}"

    # ✅ 세션 상태 초기화 로직
    if "last_page" in st.session_state and st.session_state["last_page"] != current_page:
        # brand, country 값은 유지
        temp_brand = st.session_state.get("brand")
        temp_country = st.session_state.get("country")
        st.session_state.clear()
        st.session_state["brand"] = temp_brand
        st.session_state["country"] = temp_country

    st.session_state["last_page"] = current_page

    # ✅ 본문 출력
    if dashboard_type == "👤 딜러 전용 대시보드":
        if dealer_menu == "🏠 홈":
            run_home1()
        elif dealer_menu == "🧾 고객 상담":
            run_input_customer_info()
        elif dealer_menu == "📊 고객 분석":
            run_eda()

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


if __name__ == "__main__":
    main()
