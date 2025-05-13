import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu

def run_description1():
    st.title('데이터 전처리')
    
    # 데이터 로드
    df = pd.read_csv('data/현대_고객_데이터_완성.csv')
    df1 = pd.read_csv('main/project_1/data_mini1/description1.csv')
    df2 = pd.read_csv("main/project_1/data_mini1/description2.csv")
    df3=pd.read_csv("data/기아_고객데이터_신규입력용.csv")
    
    # 옵션 메뉴 설정
    selected = option_menu(
        menu_title=None,
        options=["원본 데이터", "RFM 분석", "연령 변환", "전처리 결과", "클러스터링", "이메일 발송"],
        icons=["database", "car-front", "leaf", "graph-up", "calendar", "check-square", "diagram-3", "envelope"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "orange", "font-size": "14px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1"},
        }
    )

    if selected == "원본 데이터":
        st.subheader('현대 고객 데이터')
        st.dataframe(df.head(), hide_index=True)
        st.subheader('기아 고객 데이터')
        st.dataframe(df3.head(), hide_index=True)



    elif selected == "RFM 고객 세그먼트 클러스터링":
        st.subheader('RFM 고객 세그먼트 분석 및 수정 🙆')
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.histogram(df, 
                            x="제품 구매 빈도 (Purchase Frequency)", 
                            color="고객 세그먼트 (Customer Segment)", 
                            title="구매빈도와 고객 세그먼트 관계",
                            labels={"제품 구매 빈도 (Purchase Frequency)": "구매빈도", 
                                    "count": "가입 수", 
                                    "고객 세그먼트 (Customer Segment)": "고객 세그먼트"},
                            barmode="stack")
            fig1.update_layout(xaxis_title="구매빈도", yaxis_title="가입 수", legend_title="고객 세그먼트")
            st.plotly_chart(fig1)

        with col2:
            fig2 = px.box(df, 
                        x="고객 세그먼트 (Customer Segment)", 
                        y="거래 금액 (Transaction Amount)", 
                        title="고객 세그먼트별 거래 금액 분포",
                        labels={"고객 세그먼트 (Customer Segment)": "고객 세그먼트", 
                                "거래 금액 (Transaction Amount)": "거래 금액"},
                        color="고객 세그먼트 (Customer Segment)",
                        color_discrete_sequence=px.colors.qualitative.Set1)
            fig2.update_layout(xaxis_title="고객 세그먼트", yaxis_title="거래 금액")
            st.plotly_chart(fig2)

        st.markdown("""
                    📌 구매빈도 횟수와 무관해보이는 세그먼트 구분<br>📌 일반, 신규 거래금액과 크게 차이가 없는 이탈가능 세그먼트의 거래금액 분포<br>
                    이탈가능 고객에게 적극적인 마케팅을 할 경우 VIP 고객이 될 수 있다는 잠재적 가능성이 있다고 보여집니다. 
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            df1['가입연도'] = df1['가입연도'].astype(int)
            fig = px.histogram(df1, 
                                x="가입연도", 
                                color="고객 세그먼트 (Customer Segment)", 
                                title="가입연도와 고객 세그먼트 관계",
                                labels={"가입연도": "가입연도", 
                                        "count": "가입 수", 
                                        "고객 세그먼트 (Customer Segment)": "고객 세그먼트"},
                                barmode="stack")
            fig.update_layout(
                xaxis_title="가입연도",
                yaxis_title="가입 수",
                legend_title="고객 세그먼트",
                xaxis=dict(tickmode='array', tickvals=[2022, 2023, 2024, 2025], ticktext=['2022', '2023', '2024', '2025'])
            )
            st.plotly_chart(fig)

        with col2:
            st.markdown("""
            <br><br><br><br><br><br>
            <span style="color:red;">2022, 2023, 2024년 가입자도 신규로 처리</span>된 경우가 많았습니다.<br>
            클라이언트측에서 업데이트를 처리하지 않은것으로 판단하고,<br>2025년 가입자만 신규 세그먼트로<br>
            그 외 신규세그먼트는 일반으로 변경 하였습니다.
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        category_order = ['신규', '일반', 'vip', '이탈가능', '총 인원']

        with col1:
            segment_counts1 = df1['고객 세그먼트 (Customer Segment)'].value_counts().reindex(category_order).fillna(0).astype(int)
            total_count1 = segment_counts1.sum()
            segment_counts1['총 인원'] = total_count1
            st.write(segment_counts1)
            st.markdown("변경 전 고객 세그먼트 분포")

        with col2:
            segment_counts2 = df2['고객 세그먼트'].value_counts().reindex(category_order).fillna(0).astype(int)
            total_count2 = segment_counts2.sum()
            segment_counts2['총 인원'] = total_count2
            st.write(segment_counts2)
            st.markdown("변경 후 고객 세그먼트 분포")
        
        st.markdown("**고객 정보 입력**시 기본값은 신규로, 하지만 클라이언트가 세그먼트를 변경할 수 있도록 하였습니다.")

    elif selected == "연령 변환":
        st.subheader('👵 연령 변환')
        st.markdown("""고객 생년월일 데이터를 25년 3월 기준 연령으로 변환 하였습니다.""")
        merged_df = pd.concat([df['생년월일 (Date of Birth)'], df2['연령']], axis=1)
        merged_df.columns = ['원본파일의 생년월일 (Date of Birth)', '변환 후 연령']
        st.dataframe(merged_df, hide_index=True)

    elif selected == "전처리 결과":
        st.subheader('전처리 후 고객정보 데이터셋 📊')
        df2['휴대폰번호'] = df2['휴대폰번호'].astype(str).apply(lambda x: '0' + x)
        st.dataframe(df2.head(), hide_index=True)

    elif selected == "클러스터링":
        st.title("KMeans 클러스터링 진행")
        st.subheader('클러스터링을 위한 X 데이터 선정')
        st.markdown("""
    위의 가공 데이터를 바탕으로 클러스터링을 위한 X 데이터를 선정하였습니다.
    - 연령
    - 거래 금액
    - 제품 구매 빈도
    - 성별,차량구분
    - 거래 방식
    - 제품 출시년월
    - 제품 구매 날짜
    - 고객 세그먼트
    - 친환경차 
        """)

        st.markdown("""<b>고객 세그먼트 (Customer Segment)를 클러스터링 결과로 보지 않고 X 값으로 활용한 이유:</b><br>
        세그먼트는 클라이언트의 전략적 판단에 따라 고객의 특성을 기반으로 나눈 값으로 보았습니다.<br>
                    클러스터링을 통해 고객을 더 세밀하게 분류한 후, 이를 기존 세그먼트와 결합하면, 비즈니스 전략에 더 유용한 인사이트를 제공할 수 있습니다.<br>
                    """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image('main/project_1/img/elbow.png', use_column_width=True)
        with col2:
            st.markdown("""<br><br><br><br><br><br>
    엘보우 기법 분석 결과 클러스터 수를 8개로 선정하여 KMeans 클러스터링을 진행하였습니다.<br>
                        클러스터링 결과는 EDA페이지에서 확인할 수 있습니다.<br>
                        """, unsafe_allow_html=True)

        st.subheader("SVC 모델을 활용한 신규 고객 클러스터링 분류")
        col1, col2 = st.columns(2)
        with col1:
            st.image('main_project/project_1/img/sc3.png', use_column_width=True)
        with col2:
            st.markdown("""
    파이프라인을 구축하여 새 고객 데이터가 입력되면 카테고리컬 데이터는 인코딩, 수치형 데이터는 스케일링이 자동으로 수행과, SVC 모델을 통해 클러스터링 및 분류가 이루어지도록 설계하였습니다.
                    """)
        col1, col2 = st.columns(2)
        with col1:
            st.code("""
    # 새로운 고객 데이터 생성
    new_customer_data = {
        "성별": ["남성"],
        "차량구분": ["대형 세단"],
        "거래 방식": ["현금"],
        "제품 출시년월": ["2023-01"],
        "제품 구매 날짜": ["2025-03-15"],
        "고객 세그먼트": ["신규"],
        "친환경차": ["부"],
        "연령": [21],
        "거래 금액": [90000000],
        "제품 구매 빈도": [2]
    }""")
        with col2:
            st.image('main_project/project_1/img/sc4.png', use_column_width=True)

    elif selected == "이메일 발송":
        st.subheader("고객 세그먼트별 프로모션 이메일 발송")
        st.markdown("""
    분석 결과를 토대로 고객 클러스터링별 프로모션 이메일이 발송되도록 설정하였습니다.
    """)
        col1, col2 = st.columns(2)
        with col1:
            st.image('main_project/project_1/img/sc1.png', use_column_width=True)
            st.markdown("0번 클러스터 프로모션 메일 예시")
        with col2:
            st.image('main_project/project_1/img/sc2.png', use_column_width=True)
            st.markdown("1번 클러스터 프로모션 메일 예시")