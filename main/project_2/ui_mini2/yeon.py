import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
from PIL import Image
import yfinance as yf
import matplotlib.colors as mcolors

# CSS 스타일 (간결한 버전)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    .highlight-box {
        background-color: #f0f7ff;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4a6fa5;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
    .neutral {
        color: #ffc107;
        font-weight: bold;
    }
    .section-title {
        font-size: 1.5rem;
        color: #2a3f5f;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e6e6e6;
    }
    .chart-container {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def reset_form():
    st.session_state.clear()

def get_country_flag(country_name):
    flag_mapping = {
        '미국': '🇺🇸', '중국': '🇨🇳', '일본': '🇯🇵', '독일': '🇩🇪',
        '영국': '🇬🇧', '프랑스': '🇫🇷', '한국': '🇰🇷', '인도': '🇮🇳',
        '브라질': '🇧🇷', '캐나다': '🇨🇦', '호주': '🇦🇺', '이탈리아': '🇮🇹',
        '스페인': '🇪🇸', '멕시코': '🇲🇽', '인도네시아': '🇮🇩', '터키': '🇹🇷',
        '네덜란드': '🇳🇱', '스위스': '🇨🇭', '사우디아라비아': '🇸🇦', '아르헨티나': '🇦🇷'
    }
    return flag_mapping.get(country_name, '')

def fetch_gdp_data(country_name):
    country_code_map = {
        '미국': 'USA', '중국': 'CHN', '일본': 'JPN', '독일': 'DEU',
        '영국': 'GBR', '프랑스': 'FRA', '한국': 'KOR', '인도': 'IND',
        '브라질': 'BRA', '캐나다': 'CAN', '호주': 'AUS', '이탈리아': 'ITA',
        '스페인': 'ESP', '멕시코': 'MEX', '인도네시아': 'IDN', '터키': 'TUR',
        '네덜란드': 'NLD', '스위스': 'CHE', '사우디아라비아': 'SAU', '아르헨티나': 'ARG'
    }
    country_code = country_code_map.get(country_name, None)
    if country_code:
        try:
            url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1 and data[1]:
                    return data[1][0]['value'] / 1e9  # 단위: 10억 달러
        except:
            pass
    return None

def get_change_reason(change_rate):
    if change_rate > 30:
        return {
            "text": "📈 급격한 증가 (30% 초과)",
            "reason": "신규 시장 진출 성공, 경쟁사 제품 리콜, 현지 통화 강세, 정부 인센티브 확대, 신제품 출시",
            "suggestion": "생산량 확대 고려, 서비스 네트워크 강화, 가격 인상 검토",
            "class": "positive"
        }
    elif 15 < change_rate <= 30:
        return {
            "text": "📈 강한 증가 (15%~30%)",
            "reason": "현지 경제 호황, 브랜드 인지도 상승, 모델 라인업 강화, 환율 영향 (원화 약세), 계절적 수요 증가",
            "suggestion": "재고 관리 강화, 마케팅 투자 유지, 고객 만족도 조사 실시",
            "class": "positive"
        }
    elif 5 < change_rate <= 15:
        return {
            "text": "📈 안정적 증가 (5%~15%)",
            "reason": "꾸준한 마케팅 효과, 소폭 가격 경쟁력 향상, 품질 인식 개선, 소비자 신뢰 상승, 부분 모델 변경 효과",
            "suggestion": "현재 전략 유지, 고객 피드백 수집, 경쟁사 동향 모니터링",
            "class": "positive"
        }
    elif -5 <= change_rate <= 5:
        return {
            "text": "➡️ 안정 유지 (-5%~5%)",
            "reason": "시장 상황 유지, 경쟁사 유사 성과, 계절 영향 없음, 경제 상황 중립, 마케팅 효과 중립",
            "suggestion": "시장 변화 모니터링, 고객 설문 실시, 전략 재검토",
            "class": "neutral"
        }
    elif -15 <= change_rate < -5:
        return {
            "text": "📉 감소 추세 (-15%~-5%)",
            "reason": "경제 불황, 경쟁사 강세, 환율 영향, 모델 노후화, 수요 감소",
            "suggestion": "프로모션 강화, 가격 경쟁력 분석, 모델 업데이트 계획 수립",
            "class": "negative"
        }
    elif -30 <= change_rate < -15:
        return {
            "text": "📉 급격한 감소 (-30%~-15%)",
            "reason": "규제 강화, 정치 불안, 딜러 파산, 경쟁사 할인, 품질 문제 발생",
            "suggestion": "사정 긴급 점검, 위기 대응 팀 구성, 긴급 마케팅 전략 수립, 본사 지원 검토",
            "class": "negative"
        }
    else:
        return {
            "text": "📉 위험한 감소 (-30% 미만)",
            "reason": "운영 위기, 모델 판매 중단, 경제 위기/전쟁, 시장 점유율 급증, 브랜드 이미지 손상",
            "suggestion": "긴급 대책 회의 소집, 현지 실사 파견, 구조 조정 검토, 시장 철수 검토",
            "class": "negative"
        }

def create_tab_buttons():
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "📊 단일 국가 예측"
    cols = st.columns(2)
    tabs = ["📊 단일 국가 예측", "🌍 다중 국가 비교"]
    for i, tab in enumerate(tabs):
        with cols[i]:
            if st.button(tab, key=f"tab_{i}",
                         type="primary" if st.session_state.current_tab == tab else "secondary",
                         use_container_width=True):
                st.session_state.current_tab = tab
    return st.session_state.current_tab

def create_gdp_export_scatter(df, selected_country):
    latest_year = df['날짜'].dt.year.max()
    data = df[df['날짜'].dt.year == latest_year].groupby('국가명')['수출량'].sum().reset_index()
    data['GDP'] = data['국가명'].apply(lambda x: fetch_gdp_data(x) or 0)
    fig = px.scatter(data, x='GDP', y='수출량', size='수출량', color='국가명',
                     title="GDP 대비 수출량 분석",
                     labels={'GDP': 'GDP (10억$)', '수출량': '총 수출량'},
                     size_max=60)
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(hovermode="closest")
    return fig

def run_yeon():
    # 모델 및 데이터 로드


    model = joblib.load("main/project_2/models_mini2/h_lgbm_tuned_model.pkl")
    scaler = joblib.load("main/project_2/models_mini2/h_scaler.pkl")
    model_columns = joblib.load("main/project_2/models_mini2/h_model_columns.pkl")
    df = pd.read_csv("main/project_2/data_mini2/현대.csv")


    st.title("🚗 기후별 수출량 분석 대시보드")
    st.markdown("""
    <div style="margin-bottom: 2rem; color: #666;">
        기아 자동차의 글로벌 수출량을 분석하고 예측하는 대시보드입니다. 단일 국가 예측과 다중 국가 비교 기능을 제공합니다.
    </div>
    """, unsafe_allow_html=True)
    
    # 데이터 전처리
    id_vars = ['국가명', '연도', '기후대', 'GDP', '차종 구분', '차량 구분']
    month_cols = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']
    df_long = pd.melt(df, id_vars=id_vars, value_vars=month_cols, var_name='월', value_name='수출량')
    df_long['월'] = df_long['월'].str.replace('월','').astype(int)
    df_long['날짜'] = pd.to_datetime(df_long['연도'].astype(str) + '-' + df_long['월'].astype(str) + '-01')
    df_long = df_long.sort_values(by=['국가명','날짜'])
    latest_year = df_long["날짜"].dt.year.max()
    
    current_tab = create_tab_buttons()
    
    if 'prediction_made' not in st.session_state:
        st.session_state.prediction_made = False
    if 'comparison_made' not in st.session_state:
        st.session_state.comparison_made = False
    
    if current_tab == "📊 단일 국가 예측":
        st.markdown("### 📊 단일 국가 수출량 예측")
        
        with st.expander("🔍 분석 조건 설정", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_climate = st.selectbox("🌍 기후대", sorted(df["기후대"].unique()), key='climate_select')
                filtered_countries = sorted(df[df["기후대"] == selected_climate]["국가명"].unique())
                selected_country = st.selectbox("🏳️ 국가명", filtered_countries, key='country_select')
                target_year = st.number_input("📅 예측 연도", min_value=2000, max_value=datetime.now().year+5,
                                              value=datetime.now().year, key='year_select')
                target_month = st.number_input("📆 예측 월", min_value=1, max_value=12,
                                               value=datetime.now().month, key='month_select')
            with col2:
                selected_car_type = st.selectbox("🚘 차종 구분", sorted(df["차종 구분"].unique()), key='car_type_select')
                if "차종" in df.columns:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차종"].unique())
                else:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차량 구분"].unique())
                selected_car = st.selectbox("🚗 차량 구분", filtered_car_options, key='car_select')
        
        col1, col2 = st.columns([4,1])
        with col1:
            predict_btn = st.button("🔮 예측 실행", type="primary", use_container_width=True)
        with col2:
            reset_btn = st.button("🔄 초기화", on_click=reset_form, use_container_width=True)
        
        if predict_btn:
            st.session_state.prediction_made = True
        
        if st.session_state.prediction_made or ('prediction_result' in st.session_state and not reset_btn):
            # 단일 국가 데이터 (AND 조건)
            country_data = df_long[
                (df_long["국가명"] == selected_country) |
                (df_long["차종 구분"] == selected_car_type) |
                (df_long["차량 구분"] == selected_car)
            ].sort_values(by="날짜", ascending=False)
            
            if country_data.empty:
                st.warning("⚠️ 선택한 조건에 맞는 데이터가 없습니다. 다른 조건을 선택해주세요.")
                st.session_state.prediction_made = False
                return
            
            if predict_btn:
                auto_current_export = country_data["수출량"].iloc[0]
                auto_prev_export = country_data["수출량"].iloc[1] if len(country_data) >= 2 else 0.0
                prev_year_data = df_long[
                    (df_long["국가명"] == selected_country) &
                    (df_long["차종 구분"] == selected_car_type) &
                    (df_long["차량 구분"] == selected_car) &
                    (df_long["날짜"].dt.year == target_year-1) |
                    (df_long["날짜"].dt.month == target_month)
                ]
                prev_year_export = prev_year_data["수출량"].values[0] if not prev_year_data.empty else 0
                input_data = {
                    "수출량": [auto_current_export],
                    "전월_수출량": [auto_prev_export],
                    "연도": [target_year],
                    "월": [target_month],
                    "GDP": [df[df["국가명"] == selected_country]["GDP"].iloc[0]],
                    "국가명": [selected_country],
                    "기후대": [selected_climate],
                    "차종 구분": [selected_car_type],
                    "차량 구분": [selected_car]
                }
                input_df = pd.DataFrame(input_data)
                input_encoded = pd.get_dummies(input_df, columns=["국가명", "기후대", "차종 구분", "차량 구분"])
                input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)
                input_scaled = scaler.transform(input_encoded)
                prediction = model.predict(input_scaled)[0]
                st.session_state.prediction_result = {
                    'selected_country': selected_country,
                    'selected_car_type': selected_car_type,
                    'selected_car': selected_car,
                    'auto_current_export': auto_current_export,
                    'auto_prev_export': auto_prev_export,
                    'prev_year_export': prev_year_export,
                    'prediction': prediction,
                    'target_year': target_year,
                    'target_month': target_month,
                    'selected_climate': selected_climate
                }
            else:
                result = st.session_state.prediction_result
                selected_country = result['selected_country']
                selected_car_type = result['selected_car_type']
                selected_car = result['selected_car']
                auto_current_export = result['auto_current_export']
                auto_prev_export = result['auto_prev_export']
                prev_year_export = result['prev_year_export']
                prediction = result['prediction']
                target_year = result['target_year']
                target_month = result['target_month']
                selected_climate = result['selected_climate']
            
            # 예측 결과 계산
            yearly_change = ((prediction - prev_year_export) / prev_year_export * 100) if prev_year_export != 0 else 0
            change_info = get_change_reason(yearly_change)
            gdp_value = fetch_gdp_data(selected_country) or df[df["국가명"] == selected_country]["GDP"].iloc[0]
            st.write("")
            st.write("")
            # 예측 결과 표시
            st.markdown("### 📌 예측 결과 요약")

            st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%); 
                border-radius: 12px; padding: 1.5rem; margin: 1.5rem 0;
                border-left: 5px solid #4a6fa5;">
        <h3 style="color: #2a3f5f; margin-top: 0;">✨ 핵심 예측 지표</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
            <div style="background: white; border-radius: 10px; padding: 1.5rem; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
                <div style="font-size: 1rem; color: #666; margin-bottom: 0.5rem;">예상 수출량</div>
                <div style="font-size: 2.5rem; font-weight: bold; color: #2a3f5f;">
                    {prediction:,.0f}
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    {target_year}년 {target_month}월 예측
                </div>
            </div>
            <div style="background: white; border-radius: 10px; padding: 1.5rem; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;">
                <div style="font-size: 1rem; color: #666; margin-bottom: 0.5rem;">전년 동월 대비</div>
                <div style="font-size: 2.5rem; font-weight: bold; color: {color};">
                    {yearly_change:+.1f}%
                </div>
                <div style="font-size: 0.9rem; color: #666;">
                    {prev_year_export:,.0f} → {prediction:,.0f}
                </div>
            </div>
        </div>
    </div>
    """.format(
        prediction=prediction,
        target_year=target_year,
        target_month=target_month,
        yearly_change=yearly_change,
        prev_year_export=prev_year_export,
        color="green" if yearly_change >= 5 else ("red" if yearly_change <= -5 else "orange")
    ), unsafe_allow_html=True)






            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 국가</div>
                    <div style="font-size:1.2rem; font-weight:bold;">{get_country_flag(selected_country)} {selected_country}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 차량</div>
                    <div style="font-size:1.2rem; font-weight:bold;">{selected_car_type} - {selected_car}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 기후대</div>
                    <div style="font-size:1.2rem; font-weight:bold;">{selected_climate}</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")   
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">예측 수출량</div>
                    <div style="font-size:1.5rem; font-weight:bold;">{prediction:,.0f}</div>
                    <div style="font-size:0.9rem;">{target_year}년 {target_month}월</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">전년 동월 대비</div>
                    <div style="font-size:1.5rem; font-weight:bold; class="{change_info['class']}">{yearly_change:.1f}%</div>
                    <div style="font-size:0.9rem;">{change_info['text']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.9rem; color:#666;">국가 GDP</div>
                    <div style="font-size:1.5rem; font-weight:bold;">{gdp_value:,.1f}</div>
                    <div style="font-size:0.9rem;">10억 달러</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            # 분석 인사이트 섹션
            st.markdown("### 🔍 분석 인사이트")
            with st.container():
                st.markdown(f"""
                <div class="highlight-box">
                    <h4>📈 변화 원인 분석</h4>
                    <p><strong>{change_info['text']}</strong></p>
                    <p><strong>주요 원인:</strong> {change_info['reason']}</p>
                    <p><strong>제안 사항:</strong> {change_info['suggestion']}</p>
                </div>
                """, unsafe_allow_html=True)
            st.write("")
            st.write("")
            # 차트 분석 섹션
            st.write("")
            st.write("")
            st.markdown("### 📊 차트 분석")
            
            # 첫 번째 행 차트
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 기후대별 수출량 비교")
                climate_data = df_long[
                    (df_long["국가명"] == selected_country) |
                    (df_long["차종 구분"] == selected_car_type) |
                    (df_long["차량 구분"] == selected_car) |
                    (df_long["날짜"].dt.year == target_year-1)
                ].groupby("기후대")["수출량"].sum().reset_index()
                
                if not climate_data.empty:
                    fig_climate = px.bar(
                        climate_data,
                        x="기후대",
                        y="수출량",
                        title=f"{selected_car_type} - {selected_car} 기후대별 총 수출량",
                        labels={"수출량": "총 수출량", "기후대": "기후대"},
                        height=400,
                        color="기후대",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_climate.update_layout(showlegend=False)
                    st.plotly_chart(fig_climate, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 각 기후대에서 선택한 차량의 총 수출량을 비교  
                    - 높은 막대는 해당 기후대에서 수출이 활발함을 의미  
                    - 기후 특성에 따른 수출 패턴 파악 가능
                    """)
                else:
                    st.warning("기후대별 데이터가 없습니다.")
            
            with col2:
                st.markdown("#### GDP 대비 수출량")
                bubble_fig = create_gdp_export_scatter(df_long, selected_country)
                st.plotly_chart(bubble_fig, use_container_width=True)
                st.caption("""
                    **해석 방법:**  
                    - X축: 국가 GDP (10억 달러)  
                    - Y축: 총 수출량  
                    - 버블 크기: 수출량 규모  
                    - 선택 국가는 강조 표시됨  
                    - GDP 대비 수출 효율성 분석 가능
                    """)
            
            # 두 번째 행 차트
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 차량 종류별 수출 비중")
                country_car_data = df_long[
                    (df_long["국가명"] == selected_country) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby(["차종 구분", "차량 구분"])["수출량"].sum().reset_index()
                
                if not country_car_data.empty:
                    country_car_data = country_car_data.sort_values("수출량", ascending=False).head(10)
                    fig_pie = px.pie(country_car_data, names="차량 구분", values="수출량",
                                     title=f"{selected_country}의 차량 종류별 수출량 비중",
                                     height=400, color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    fig_pie.update_layout(showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 선택 국가에서 어떤 차량이 많이 수출되는지 비중 확인  
                    - 전체 판매에서 차량별 점유율 파악  
                    - 주력 모델과 마이너 모델 식별 가능
                    """)
                else:
                    st.warning("차량 종류별 데이터가 없습니다.")
            
            with col2:
                st.markdown("#### 국가별 수출량 순위")
                car_data = df_long[
                    ((df_long["차종 구분"] == selected_car_type) | (df_long["차량 구분"] == selected_car)) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby("국가명")["수출량"].sum().reset_index()
                
                if not car_data.empty:
                    fig_bar = px.bar(
                        car_data,
                        x="국가명",
                        y="수출량",
                        title=f"{selected_car_type} - {selected_car} 국가별 수출량",
                        labels={"수출량": "총 수출량", "국가명": "국가명"},
                        height=400,
                        color="국가명",
                        color_discrete_sequence=px.colors.qualitative.Vivid
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 선택 차량의 국가별 수출량 순위  
                    - 글로벌 시장에서의 상대적 위치 파악  
                    - 경쟁 국가와의 비교 가능  
                    - 높은 막대는 주요 시장을 의미
                    """)
                else:
                    st.warning("국가별 데이터가 없습니다.")
    
    elif current_tab == "🌍 다중 국가 비교":
        st.markdown("### 🌍 다중 국가 비교 분석")
        
        with st.expander("🔍 비교 조건 설정", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_countries = st.multiselect("비교할 국가 선택",
                                                    sorted(df["국가명"].unique()),
                                                    default=sorted(df["국가명"].unique())[:3],
                                                    key='multi_country_select')
                if len(selected_countries) < 2:
                    st.warning("최소 2개 국가를 선택해주세요.")
                    st.stop()
            with col2:
                selected_car_type = st.selectbox("🚘 차종 구분", sorted(df["차종 구분"].unique()), key='multi_car_type_select')
                if "차종" in df.columns:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차종"].unique())
                else:
                    filtered_car_options = sorted(df[df["차종 구분"] == selected_car_type]["차량 구분"].unique())
                selected_car = st.selectbox("🚗 차량 구분", filtered_car_options, key='multi_car_select')
            
            col1, col2 = st.columns([4,1])
            with col1:
                compare_btn = st.button("🔍 비교하기", type="primary", use_container_width=True)
            with col2:
                reset_btn = st.button("🔄 초기화", on_click=reset_form, use_container_width=True)
        
        if compare_btn:
            st.session_state.comparison_made = True
        

           



        if st.session_state.comparison_made or ('multi_comparison_result' in st.session_state and not reset_btn):
            if compare_btn:
                filtered_data = df_long[
                    (df_long["국가명"].isin(selected_countries)) |
                    ((df_long["차종 구분"] == selected_car_type) & (df_long["차량 구분"] == selected_car)) &
                    (df_long["날짜"].dt.year == latest_year)
                ]
                if filtered_data.empty:
                    st.warning("⚠️ 선택한 조건에 맞는 데이터가 없습니다. 다른 조건을 선택해주세요.")
                    st.stop()
                st.session_state.multi_comparison_result = {
                    'filtered_data': filtered_data,
                    'selected_countries': selected_countries,
                    'selected_car_type': selected_car_type,
                    'selected_car': selected_car
                }
            else:
                result = st.session_state.multi_comparison_result
                filtered_data = result['filtered_data']
                selected_countries = result['selected_countries']
                selected_car_type = result['selected_car_type']
                selected_car = result['selected_car']
            
            # 요약 정보 표시
            st.markdown("### 📌 비교 요약")

    

            summary_data = filtered_data.groupby("국가명")["수출량"].sum().reset_index().sort_values("수출량", ascending=False)
            
            cols = st.columns(len(selected_countries))
            for idx, (_, row) in enumerate(summary_data.iterrows()):
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:1rem; font-weight:bold;">{get_country_flag(row['국가명'])} {row['국가명']}</div>
                        <div style="font-size:1.2rem;">{row['수출량']:,.0f}</div>
                        <div style="font-size:0.8rem;">총 수출량</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 차트 분석 섹션
            st.markdown("### 📊 비교 차트")
            
            # 첫 번째 행 차트
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 국가별 수출량 비교")
                fig_bar = px.bar(summary_data,
                                 x="국가명", y="수출량",
                                 title=f"{selected_car_type} - {selected_car} 국가별 수출량",
                                 labels={"수출량": "총 수출량", "국가명": "국가명"},
                                 height=400, color="국가명",
                                 color_discrete_sequence=px.colors.qualitative.Vivid)
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
                st.caption("""
                **해석 방법:**  
                - 선택 국가들의 총 수출량을 직관적으로 비교  
                - 막대 높이로 시장 규모 파악  
                - 상대적 순위와 격차 확인 가능  
                - 주요 시장 식별에 유용
                """)
            
            with col2:
                st.markdown("#### 차량 종류별 수출 분포")
                heatmap_data = df_long[
                    (df_long["국가명"].isin(selected_countries)) &
                    (df_long["날짜"].dt.year == latest_year)
                ].groupby(["국가명", "차량 구분"])["수출량"].sum().reset_index()
                
                if not heatmap_data.empty:
                    fig_heat = px.density_heatmap(heatmap_data,
                                                  x="국가명",
                                                  y="차량 구분",
                                                  z="수출량",
                                                  title=f"국가별 차량 종류별 수출량",
                                                  height=400,
                                                  color_continuous_scale='Viridis')
                    st.plotly_chart(fig_heat, use_container_width=True)
                    st.caption("""
                    **해석 방법:**  
                    - 국가별로 어떤 차량이 많이 수출되는지 시각화  
                    - 진한 색상은 높은 수출량을 의미  
                    - 국가별 선호 차량 패턴 파악 가능  
                    - 제품 포트폴리오 전략 수립에 활용
                    """)
                else:
                    st.warning("히트맵 생성에 필요한 데이터가 없습니다.")
            
            # 두 번째 행 차트
            st.markdown("#### 월별 수출량 추이 비교")
            monthly_data = filtered_data.groupby(['국가명', '월'])['수출량'].mean().reset_index()
            fig_line = px.line(monthly_data,
                               x="월", y="수출량", color="국가명",
                               title=f"{selected_car_type} - {selected_car} 국가별 월별 수출량 추이",
                               labels={"수출량": "평균 수출량", "월": "월"},
                               height=400, color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig_line, use_container_width=True)
            st.caption("""
            **해석 방법:**  
            - 국가별 월별 수출 패턴 비교  
            - 계절적 변동성 분석  
            - 추세선을 통해 성장/감소 추세 파악  
            - 특정 시기의 급변동 포인트 확인  
            - 마케팅 캠페인 효과 측정에 활용
            """)

