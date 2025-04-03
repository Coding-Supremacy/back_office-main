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
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df_export = pd.read_csv(os.path.join(BASE_DIR, "data_mini2/현대_지역별수출실적.csv"))
    df_sales = pd.read_csv(os.path.join(BASE_DIR, "data_mini2/현대_차종별판매실적.csv"))
    df_factory = pd.read_csv(os.path.join(BASE_DIR, "data_mini2/현대_공장별_판매실적.csv"))
    return df_export, df_sales, df_factory

df_export, df_sales, df_factory = load_data()

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
        options=["📊 지역별 수출 분석", "🏎️ 차종별 판매 분석", "🏭 공장별 판매분석"],
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

    elif selected == "🏭 공장별 판매분석":

        def render_page_description(page_name):
            descriptions = {
                "📈 차량 트렌드": """
        <div style="border-left: 6px solid #2E86C1; background-color: #EBF5FB; padding: 10px; border-radius: 6px;">
        이 페이지는 <strong>공장별로 생산된 차량 모델들의 월별 판매량</strong>을 비교할 수 있는 <strong>분석 대시보드</strong>입니다.<br>
        <strong>공장을 선택하면</strong>, 해당 공장에서 생산된 차량 모델 중 원하는 모델을 선택하여  
        <strong>월별 판매 트렌드</strong>를 확인할 수 있습니다.
        </div>
        """,
                "🏭 공장 총 판매량": """
        <div style="border-left: 6px solid #2E86C1; background-color: #EBF5FB; padding: 10px; border-radius: 6px;">
        이 페이지에서는 <strong>공장별 연간 총 판매량</strong>을 한눈에 확인할 수 있습니다.<br>
        <strong>판매량이 많은 공장</strong>을 파악하고, 선택적으로 <strong>판매량이 0인 공장 제외</strong> 기능도 사용할 수 있습니다.
        </div>
        """,
                "🥧 내수/수출 비율": """
        <div style="border-left: 6px solid #2E86C1; background-color: #EBF5FB; padding: 10px; border-radius: 6px;">
        이 페이지에서는 <strong>공장별 차량의 내수용과 수출용 비율</strong>을 <strong>파이 차트</strong>로 확인할 수 있습니다.<br>
        <strong>공장을 선택</strong>하면 해당 공장의 <strong>생산 방향(내수/수출)</strong>을 직관적으로 파악할 수 있습니다.
        </div>
        """
            }

            if page_name in descriptions:
                st.markdown(descriptions[page_name], unsafe_allow_html=True)
                

        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        # 전처리
        month_cols = ['1월', '2월', '3월', '4월', '5월', '6월', '7월',
              '8월', '9월', '10월', '11월', '12월']
        df_factory[month_cols] = df_factory[month_cols].apply(pd.to_numeric, errors='coerce')
        df_factory["총합"] = df_factory[month_cols].sum(axis=1)


        tab1, tab2, tab3 = st.tabs(["🏭 공장 총 판매량", "📈 차량 트렌드", "🥧 내수/수출 비율"])

        # 1. 차량 모델별 월별 판매 트렌드
        with tab1:
            st.subheader("🏭 공장별 연간 총 판매량")
            render_page_description("🏭 공장 총 판매량")
            st.divider()

            # 원본 공장별 데이터
            plant_df = df_factory.groupby("공장명(국가)")["총합"].sum().reset_index()

            # ✅ 사용자 선택: 0인 데이터 제외 여부
            exclude_zero = st.checkbox("판매량이 0인 공장 제외하기", value=True)

            if exclude_zero:
                plant_df = plant_df[plant_df["총합"] > 0]

            fig = px.bar(
                plant_df,
                x="공장명(국가)",
                y="총합",
                color="공장명(국가)",
                text_auto=True,
                title="공장별 총 판매량"
            )
            fig.update_layout(xaxis_title="공장명", yaxis_title="연간 판매량")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            <div style="border-left: 6px solid #117A65; background-color: #E8F8F5; padding: 12px; border-radius: 6px;">
            <h5>📌 <strong>공장별 연간 총 판매량 분석 요약</strong></h5>
            <ol>
            <li><strong>인도 HMI 공장</strong>이 총 <strong>1,595,495대</strong>로 가장 높은 생산량을 기록하며 <strong>압도적 1위</strong></li>
            <li><strong>미국 HMMA</strong>(747,232대), <strong>체코 HMMC</strong>(689,355대)도 뒤를 이어 유럽·미주 수출 핵심</li>
            <li>중국 <strong>BHMC, HAOS</strong> 및 브라질 <strong>HMB</strong>는 각 40만 대 내외로 기여</li>
            <li><strong>베트남, 인도네시아, 싱가포르</strong> 등 신흥국 공장은 <strong>10만 대 이하</strong>로 소규모 생산</li>
            </ol>
            <p><strong>✅ 분석 포인트:</strong> HMI 중심 생산 집중 구조, 공장별 역할 특화, 신흥국 공장 성장 여지</p>
            </div>
            """, unsafe_allow_html=True)
            

        # 2. 공장별 총 판매량
        with tab2:
            st.subheader("📈 차량 모델별 월별 판매 트렌드")
            render_page_description("📈 차량 트렌드")
            st.divider()

            # 공장 선택
            selected_factory = st.selectbox("공장을 선택하세요", df_factory["공장명(국가)"].unique(), key="factory_selector_tab1")

            # 해당 공장에서 생산된 차량 모델 리스트 추출
            filtered_df = df_factory[df_factory["공장명(국가)"] == selected_factory]
            if filtered_df[month_cols].sum().sum() == 0:
                st.warning(f"⚠️ 선택한 공장({selected_factory})의 판매 데이터가 존재하지 않습니다.")
            else:
                model_df = filtered_df.groupby("차량 모델")[month_cols].sum().T
                model_df.columns.name = None
                model_df.index.name = "월"

                # 판매량 기준 상위 3개 모델 선택
                top_models = filtered_df.groupby("차량 모델")["총합"].sum().sort_values(ascending=False).head(3).index.tolist()

                # 멀티셀렉트
                selected_models = st.multiselect(
                    "차량 모델 선택", options=model_df.columns.tolist(), default=top_models
                )

                # 시각화
                if selected_models:
                    trend_df = model_df[selected_models].reset_index().melt(id_vars="월", var_name="차량 모델", value_name="판매량")
                    fig = px.line(trend_df, x="월", y="판매량", color="차량 모델", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("차량 모델을 선택해주세요.")
                if selected_factory == 'HMI':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HMI 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(Creta, Venue, i20)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>Creta(SU2i)</strong> 모델이 <strong>월 평균 약 3만 대 이상</strong>으로 <strong>가장 높은 판매량</strong>을 기록</li>
                    <li><strong>Venue(QXi)</strong>는 월 평균 2만 대 내외로, 꾸준한 중간 수요 유지</li>
                    <li><strong>i20(BI3 5DR)</strong>는 월 평균 1만 대 초반 수준으로, <strong>소형차 수요 대응</strong> 역할</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HMI 공장은 <strong>Creta 중심의 SUV 라인업이 강세</strong>이며, 다양한 수요층을 위한 <strong>중·소형 모델 분산 생산 전략</strong>을 병행</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HAOS':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HAOS 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(i20, i10, Bayon)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>i20 (BC3)</strong> 모델은 월 평균 약 2만 대 전후의 판매량으로 <strong>HAOS 공장 내 최상위 주력 모델</strong>로 확인됩니다.</li>
                    <li><strong>i10 (AC3)</strong>는 꾸준히 월 1.2~1.5만 대 수준을 기록하며, <strong>안정적인 판매 흐름</strong>을 유지합니다.</li>
                    <li><strong>Bayon (BC3 CUV)</strong>는 전체적으로 1만 대 초반의 판매량을 보이며, <strong>CUV 시장 공략용 전략 모델</strong>로 판단됩니다.</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HAOS 공장은 <strong>소형 해치백 및 크로스오버 차량 중심</strong>의 생산 라인업으로 구성되어 있으며, <strong>유럽 도심형 시장 대응</strong>에 최적화된 모델이 집중 배치됨</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'BHMC':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>BHMC 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(Elantra, Tucson, BHMC 기타)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>Elantra(CN7c)</strong>는 전월 대비 등락은 있지만 전체적으로 <strong>월 평균 1.5~2만 대 이상</strong>을 유지하며 <strong>지속적인 판매 강세</strong>를 보임</li>
                    <li><strong>Tucson(NX4c)</strong>는 <strong>1만 대 이하 중위권 모델</strong>로서 꾸준한 수요 흐름을 보이며, 하반기 상승세도 확인됨</li>
                    <li><strong>BHMC 기타 모델</strong>도 하반기 들어 <strong>점진적인 판매 증가</strong>가 확인되며, <strong>내수 수요 또는 신차 전략 모델일 가능성</strong></li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> BHMC 공장은 <strong>Elantra 중심의 세단 라인업</strong>이 주력이며, <strong>SUV(Tucson)</strong> 및 기타 모델의 병행 생산 전략이 수요 대응에 기여</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HMMA':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HMMA 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(Tucson, Santa-Fe (TMa), Santa-Fe (MX5a))</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>Tucson(NX4a)</strong>는 <strong>월 평균 2.5만 대 이상</strong>의 높은 수요를 유지하며, <strong>1월에 최대 판매량(약 3.5만 대 이상)</strong>을 기록</li>
                    <li><strong>Santa-Fe(TMa)</strong>와 <strong>Santa-Fe(MX5a)</strong>는 <strong>각각 1만 대 전후의 판매량</strong>을 기록하며, <strong>중형 SUV 수요를 분산 대응</strong></li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HMMA 공장은 <strong>Tucson 중심의 주력 SUV 라인업</strong>과 함께, <strong>세대 전환 중인 Santa-Fe 모델군</strong>을 병행 생산하며 미국 시장 수요에 유연하게 대응</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HMMC':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HMMC 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(Tucson, Tucson HEV, i30)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>Tucson(NX4e)</strong>는 <strong>월 평균 2.5만 대</strong> 수준의 안정적 수요 유지, <strong>1월 최고 판매량</strong> 기록</li>
                    <li><strong>Tucson HEV(NX4e HEV)</strong>는 <strong>하이브리드 라인업으로 월 1.3~1.5만 대</strong>의 꾸준한 수요 보임</li>
                    <li><strong>i30(PDe)</strong>는 <strong>월 5천~1만 대</strong> 사이로 소형 해치백 모델 수요를 충족</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HMMC는 <strong>Tucson 시리즈 중심의 SUV + HEV 전략</strong>에 <strong>i30</strong>로 유럽 시장 소형차 수요를 병행 대응 중</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HMB':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HMB 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(HB20, Creta SU2b, Creta GSb)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>HB20(BR2)</strong>는 <strong>브라질 내수 시장 중심</strong>으로, <strong>월 2.5~3만 대 수준</strong>의 강한 판매량 유지</li>
                    <li><strong>Creta(SU2b)</strong>는 월 평균 1만 대 초반대로 <strong>SUV 수요에 안정적으로 대응</strong></li>
                    <li><strong>Creta(GSb)</strong>는 상대적으로 적은 수량이지만, <strong>특정 지역 시장 공략용</strong>으로 소량 생산 지속</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HMB 공장은 <strong>HB20 중심의 소형차 전략</strong>을 주력으로 하며, <strong>Creta 시리즈로 SUV 수요</strong>까지 포괄</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HMMI':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HMMI 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(Creta, Stargazer, IONIQ5)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>Creta(SU2id)</strong>는 <strong>월 9천~1만 대 수준</strong>으로 <strong>HMMI 주력 모델</strong>로 활약 중</li>
                    <li><strong>Stargazer(KS)</strong>는 MPV 수요에 대응하며 월 4천~6천 대 내외의 <strong>안정적 생산량</strong> 유지</li>
                    <li><strong>IONIQ5(NE)</strong>는 전기차 수요에 따라 <strong>월 1천 대 이하의 소량 생산</strong>이지만, 친환경차 라인업 강화 목적</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HMMI 공장은 <strong>주력 SUV(Creta)와 MPV(Stargazer)의 안정적 운영</strong>과 함께, <strong>전기차(IONIQ5) 생산 거점</strong>으로의 역할도 병행</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HTBC':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HTBC 공장 월별 판매 트렌드 분석</strong></h5>
                    <p>※ 해당 분석은 <strong>HTBC 공장에서 생산된 전체 차량</strong> 데이터를 기반으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>연간 생산량은 300~500대 수준</strong>으로 규모는 작지만, <strong>하반기(7~10월) 생산 증가세</strong>가 눈에 띔</li>
                    <li><strong>8월 기준 최대 생산량 496대</strong>로 특정 목적의 <strong>소규모 집중 생산</strong> 가능성</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HTBC는 <strong>전략적/지역 특화 목적</strong>의 생산거점 또는 시험 생산 공장으로 추정 가능</p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'Vietnam':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>Vietnam 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>판매량 상위 3개 모델(Accent, Creta, Tucson)</strong>을 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>Accent(HCv)</strong>는 연초(1~3월)에 <strong>2~3천 대 수준의 강세</strong>를 보였으며, 이후 하향 안정세를 유지하며 연중 꾸준한 수요를 기록</li>
                    <li><strong>Creta(SU2v)</strong>는 <strong>1천~1.8천 대 수준의 판매량</strong>을 기록하며 중간 수요를 지속적으로 견인</li>
                    <li><strong>Tucson(NX4v)</strong>는 상반기 부진했지만 <strong>10~11월 급증</strong>하며 연말 전략 차종으로서 존재감을 드러냄</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> Vietnam 공장은 <strong>연초에는 세단(Accent)</strong> 중심의 안정적 수요를 기반으로 생산했으며, <strong>하반기부터 SUV 차종(Creta, Tucson)의 비중이 급격히 확대</strong>된 것으로 판단됨</p>
                    <p>📌 <strong>추가 인사이트:</strong> <span style="color:#5D6D7E;"><em>6~9월 기간 중 일부 모델의 생산량 저조는 글로벌 공급망 이슈 또는 공장 설비 점검 가능성도 고려할 수 있음</em></span></p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'Singapore':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>Singapore 공장 상위 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 아래 분석은 <strong>생산된 전체 3개 모델(IONIQ5, IONIQ6, IONIQ5 Robotaxi)</strong>의 월별 데이터를 기준으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>IONIQ5 (NE)</strong> 모델이 압도적으로 높은 비중을 차지하며, <strong>하반기(7~12월)에 판매량이 급증</strong>해 전기 SUV 라인업의 전략적 우위를 나타냄</li>
                    <li><strong>IONIQ6 (CE)</strong>는 월 평균 10~15대 수준으로, 소규모 세단 전기차 시장 대응 차종으로 활용</li>
                    <li><strong>IONIQ5 Robotaxi (NE R)</strong>는 월 1~2대 수준의 <strong>초기 시험 운영 목적</strong> 생산으로 보이며, 파일럿 프로젝트 형태로 해석 가능</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> Singapore 공장은 <strong>프리미엄 전기 SUV(IONIQ5)를 중심으로 한 고부가가치 라인업</strong>에 집중하고 있으며, <strong>신기술 도입(자율주행 기반)</strong>을 위한 로보택시의 생산 테스트도 병행 중</p>
                    <p>📌 <strong>맞춤형 인사이트:</strong> <span style="color:#5D6D7E;"><em>IONIQ5의 꾸준한 증가 추세는 싱가포르 내 EV 수요 확대 및 친환경 정책 강화의 영향을 반영</em></span></p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'CKD':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>CKD 공장 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 본 분석은 <strong>CKD 공장에서 생산된 2개 모델(PV, CV)</strong>의 월별 판매 추이를 기반으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>PV</strong>(Passenger Vehicle, 승용차) 모델이 <strong>전체 생산량의 대부분</strong>을 차지하며, 월별 평균 <strong>9천 대 이상</strong>으로 꾸준한 수요 유지</li>
                    <li><strong>CV</strong>(Commercial Vehicle, 상용차)는 월별 <strong>100대 내외</strong>로 매우 소량 생산되며, <strong>특정 지역 목적의 수요 대응</strong> 수준</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> CKD 공장은 <strong>승용차 중심의 대량 조립 생산 체계</strong>를 운영하고 있으며, <strong>소규모 상용차 생산</strong>은 보완적 전략으로 해석 가능</p>
                    <p>📌 <strong>맞춤형 인사이트:</strong> <span style="color:#5D6D7E;"><em>조립 방식(CKD: 완성차 부품 수출 후 현지 조립) 특성상, <strong>물류 효율성과 대량 생산이 용이한 승용 모델</strong>에 집중된 것으로 보임</em></span></p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'HMGMA':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>HMGMA 공장 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 본 분석은 <strong>단일 모델 IONIQ5(NEa)</strong>의 월별 판매 추이를 기반으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>1월</strong>에 <strong>1,600대</strong> 이상 출고되며 강한 생산 시작을 보였으나, <strong>2월~11월까지 생산량 0</strong>으로 유지</li>
                    <li><strong>12월</strong>에 <strong>1,000대</strong> 규모로 생산 재개 → 연말 <strong>단기 집중 생산</strong> 가능성</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> HMGMA 공장은 <strong>단일 모델 전기차 생산 중심</strong이며, <strong>간헐적 집중 생산 전략</strong>을 취하는 것으로 해석됨</p>
                    <p>📌 <strong>맞춤형 인사이트:</strong> <span style="color:#5D6D7E;"><em>생산 장비 세팅, 부품 수급, 지역 배정 이슈 등으로 인해 <strong>일시적 가동 중단 또는 배치 변경</strong> 가능성 존재</em></span></p>
                    </div>
                    """, unsafe_allow_html=True)
                elif selected_factory == 'KMX':
                    st.markdown("""
                    <div style="border-left: 6px solid #884EA0; background-color: #F5EEF8; padding: 12px; border-radius: 6px;">
                    <h5>📌 <strong>KMX 공장 차량 모델 판매 트렌드 분석</strong></h5>
                    <p>※ 본 분석은 <strong>등록된 차량 모델 2종(NX4m, HCm)</strong> 중 <strong>실질 생산이 확인된 NX4m</strong> 모델 중심으로 작성되었습니다.</p>
                    <ol>
                    <li><strong>NX4m 모델</strong>은 <strong>상반기(2~5월) 생산 공백</strong> 후, <strong>6월부터 생산 재개</strong></li>
                    <li><strong>7월~10월</strong> 사이 <strong>최대 3,000대 이상</strong>의 출고량 기록 → <strong>하반기 집중형 생산 패턴</strong> 확인</li>
                    <li><strong>HCm 모델</strong>은 연간 생산 실적 없음 → <strong>등록만 되어 있고 미생산</strong> 모델일 가능성</li>
                    </ol>
                    <p><strong>✅ 분석 포인트:</strong> KMX 공장은 <strong>하반기 집중형 생산 스케줄</strong>을 운영 중이며, <strong>NX4m 단일 모델 전담 생산체계</strong>로 해석됨</p>
                    <p>📌 <strong>맞춤형 인사이트:</strong> <span style="color:#5D6D7E;"><em>특정 해외 시장 또는 시즌 수요에 맞춘 <strong>한정형 생산 전략</strong> 가능성 존재</em></span></p>
                    </div>
                    """, unsafe_allow_html=True)

        # 3. 공장별 내수/수출 비율
        with tab3:
            st.subheader("🥧 공장별 내수/수출 비율 or 전체 생산 추이")
            render_page_description("🥧 내수/수출 비율")
            st.divider()

            month_cols = ['1월', '2월', '3월', '4월', '5월', '6월',
                        '7월', '8월', '9월', '10월', '11월', '12월']

            # ✅ 공장 선택
            factories = df_factory["공장명(국가)"].unique().tolist()
            selected_factory = st.selectbox("공장을 선택하세요", factories, key="factory_selector_tab3")

            # ✅ 해당 공장 데이터 필터링
            filtered_df = df_factory[df_factory["공장명(국가)"] == selected_factory]
            sales_types = filtered_df["판매 구분"].unique()

            # ✅ 데이터 총합이 0인지 체크 함수
            def is_data_zero(df):
                return df[month_cols].sum().sum() == 0

            # ✅ 내수/수출 둘 다 있는 경우 → 실제 데이터 존재 여부에 따라 분기 처리
            if set(["내수용", "수출용"]).issubset(sales_types):
                pie_df = filtered_df.groupby("판매 구분")[month_cols].sum().sum(axis=1).reset_index()
                pie_df.columns = ["판매 구분", "합계"]

                # ▶️ 실제 판매량이 존재하는 데이터만 필터링
                pie_df = pie_df[pie_df["합계"] > 0]

                if pie_df.empty:
                    st.warning("⚠️ 해당 공장의 판매량이 0이기 때문에 분석할 수 없습니다.")
                elif len(pie_df) == 1:
                    # 한쪽만 데이터가 있는 경우 → 라인차트
                    sales_type = pie_df["판매 구분"].values[0]
                    target_df = filtered_df[filtered_df["판매 구분"] == sales_type]
                    total_by_month = target_df[month_cols].sum().reset_index()
                    total_by_month.columns = ["월", "판매량"]

                    fig = px.line(total_by_month, x="월", y="판매량", markers=True,
                                title=f"{selected_factory} 월별 판매량 추이 ({sales_type} 기반)")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # 내수/수출 둘 다 판매량 있음 → 파이차트
                    fig = px.pie(pie_df, names="판매 구분", values="합계",
                                title=f"{selected_factory} 내수/수출 비율")
                    st.plotly_chart(fig, use_container_width=True)

            # ✅ 합계만 있는 경우
            elif set(sales_types) == {"합계"}:
                if is_data_zero(filtered_df):
                    st.warning("⚠️ 해당 공장의 판매량이 0이기 때문에 분석할 수 없습니다.")
                else:
                    total_by_month = filtered_df[month_cols].sum().reset_index()
                    total_by_month.columns = ["월", "판매량"]

                    fig = px.line(total_by_month, x="월", y="판매량", markers=True,
                                title=f"{selected_factory} 월별 판매량 추이 (합계 기반)")
                    st.plotly_chart(fig, use_container_width=True)

            # ✅ 수출용만 있는 경우
            elif set(sales_types) == {"수출용"}:
                if is_data_zero(filtered_df):
                    st.warning("⚠️ 해당 공장의 판매량이 0이기 때문에 분석할 수 없습니다.")
                else:
                    total_by_month = filtered_df[month_cols].sum().reset_index()
                    total_by_month.columns = ["월", "판매량"]

                    fig = px.line(total_by_month, x="월", y="판매량", markers=True,
                                title=f"{selected_factory} 월별 판매량 추이 (수출용 기반)")
                    st.plotly_chart(fig, use_container_width=True)

            # ✅ 내수용만 있는 경우
            elif set(sales_types) == {"내수용"}:
                if is_data_zero(filtered_df):
                    st.warning("⚠️ 해당 공장의 판매량이 0이기 때문에 분석할 수 없습니다.")
                else:
                    total_by_month = filtered_df[month_cols].sum().reset_index()
                    total_by_month.columns = ["월", "판매량"]

                    fig = px.line(total_by_month, x="월", y="판매량", markers=True,
                                title=f"{selected_factory} 월별 판매량 추이 (내수용 기반)")
                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.warning("⚠️ 해당 공장의 판매량이 0이기 때문에 분석할 수 없습니다.")

            st.divider()

            # ✅ 각 공장별 차트 분석 셜명
            if selected_factory == 'HMI':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HMI 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>내수 비중 79.1%</strong>, <strong>수출 비중 20.9%</strong>로 <strong>인도 내수시장 중심</strong의 생산 구조</li>
                <li>전체 생산량의 4분의 3 이상이 현지 시장 소비용 → <strong>지역 수요 대응형</strong> 공장으로 운영 중</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HMI는 인도 로컬 시장에 최적화된 <strong>내수 특화 생산 거점</strong>으로, 수출보다는 국내 안정적 공급에 초점</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HAOS':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HAOS 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>수출 비중이 83.3%</strong>로, 전체 생산량 대부분이 <strong>해외 수출용</strong>으로 운영되는 공장</li>
                <li><strong>내수용 비중은 16.7%</strong>로 제한적이며, <strong>글로벌 시장 대응 중심의 생산 전략</strong>이 특징</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HAOS는 명확한 <strong>수출 특화 공장</strong>으로, 다수의 수출국 공급을 위한 전략적 생산 거점 역할 수행</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory  == 'BHMC':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>BHMC 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>내수 비중이 88.1%</strong>로, 대부분의 차량이 <strong>중국 내수시장</strong>을 대상으로 생산됨</li>
                <li><strong>수출 비중은 11.9%</strong>에 불과하여, 해외 시장보다는 <strong>현지 공급 중심</strong>의 전략</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> BHMC는 수출보다는 <strong>중국 내 내수 수요 대응형 생산거점</strong>으로 운영되고 있음</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HMMA':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HMMA 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>내수 비중이 94.4%</strong>로, 거의 모든 생산량이 <strong>미국 내수 시장</strong>에 공급됨</li>
                <li><strong>수출 비중은 5.57%</strong>에 불과하여, 해외 공급은 제한적으로 운영 중</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HMMA는 <strong>현지 소비 중심</strong>의 전략적 내수 거점으로, 미국 내 수요 대응을 위한 <strong>고정 공급 허브</strong> 역할을 수행</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HMMC' :
                st.markdown("""
                <div style="border-left: 6px solid #117A65; background-color: #E8F8F5; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HMMC 공장 월별 판매량 추이 분석</strong></h5>
                <p>※ 본 데이터는 <strong>수출 기준</strong>으로 제공된 월별 총 판매량 기반 분석입니다.</p>
                <ol>
                <li><strong>1월 판매량(약 78,000대)</strong>이 연중 최고치를 기록</li>
                <li><strong>7~8월</strong>에는 계절성 영향으로 <strong>최저점(약 47,000대)</strong>까지 하락</li>
                <li><strong>9~10월</strong> 이후 가을부터는 회복세로 전환되어 안정적 흐름</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HMMC는 <strong>수출 중심의 대량 생산 공장</strong>으로, <strong>계절성과 분기별 수요 패턴</strong>이 뚜렷하게 나타남</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HMB':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HMB 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>내수 비중이 91.9%</strong>로, 대부분의 생산량이 <strong>현지(브라질) 시장</strong>에 집중됨</li>
                <li><strong>수출 비중은 8.07%</strong>로 제한적이며, 주변 남미 국가로의 소량 수출 추정 가능</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HMB는 브라질을 중심으로 한 <strong>내수 특화형 공장</strong>으로, <strong>지역 시장 안정 공급</strong>이 주된 전략으로 보임</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HMMI':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HMMI 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>수출 비중이 69.5%</strong>, <strong>내수 비중 30.5%</strong>로 <strong>수출 중심 + 내수 병행</strong> 전략을 채택</li>
                <li>다양한 시장을 대상으로 생산이 이루어지는 <strong>복합형 생산 거점</strong>으로 분석 가능</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HMMI는 <strong>글로벌 수출 확대와 인도네시아 내수 대응</strong>을 동시에 고려한 <strong>혼합형 전략 공장</strong>으로 운영됨</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HTBC':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HTBC 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>수출 비중 58.5%</strong>, <strong>내수 비중 41.5%</strong>로 <strong>균형 잡힌 수출 중심 공장</strong></li>
                <li>수출이 과반을 넘지만, 내수도 무시할 수 없는 수준으로 <strong>복합형 운영 전략</strong>이 적용된 것으로 분석</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> HTBC는 <strong>수출 확대와 동시에 내수 대응</strong>을 위한 <strong>혼합형 공장</strong>으로, 전략 유연성이 높은 운영 형태를 보여줌</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'Vietnam':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>Vietnam 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>내수 비중 97.2%</strong>로, 사실상 <strong>전량 현지 시장</strong> 공급을 위한 생산 구조</li>
                <li><strong>수출은 0.4%</strong>, <strong>합계 항목 2.3%</strong>로 해외 시장 대응은 거의 이루어지지 않음</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> Vietnam 공장은 <strong>현지 수요 충족을 위한 내수 전용 공장</strong>으로, <strong>공급 안정성과 생산 최적화</strong>에 초점을 둔 구조로 파악됨</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'Singapore':
                st.markdown("""
                <div style="border-left: 6px solid #2980B9; background-color: #EBF5FB; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>Singapore 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>수출 51.2%</strong>, <strong>내수 48.8%</strong>로 <strong>거의 완전한 균형형 생산</strong> 구조</li>
                <li>내수와 수출을 동시에 고려한 <strong>전략 유연성이 높은 운영 방식</strong></li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> Singapore 공장은 <strong>현지 공급과 해외 시장 대응을 동시 수행</strong>하는 <strong>하이브리드 전략 공장</strong>으로 분류 가능</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'CKD':
                st.markdown("""
                <div style="border-left: 6px solid #117A65; background-color: #E8F8F5; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>CKD 공장 월별 판매량 추이 분석</strong></h5>
                <p>※ 본 데이터는 <strong>내수/수출 구분 없이 '합계 기준'</strong>으로 제공된 월별 판매 실적입니다.</p>
                <ol>
                <li><strong>1월 판매량(약 13,000대)</strong>가 연중 최고치로 출발</li>
                <li><strong>2월 일시적 저조(약 7,400대)</strong> 이후 <strong>9~10천 대 수준 유지</strong></li>
                <li>연간 전체적으로 <strong>변동 폭은 크지 않으며</strong>, <strong>계단식 안정 흐름</strong>을 유지</li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> CKD 공장은 <strong>연초 집중 생산 이후 연중 고른 생산</strong>을 통해 공급 안정성을 추구하는 것으로 분석됨</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'HMGMA':
                st.markdown("""
                <div style="border-left: 6px solid #117A65; background-color: #E8F8F5; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>HMGMA 공장 월별 판매 트렌드 분석</strong></h5>
                <p>※ 본 데이터는 내수/수출을 구분하였으나, 실제 판매 실적은 <strong>‘내수용’ 기준</strong>만 존재합니다.</p>
                <ol>
                <li>1월 판매량 <strong>1,623대</strong>, 12월 <strong>1,006대</strong> 기록 – <strong>특정 시점 집중 생산</strong></li>
                <li>2월~11월 <strong>판매량 0</strong> – <strong>생산 또는 공급 중단 상태</strong> 추정</li>
                <li>연간 기준 <strong>판매 빈도 불규칙</strong> – <strong>상시 운영보다는 비정기적 생산 패턴</strong></li>
                </ol>
                <p>✅ <strong>분석 포인트:</strong> HMGMA 공장은 <strong>한정된 기간에만 생산이 집중</strong>되며, <strong>수출 실적이 없는 내수 특화형 공장</strong>으로 해석 가능</p>
                </div>
                """, unsafe_allow_html=True)
            elif selected_factory == 'KMX':
                st.markdown("""
                <div style="border-left: 6px solid #117A65; background-color: #E8F8F5; padding: 12px; border-radius: 6px;">
                <h5>📌 <strong>KMX 공장 내수/수출 비율 분석</strong></h5>
                <ol>
                <li><strong>100% 수출 비중</strong>으로, <strong>내수 판매는 전혀 없음</strong></li>
                <li>글로벌 수출 공급을 전담하는 <strong>수출 중심 생산기지</strong></li>
                </ol>
                <p><strong>✅ 분석 포인트:</strong> KMX는 <strong>오직 해외 시장만을 타겟</strong>으로 하는 <strong>완전 수출형 공장</strong>으로 운영 중</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()

            # 현대 지역별 수출실적 분석 요약표 작업
            
            df_factory_melted =  df_factory.melt(id_vars=['공장명(국가)', '차량 모델', '판매 구분', '연도'], 
                                    value_vars=["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"] ,
                                    var_name='월', value_name='판매량')
                    
            st.subheader("📌 현대 공장별 내수/수출별 판매량 통계 요약")
            st.write('')

            내수_수출_피벗 = df_factory_melted.pivot_table(
                    index='공장명(국가)',
                    columns='판매 구분',
                    values='판매량',
                    aggfunc='sum',
                    fill_value=0
                )
            
            # 스타일링을 위해 복사본 생성
            내수_수출_styled = 내수_수출_피벗.copy()

            # 스타일링 적용
            styled_내수_수출 = (
                내수_수출_styled.style
                .format('{:,.0f}')  # 숫자 포맷
                .background_gradient(cmap='Blues')
            )
            st.dataframe(styled_내수_수출, use_container_width=True)    

        
        st.markdown("</div>", unsafe_allow_html=True)