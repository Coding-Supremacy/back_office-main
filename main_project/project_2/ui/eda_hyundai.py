import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import os

# CSS 스타일링 (이전 스타일 코드 그대로 사용)
st.markdown("""
<style>
    /* CSS 스타일 코드 (이전 예시와 동일) */
    /* 이 부분은 현대차 대시보드 스타일을 그대로 가져와서 사용하시면 됩니다. */
</style>
""", unsafe_allow_html=True)



# 데이터 로드 함수
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    df_export = pd.read_csv(os.path.join(BASE_DIR, "data/현대_지역별수출실적.csv"))
    df_sales = pd.read_csv(os.path.join(BASE_DIR, "data/현대_차종별판매실적.csv"))
    return df_export, df_sales

df_export, df_sales = load_data()

def car_type():
    car_types = {
            '세단 내연기관': [
                'Avante (CN7)', 'Sonata (LF)', 'Sonata (DN8)',
                'Grandeur (IG)', 'Grandeur (GN7)', 'G70 (IK)',
                'G80 (RG3)', 'G90 (HI)',  'Verna (Hci)', 'Verna (BN7i)',
                'Elantra (CN7c)', 'La festa (SQ)', 'Verna (YC)',
                'Celesta (ID)', 'Mistra (DU2)', 'Elantra (CN7a)',
                'Sonata (DN8a)', 'Solaris (HCr)', 'Accent (HCv)',
                'Accent (BN7v)', 'Elantra (CN7v)'
            ],
            '세단 하이브리드': [
                'Avante (CN7 HEV)', 'IONIQ (AE HEV)', 'Sonata (DN8 HEV)',
                'Grandeur (IG HEV)', 'Grandeur (GN7 HEV)'
            ],
            '세단 전기차': [
                'IONIQ (AE EV)', 'IONIQ 6 (CE)', 'G80 (RG3 EV)'
            ],
            'SUV 내연기관': [
                'Venue (QX)', 'Kona (OS)',  'Kona (SX2)', 'Tucson (TL)',
                'Tucson (NX4)', 'Santa-Fe (TM)', 'Santa-Fe (MX5)',
                'Palisade (LX2)', 'GV80 (JX)', 'Exter (AI3 SUV)', 'Venue (QXi)',
                'Creta (SU2i)', 'Creta(SU2i)', 'Bayon (BC3 CUV)',
                'Mufasa (NU2)', 'Tucson (NX4c)', 'ix35 (NU)',
                'Santa Fe (MX5c)', 'Santa Fe (TMc)', 'Tucson (NX4a)',
                'Tucson OB (NX4a OB)', 'Santa-Fe (TMa)', 'GV70 (JKa)',
                'Tucson (TLe)', 'Tucson (NX4e)',  'Creta (SU2r)',
                'Creta (GSb)', 'Creta (SU2b)', 'Santa-Fe (TMid)',
                'Santa-Fe (MX5id)',  'Creta (SU2id)',
                'Creta (SU2v)', 'Tucson (NX4v)', 'Santa Fe (TMv)',
                'Santa Fe (MX5v)', 'Palisade (LX3)',
                'GV80 Coupe (JX Coupe)'
            ],
            'SUV 하이브리드': [
                'Kona (OS HEV)', 'Kona (SX2 HEV)', 'Tucson (NX4 HEV)',
                'Santa-Fe (TM HEV)', 'Santa-Fe (MX5 HEV)',
                'Santa Fe HEV (TMa HEV)', 'Tucson HEV (NX4c HEV)',
                'Santa-Fe HEV (MX5a HEV)',  'Tucson HEV (NX4e HEV)',
                'Santa Fe HEV (TMv HEV)', 'Santa-Fe (MX5id HEV)'
            ],
            'SUV 전기차': [
                'Kona (OS EV)', 'Kona (OS N)', 'Kona (SX2 EV)', 'NEXO (FE)',
                'IONIQ 5 (NE)', 'IONIQ 5 N (NE N)', 'Kona N (OS N)',
                'Tucson (NX4 PHEV)', 'Santa-Fe (TM PHEV)',
                'Santa-Fe (MX5 PHEV)', 'GV70 EV (JK EV)',
                'Kona EV (OSi EV)', 'IONIQ5 (NEi)', 'Tucson (NX4i)',
                'Exter(AI3 SUV)', 'Venue(QXi)', 'Creta(SU2i)',
                'Creta(SU2i LWB)', 'Tucson OB (NX4a OB)',  'Ioniq5 (NEa)',
                'Kona EV (OSe EV)', 'Kona EV (SX2e EV)',
                'Tucson PHEV (NX4e PHEV)',  'Kona EV (SX2id EV)',
                'IONIQ5 (NE)', 'IONIQ5 (NEid N)', 'GV70 (JKa)',
                'GV70 EV (Jka EV)', 'IONIQ5 (NEv)', 'GV60 (JW)',
                'Palisade (LX3 HEV)', 'Palisade (LX2v)', 'Santa Fe (TMv)'
            ],
            '기타': [
                'Veloster (JS N)', 'G70 S/B (IK S/B)', 'Casper (AX)', 'LCV',
                'HCV', 'i30 (PD)', 'Grand i10 (AI3 5DR)', 'i20 (BI3 5DR)',
                'i10 (AC3)', 'i20 (BC3)', 'i20 N (BC3 N)', 'Custo (KU)',
                'BHMC', 'i30 (PDe)', 'i30 (Pde N)', 'HB20 (BR2)',
                'Stargazer (KS)', 'HTBC', 'NX4m', 'HCm', 'Others', 'CV',
                'i10(AI3v 4DR)', 'i10(AI3v 5DR)', 'Kusto (KUv)', 'Porter (HRv)',
                'Mighty (LTv)', 'Mighty (VTv)', 'Mighty (QTv)',
                'Mighty (QTc)', 'Truck',  'IONIQ5 Robotaxi (NE R)',
                'PV', 'G90', 'Casper (AX EV)', 'Casper EV (AX EV)',
                'IONIQ New Car (ME)', 'Palisade (LX3 HEV)', 'Santa Fe (TMv)', 'Santa Fe (MX5v)'
            ]
                   
        }
    return car_types
car_types = car_type()

