import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu

def run_predata1():
    st.title('원본 데이터 확인')
    
    # 데이터 로드
    df = pd.read_csv('data/현대_고객_데이터_완성.csv')
    df3 = pd.read_csv("data/기아_고객데이터_신규입력용.csv")
    

    st.subheader('현대 고객 데이터')
    
    # Initialize page state for Hyundai data
    if 'hyundai_page' not in st.session_state:
        st.session_state.hyundai_page = 1
        
    # Pagination for Hyundai data
    page_size = 7
    total_pages_hyundai = max(1, (len(df) // page_size) + (1 if len(df) % page_size else 0))
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button('◀ 이전', key='hyundai_prev', disabled=(st.session_state.hyundai_page <= 1)):
            st.session_state.hyundai_page -= 1
            st.rerun()
    with col2:
        st.write(f"페이지 {st.session_state.hyundai_page} / {total_pages_hyundai}")
    with col3:
        if st.button('다음 ▶', key='hyundai_next', disabled=(st.session_state.hyundai_page >= total_pages_hyundai)):
            st.session_state.hyundai_page += 1
            st.rerun()
            
    start_idx = (st.session_state.hyundai_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df))
    st.dataframe(df.iloc[start_idx:end_idx], height=300)
    
    st.subheader('기아 고객 데이터')
    
    # Initialize page state for Kia data
    if 'kia_page' not in st.session_state:
        st.session_state.kia_page = 1
        
    # Pagination for Kia data
    total_pages_kia = max(1, (len(df3) // page_size) + (1 if len(df3) % page_size else 0))
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button('◀ 이전', key='kia_prev', disabled=(st.session_state.kia_page <= 1)):
            st.session_state.kia_page -= 1
            st.rerun()
    with col2:
        st.write(f"페이지 {st.session_state.kia_page} / {total_pages_kia}")
    with col3:
        if st.button('다음 ▶', key='kia_next', disabled=(st.session_state.kia_page >= total_pages_kia)):
            st.session_state.kia_page += 1
            st.rerun()
            
    start_idx = (st.session_state.kia_page - 1) * page_size
    end_idx = min(start_idx + page_size, len(df3))
    st.dataframe(df3.iloc[start_idx:end_idx], height=300)


    st.markdown("---")
    st.markdown("""
**📌 데이터 출처**  
- [협력사 파일제공](https://block-edu.s3.ap-northeast-2.amazonaws.com/%EA%B3%A0%EA%B0%9Ddb_%ED%99%95%EC%9E%A5%EB%B3%B83.csv)  
- 기아 고객 가상데이터- ChatGPT를 통해 생성한 내부 시뮬레이션용 데이터
""")