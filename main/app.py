import streamlit as st
from streamlit_option_menu import option_menu
import webbrowser

# 페이지 설정 (항상 최상단에 배치)
st.set_page_config(page_icon="🚗", page_title="Hyundai,Kia 고객 관리 시스템", layout="wide")

# 모듈 임포트
from project_1.ui_mini1.mini1_predata1 import run_predata1
from project_2.ui_mini2.mini2_predata2 import run_predata2
from project_2.ui_mini2.mini2_all_eda import run_all_eda
from project_1.ui_mini1.Car_insurance import run_car_customer_info
from project_1.ui_mini1.Car_insurance_ca import run_car_customer_ca
from project_1.ui_mini1.Car_insurance_us import run_car_customer_us
from project_1.ui_mini1.Car_insurance_mx import run_car_customer_mx
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

# 세션 상태 초기화 (없으면 기본값 설정)
if "brand" not in st.session_state:
    st.session_state["brand"] = "현대"
if "country" not in st.session_state:
    st.session_state["country"] = "대한민국"
if "dashboard_type" not in st.session_state:
    st.session_state["dashboard_type"] = "👤 딜러 전용 대시보드"

def run_insurance_consultation(country):
    """
    선택된 국가에 따라 보험 상담 기능을 실행합니다.
    """
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

    # Google Slides 링크
    SLIDES_LINK = "https://docs.google.com/presentation/d/1KC_awDiqIaV97Uzoqm72udBRS-SShRZt/edit?slide=id.p1#slide=id.p1"

    # 사이드바 영역 설정
    with st.sidebar:
        # 1. 브랜드 선택 (항상 상단)
        brand = option_menu(
            menu_title="브랜드 선택",
            options=["현대", "기아"],
            icons=["car-front", "truck"],
            default_index=0,
            orientation="horizontal"
        )
        st.session_state["brand"] = brand

        # 2. 대시보드 유형 선택
        dashboard_type = option_menu(
            menu_title="대시보드 선택",
            options=["👤 딜러 전용 대시보드", "📈 글로벌 수출 전략 대시보드"],
            icons=["person-badge", "bar-chart"],
            default_index=0,
        )
        st.session_state["dashboard_type"] = dashboard_type

        # 3. 하위 메뉴 설정
        if dashboard_type == "👤 딜러 전용 대시보드":
            # 국가 선택
            country = st.selectbox(
                "국가 선택",
                ["대한민국", "미국", "캐나다", "멕시코"]
            )
            st.session_state["country"] = country

            # 딜러 서브 메뉴
            dealer_menu = option_menu(
                menu_title="딜러 메뉴",
                options=["🏠 홈", "🧾 고객 상담", "🧾 보험 상담", "📊 고객 분석","💾원본 데이터 확인", "👩‍💻개발 기술서 확인"],
                icons=["house", "chat-dots", "pie-chart", "bar-chart", "database", "file-earmark-slides"],
                default_index=0
            )
        elif dashboard_type == "📈 글로벌 수출 전략 대시보드":
            # 브랜드에 따라 분석 메뉴 다르게 구성
            if brand == "기아":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 기아 기후별 예측","🌎글로벌 고객 데이터 분석", "🚗 기아 23년~25년 수출 분석", "📈 시장 트렌드", "📀원본 데이터 확인", "🧑‍💻개발 기술서 확인"],
                    icons=["house", "geo-alt", "cloud-sun","globe", "truck", "graph-up", "database", "file-earmark-slides"],
                    default_index=0
                )
            elif brand == "현대":
                analysis_menu = option_menu(
                    menu_title="분석 메뉴",
                    options=["🏠 홈", "📍 지역별 예측", "🌦️ 현대 기후별 예측","🌎글로벌 고객 데이터 분석", "🚙 현대 23년~25년 수출 분석", "📈 시장 트렌드", "📀원본 데이터 확인","🧑‍💻개발 기술서 확인"],
                    icons=["house", "geo-alt", "cloud-sun","globe", "car-front", "graph-up", "database", "file-earmark-slides"],
                    default_index=0
                )

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
        elif dealer_menu =="💾원본 데이터 확인":
            run_predata1()
        elif dealer_menu == "👩‍💻개발 기술서 확인":
            webbrowser.open_new_tab(SLIDES_LINK)
            st.warning("브라우저에서 개발과정 문서가 열립니다. 팝업이 차단된 경우 수동으로 열어주세요.")
            
    elif st.session_state["dashboard_type"] == "📈 글로벌 수출 전략 대시보드":
        if analysis_menu == "🏠 홈":
            run_home2()
        elif analysis_menu == "📍 지역별 예측":
            run_prediction_region()
        elif analysis_menu in ["🌦️ 기아 기후별 예측", "🌦️ 현대 기후별 예측"]:
            if st.session_state["brand"] == "기아":
                run_prediction_climate()
            elif st.session_state["brand"] == "현대":
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
        elif analysis_menu =="📀원본 데이터 확인":
            run_predata2()
        elif analysis_menu == "🧑‍💻개발 기술서 확인":
            webbrowser.open_new_tab(SLIDES_LINK)
            st.warning("브라우저에서 개발과정 문서가 열립니다. 팝업이 차단된 경우 수동으로 열어주세요.")

if __name__ == "__main__":
    main()