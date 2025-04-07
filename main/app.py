import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 설정
st.set_page_config(page_icon="🚗", page_title="Hyundai,Kia 고객 관리 시스템", layout="wide")

# 모듈 임포트
from project_2.ui_mini2.mini2_all_eda import run_all_eda
from project_1.ui_mini1.Car_insurance import run_car_customer_info
from project_1.ui_mini1.Car_insurance_ca import run_car_customer_ca
from project_1.ui_mini1.Car_insurance_us import run_car_customer_us
from project_1.ui_mini1.Car_insurance_mx import run_car_customer_mx
from project_1.ui_mini1.mini1_description import run_description1
from project_2.ui_mini2.mini2_description import run_description2
from project_1.ui_mini1.mini1_eda import run_eda
from project_1.ui_mini1.mini1_home import run_home1
from project_1.ui_mini1.mini1_input_new_customer_info import run_input_customer_info
from project_2.ui_mini2.mini2_eda_hyundai import run_eda_hyundai
from project_2.ui_mini2.mini2_eda_kia import run_eda_kia
from project_2.ui_mini2.mini2_prediction_climate import run_prediction_climate
from project_2.ui_mini2.mini2_prediction_region import run_prediction_region
from project_2.ui_mini2.mini2_trend import run_trend
from project_2.ui_mini2.mini2_home import run_home2
from project_2.ui_mini2.yeon import run_yeon

# 세션 상태 초기화
if "brand" not in st.session_state:
    st.session_state["brand"] = "현대"
if "country" not in st.session_state:
    st.session_state["country"] = "대한민국"
if "dashboard_type" not in st.session_state:
    st.session_state["dashboard_type"] = "👤 딜러 전용 대시보드"
if "prev_analysis_menu" not in st.session_state:
    st.session_state["prev_analysis_menu"] = None

def run_insurance_consultation(country):
    if country == "대한민국":
        run_car_customer_info()
    elif country == "미국":
        run_car_customer_us()
    elif country == "캐나다":
        run_car_customer_ca()
    elif country == "멕시코":
        run_car_customer_mx()
    else:
        st.error("해당 국가의 보험 상담 내용이 준비되지 않았습니다.")

def main():
    analysis_menu = None
    dealer_menu = None

    with st.sidebar:
        brand = option_menu(
            menu_title="브랜드 선택",
            options=["현대", "기아"],
            icons=["car-front", "truck"],
            default_index=0,
            orientation="horizontal"
        )
        st.session_state["brand"] = brand

        dashboard_type = option_menu(
            menu_title="대시보드 선택",
            options=["👤 딜러 전용 대시보드", "📈 글로벌 수출 전략 대시보드"],
            icons=["person-badge", "bar-chart"],
            default_index=0,
        )
        st.session_state["dashboard_type"] = dashboard_type

        if dashboard_type == "👤 딜러 전용 대시보드":
            country = st.selectbox(
                "국가 선택",
                ["대한민국", "미국", "캐나다", "멕시코"]
            )
            st.session_state["country"] = country

            dealer_menu = option_menu(
                menu_title="딜러 메뉴",
                options=["🏠 홈", "🧾 고객 상담", "🧾 보험 상담", "📊 고객 분석", "👩‍💻개발과정"],
                icons=["house", "chat-dots", "pie-chart"],
                default_index=0
            )
        elif dashboard_type == "📈 글로벌 수출 전략 대시보드":
            if brand == "기아":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 기아 기후별 예측", "🌎글로벌 고객 데이터 분석", "🚗 기아 23년~25년 수출 분석", "📈 시장 트렌드", "🧑‍💻개발과정"],
                    icons=["house", "geo-alt", "cloud-sun", "bi bi-globe-americas", "truck", "graph-up"],
                    default_index=0
                )
            elif brand == "현대":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 현대 기후별 예측", "🌎글로벌 고객 데이터 분석", "🚙 현대 23년~25년 수출 분석", "📈 시장 트렌드", "🧑‍💻개발과정"],
                    icons=["house", "geo-alt", "cloud-sun", "bi bi-globe-americas", "car-front", "graph-up"],
                    default_index=0
                )

    # 기후별 예측 → 다른 메뉴로 바뀌었을 경우에만 초기화
    if st.session_state["prev_analysis_menu"] in ["🌦️ 기아 기후별 예측", "🌦️ 현대 기후별 예측"] and \
        analysis_menu not in ["🌦️ 기아 기후별 예측", "🌦️ 현대 기후별 예측"]:
        for key in ["selected_climate", "selected_country", "model_result"]:
            if key in st.session_state:
                del st.session_state[key]

    # 이전 메뉴 갱신
    st.session_state["prev_analysis_menu"] = analysis_menu

    # --- 본문 콘텐츠 출력 ---
    if st.session_state["dashboard_type"] == "👤 딜러 전용 대시보드":
        if dealer_menu == "🏠 홈":
            run_home1()
        elif dealer_menu == "🧾 고객 상담":
            run_input_customer_info()
        elif dealer_menu == "🧾 보험 상담":
            run_insurance_consultation(st.session_state["country"])
        elif dealer_menu == "📊 고객 분석":
            run_eda()
        elif dealer_menu == "👩‍💻개발과정":
            run_description1()

    elif st.session_state["dashboard_type"] == "📈 글로벌 수출 전략 대시보드":
        if analysis_menu == "🏠 홈":
            run_home2()
        elif analysis_menu == "📍 지역별 예측":
            run_prediction_region()
        elif analysis_menu == "🌦️ 기아 기후별 예측":
            run_prediction_climate()
        elif analysis_menu == "🌦️ 현대 기후별 예측":
            run_yeon()
        elif analysis_menu == "🌎글로벌 고객 데이터 분석":
            run_all_eda()
        elif analysis_menu in ["🚗 기아 23년~25년 수출 분석", "🚙 현대 23년~25년 수출 분석"]:
            if st.session_state["brand"] == "기아":
                run_eda_kia()
            elif st.session_state["brand"] == "현대":
                run_eda_hyundai()
        elif analysis_menu == "📈 시장 트렌드":
            run_trend()
        elif analysis_menu == "🧑‍💻개발과정":
            run_description2()

if __name__ == "__main__":
    main()
