import streamlit as st
from streamlit_option_menu import option_menu

# 페이지 설정 (항상 최상단에 배치)
st.set_page_config(page_icon="🚗", page_title="Hyundai 고객 관리 시스템", layout="wide")

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

# 다국어 지원을 위한 텍스트 딕셔너리 (완전한 버전)
LANGUAGES = {
    "대한민국": {
        "brand_select": "브랜드 선택",
        "dashboard_select": "대시보드 선택",
        "country_select": "국가 선택",
        "dealer_menu": "딜러 메뉴",
        "dealer_dashboard": "👤 딜러 전용 대시보드",
        "analysis_dashboard": "📈 영업 기획·분석 대시보드",
        "menu_options": {
            "home": "🏠 홈",
            "customer_consult": "🧾 고객 상담",
            "insurance_consult": "🧾 보험 상담",
            "customer_analysis": "📊 고객 분석",
            "dev_process": "👩‍💻개발과정"
        }
    },
    "미국": {
        "brand_select": "Brand Selection",
        "dashboard_select": "Dashboard Selection",
        "country_select": "Country Selection",
        "dealer_menu": "Dealer Menu",
        "dealer_dashboard": "👤 Dealer Dashboard",
        "analysis_dashboard": "📈 Sales Planning & Analysis Dashboard",
        "menu_options": {
            "home": "🏠 Home",
            "customer_consult": "🧾 Customer Consultation",
            "insurance_consult": "🧾 Insurance Consultation",
            "customer_analysis": "📊 Customer Analysis",
            "dev_process": "👩‍💻Development Process"
        }
    },
    "캐나다": {
        "brand_select": "Sélection de la marque",
        "dashboard_select": "Sélection du tableau de bord",
        "country_select": "Sélection du pays",
        "dealer_menu": "Menu du concessionnaire",
        "dealer_dashboard": "👤 Tableau de bord du concessionnaire",
        "analysis_dashboard": "📈 Tableau de bord de planification et d'analyse des ventes",
        "menu_options": {
            "home": "🏠 Accueil",
            "customer_consult": "🧾 Consultation client",
            "insurance_consult": "🧾 Consultation d'assurance",
            "customer_analysis": "📊 Analyse client",
            "dev_process": "👩‍💻Processus de développement"
        }
    },
    "멕시코": {
        "brand_select": "Selección de marca",
        "dashboard_select": "Selección de panel",
        "country_select": "Selección de país",
        "dealer_menu": "Menú del distribuidor",
        "dealer_dashboard": "👤 Panel del distribuidor",
        "analysis_dashboard": "📈 Panel de planificación y análisis de ventas",
        "menu_options": {
            "home": "🏠 Inicio",
            "customer_consult": "🧾 Consulta al cliente",
            "insurance_consult": "🧾 Consulta de seguros",
            "customer_analysis": "📊 Análisis del cliente",
            "dev_process": "👩‍💻Proceso de desarrollo"
        }
    }
}

# 세션 상태 초기화
def init_session_state():
    if "brand" not in st.session_state:
        st.session_state.brand = "현대"
    if "country" not in st.session_state:
        st.session_state.country = "대한민국"
    if "dashboard_type" not in st.session_state:
        st.session_state.dashboard_type = "dealer"
    if "selected_menu" not in st.session_state:
        st.session_state.selected_menu = "home"
    if "force_update" not in st.session_state:
        st.session_state.force_update = False

init_session_state()

def get_text(key):
    """현재 선택된 국가에 따라 해당 언어의 텍스트를 반환"""
    country = st.session_state.get("country", "대한민국")
    lang_dict = LANGUAGES.get(country, LANGUAGES["대한민국"])
    
    if "menu_options" in lang_dict and key in lang_dict["menu_options"]:
        return lang_dict["menu_options"][key]
    return lang_dict.get(key, key)