# 차종 판매실적 반복 함수
def filter_sales_data_by_year_and_type():
    df_sales_melted =  df_sales.melt(id_vars=['차량 모델', '차량 유형', '판매 구분', '연도'], 
                                        value_vars=["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"] ,
                                        var_name='월', value_name='판매량')
    
    # 카테고리 매핑 딕셔너리 만들기
    car_category_map = {}
    for category, models in car_types.items():
        for model in models:
            car_category_map[model] = category

    # df_sales에 카테고리 컬럼 추가
    df_sales_melted['카테고리'] = df_sales_melted['차량 모델'].map(car_category_map)
            
    모델_유형_2023 = df_sales_melted.loc[df_sales_melted['연도'] == 2023] 
    모델_유형_2024 = df_sales_melted.loc[df_sales_melted['연도'] == 2024]

    모델_유형_국내_2023 = 모델_유형_2023.loc[모델_유형_2023['판매 구분'] == '내수용']
    모델_유형_해외_2023 = 모델_유형_2023.loc[모델_유형_2023['판매 구분'] != '내수용']

    모델_유형_국내_2024 = 모델_유형_2024.loc[모델_유형_2024['판매 구분'] == '내수용']
    모델_유형_해외_2024 = 모델_유형_2024.loc[모델_유형_2024['판매 구분'] != '내수용']

    전체_국내 = df_sales_melted.loc[df_sales_melted['판매 구분'] == '내수용']
    전체_해외 = df_sales_melted.loc[df_sales_melted['판매 구분'] != '내수용']
    
    # 전체_국내에 카테고리 컬럼 추가
    전체_국내['카테고리'] = 전체_국내['차량 모델'].map(car_category_map)
    # 전체_해외에 카테고리 컬럼 추가
    전체_해외['카테고리'] = 전체_해외['차량 모델'].map(car_category_map)

    

    

    return df_sales_melted, 모델_유형_2023, 모델_유형_2024, 모델_유형_국내_2023, 모델_유형_해외_2023, 모델_유형_국내_2024, 모델_유형_해외_2024, 전체_국내, 전체_해외

df_sales_melted, 모델_유형_2023, 모델_유형_2024, 모델_유형_국내_2023, 모델_유형_해외_2023, 모델_유형_국내_2024, 모델_유형_해외_2024, 전체_국내, 전체_해외 = filter_sales_data_by_year_and_type()


