import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

def run_description2():
    
    options=["원본데이터","데이터 전처리","대륙별 판매량 예측모델", "기후별 판매량 예측모델"]
    st.write("")
    st.write("")
    selected = option_menu(
    menu_title=None,
    options=options,
    default_index=0,
    orientation="horizontal",
    icons=["bi bi-gear", "bi bi-bar-chart-line", "bi bi-bar-chart-line-fill", "bi bi-bar-chart-line"],
    styles={
        "container": {"padding": "0!important", "background-color": "#f9f9f9"},
        "icon": {"color": "#2E86C1", "font-size": "20px"},
        "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
        "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
    }
    )

    if selected == options[0]:
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

    if selected ==options[1]: # 데이터 전처리 메뉴
        st.markdown("""
    ### 🛠 데이터 전처리 및 통합 과정

    1. **문자열 → 정수형 변환**  
    - `예: "5,388" → 5388`  
    - 쉼표(,)가 포함된 문자열 형태의 수치를 `int`형으로 변환하여 수치 계산 가능하도록 처리하였습니다. <br><br>

    2. **연도 컬럼 추가 및 통합**  
    - 실적 데이터에 연도(`2023`, `2024`, `2025`) 정보를 나타내는 `연도` 컬럼을 추가하였습니다.  
    - 이후, 연도별로 나누어져 있던 **차종별 / 지역별 / 공장별 / 국가별 실적 데이터**를  
        `pd.concat()`을 활용하여 하나의 데이터프레임으로 **연도 기준 통합**하였습니다.  
    - 이를 통해 **전년도 대비 실적 비교**나 **연도별 추세 분석**이 용이해졌습니다.<br><br>
                    
    3. **현대·기아 간 컬럼명 표준화**  
    - 4종류의 실적 분석 파일에서 사용된 **서로 다른 형식의 영문 컬럼명**을  
        분석 목적에 맞게 **공통된 한글 컬럼명**으로 통일하였습니다.  
    - 예시:  
        - `"Domestic"` → `"내수용"`  
        - `"Recreational Vehicle"` → `"휴양용 차량"`  
        - `"Mexico"` → `"북미-멕시코"`  
        - `"U.S.A"`, `"U.S.A."` → `"북미-미국"`<br><br>

    4. **결측치 처리**  
    - 주요 수치 컬럼의 `NaN` 값은 `0` 또는 일부만 누락된 경우 해당 행의 최소값(min) 으로 대체하여 데이터 연속성을 유지하였습니다.


    """, unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("""
    ### 📈 데이터 전처리 결과""")
        df1=pd.read_csv('main_project/project_2/ui/data/기아_지역별수출실적_전처리.csv')
        df2=pd.read_csv('main_project/project_2/ui/data/현대_차종별판매실적.csv')
        df1_filtered = df1[df1["차량 구분"] != "총합"]
        df1_top5 = df1_filtered.sort_values(by="2월", ascending=False).head(5)
        df2_top5 = df2.sort_values(by="2월", ascending=False).head(5)
        st.markdown("기아 지역별 수출실적 전처리 결과")
        st.dataframe(df1_top5.head(),hide_index=True)
        st.markdown("현대 차종별 수출실적 전처리 결과")
        st.dataframe(df2_top5.head(),hide_index=True)

    if selected ==options[2]: # 대륙별 판매량 예측모델
        st.markdown("---")
        st.markdown("""
    ### 📈  지역별 Prophet 예측 + 자동차 시장 트렌드 반영 LLM 분석 모델 제작과정""")
        df1=pd.read_csv('yeseul/mini2_data/현대_지역별수출실적.csv')
        df2=pd.read_csv('yeseul/mini2_data/현대_시장구분별_수출실적.csv')
        st.markdown("""
    원본 데이터를 **Prophet 모델**에 적합한 형태로 변환하기 위해
    `pd.melt()` 함수를 활용하여 **시계열 데이터**로 wide → long 변환하였습니다.
        """)

        st.write('**원본 데이터**')
        st.markdown("""
    - 행(row): "국가", "연도" 조합으로 구분된 레코드
    - 열(column): 1월 ~ 12월까지의 월별 수출 실적 수치가 나열된 **Wide Format**""")
        st.dataframe(df1.head(),hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("")
            st.write('**Melt 후 데이터**')
            st.dataframe(df2.head(),hide_index=True)
        with col2:
            st.markdown("""<br><br>
        - 월별 수치 컬럼들(`1월` ~ `12월`)은 하나의 컬럼으로 변환하여 → **"월"** 컬럼 생성<br>
        - `연도` + `월` 정보를 합쳐 **datetime** 형식의 → **"날짜"** 컬럼 생성  <br>
        - 원본 데이터 중 2025-02-01 이후의 데이터는 제거<br>
        - 최소 18개월 이상의 정보가 있어야 학습이 가능한 Prophet 모델을 위해 2021, 2022년 학습데이터 추가<br>
        - Prophet 모델 입력 형식에 맞추기 위해 컬럼명을 다음과 같이 변경:  
        - `"날짜"` → **`ds`** (Date Stamp, 날짜 정보, Prophet 예측을 위해 정렬처리)<br>
        - `"수출실적"` → **`y`** (예측 대상 값)  
        """, unsafe_allow_html=True)
            
        st.markdown("""
    Prophet은 기본적으로 일간(daily), 주간(weekly), 연간(yearly) 계절성을 자동으로 탐지하여 적용합니다.<br>
    그러나 분석 데이터는 **월별 수출 실적 데이터**로, 일, 주 단위 seasonality는 존재하지 않습니다.
                    """,unsafe_allow_html=True)
        st.code("model = Prophet(daily_seasonality=False, weekly_seasonality=False)")
        st.markdown("""
    - 존재하지 않는 일간, 주간 패턴을 학습하려는 것을 방지  
    - **과적합(Overfitting)** 및 불필요한 계산 리소스를 줄이기 위해  
    - `(daily_seasonality=False, weekly_seasonality=False)` 설정으로 **일간, 주간 계절성 비활성화**
                    """,unsafe_allow_html=True)

        st.write('**예측 결과 그래프 샘플**')
        st.image('main_project/project_2/img/아시아_수출실적.png')

        st.markdown("""

        📰 **네이버 뉴스 API 연동**
        - 선택한 시장(국가명)을 키워드로 하여  
        `"국가명 + 자동차 수출"` 관련 **최신 뉴스 기사 수집**
        - 수치 예측 외에 **최근 트렌드 분석과 세계 자동차시장 동향**을 함께 파악 가능
                    
        🧠 **GPT 기반 AI 해석 자동화**

        예측 수치와 뉴스 기사 데이터를 기반으로 GPT 모델을 활용하여  
        다음과 같은 항목을 자동으로 분석합니다:
        1. **시장 예측 요약**: 예측 결과 기반의 증가/감소 트렌드 분석  
        2. **최근 동향 정리**: 뉴스 키워드 기반 이슈 요약  
        3. **수출 패턴 분석**: Prophet 곡선을 기반으로 시각적 추세 해석  
        4. **전략적 제언**: 생산기획·마케팅 관점의 실행 가능한 전략 제시
        > 👉 판매량 예측 그래프 + 뉴스 기사를 통한 시장 동향 + AI 해석을 종합적으로 제공하여  
        > **경영진, 마케팅팀, 생산기획팀의 전략 수립에 핵심 인사이트를 지원합니다.**
        """)
        st.markdown("**프롬프트 설계 문장**")
        st.code(
            'prompt = f"""\n'
            '당신은 자동차 수출 시장을 분석하는 전문 보고서 작성자입니다. 아래 정보를 바탕으로, [시장 분석 보고서]를 작성해주세요.\n\n'
            '- 브랜드: {{channel}}\n'
            '- 시장명: {{selected_label}}\n'
            '- 최근 12개월간 실제 수출 실적: {{actual_trend_str}}\n'
            '- 선택한 분기: {{selected_q_label}}\n'
            '- ±1분기 예측 추세: {{forecast_trend}}  \n'
            '- ±1분기 예측 수출량 추이: {{trend_data_str}}\n'
            '- 최근 뉴스 키워드: {{news_keywords}}\n\n'
            '보고서 형식은 다음과 같이 작성해주세요:\n\n'
            '1. **{{selected_label}} 시장 예측 분석**  \n'
            '{{selected_label}} 시장의 특징과 현재 상황을 분석합니다.\n\n'
            '2. **최근 동향 요약**  \n'
            '뉴스 키워드를 바탕으로 최근 이슈 및 자동차 수출과 관련된 주요 변화 사항을 서술합니다.  \n'
            '해당 뉴스 키워드가 자동차 수출 시장에 긍정적 혹은 부정적인 영향을 줄지도 분석해주세요.\n\n'
            '3. **선택된 시점 ±1분기 예측 분석**  \n'
            '선택된 분기를 기준으로 총 6개월의 수출 예측 흐름을 분석해주세요.  \n'
            '어떤 요인들이 영향을 미칠 것으로 보이며, 어떤 주의사항이나 기회가 있는지 설명해주세요.\n\n'
            '4. **전략적 제언**  \n'
            '자동차 제조업체 또는 관련 산업이 향후 어떻게 대응하면 좋을지 구체적이고 현실적인 전략을 제시해주세요.\n\n'
            '보고서는 **전문적이지만 이해하기 쉽게**, **한글로** 작성해주세요.\n'
            '"""',
            language="python"
        )
        st.markdown("""**사용 모델**: `gpt-4-0125-preview`<br>
                    선정 이유: 리서치/분석/요약에 매우 적합, 긴 문서도 처리 가능 """,unsafe_allow_html=True)
        st.image('main_project/project_2/img/ai분석결과_예시.png')
        st.markdown("""
        프롬프트 엔지니어링을 토대로, 예측 지표와 뉴스 키워드를 결합한 **AI 기반 시장 보고서**가 자동 생성됩니다.  
        이 보고서는 수출 트렌드, 이슈 요약, 전략 제언까지 포함하여 의사결정자에게 **실질적인 인사이트**를 제공합니다.
        """)

    if selected ==options[3]: # 기후별 판매량 예측모델
            st.markdown("")
            st.subheader("🚗 차량구분 재분류")

            st.image('main_project/project_2/img/climate3.png')
            st.markdown("""
    기존의 차량 분류를 수출 전략을 세분화라기위해 더욱 세밀하게 분류했습니다.  
    `'상업용차', '상업용차(CKD)', '전기차', '미니밴', '미니밴(전기차)', '미니밴(CKD)', '세단','SUV', '세단(CKD)', '특수차', '특수차(CKD)', '소형차', 'SUV(CKD)'`13 가지로 재구성했습니다.
            """, unsafe_allow_html=True)
            st.subheader("🌍 기후대 컬럼 추가")
            st.markdown("""
    국가별 자동차 수요에 영향을 주는 기후 특성을 반영하기 위해, 각 국가에 대표 기후대를 지정했습니다.
    `한대, 냉대, 온대, 건조, 열대`의 5개 범주로 구분하였습니다.
            """, unsafe_allow_html=True)
            st.subheader("💰 GDP 컬럼 추가")
            st.markdown("""
    국가별 구매력 반영을 위해 **GDP 데이터**를 검색을 통해 찾아 컬럼을 추가하였습니다.
    결측치 처리: 유사국 기반 보정
    일부 누락된 수출실적은 **GDP 수준과 기후대가 유사한 국가군의 평균값을 기반으로 보완**했습니다.
    단순 평균보다 현실적인 방식으로, 데이터 신뢰도와 모델 성능을 동시에 향상시켰습니다.
        """, unsafe_allow_html=True)
            st.markdown("**GDP+기후별 전처리 후 데이터**")
            df1=pd.read_csv('main_project/project_2/ui/data/기아_gdp.csv')
            st.dataframe(df1.head(),hide_index=True)

            st.markdown("""
### 🔄 데이터 구조 변환 및 전처리  
월별 데이터를 Long 형식으로 변환하고, **날짜 컬럼** 생성  
**전월 수출량(lag), 다음달 수출량(target)** 파생  
결측값 제거 후, **예측에 필요한 컬럼**만 추출  
**범주형 변수**
- `'국가명', '기후대', '차종', '차량 구분'`은 **One-Hot Encoding** 처리  
**수치형 변수**
- `수출량, 전월_수출량, 연도, 월, GDP`는 **StandardScaler를 적용해 스케일 정규화 수행**  
(모델 학습의 안정성과 일관성을 위해 적용)
            """)

            st.image('main_project/project_2/img/climate2.png')
            st.markdown("""
 🎯 예측 변수(X)와 타겟(y)  
✅ X (입력 피처): `수출량, 전월_수출량, 연도, 월, GDP, 국가명, 기후대 , 차종 구분 ,차량 구분`   
🎯 y (타겟): `다음달_수출`

예측 정확도를 높이기 위해         
**[LinearRegression, RandomForest, XGBoost, LightGBM]** 4개의 회귀모델을 트레이닝 데이터와 학습 데이터는 80%:20% 비율로 나누어 학습 및 검증을 진행""")
            st.image('main_project/project_2/img/climate1.png')

            

            st.markdown("""
R2 스코어 결과는 0.84~0.86으로 비슷하였고, 그 중 가장 높은 정확성을 보인 LightGBM 모델을 채택하였습니다.
            """)