def run_insurance_consultation(country):
    """선택된 국가에 따라 보험 상담 기능을 실행"""
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
    # 사이드바 영역 설정
    with st.sidebar:
        # 1. 브랜드 선택 (항상 상단) - 언어 적용
        brand = option_menu(
            menu_title=get_text("brand_select"),
            options=["현대", "기아"],
            icons=["car-front", "truck"],
            default_index=0 if st.session_state.brand == "현대" else 1,
            orientation="horizontal",
            key="brand_menu"
        )
        if brand != st.session_state.brand:
            st.session_state.brand = brand
            st.rerun()

        # 2. 대시보드 유형 선택 (이 부분만 한국어 고정)
        dashboard_type = option_menu(
            menu_title=LANGUAGES["대한민국"]["dashboard_select"],
            options=["👤 딜러 전용 대시보드", "📈 영업 기획·분석 대시보드"],
            icons=["person-badge", "bar-chart"],
            default_index=0 if st.session_state.dashboard_type == "dealer" else 1,
            key="dashboard_menu"
        )
        
        # 대시보드 타입 업데이트
        new_dashboard_type = "dealer" if dashboard_type == "👤 딜러 전용 대시보드" else "analysis"
        if new_dashboard_type != st.session_state.dashboard_type:
            st.session_state.dashboard_type = new_dashboard_type
            st.rerun()

        # 3. 하위 메뉴 설정
        if st.session_state.dashboard_type == "dealer":
            # 국가 선택 - 언어 적용
            country_options = ["대한민국", "미국", "캐나다", "멕시코"]
            country = st.selectbox(
                get_text("country_select"),
                country_options,
                index=country_options.index(st.session_state.country),
                key="country_select"
            )
            
            if country != st.session_state.country:
                st.session_state.country = country
                st.rerun()

            # 딜러 서브 메뉴 - 언어 적용 (제목 포함)
            menu_options = [
                get_text("home"),
                get_text("customer_consult"),
                get_text("insurance_consult"),
                get_text("customer_analysis"),
                get_text("dev_process")
            ]
            
            selected_menu = option_menu(
                menu_title=get_text("dealer_menu"),  # 제목도 언어 적용
                options=menu_options,
                icons=["house", "chat-dots", "pie-chart", "graph-up", "laptop"],
                default_index=0,
                key="dealer_menu"
            )
            
            # 선택된 메뉴 매핑
            menu_mapping = {
                get_text("home"): "home",
                get_text("customer_consult"): "customer_consult",
                get_text("insurance_consult"): "insurance_consult",
                get_text("customer_analysis"): "customer_analysis",
                get_text("dev_process"): "dev_process"
            }
            st.session_state.selected_menu = menu_mapping.get(selected_menu, "home")
            
        elif st.session_state.dashboard_type == "analysis":
            # 영업 기획·분석 대시보드 (한국어 고정)
            if st.session_state.brand == "기아":
                menu_options = [
                    "🏠 홈", "📍 지역별 예측", "🌦️ 기아 기후별 예측", 
                    "🌎글로벌 고객 데이터 분석", "🚗 기아 분석", 
                    "📈 시장 트렌드", "🧑‍💻개발과정"
                ]
            else:
                menu_options = [
                    "🏠 홈", "📍 지역별 예측", "🌦️ 현대 기후별 예측", 
                    "🌎글로벌 고객 데이터 분석", "🚙 현대 분석", 
                    "📈 시장 트렌드", "🧑‍💻개발과정"
                ]
            
            selected_menu = option_menu(
                menu_title="분석 메뉴",  # 한국어 고정
                options=menu_options,
                icons=["house", "geo-alt", "cloud-sun", "globe-americas", "truck", "graph-up", "laptop"],
                default_index=0,
                key="analysis_menu"
            )
            
            # 선택된 메뉴 매핑
            menu_mapping = {option: option for option in menu_options}
            st.session_state.selected_menu = menu_mapping.get(selected_menu, "🏠 홈")

    # 메인 콘텐츠 영역 (사이드바 외부)
    if st.session_state.dashboard_type == "dealer":
        if st.session_state.selected_menu == "home":
            run_home1()
        elif st.session_state.selected_menu == "customer_consult":
            run_input_customer_info()
        elif st.session_state.selected_menu == "insurance_consult":
            run_insurance_consultation(st.session_state.country)
        elif st.session_state.selected_menu == "customer_analysis":
            run_eda()
        elif st.session_state.selected_menu == "dev_process":
            run_description1()
            
    elif st.session_state.dashboard_type == "analysis":
        if st.session_state.selected_menu == "🏠 홈":
            run_home2()
        elif st.session_state.selected_menu == "📍 지역별 예측":
            run_prediction_region()
        elif st.session_state.selected_menu in ["🌦️ 기아 기후별 예측", "🌦️ 현대 기후별 예측"]:
            if st.session_state.brand == "기아":
                run_prediction_climate()
            else:
                run_yeon()
        elif st.session_state.selected_menu == "🌎글로벌 고객 데이터 분석":
            run_all_eda()
        elif st.session_state.selected_menu in ["🚗 기아 분석", "🚙 현대 분석"]:
            if st.session_state.brand == "기아":
                run_eda_kia()
            else:
                run_eda_hyundai()
        elif st.session_state.selected_menu == "📈 시장 트렌드":
            run_trend()
        elif st.session_state.selected_menu == "🧑‍💻개발과정":
            run_description2()

if __name__ == "__main__":
    main()