# 메인 함수
def run_eda_hyundai():

    st.markdown("<h1 style='text-align: center;'>🏎️ 현대 수출실적 대시보드</h1>", unsafe_allow_html=True)

    selected = option_menu(
        menu_title=None,
        options=["📊 지역별 수출 분석", "🏎️ 차종별 판매 분석"],
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f9f9f9"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px", "padding": "10px"},
            "nav-link-selected": {"background-color": "#2E86C1", "color": "white"},
        }
    )

    if selected == "📊 지역별 수출 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("📊 지역별 수출 실적 변화")

        # 데이터 전처리 (차량 구분을 고려하지 않고 모든 데이터를 사용)
        df_export_filtered = df_export.copy()  # 차량 구분 없이 전체 데이터를 사용
        countries = df_export_filtered['국가'].unique()

        selected_countries = st.multiselect("국가를 선택하세요:", options=list(countries), default=list(countries))

        if selected_countries:
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            for country in selected_countries:
                country_data = df_export_filtered[df_export_filtered['국가'] == country].copy()

                # 연도별 월별 판매량 데이터를 하나의 Series로 만들기
                monthly_sales = []
                years = country_data['연도'].unique()

                for year in years:
                    year_data = country_data[country_data['연도'] == year]
                    month_cols = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
                    for month in month_cols:
                        if month in year_data.columns:
                            sales = year_data[month].values
                            if len(sales) > 0:
                                monthly_sales.append(sales[0])
                            else:
                                monthly_sales.append(None)
                        else:
                            monthly_sales.append(None)

                # x축 날짜 생성 및 2025-03-01 이후 데이터 제거
                dates = pd.date_range(start='2023-01-01', periods=len(monthly_sales), freq='M')
                dates = dates[dates <= pd.to_datetime('2025-03-01')]
                monthly_sales = monthly_sales[:len(dates)]

                # NaN 값을 제외한 데이터만 플롯
                valid_indices = [i for i, x in enumerate(monthly_sales) if pd.notna(x)]
                valid_dates = [dates[i] for i in valid_indices]  # Use list comprehension
                valid_sales = [monthly_sales[i] for i in valid_indices]  # Use list comprehension

                fig.add_trace(
                    go.Scatter(x=valid_dates, y=valid_sales, mode='lines+markers', name=country,
                            hovertemplate='%{x|%Y-%m-%d}<br>판매량: %{y:,.0f}<extra></extra>')
                )
            
            # x축 범위를 데이터에 맞게 조정
            fig.update_layout(
                title='주요 시장별 수출량 변화', 
                xaxis_title='날짜', 
                yaxis_title='판매량', 
                legend_title='국가', 
                hovermode="closest",
                xaxis_range=[min(valid_dates), max(valid_dates)] if valid_dates else None  # 데이터가 있는 경우에만 범위 설정
            )

            st.plotly_chart(fig, use_container_width=True)
            st.divider()

            st.markdown("""
            <div style="background-color:#FFEBCD; padding:15px; border-radius:10px;">
            <span style="font-size:20px; font-weight:bold;">📌 2023-2025년 현대차 지역별 수출 실적 분석</span><br>

            1. <b>북미-미국</b>은 전체 수출의 <b>50% 이상</b> 차지하며 압도적 1위 (2023-2024년 평균 월 4.8만~5.7만대)<br>
            → <span style='color:#D35400'>2024년 10월 <b>63,939대</b></span>로 최고 기록, <span style='color:#D35400'>2025년 1월 <b>41,454대</b></span>로 출발

            2. <b>북미-캐나다</b>는 매년 안정적 판매를 유지하며 <b>월 1만대 내외</b> 유지<br>
            → <span style='color:#2E86C1'>2024년 12월 <b>10,807대</b></span> 기록

            3. <b>서유럽</b>은 상반기 24년 4월에 12,855대로 증가했다가 다시 감소하며, <b>하반기(10-12월) 판매 강세</b><br>
            → <span style='color:#2E8B57'>2024년 4월 <b>12,855대</b></span>로 연중 최고치 기록<br>
            → 2024년 4월 이후로 감소했다가 2024년 12월 <span style='color:#2E8B57'><b>12,842대</b><span>로 다시 증가                        

            4. <b>중동·아프리카</b>는 계절 변동성 크며 <b>2023년 3월 12,760대 → 2024년 3월 8,131대</b>로 감소<br>
            → 수요 감소 추세 대비 전략 조정 필요

            </div>
            """, unsafe_allow_html=True)
            st.write('')
            st.success("""
            ✅ **마케팅 전략 권장사항**  
            1. 북미-미국: 안정적 공급망 유지  
            2. 중동·아프리카: 2023년 3월 실적(12,760대) 재현을 위한 타겟 마케팅  
            3. 북미-멕시코: 2024년 3~4월 급증 원인 분석 후 확대 적용  
            """)

            st.divider()
            # 현대 지역별 수출실적 분석 요약표 작업
            
            df_export_melted =  df_export.melt(id_vars=['국가', '연도'], 
                                    value_vars=["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"] ,
                                    var_name='월', value_name='판매량')
                    
            st.subheader("📌 현대 지역별 수출실적 통계 요약")
            st.write('')

            국가_연도_피벗 = df_export_melted.pivot_table(
                    index='국가',
                    columns='연도',
                    values='판매량',
                    aggfunc='sum',
                    fill_value=0
                )
            총합 = 국가_연도_피벗.sum(axis=1)
            국가_연도_피벗.insert(0, '총합', 총합)
            국가_연도_피벗 = 국가_연도_피벗.sort_values(by='총합', ascending=False)

            # 스타일링을 위해 복사본 생성
            국가_연도_styled = 국가_연도_피벗.copy()

            # 스타일링 적용
            styled_국가_연도 = (
                국가_연도_styled.style
                .format('{:,.0f}')  # 숫자 포맷
                .background_gradient(cmap='Blues')
            )
            # 월 순서를 올바르게 정의
            month_order = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']

            st.write("""##### 🌍 주요 시장별 전체 판매량 📅(연도기준)""")
            st.dataframe(styled_국가_연도, use_container_width=True)

            st.write("""##### 📆 2023년도 월별 판매량""")
            모델_유형_2023 = df_export_melted.loc[df_export_melted['연도'] == 2023] 

            월별_2023_피벗 = 모델_유형_2023.pivot_table(index='국가', columns='월', values='판매량', aggfunc='sum', fill_value=0).reindex(columns=month_order)
            월별_2023_피벗.insert(0, '총합', 월별_2023_피벗.sum(axis=1))
            월별_2023_피벗 = 월별_2023_피벗.sort_values(by='총합', ascending=False)
            총합_행 = 월별_2023_피벗.sum(numeric_only=True)
            총합_행.name = '총합'
            월별2023피벗 = pd.concat([총합_행.to_frame().T, 월별_2023_피벗])

            # --------------------------
            # 👉 스타일링 (색상 강조 포함)
            # --------------------------
            def highlight_total_cells(val, row_idx, col_name):
                if row_idx == '총합' or col_name == '총합':
                    return 'background-color: #d5f5e3'  # 연한 초록색
                return ''

            styled_월별2023 = 월별2023피벗.style.format('{:,}').apply(
                lambda row: [
                    highlight_total_cells(val, row.name, col)
                    for col, val in zip(row.index, row)
                ],
                axis=1
            ).set_properties(**{'text-align': 'center'}).set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
            ])

            st.dataframe(styled_월별2023)

            st.write("""##### 📆 2024년도 월별 판매량""")
            모델_유형_2024 = df_export_melted.loc[df_export_melted['연도'] == 2024] 

            월별_2024_피벗 = 모델_유형_2024.pivot_table(index='국가', columns='월', values='판매량', aggfunc='sum', fill_value=0).reindex(columns=month_order)
            월별_2024_피벗.insert(0, '총합', 월별_2024_피벗.sum(axis=1))
            월별_2024_피벗 = 월별_2024_피벗.sort_values(by='총합', ascending=False)
            총합_행 = 월별_2024_피벗.sum(numeric_only=True)
            총합_행.name = '총합'
            월별2024피벗 = pd.concat([총합_행.to_frame().T, 월별_2024_피벗])

            # --------------------------
            # 👉 스타일링 (색상 강조 포함)
            # --------------------------
            def highlight_total_cells(val, row_idx, col_name):
                if row_idx == '총합' or col_name == '총합':
                    return 'background-color: #d5f5e3'  # 연한 초록색
                return ''

            styled_월별2024 = 월별2024피벗.style.format('{:,}').apply(
                lambda row: [
                    highlight_total_cells(val, row.name, col)
                    for col, val in zip(row.index, row)
                ],
                axis=1
            ).set_properties(**{'text-align': 'center'}).set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
            ])

            st.dataframe(styled_월별2024)
                
            st.write("""##### 📆 국가 월별 통계 (2023년~2025년 누적 기준)""")
            
            국가_월_피벗 = df_export_melted.pivot_table(index='국가', columns='월', values='판매량', aggfunc='sum', fill_value=0).reindex(columns=month_order)
            국가_월_피벗.insert(0, '총합', 국가_월_피벗.sum(axis=1))
            국가_월_피벗 = 국가_월_피벗.sort_values(by='총합', ascending=False)
            총합_행 = 국가_월_피벗.sum(numeric_only=True)
            총합_행.name = '총합'
            국가월피벗 = pd.concat([총합_행.to_frame().T, 국가_월_피벗])

            # --------------------------
            # 👉 스타일링 (색상 강조 포함)
            # --------------------------
            def highlight_total_cells(val, row_idx, col_name):
                if row_idx == '총합' or col_name == '총합':
                    return 'background-color: #d5f5e3'  # 연한 초록색
                return ''

            styled_국가전체월 = 국가월피벗.style.format('{:,}').apply(
                lambda row: [
                    highlight_total_cells(val, row.name, col)
                    for col, val in zip(row.index, row)
                ],
                axis=1
            ).set_properties(**{'text-align': 'center'}).set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
            ])

            st.dataframe(styled_국가전체월)
        
        st.markdown("</div>", unsafe_allow_html=True)

    elif selected == "🏎️ 차종별 판매 분석":
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.subheader("🏎️ 차종별 판매 실적")

        # 연도 선택 UI
        year_filter = st.radio(
            "연도 선택",
            ["2023년", "2024년", "전체"],
            horizontal=True,
            key="year_selection"
        )

        # 데이터 필터링 로직 (수정된 부분)
        if year_filter == '2023년':
            available_models = df_sales[df_sales['연도'] == 2023]['차량 모델'].unique()
            df_filtered = df_sales[df_sales['연도'] == 2023].copy()
            max_date = pd.to_datetime('2023-12')  # 2023년 12월까지만 표시
        elif year_filter == '2024년':
            available_models = df_sales[df_sales['연도'] == 2024]['차량 모델'].unique()
            df_filtered = df_sales[df_sales['연도'] == 2024].copy()
            max_date = pd.to_datetime('2024-12')  # 2024년 12월까지만 표시
        else:
            available_models = df_sales['차량 모델'].unique()
            df_filtered = df_sales.copy()
            max_date = pd.to_datetime('2025-01')  # 전체 선택 시 2025-01까지

        # 차종 카테고리 필터링
        filtered_car_types = {
            category: [model for model in models if model in available_models]
            for category, models in car_types.items()
        }
        selectable_categories = [category for category, models in filtered_car_types.items() if models]

        # 선택 가능한 카테고리가 없는 경우
        if not selectable_categories:
            st.warning(f"{year_filter}에는 해당 데이터가 없습니다.")
        else:
            selected_type = st.selectbox('차종 카테고리 선택', selectable_categories)
            df_filtered = df_filtered[df_filtered['차량 모델'].isin(filtered_car_types[selected_type])].copy()

            # 내수용/수출용 분리
            df_domestic = df_filtered[df_filtered['판매 구분'] == '내수용']
            df_international = df_filtered[df_filtered['판매 구분'] != '내수용']

            # 월별 데이터 변환 (수정된 함수)
            months = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
            month_mapping = {month: idx + 1 for idx, month in enumerate(months)}

            def create_melted_dataframe(df, max_date):
                df_melted = pd.DataFrame()
                for year in df['연도'].unique():
                    year_data = df[df['연도'] == year]
                    for month in months:
                        if month in year_data.columns:
                            temp_df = year_data[['차량 모델', month]].copy()
                            temp_df.rename(columns={month: '판매량'}, inplace=True)
                            temp_df['연도'] = year
                            temp_df['월'] = month
                            df_melted = pd.concat([df_melted, temp_df], ignore_index=True)
                
                df_melted['월'] = df_melted['월'].map(month_mapping)
                df_melted['연도-월'] = pd.to_datetime(
                    df_melted['연도'].astype(str) + '-' + df_melted['월'].astype(str), 
                    format='%Y-%m'
                )
                df_melted = df_melted[df_melted['연도-월'] <= max_date]  # 핵심 수정 부분
                return df_melted

            df_melted_domestic = create_melted_dataframe(df_domestic, max_date)
            df_melted_international = create_melted_dataframe(df_international, max_date)

            # 그래프 생성
            if df_melted_domestic.empty and df_melted_international.empty:
                st.warning(f"{year_filter}에는 {selected_type} 카테고리의 판매 데이터가 없습니다.")
            else:
                # 국내 판매량 그래프
                fig_domestic = px.line(
                    df_melted_domestic,
                    x='연도-월',
                    y='판매량',
                    color='차량 모델',
                    title=f'{selected_type} 국내 월별 판매량 ({year_filter})',
                    labels={'판매량': '판매량 (대)'}
                )
                fig_domestic.update_layout(xaxis_title='연도-월', yaxis_title='판매량')

                # 해외 판매량 그래프
                fig_international = px.line(
                    df_melted_international,
                    x='연도-월',
                    y='판매량',
                    color='차량 모델',
                    title=f'{selected_type} 해외 월별 판매량 ({year_filter})',
                    labels={'판매량': '판매량 (대)'}
                )
                fig_international.update_layout(xaxis_title='연도-월', yaxis_title='판매량')

                # 그래프 표시
                st.plotly_chart(fig_domestic, use_container_width=True)
                st.plotly_chart(fig_international, use_container_width=True)

        # 현대 차종별 판매실적 분석 요약표 작업
        # 월 순서를 올바르게 정의
        month_order = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월']
        if year_filter == '2023년':
            
            if selected_type == '세단 내연기관':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단내연기관_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 내연기관']
                세단내연기관_전체_피벗 = 세단내연기관_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단내연기관_전체_피벗.sum(axis=1)
                세단내연기관_전체_피벗.insert(0, '총합', 총합)
                세단내연기관_전체_피벗 = 세단내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단내연기관_전체_피벗])

                # 스타일링을 위해 복사본 생성
                세단내연전체_styled = 세단내연기관_전체_피벗.copy()

                # 스타일링 적용
                styled_세단내연전체 = (
                    세단내연전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )

                st.write('')
                st.write("""##### 📅 세단내연기관 연간 총 판매량 """)
                st.dataframe(styled_세단내연전체, use_container_width=True)


                # 국내
                세단_내연기관 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == '세단 내연기관']
                세단_내연기관_피벗 = 세단_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_내연기관_피벗 = 세단_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_내연기관_피벗.insert(0, '총합', 세단_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_내연기관_피벗 = 세단_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관피벗 = pd.concat([총합_행.to_frame().T, 세단_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단내연기관 = 세단내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) 세단내연기관 월별 판매량""")
                st.dataframe(styled_세단내연기관, use_container_width=True)

                # 해외
                세단_내연기관 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == '세단 내연기관']
                세단_내연기관_피벗 = 세단_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_내연기관_피벗 = 세단_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_내연기관_피벗.insert(0, '총합', 세단_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_내연기관_피벗 = 세단_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관피벗 = pd.concat([총합_행.to_frame().T, 세단_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단내연기관 = 세단내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) 세단내연기관 월별 판매량""")
                st.dataframe(styled_세단내연기관, use_container_width=True)

            elif selected_type == '세단 하이브리드' :
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단하이브리드_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 하이브리드']
                세단하이브리드_전체_피벗 = 세단하이브리드_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단하이브리드_전체_피벗.sum(axis=1)
                세단하이브리드_전체_피벗.insert(0, '총합', 총합)
                세단하이브리드_전체_피벗 = 세단하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단하이브리드_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단하이브리드_전체_피벗])

                # 스타일링을 위해 복사본 생성
                세단하이브리드전체_styled = 세단하이브리드_전체_피벗.copy()

                # 스타일링 적용
                styled_세단하이브리드전체 = (
                    세단하이브리드전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )

                st.write('')
                st.write("""##### 📅 세단하이브리드 연간 총 판매량 """)
                st.dataframe(styled_세단하이브리드전체, use_container_width=True)


                # 국내
                세단_하이브리드 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == '세단 하이브리드']
                세단_하이브리드_피벗 = 세단_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_하이브리드_피벗 = 세단_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_하이브리드_피벗.insert(0, '총합', 세단_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_하이브리드_피벗 = 세단_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단하이브리드피벗 = pd.concat([총합_행.to_frame().T, 세단_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단하이브리드 = 세단하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) 세단하이브리드 월별 판매량""")
                st.dataframe(styled_세단하이브리드, use_container_width=True)

                # 해외
                세단_하이브리드 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == '세단 하이브리드']
                세단_하이브리드_피벗 = 세단_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_하이브리드_피벗 = 세단_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_하이브리드_피벗.insert(0, '총합', 세단_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_하이브리드_피벗 = 세단_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단하이브리드피벗 = pd.concat([총합_행.to_frame().T, 세단_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단하이브리드 = 세단하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (해외) 세단하이브리드 월별 판매량""")
                st.dataframe(styled_세단하이브리드, use_container_width=True)

            elif selected_type == '세단 전기차':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단전기차_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 전기차']
                세단전기차_전체_피벗 = 세단전기차_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단전기차_전체_피벗.sum(axis=1)
                세단전기차_전체_피벗.insert(0, '총합', 총합)
                세단전기차_전체_피벗 = 세단전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단전기차_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단전기차_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #87CEEB'  # 연한 초록색
                    return ''

                styled_세단전기차 = 세단전기차_전체_피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write('')
                st.write("""##### 📅 세단전기차 연간 총 판매량 """)
                st.dataframe(styled_세단전기차, use_container_width=True)


                # 국내
                세단_전기차 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == '세단 전기차']
                세단_전기차_피벗 = 세단_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_전기차_피벗 = 세단_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_전기차_피벗.insert(0, '총합', 세단_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_전기차_피벗 = 세단_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단전기차피벗 = pd.concat([총합_행.to_frame().T, 세단_전기차_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단전기차 = 세단전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) 세단전기차 월별 판매량""")
                st.dataframe(styled_세단전기차, use_container_width=True)

                # 해외
                세단_전기차 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == '세단 전기차']
                세단_전기차_피벗 = 세단_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_전기차_피벗 = 세단_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_전기차_피벗.insert(0, '총합', 세단_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_전기차_피벗 = 세단_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단전기차피벗 = pd.concat([총합_행.to_frame().T, 세단_전기차_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단전기차 = 세단전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) 세단전기차 월별 판매량""")
                st.dataframe(styled_세단전기차, use_container_width=True)

            elif selected_type == 'SUV 내연기관':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                SUV내연기관_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 내연기관']
                SUV내연기관_전체_피벗 = SUV내연기관_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV내연기관_전체_피벗.sum(axis=1)
                SUV내연기관_전체_피벗.insert(0, '총합', 총합)
                SUV내연기관_전체_피벗 = SUV내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV내연기관_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV내연기관전체_styled = SUV내연기관_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV내연기관전체 = (
                    SUV내연기관전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                
                st.write('')
                st.write("""##### 📅 SUV 내연기관 연간 총 판매량 """)
                st.dataframe(styled_SUV내연기관전체, use_container_width=True)


                # 국내
                SUV_내연기관 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == 'SUV 내연기관']
                SUV_내연기관_피벗 = SUV_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_내연기관_피벗 = SUV_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_내연기관_피벗.insert(0, '총합', SUV_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_내연기관_피벗 = SUV_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관피벗 = pd.concat([총합_행.to_frame().T, SUV_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV내연기관 = SUV내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) SUV 내연기관 월별 판매량""")
                st.dataframe(styled_SUV내연기관, use_container_width=True)

                # 해외
                SUV_내연기관 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == 'SUV 내연기관']
                SUV_내연기관_피벗 = SUV_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_내연기관_피벗 = SUV_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_내연기관_피벗.insert(0, '총합', SUV_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_내연기관_피벗 = SUV_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관피벗 = pd.concat([총합_행.to_frame().T, SUV_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV내연기관 = SUV내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) SUV 내연기관 월별 판매량""")
                st.dataframe(styled_SUV내연기관, use_container_width=True)

            elif selected_type == 'SUV 하이브리드':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")

                SUV하이브리드_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 하이브리드']
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV하이브리드_전체_피벗.sum(axis=1)
                SUV하이브리드_전체_피벗.insert(0, '총합', 총합)
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV하이브리드_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV하이브리드전체_styled = SUV하이브리드_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV하이브리드전체 = (
                    SUV하이브리드전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
        
                st.write('')
                st.write("""##### 📅 SUV 하이브리드 연간 총 판매량 """)
                st.dataframe(styled_SUV하이브리드전체, use_container_width=True)


                # 국내
                SUV_하이브리드 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == 'SUV 하이브리드']
                SUV_하이브리드_피벗 = SUV_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_하이브리드_피벗.insert(0, '총합', SUV_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드피벗 = pd.concat([총합_행.to_frame().T, SUV_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV하이브리드 = SUV하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) SUV 하이브리드 월별 판매량""")
                st.dataframe(styled_SUV하이브리드, use_container_width=True)

                # 해외
                SUV_하이브리드 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == 'SUV 하이브리드']
                SUV_하이브리드_피벗 = SUV_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_하이브리드_피벗.insert(0, '총합', SUV_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드피벗 = pd.concat([총합_행.to_frame().T, SUV_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV하이브리드 = SUV하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) SUV 하이브리드 월별 판매량""")
                st.dataframe(styled_SUV하이브리드, use_container_width=True)

            elif selected_type == 'SUV 전기차':
            
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                SUV전기차_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 전기차']
                SUV전기차_전체_피벗 = SUV전기차_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV전기차_전체_피벗.sum(axis=1)
                SUV전기차_전체_피벗.insert(0, '총합', 총합)
                SUV전기차_전체_피벗 = SUV전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV전기차_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV전기차전체_styled = SUV전기차_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV전기차전체 = (
                    SUV전기차전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 SUV 전기차 연간 총 판매량 """)
                st.dataframe(styled_SUV전기차전체, use_container_width=True)


                # 국내
                SUV_전기차 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == 'SUV 전기차']
                SUV_전기차_피벗 = SUV_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_전기차_피벗 = SUV_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_전기차_피벗.insert(0, '총합', SUV_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_전기차_피벗 = SUV_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                
                SUV전기차피벗 = pd.concat([총합_행.to_frame().T, SUV_전기차_피벗])
                
                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV전기차 = SUV전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) SUV 전기차 월별 판매량""")
                st.dataframe(styled_SUV전기차, use_container_width=True)

                # 해외
                SUV_전기차 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == 'SUV 전기차']
                SUV_전기차_피벗 = SUV_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_전기차_피벗 = SUV_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_전기차_피벗.insert(0, '총합', SUV_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_전기차_피벗 = SUV_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차피벗 = pd.concat([총합_행.to_frame().T, SUV_전기차_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV전기차 = SUV전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) SUV 전기차 월별 판매량""")
                st.dataframe(styled_SUV전기차, use_container_width=True)

            elif selected_type == '기타':
            
                st.subheader("📊 현대 차종별 판매실적 통계 요약")

                기타_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '기타']
                기타_전체_피벗 = 기타_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 기타_전체_피벗.sum(axis=1)
                기타_전체_피벗.insert(0, '총합', 총합)
                기타_전체_피벗 = 기타_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 기타_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타_전체_피벗 = pd.concat([총합_행.to_frame().T, 기타_전체_피벗])

                # 스타일링을 위해 복사본 생성
                기타전체_styled = 기타_전체_피벗.copy()

                # 스타일링 적용
                styled_기타전체 = (
                    기타전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 기타 연간 총 판매량 """)
                st.dataframe(styled_기타전체, use_container_width=True)


                # 국내
                기타 = 모델_유형_국내_2023.loc[모델_유형_국내_2023['카테고리'] == '기타']
                기타_피벗 = 기타.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                기타_피벗 = 기타_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                기타_피벗.insert(0, '총합', 기타_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                기타_피벗 = 기타_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 기타_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                
                기타피벗 = pd.concat([총합_행.to_frame().T, 기타_피벗])
                
                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_기타 = 기타피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) 기타 월별 판매량""")
                st.dataframe(styled_기타, use_container_width=True)

                # 해외
                기타 = 모델_유형_해외_2023.loc[모델_유형_해외_2023['카테고리'] == '기타']
                기타_피벗 = 기타.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                기타_피벗 = 기타_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                기타_피벗.insert(0, '총합', 기타_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                기타_피벗 = 기타_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 기타_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타피벗 = pd.concat([총합_행.to_frame().T, 기타_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_기타 = 기타피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) 기타 월별 판매량""")
                st.dataframe(styled_기타, use_container_width=True)

        if year_filter == '2024년':

            if selected_type == '세단 내연기관':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단내연기관_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 내연기관']
                세단내연기관_전체_피벗 = 세단내연기관_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단내연기관_전체_피벗.sum(axis=1)
                세단내연기관_전체_피벗.insert(0, '총합', 총합)
                세단내연기관_전체_피벗 = 세단내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단내연기관_전체_피벗])

                # 스타일링을 위해 복사본 생성
                세단내연전체_styled = 세단내연기관_전체_피벗.copy()

                # 스타일링 적용
                styled_세단내연전체 = (
                    세단내연전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )

                st.write('')
                st.write("""##### 📅 세단내연기관 연간 총 판매량 """)
                st.dataframe(styled_세단내연전체, use_container_width=True)


                # 국내
                세단_내연기관 = 모델_유형_국내_2024.loc[모델_유형_국내_2024['카테고리'] == '세단 내연기관']
                세단_내연기관_피벗 = 세단_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_내연기관_피벗 = 세단_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_내연기관_피벗.insert(0, '총합', 세단_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_내연기관_피벗 = 세단_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관피벗 = pd.concat([총합_행.to_frame().T, 세단_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단내연기관 = 세단내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) 세단내연기관 월별 판매량""")
                st.dataframe(styled_세단내연기관, use_container_width=True)

                # 해외
                세단_내연기관 = 모델_유형_해외_2024.loc[모델_유형_해외_2024['카테고리'] == '세단 내연기관']
                세단_내연기관_피벗 = 세단_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_내연기관_피벗 = 세단_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_내연기관_피벗.insert(0, '총합', 세단_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_내연기관_피벗 = 세단_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관피벗 = pd.concat([총합_행.to_frame().T, 세단_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단내연기관 = 세단내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) 세단내연기관 월별 판매량""")
                st.dataframe(styled_세단내연기관, use_container_width=True)

            
            elif selected_type == 'SUV 내연기관':
        
                st.subheader("📊 현대 차종별 판매실적 통계 요약")

                SUV내연기관_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 내연기관']
                SUV내연기관_전체_피벗 = SUV내연기관_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV내연기관_전체_피벗.sum(axis=1)
                SUV내연기관_전체_피벗.insert(0, '총합', 총합)
                SUV내연기관_전체_피벗 = SUV내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV내연기관_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV내연기관전체_styled = SUV내연기관_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV내연기관전체 = (
                    SUV내연기관전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                
                st.write('')
                st.write("""##### 📅 SUV 내연기관 연간 총 판매량 """)
                st.dataframe(styled_SUV내연기관전체, use_container_width=True)


                # 국내
                SUV_내연기관 = 모델_유형_국내_2024.loc[모델_유형_국내_2024['카테고리'] == 'SUV 내연기관']
                SUV_내연기관_피벗 = SUV_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_내연기관_피벗 = SUV_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_내연기관_피벗.insert(0, '총합', SUV_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_내연기관_피벗 = SUV_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관피벗 = pd.concat([총합_행.to_frame().T, SUV_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV내연기관 = SUV내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) SUV 내연기관 월별 판매량""")
                st.dataframe(styled_SUV내연기관, use_container_width=True)

                # 해외
                SUV_내연기관 = 모델_유형_해외_2024.loc[모델_유형_해외_2024['카테고리'] == 'SUV 내연기관']
                SUV_내연기관_피벗 = SUV_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_내연기관_피벗 = SUV_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_내연기관_피벗.insert(0, '총합', SUV_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_내연기관_피벗 = SUV_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관피벗 = pd.concat([총합_행.to_frame().T, SUV_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV내연기관 = SUV내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) SUV 내연기관 월별 판매량""")
                st.dataframe(styled_SUV내연기관, use_container_width=True)

            elif selected_type == 'SUV 하이브리드':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")

                SUV하이브리드_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 하이브리드']
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV하이브리드_전체_피벗.sum(axis=1)
                SUV하이브리드_전체_피벗.insert(0, '총합', 총합)
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV하이브리드_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV하이브리드전체_styled = SUV하이브리드_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV하이브리드전체 = (
                    SUV하이브리드전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
        
                st.write('')
                st.write("""##### 📅 SUV 하이브리드 연간 총 판매량 """)
                st.dataframe(styled_SUV하이브리드전체, use_container_width=True)


                # 국내
                SUV_하이브리드 = 모델_유형_국내_2024.loc[모델_유형_국내_2024['카테고리'] == 'SUV 하이브리드']
                SUV_하이브리드_피벗 = SUV_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_하이브리드_피벗.insert(0, '총합', SUV_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드피벗 = pd.concat([총합_행.to_frame().T, SUV_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV하이브리드 = SUV하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) SUV 하이브리드 월별 판매량""")
                st.dataframe(styled_SUV하이브리드, use_container_width=True)

                # 해외
                SUV_하이브리드 = 모델_유형_해외_2024.loc[모델_유형_해외_2024['카테고리'] == 'SUV 하이브리드']
                SUV_하이브리드_피벗 = SUV_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_하이브리드_피벗.insert(0, '총합', SUV_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드피벗 = pd.concat([총합_행.to_frame().T, SUV_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV하이브리드 = SUV하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) SUV 하이브리드 월별 판매량""")
                st.dataframe(styled_SUV하이브리드, use_container_width=True)

            elif selected_type == 'SUV 전기차':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")

                SUV전기차_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 전기차']
                SUV전기차_전체_피벗 = SUV전기차_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV전기차_전체_피벗.sum(axis=1)
                SUV전기차_전체_피벗.insert(0, '총합', 총합)
                SUV전기차_전체_피벗 = SUV전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV전기차_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV전기차전체_styled = SUV전기차_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV전기차전체 = (
                    SUV전기차전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 SUV 전기차 연간 총 판매량 """)
                st.dataframe(styled_SUV전기차전체, use_container_width=True)


                # 국내
                SUV_전기차 = 모델_유형_국내_2024.loc[모델_유형_국내_2024['카테고리'] == 'SUV 전기차']
                SUV_전기차_피벗 = SUV_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_전기차_피벗 = SUV_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_전기차_피벗.insert(0, '총합', SUV_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_전기차_피벗 = SUV_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                
                SUV전기차피벗 = pd.concat([총합_행.to_frame().T, SUV_전기차_피벗])
                
                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV전기차 = SUV전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) SUV 전기차 월별 판매량""")
                st.dataframe(styled_SUV전기차, use_container_width=True)

                # 해외
                SUV_전기차 = 모델_유형_해외_2024.loc[모델_유형_해외_2024['카테고리'] == 'SUV 전기차']
                SUV_전기차_피벗 = SUV_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_전기차_피벗 = SUV_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_전기차_피벗.insert(0, '총합', SUV_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_전기차_피벗 = SUV_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차피벗 = pd.concat([총합_행.to_frame().T, SUV_전기차_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV전기차 = SUV전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) SUV 전기차 월별 판매량""")
                st.dataframe(styled_SUV전기차, use_container_width=True)

            elif selected_type == '기타':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")

                기타_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '기타']
                기타_전체_피벗 = 기타_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 기타_전체_피벗.sum(axis=1)
                기타_전체_피벗.insert(0, '총합', 총합)
                기타_전체_피벗 = 기타_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 기타_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타_전체_피벗 = pd.concat([총합_행.to_frame().T, 기타_전체_피벗])

                # 스타일링을 위해 복사본 생성
                기타전체_styled = 기타_전체_피벗.copy()

                # 스타일링 적용
                styled_기타전체 = (
                    기타전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 기타 연간 총 판매량 """)
                st.dataframe(styled_기타전체, use_container_width=True)

                # 국내
                기타 = 모델_유형_국내_2024.loc[모델_유형_국내_2024['카테고리'] == '기타']
                기타_피벗 = 기타.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                기타_피벗 = 기타_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                기타_피벗.insert(0, '총합', 기타_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                기타_피벗 = 기타_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 기타_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                
                기타피벗 = pd.concat([총합_행.to_frame().T, 기타_피벗])
                
                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_기타 = 기타피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 (국내) 기타 월별 판매량""")
                st.dataframe(styled_기타, use_container_width=True)

                # 해외
                기타 = 모델_유형_해외_2024.loc[모델_유형_해외_2024['카테고리'] == '기타']
                기타_피벗 = 기타.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                기타_피벗 = 기타_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                기타_피벗.insert(0, '총합', 기타_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                기타_피벗 = 기타_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 기타_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타피벗 = pd.concat([총합_행.to_frame().T, 기타_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_기타 = 기타피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 (해외) 기타 월별 판매량""")
                st.dataframe(styled_기타, use_container_width=True)

        if year_filter == '전체':

            if selected_type == '세단 내연기관':            
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단내연기관_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 내연기관']
                세단내연기관_전체_피벗 = 세단내연기관_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단내연기관_전체_피벗.sum(axis=1)
                세단내연기관_전체_피벗.insert(0, '총합', 총합)
                세단내연기관_전체_피벗 = 세단내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단내연기관_전체_피벗])

                # 스타일링을 위해 복사본 생성
                세단내연전체_styled = 세단내연기관_전체_피벗.copy()

                # 스타일링 적용
                styled_세단내연전체 = (
                    세단내연전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 세단내연기관 연간 총 판매량 """)
                st.dataframe(styled_세단내연전체, use_container_width=True)

                # 국내
                세단내연기관_전체 = 전체_국내.loc[전체_국내['카테고리'] == '세단 내연기관']
                세단내연기관_전체_피벗 = 세단내연기관_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단내연기관_전체_피벗.sum(axis=1)
                세단내연기관_전체_피벗.insert(0, '총합', 총합)
                세단내연기관_전체_피벗 = 세단내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관전체피벗 = pd.concat([총합_행.to_frame().T, 세단내연기관_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단내연기관전체 = 세단내연기관전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] 세단내연기관 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_세단내연기관전체, use_container_width=True)

                # 해외
                세단_내연기관 = 전체_해외.loc[전체_해외['카테고리'] == '세단 내연기관']
                세단_내연기관_피벗 = 세단_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_내연기관_피벗 = 세단_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_내연기관_피벗.insert(0, '총합', 세단_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_내연기관_피벗 = 세단_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단내연기관피벗 = pd.concat([총합_행.to_frame().T, 세단_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단내연기관 = 세단내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] 세단내연기관 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_세단내연기관, use_container_width=True)

            
            elif selected_type == '세단 하이브리드':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단하이브리드_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 하이브리드']
                세단하이브리드_전체_피벗 = 세단하이브리드_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단하이브리드_전체_피벗.sum(axis=1)
                세단하이브리드_전체_피벗.insert(0, '총합', 총합)
                세단하이브리드_전체_피벗 = 세단하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단하이브리드_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단하이브리드_전체_피벗])

                # 스타일링을 위해 복사본 생성
                세단하이브리드전체_styled = 세단하이브리드_전체_피벗.copy()

                # 스타일링 적용
                styled_세단하이브리드전체 = (
                    세단하이브리드전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 세단하이브리드 연간 총 판매량 """)
                st.dataframe(styled_세단하이브리드전체, use_container_width=True)

                
                # 국내
                세단하이브리드_전체 = 전체_국내.loc[전체_국내['카테고리'] == '세단 하이브리드']
                세단하이브리드_전체_피벗 = 세단하이브리드_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단하이브리드_전체_피벗.sum(axis=1)
                세단하이브리드_전체_피벗.insert(0, '총합', 총합)
                세단하이브리드_전체_피벗 = 세단하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단하이브리드전체피벗 = pd.concat([총합_행.to_frame().T, 세단하이브리드_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단하이브리드전체 = 세단하이브리드전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] 세단하이브리드 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_세단하이브리드전체, use_container_width=True)

                # 해외
                세단_하이브리드 = 전체_해외.loc[전체_해외['카테고리'] == '세단 하이브리드']
                세단_하이브리드_피벗 = 세단_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_하이브리드_피벗 = 세단_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_하이브리드_피벗.insert(0, '총합', 세단_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_하이브리드_피벗 = 세단_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단하이브리드피벗 = pd.concat([총합_행.to_frame().T, 세단_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단하이브리드 = 세단하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] 세단하이브리드 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_세단하이브리드, use_container_width=True)

            elif selected_type == '세단 전기차':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                세단전기차_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '세단 전기차']
                세단전기차_전체_피벗 = 세단전기차_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단전기차_전체_피벗.sum(axis=1)
                세단전기차_전체_피벗.insert(0, '총합', 총합)
                세단전기차_전체_피벗 = 세단전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단전기차_전체_피벗 = pd.concat([총합_행.to_frame().T, 세단전기차_전체_피벗])

                # 스타일링을 위해 복사본 생성
                세단전기차전체_styled = 세단전기차_전체_피벗.copy()

                # 스타일링 적용
                styled_세단전기차전체 = (
                    세단전기차전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 세단전기차 연간 총 판매량 """)
                st.dataframe(styled_세단전기차전체, use_container_width=True)

                # 국내
                세단전기차_전체 = 전체_국내.loc[전체_국내['카테고리'] == '세단 전기차']
                세단전기차_전체_피벗 = 세단전기차_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 세단전기차_전체_피벗.sum(axis=1)
                세단전기차_전체_피벗.insert(0, '총합', 총합)
                세단전기차_전체_피벗 = 세단전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 세단전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단전기차전체피벗 = pd.concat([총합_행.to_frame().T, 세단전기차_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단전기차전체 = 세단전기차전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] 세단전기차 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_세단전기차전체, use_container_width=True)

                # 해외
                세단_전기차 = 전체_해외.loc[전체_해외['카테고리'] == '세단 전기차']
                세단_전기차_피벗 = 세단_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                세단_전기차_피벗 = 세단_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                세단_전기차_피벗.insert(0, '총합', 세단_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                세단_전기차_피벗 = 세단_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 세단_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                세단전기차피벗 = pd.concat([총합_행.to_frame().T, 세단_전기차_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_세단전기차 = 세단전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] 세단전기차 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_세단전기차, use_container_width=True)

            elif selected_type == 'SUV 내연기관':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                SUV내연기관_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 내연기관']
                SUV내연기관_전체_피벗 = SUV내연기관_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV내연기관_전체_피벗.sum(axis=1)
                SUV내연기관_전체_피벗.insert(0, '총합', 총합)
                SUV내연기관_전체_피벗 = SUV내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV내연기관_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV내연기관전체_styled = SUV내연기관_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV내연기관전체 = (
                    SUV내연기관전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 SUV내연기관 연간 총 판매량 """)
                st.dataframe(styled_SUV내연기관전체, use_container_width=True)

                # 국내
                SUV내연기관_전체 = 전체_국내.loc[전체_국내['카테고리'] == 'SUV 내연기관']
                SUV내연기관_전체_피벗 = SUV내연기관_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV내연기관_전체_피벗.sum(axis=1)
                SUV내연기관_전체_피벗.insert(0, '총합', 총합)
                SUV내연기관_전체_피벗 = SUV내연기관_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV내연기관_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관전체피벗 = pd.concat([총합_행.to_frame().T, SUV내연기관_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV내연기관전체 = SUV내연기관전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] SUV내연기관 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_SUV내연기관전체, use_container_width=True)

                # 해외
                SUV_내연기관 = 전체_해외.loc[전체_해외['카테고리'] == 'SUV 내연기관']
                SUV_내연기관_피벗 = SUV_내연기관.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_내연기관_피벗 = SUV_내연기관_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_내연기관_피벗.insert(0, '총합', SUV_내연기관_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_내연기관_피벗 = SUV_내연기관_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_내연기관_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV내연기관피벗 = pd.concat([총합_행.to_frame().T, SUV_내연기관_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV내연기관 = SUV내연기관피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] SUV내연기관 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_SUV내연기관, use_container_width=True)

            elif selected_type == 'SUV 하이브리드':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                SUV하이브리드_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 하이브리드']
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV하이브리드_전체_피벗.sum(axis=1)
                SUV하이브리드_전체_피벗.insert(0, '총합', 총합)
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV하이브리드_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV하이브리드전체_styled = SUV하이브리드_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV하이브리드전체 = (
                    SUV하이브리드전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 SUV하이브리드 연간 총 판매량 """)
                st.dataframe(styled_SUV하이브리드전체, use_container_width=True)

                # 국내
                SUV하이브리드_전체 = 전체_국내.loc[전체_국내['카테고리'] == 'SUV 하이브리드']
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV하이브리드_전체_피벗.sum(axis=1)
                SUV하이브리드_전체_피벗.insert(0, '총합', 총합)
                SUV하이브리드_전체_피벗 = SUV하이브리드_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV하이브리드_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드전체피벗 = pd.concat([총합_행.to_frame().T, SUV하이브리드_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV하이브리드전체 = SUV하이브리드전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] SUV하이브리드 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_SUV하이브리드전체, use_container_width=True)

                # 해외
                SUV_하이브리드 = 전체_해외.loc[전체_해외['카테고리'] == 'SUV 하이브리드']
                SUV_하이브리드_피벗 = SUV_하이브리드.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_하이브리드_피벗.insert(0, '총합', SUV_하이브리드_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_하이브리드_피벗 = SUV_하이브리드_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_하이브리드_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV하이브리드피벗 = pd.concat([총합_행.to_frame().T, SUV_하이브리드_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV하이브리드 = SUV하이브리드피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] SUV하이브리드 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_SUV하이브리드, use_container_width=True)

            elif selected_type == 'SUV 전기차':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                SUV전기차_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == 'SUV 전기차']
                SUV전기차_전체_피벗 = SUV전기차_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV전기차_전체_피벗.sum(axis=1)
                SUV전기차_전체_피벗.insert(0, '총합', 총합)
                SUV전기차_전체_피벗 = SUV전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차_전체_피벗 = pd.concat([총합_행.to_frame().T, SUV전기차_전체_피벗])

                # 스타일링을 위해 복사본 생성
                SUV전기차전체_styled = SUV전기차_전체_피벗.copy()

                # 스타일링 적용
                styled_SUV전기차전체 = (
                    SUV전기차전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 SUV전기차 연간 총 판매량 """)
                st.dataframe(styled_SUV전기차전체, use_container_width=True)

                # 국내
                SUV전기차_전체 = 전체_국내.loc[전체_국내['카테고리'] == 'SUV 전기차']
                SUV전기차_전체_피벗 = SUV전기차_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = SUV전기차_전체_피벗.sum(axis=1)
                SUV전기차_전체_피벗.insert(0, '총합', 총합)
                SUV전기차_전체_피벗 = SUV전기차_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = SUV전기차_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차전체피벗 = pd.concat([총합_행.to_frame().T, SUV전기차_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV전기차전체 = SUV전기차전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] SUV전기차 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_SUV전기차전체, use_container_width=True)

                # 해외
                SUV_전기차 = 전체_해외.loc[전체_해외['카테고리'] == 'SUV 전기차']
                SUV_전기차_피벗 = SUV_전기차.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                SUV_전기차_피벗 = SUV_전기차_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                SUV_전기차_피벗.insert(0, '총합', SUV_전기차_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                SUV_전기차_피벗 = SUV_전기차_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = SUV_전기차_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                SUV전기차피벗 = pd.concat([총합_행.to_frame().T, SUV_전기차_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_SUV전기차 = SUV전기차피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] SUV전기차 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_SUV전기차, use_container_width=True)

            elif selected_type == '기타':
                
                st.subheader("📊 현대 차종별 판매실적 통계 요약")
                
                기타_전체 = df_sales_melted.loc[df_sales_melted['카테고리'] == '기타']
                기타_전체_피벗 = 기타_전체.pivot_table(index='차량 모델', columns='연도', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 기타_전체_피벗.sum(axis=1)
                기타_전체_피벗.insert(0, '총합', 총합)
                기타_전체_피벗 = 기타_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 기타_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타_전체_피벗 = pd.concat([총합_행.to_frame().T, 기타_전체_피벗])

                # 스타일링을 위해 복사본 생성
                기타전체_styled = 기타_전체_피벗.copy()

                # 스타일링 적용
                styled_기타전체 = (
                    기타전체_styled.style
                    .format('{:,.0f}')  # 숫자 포맷
                    .background_gradient(cmap='Blues')
                )
                st.write('')
                st.write("""##### 📅 기타 연간 총 판매량 """)
                st.dataframe(styled_기타전체, use_container_width=True)

                # 국내
                기타_전체 = 전체_국내.loc[전체_국내['카테고리'] == '기타']
                기타_전체_피벗 = 기타_전체.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)

                총합 = 기타_전체_피벗.sum(axis=1)
                기타_전체_피벗.insert(0, '총합', 총합)
                기타_전체_피벗 = 기타_전체_피벗.sort_values(by='총합', ascending=False)
                총합_행 = 기타_전체_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타전체피벗 = pd.concat([총합_행.to_frame().T, 기타_전체_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_기타전체 = 기타전체피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])
                st.write("""##### 📆 [국내] 기타 월별 판매량 (2023년 ~ 2025년 누적) """)
                st.dataframe(styled_기타전체, use_container_width=True)

                # 해외
                기타 = 전체_해외.loc[전체_해외['카테고리'] == '기타']
                기타_피벗 = 기타.pivot_table(index='차량 모델', columns='월', values='판매량', aggfunc='sum', fill_value=0)
                # 월 순서대로 열 정렬 (총합 열은 아직 없음)
                기타_피벗 = 기타_피벗.reindex(columns=month_order)

                # 총합 열 추가 (맨 앞에 넣기 위해 insert 사용)
                기타_피벗.insert(0, '총합', 기타_피벗.sum(axis=1))
                # 총합 내림차순 정렬
                기타_피벗 = 기타_피벗.sort_values(by='총합', ascending=False)
                # 총합 행 추가
                총합_행 = 기타_피벗.sum(numeric_only=True)
                총합_행.name = '총합'
                기타피벗 = pd.concat([총합_행.to_frame().T, 기타_피벗])

                # --------------------------
                # 👉 스타일링 (색상 강조 포함)
                # --------------------------
                def highlight_total_cells(val, row_idx, col_name):
                    if row_idx == '총합' or col_name == '총합':
                        return 'background-color: #d5f5e3'  # 연한 초록색
                    return ''

                styled_기타 = 기타피벗.style.format('{:,}').apply(
                    lambda row: [
                        highlight_total_cells(val, row.name, col)
                        for col, val in zip(row.index, row)
                    ],
                    axis=1
                ).set_properties(**{'text-align': 'center'}).set_table_styles([
                    {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#f8f9f9')]}
                ])

                st.write("""##### 📆 [해외] 기타 월별 판매량 (2023년 ~ 2025년 누적)""")
                st.dataframe(styled_기타, use_container_width=True)

        
        st.markdown("</div>", unsafe_allow_html=True)