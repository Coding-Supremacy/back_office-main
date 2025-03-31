import threading
import streamlit as st
from streamlit_option_menu import option_menu
import warnings
warnings.filterwarnings("ignore")

# 미니프로젝트1 임포트 (고객 클러스터)
from project_1.ui_mini1 import promo_email
from project_1.ui_mini1.eda import run_eda as run_eda_mini1
from project_1.ui_mini1.home import run_home as run_home_mini1
from project_1.ui_mini1.description_mini1 import run_description_mini1
from project_1.ui_mini1.input_new_customer_info import run_input_customer_info

# 미니프로젝트2 임포트 (자동차 분석)
from project_2.ui.home import run_home as run_home_mini2
from project_2.ui.description import run_description as run_description_mini2
from project_2.ui.eda_kia import run_eda_kia
from project_2.ui.eda_hyundai import run_eda_hyundai
from project_2.ui.trend import run_trend
from project_2.ui.prediction_region import run_prediction_region
from project_2.ui.ho import run_ho


# 페이지 설정
st.set_page_config(
    page_title="통합 분석 시스템",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 통합
def configure_styles():
    st.markdown("""
    <style>
        /* 공통 스타일 */
        .main { padding: 2rem; }
        .sidebar .sidebar-content { padding: 1rem; }
        div[data-testid="stSidebarUserContent"] { padding: 1rem; }
        .stButton>button { width: 100%; }
        .stDownloadButton>button { width: 100%; }
        
        /* 컨텐츠 영역 */
        .block-container {
            max-width: 1300px;
            margin: auto;
            padding: 2rem;
            border-radius: 10px;
            background-color: white;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        
        /* 제목 스타일 */
        h1, h2, h3 {
            color: #343a40;
        }
    </style>
    """, unsafe_allow_html=True)

# 메인 메뉴 구성
def main_menu():
    with st.sidebar:
        st.title("📊 통합 분석 시스템")
        
        # 상위 메뉴 선택 (두 프로젝트 간 전환)
        main_choice = option_menu(
            None,
            ["고객 클러스터", "현대/기아 분석"],
            icons=["people-fill", "car-front-fill"],
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {"font-size": "16px", "margin": "5px 0", "padding": "10px"},
            }
        )
        
        st.markdown("---")
        
        # 서브 메뉴 구성
        if main_choice == "고객 클러스터":
            st.markdown("## 🧑 고객 분석 메뉴")
            selected = option_menu(
                None,
                ["홈", "고객정보 입력", "고객 분석", "개발 과정"],
                icons=['house', 'person-plus', 'graph-up', 'tools'],
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "nav-link": {"font-size": "14px", "margin": "5px 0"},
                }
            )
        else:
            st.markdown("## 🚗 자동차 분석 메뉴")
            selected = option_menu(
                None,
                ["홈", "지역별 예측", "기후별 예측", "기아 분석", "현대 분석", "시장 트렌드", "프로젝트 개발과정"],
                icons=['house', 'geo-alt', 'cloud-sun', 'truck-front-fill', 'car-front', 'graph-up-arrow', 'tools'],
                default_index=0,
                styles={
                    "container": {"padding": "0!important"},
                    "nav-link": {"font-size": "14px", "margin": "5px 0"},
                }
            )
            
        st.markdown("---")
        st.markdown("## 📚 정보")
        st.info("왼쪽 메뉴에서 분석 유형을 선택해주세요")
        
    return main_choice, selected

# 페이지 라우팅
def route_pages(main_choice, selected):
    if main_choice == "고객 클러스터":
        if selected == "홈":
            run_home_mini1()
        elif selected == "고객정보 입력":
            run_input_customer_info()
        elif selected == "고객 분석":
            run_eda_mini1()
        elif selected == "개발 과정":
            run_description_mini1()
    else:
        if selected == "홈":
            run_home_mini2()
        elif selected == "지역별 예측":
            run_prediction_region()
        elif selected == "기후별 예측":
            run_ho()
        elif selected == "기아 분석":
            run_eda_kia()
        elif selected == "현대 분석":
            run_eda_hyundai()
        elif selected == "시장 트렌드":
            run_trend()
        elif selected == "프로젝트 개발과정":
            run_description_mini2()

def main():
    configure_styles()
    main_choice, selected = main_menu()
    route_pages(main_choice, selected)
    
    # 미니프로젝트1의 이메일 스케줄러 실행
    if main_choice == "고객 클러스터":
        scheduler_thread = threading.Thread(target=promo_email.schedule_worker, daemon=True)
        scheduler_thread.start()

if __name__ == "__main__":
    main()