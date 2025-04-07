import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

def run_predata2():
    st.markdown("""
### 📊 원본 데이터 보기""")

    file_map = {
        "기아 2023년 해외공장 판매실적": "main_project/project_2/ui/data/원본_기아_2023년 해외공장판매실적.CSV",
        "기아 2023년 해외현지 판매": "main_project/project_2/ui/data/원본_기아_2023년 해외현지판매.CSV",
        "기아 2024년 지역별 수출실적": "main_project/project_2/ui/data/원본_기아_2024년_지역별수출실적.csv",
        "기아 2024년 차종별 판매실적": "main_project/project_2/ui/data/원본_기아_2024년_차종별판매실적.csv",
        "현대 2023년 해외공장 판매실적": "main_project/project_2/ui/data/원본_hmc-global-plant-sales-december-y2023.csv",
        "현대 2024년 EU 소매 판매실적": "main_project/project_2/ui/data/원본_hmc-eu-retail-sales-december-y2024.csv",
        "현대 2023년 지역별 수출실적": "main_project/project_2/ui/data/원본hmc-export-by-region-december-y2023.csv",
        "현대 2023년 차종별 판매실적": "main_project/project_2/ui/data/원본_hmc-sales-by-model-december-y2023.csv",
    }

    st.markdown("데이터는 해당 형식으로 2023, 2024, 2025년 년도별로 제공받았습니다.")

    selected_label = st.selectbox("확인할 원본 데이터를 선택하세요", list(file_map.keys()))
    file_path = file_map[selected_label]

    # 페이지 세션 상태 초기화
    if 'page' not in st.session_state:
        st.session_state.page = 1

    try:
        data = pd.read_csv(file_path)

        st.subheader("📁 원본 데이터")

        # 페이지네이션 설정
        page_size = 7
        total_pages = max(1, (len(data) // page_size) + (1 if len(data) % page_size else 0))

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button('◀ 이전', disabled=(st.session_state.page <= 1)):
                st.session_state.page -= 1
                st.rerun()

        with col2:
            st.write(f"페이지 {st.session_state.page} / {total_pages}")

        with col3:
            if st.button('다음 ▶', disabled=(st.session_state.page >= total_pages)):
                st.session_state.page += 1
                st.rerun()

        start_idx = (st.session_state.page - 1) * page_size
        end_idx = min(start_idx + page_size, len(data))
        st.dataframe(data.iloc[start_idx:end_idx], height=300)

        # 데이터 요약
        with st.expander("📊 데이터 요약 정보 보기"):
            st.write(f"• 총 행 수: {len(data):,}")
            st.write("• 컬럼 구조:")
            st.json({col: str(dtype) for col, dtype in data.dtypes.items()})

    except Exception as e:
        st.error(f"❌ 파일을 불러오는 중 오류 발생: {e}")

    st.markdown("---")
    st.markdown("""
**📌 데이터 출처**  
- [기아 공식 홈페이지](https://worldwide.kia.com/kr/company/ir/archive/sales-results)  
- [현대 공식 홈페이지](https://www.hyundai.com/worldwide/ko/company/ir/ir-resources/sales-results)  
- [협력사 제공 데이터](https://block-edu.s3.ap-northeast-2.amazonaws.com/%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8+%EB%8D%B0%EC%9D%B4%ED%84%B0.zip)
""")
